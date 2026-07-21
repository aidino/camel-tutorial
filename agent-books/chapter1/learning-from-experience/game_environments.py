"""
Trò chơi săn tìm kho báu dựa trên văn bản với các cơ chế ẩn. 
Lấy cảm hứng từ những hiểu biết của Shunyu Yao về lý luận và khả năng tổng quát hóa trong AI.

"""

import random
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


# === Định nghĩa các kiểu dữ liệu cơ bản cho trò chơi ===

class ItemType(Enum):
    """Phân loại các loại vật phẩm trong trò chơi.
    
    Mỗi vật phẩm thuộc một trong các loại sau, quyết định cách
    người chơi có thể tương tác với chúng (dùng chìa khóa để mở cửa,
    dùng vũ khí để chiến đấu, v.v.)
    """
    KEY = "chìa khóa"
    WEAPON = "vũ khí"
    TREASURE = "kho báu"
    TOOL = "công cụ"
    POTION = "thuốc"


@dataclass
class Item:
    """Đại diện cho một vật phẩm trong trò chơi.
    
    Attributes:
        name: Tên định danh của vật phẩm (dùng trong logic matching, giữ tiếng Anh)
        item_type: Loại vật phẩm (ItemType enum)
        description: Mô tả hiển thị cho người chơi
        properties: Các thuộc tính bổ sung (ví dụ: giá trị kho báu)
    """
    name: str
    item_type: ItemType
    description: str
    properties: Dict[str, any] = field(default_factory=dict)


@dataclass
class Room:
    """Đại diện cho một phòng trong thế giới trò chơi.
    
    Mỗi phòng có tên, mô tả, danh sách vật phẩm, các lối ra,
    và có thể có lính canh chặn đường.
    
    Attributes:
        name: Tên định danh phòng (dùng làm key trong dict, giữ tiếng Anh)
        description: Mô tả phòng hiển thị cho người chơi
        items: Danh sách vật phẩm có trong phòng
        exits: Các lối ra (hướng -> tên phòng đích)
        locked_exits: Các lối ra bị khóa (hướng -> tên chìa khóa cần thiết)
        has_guard: Phòng có lính canh hay không
        guard_defeated: Lính canh đã bị đánh bại chưa
    """
    name: str
    description: str
    items: List[Item] = field(default_factory=list)
    exits: Dict[str, str] = field(default_factory=dict)  # hướng -> tên_phòng
    locked_exits: Dict[str, str] = field(default_factory=dict)  # hướng -> chìa_khóa_cần_thiết
    has_guard: bool = False
    guard_defeated: bool = False


# === Class chính điều khiển trò chơi ===

class TreasureHuntGame:
    """
    Trò chơi dựa trên văn bản với các cơ chế ẩn mà agent phải tự khám phá:
    1. Các chìa khóa có màu sắc tương ứng mở các cánh cửa cùng màu
    2. Lính canh chặn đường đến kho báu và cần vũ khí phù hợp để đánh bại
    3. Một số vật phẩm có thể kết hợp để tạo vật phẩm mới (chế tạo ẩn)
    4. Thuốc cung cấp khả năng tạm thời
    """
    
    def __init__(self, seed: int = None, stochastic: bool = False):
        """
        Khởi tạo môi trường trò chơi.
        
        Args:
            seed: Hạt giống ngẫu nhiên để đảm bảo tính tái lập
            stochastic: Nếu True, thêm các yếu tố ngẫu nhiên vào trò chơi
        """
        if seed is not None:
            random.seed(seed)
        
        self.stochastic = stochastic
        self.random_state = random.Random(seed) if stochastic else None
        
        # Khởi tạo trạng thái trò chơi
        self.rooms = {}
        self.current_room = None
        self.inventory = []
        self.score = 0
        self.moves = 0
        self.max_moves = 50  # Giới hạn lượt đi, giảm để episode nhanh hơn
        self.game_over = False
        self.victory = False
        self.active_effects = {}  # Hiệu ứng đang hoạt động (từ thuốc)
        
        # Cơ chế ẩn (không tiết lộ cho agent ban đầu)
        # Bảng ánh xạ chìa khóa màu -> cửa tương ứng
        self.color_key_mapping = {
            "red key": "red door",
            "blue key": "blue door",
            "golden key": "golden door"
        }
        
        # Bảng hiệu quả vũ khí: mỗi vũ khí chỉ đánh bại được một số loại kẻ thù
        self.weapon_effectiveness = {
            "rusty sword": ["weak guard"],
            "silver sword": ["weak guard", "strong guard", "dragon"]
        }
        
        # Công thức chế tạo: kết hợp các vật phẩm để tạo vật phẩm mới
        self.crafting_recipes = {
            frozenset(["rusty sword", "magic crystal"]): "silver sword"
        }
        
        self._initialize_world()
    
    def _initialize_world(self):
        """Tạo thế giới trò chơi với các phòng và vật phẩm.
        
        Xây dựng bản đồ đơn giản gồm 5 phòng, dễ học nhưng vẫn
        thể hiện đầy đủ các khái niệm (khóa/mở cửa, chiến đấu, chế tạo).
        """
        
        # Sảnh lối vào — điểm xuất phát, có thanh kiếm rỉ sét
        self.rooms["entrance"] = Room(
            name="entrance",
            description="Bạn đứng trong sảnh lối vào mờ tối. Bức tường đá vọng lại tiếng bước chân.",
            items=[
                Item("rusty sword", ItemType.WEAPON, "Một thanh kiếm cũ với những vết rỉ sét")
            ],
            exits={"north": "hallway", "east": "storage"}
        )
        
        # Phòng kho — chứa chìa khóa đỏ và pha lê ma thuật
        self.rooms["storage"] = Room(
            name="storage",
            description="Một phòng kho bụi bặm chứa đầy thùng gỗ và thùng rượu cũ.",
            items=[
                Item("red key", ItemType.KEY, "Một chiếc chìa khóa kim loại màu đỏ nhỏ"),
                Item("magic crystal", ItemType.TOOL, "Một viên pha lê phát sáng, rung lên đầy năng lượng")
            ],
            exits={"west": "entrance"}
        )
        
        # Hành lang — có cửa khóa cần chìa khóa đỏ để mở
        self.rooms["hallway"] = Room(
            name="hallway",
            description="Một hành lang dài với cánh cửa bị khóa ở phía bắc.",
            exits={"south": "entrance", "north": "guard_room"},
            locked_exits={"north": "red key"}
        )
        
        # Phòng lính canh — có lính canh mạnh chặn đường đến kho báu
        self.rooms["guard_room"] = Room(
            name="guard_room",
            description="Một căn phòng rộng với giá vũ khí. Một lính canh chặn đường đến kho báu!",
            has_guard=True,
            items=[],
            exits={"south": "hallway", "east": "treasure_room"}
        )
        
        # Phòng kho báu — đích đến cuối cùng
        self.rooms["treasure_room"] = Room(
            name="treasure_room",
            description="Phòng kho báu! Tiền vàng và đá quý lấp lánh trong ánh sáng.",
            items=[
                Item("dragon's treasure", ItemType.TREASURE, "Một kho vàng và đá quý khổng lồ", 
                     {"value": 1000})
            ],
            exits={"west": "guard_room"}
        )
        
        # Đặt phòng hiện tại là sảnh lối vào
        self.current_room = self.rooms["entrance"]
    
    def get_state_description(self) -> str:
        """Lấy mô tả bằng ngôn ngữ tự nhiên về trạng thái hiện tại của trò chơi.
        
        Trả về chuỗi mô tả bao gồm: tên phòng, mô tả phòng, 
        vật phẩm nhìn thấy, các lối ra, túi đồ, và điểm số.
        """
        desc = []
        desc.append(f"\n=== Phòng: {self.current_room.name.replace('_', ' ').title()} ===")
        desc.append(self.current_room.description)
        
        # Hiển thị cảnh báo nếu có lính canh chưa bị đánh bại
        if self.current_room.has_guard and not self.current_room.guard_defeated:
            desc.append("Một lính canh chặn đường bạn!")
        
        # Liệt kê các vật phẩm trong phòng
        if self.current_room.items:
            desc.append("\nBạn nhìn thấy:")
            for item in self.current_room.items:
                desc.append(f"  - {item.name}: {item.description}")
        
        # Liệt kê các lối ra (đánh dấu nếu bị khóa)
        exits = []
        for direction, room in self.current_room.exits.items():
            if direction in self.current_room.locked_exits:
                exits.append(f"{direction} (đã khóa)")
            else:
                exits.append(direction)
        desc.append(f"\nLối ra: {', '.join(exits)}")
        
        # Hiển thị túi đồ nếu có vật phẩm
        if self.inventory:
            desc.append(f"\nTúi đồ: {', '.join([item.name for item in self.inventory])}")
        
        desc.append(f"\nĐiểm: {self.score} | Lượt đi: {self.moves}/{self.max_moves}")
        
        return "\n".join(desc)
    
    def get_available_actions(self) -> List[str]:
        """Lấy danh sách các hành động khả dụng trong trạng thái hiện tại.
        
        Bao gồm: di chuyển, nhặt/dùng/bỏ vật phẩm, tấn công, 
        quan sát, kiểm tra túi đồ, và chế tạo.
        """
        actions = []
        
        # Hành động di chuyển — thêm mỗi hướng có lối ra
        for direction in self.current_room.exits.keys():
            actions.append(f"go {direction}")
        
        # Hành động với vật phẩm trong phòng — nhặt lên
        for item in self.current_room.items:
            actions.append(f"take {item.name}")
        
        # Hành động với vật phẩm trong túi đồ — dùng hoặc bỏ
        for item in self.inventory:
            actions.append(f"use {item.name}")
            actions.append(f"drop {item.name}")
        
        # Hành động chiến đấu — chỉ khi có lính canh chưa bị đánh bại
        if self.current_room.has_guard and not self.current_room.guard_defeated:
            for item in self.inventory:
                if item.item_type == ItemType.WEAPON:
                    actions.append(f"attack with {item.name}")
        
        # Hành động đặc biệt — luôn khả dụng
        actions.append("look around")
        actions.append("check inventory")
        
        # Chế tạo — chỉ hiển thị khi có ít nhất 2 vật phẩm trong túi đồ
        if len(self.inventory) >= 2:
            actions.append("try crafting")
        
        return actions
    
    def execute_action(self, action: str) -> Tuple[str, float, bool]:
        """
        Thực thi một hành động và trả về (phản hồi, reward, kết thúc).
        
        Đây là hàm chính xử lý tất cả input từ agent/người chơi.
        Phân tích chuỗi hành động và gọi hàm xử lý tương ứng.
        
        Args:
            action: Chuỗi hành động (ví dụ: "go north", "take red key")
            
        Returns:
            Tuple gồm: thông báo phản hồi, giá trị reward, trạng thái kết thúc
        """
        if self.game_over:
            return "Trò chơi đã kết thúc.", 0, True
        
        self.moves += 1
        action = action.lower().strip()
        
        # Reward cơ bản, có thể thêm biến động ngẫu nhiên trong chế độ stochastic
        if self.stochastic:
            # Thêm biến động nhỏ ngẫu nhiên vào reward
            reward = -0.5 + self.random_state.uniform(-0.1, 0.1)
            
            # Xác suất nhỏ hành động thất bại trong chế độ stochastic
            if self.random_state.random() < 0.03:  # 3% xác suất
                return "Bạn lóng ngóng và cần thử lại.", reward - 0.2, False
        else:
            reward = -0.5  # Reward âm mỗi lượt đi để khuyến khích hiệu quả
        
        # Kiểm tra giới hạn lượt đi
        if self.moves >= self.max_moves:
            self.game_over = True
            return "Bạn đã hết lượt đi! Trò chơi kết thúc.", -10, True
        
        # Phân tích và xử lý hành động
        if action.startswith("go "):
            direction = action[3:]
            result, move_reward = self._move(direction)
            reward += move_reward
            
        elif action.startswith("take "):
            item_name = action[5:]
            result, take_reward = self._take_item(item_name)
            reward += take_reward
            
        elif action.startswith("use "):
            item_name = action[4:]
            result, use_reward = self._use_item(item_name)
            reward += use_reward
            
        elif action.startswith("drop "):
            item_name = action[5:]
            result = self._drop_item(item_name)
            
        elif action.startswith("attack with "):
            weapon_name = action[12:]
            result, attack_reward = self._attack(weapon_name)
            reward += attack_reward
            
        elif action == "look around":
            result = self.get_state_description()
            
        elif action == "check inventory":
            if self.inventory:
                result = "Túi đồ: " + ", ".join([f"{item.name} ({item.item_type.value})" 
                                                    for item in self.inventory])
            else:
                result = "Túi đồ của bạn trống."
                
        elif action == "try crafting":
            result, craft_reward = self._try_crafting()
            reward += craft_reward
            
        else:
            result = f"Hành động không xác định: {action}"
            reward -= 1
        
        # Kiểm tra điều kiện chiến thắng
        if self._check_victory():
            self.victory = True
            self.game_over = True
            reward += 100
            result += "\n\n🎉 CHIẾN THẮNG! Bạn đã thu thập được kho báu của rồng!"
        
        return result, reward, self.game_over
    
    def _move(self, direction: str) -> Tuple[str, float]:
        """Di chuyển đến phòng khác theo hướng chỉ định.
        
        Xử lý 3 trường hợp: lối ra không tồn tại, cửa bị khóa (cần chìa khóa),
        và lính canh chặn đường. Nếu có chìa khóa phù hợp, tự động mở khóa.
        
        Args:
            direction: Hướng di chuyển (north, south, east, west)
            
        Returns:
            Tuple gồm: thông báo kết quả và giá trị reward
        """
        if direction not in self.current_room.exits:
            return f"Bạn không thể đi {direction} từ đây.", -1
        
        # Kiểm tra cửa bị khóa
        if direction in self.current_room.locked_exits:
            required_key = self.current_room.locked_exits[direction]
            if not any(item.name == required_key for item in self.inventory):
                return f"Lối ra {direction} bị khóa. Bạn cần {required_key}.", -0.5
            else:
                # Mở khóa và di chuyển
                del self.current_room.locked_exits[direction]
                room_name = self.current_room.exits[direction]
                self.current_room = self.rooms[room_name]
                return f"Bạn mở khóa cửa bằng {required_key} và đi về hướng {direction}.", 5
        
        # Kiểm tra lính canh chặn đường
        if self.current_room.has_guard and not self.current_room.guard_defeated:
            return "Một lính canh chặn đường bạn! Bạn phải đánh bại họ trước.", -1
        
        # Di chuyển đến phòng mới
        room_name = self.current_room.exits[direction]
        self.current_room = self.rooms[room_name]
        return f"Bạn di chuyển về hướng {direction} đến {self.current_room.name}.", 1
    
    def _take_item(self, item_name: str) -> Tuple[str, float]:
        """Nhặt một vật phẩm từ phòng hiện tại vào túi đồ.
        
        Reward thay đổi tùy loại vật phẩm: kho báu cho reward lớn nhất,
        chìa khóa và vũ khí cho reward trung bình.
        
        Args:
            item_name: Tên vật phẩm cần nhặt
            
        Returns:
            Tuple gồm: thông báo kết quả và giá trị reward
        """
        for item in self.current_room.items:
            if item.name.lower() == item_name.lower():
                self.current_room.items.remove(item)
                self.inventory.append(item)
                
                # Reward dựa trên loại vật phẩm
                if item.item_type == ItemType.TREASURE:
                    reward = 100  # Reward lớn khi lấy được kho báu!
                elif item.item_type == ItemType.KEY:
                    reward = 5
                elif item.item_type == ItemType.WEAPON:
                    reward = 3
                else:
                    reward = 2
                
                # Thêm biến động ngẫu nhiên trong chế độ stochastic
                if self.stochastic:
                    reward += self.random_state.uniform(-0.5, 0.5)
                    
                return f"Bạn nhặt {item.name}.", reward
        
        penalty = -0.5
        if self.stochastic:
            penalty += self.random_state.uniform(-0.1, 0.1)
        
        return f"Không có {item_name} ở đây.", penalty
    
    def _drop_item(self, item_name: str) -> str:
        """Bỏ một vật phẩm từ túi đồ xuống phòng hiện tại.
        
        Args:
            item_name: Tên vật phẩm cần bỏ
            
        Returns:
            Thông báo kết quả
        """
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                self.inventory.remove(item)
                self.current_room.items.append(item)
                return f"Bạn bỏ {item.name} xuống."
        
        return f"Bạn không có {item_name}."
    
    def _use_item(self, item_name: str) -> Tuple[str, float]:
        """Sử dụng một vật phẩm từ túi đồ.
        
        Thuốc: uống và nhận hiệu ứng (hồi phục hoặc tăng sức mạnh).
        Chìa khóa: tự động sử dụng khi di chuyển qua cửa khóa.
        Các loại khác: không thể sử dụng trực tiếp.
        
        Args:
            item_name: Tên vật phẩm cần sử dụng
            
        Returns:
            Tuple gồm: thông báo kết quả và giá trị reward
        """
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                if item.item_type == ItemType.POTION:
                    self.inventory.remove(item)
                    if "healing" in item.name:
                        return "Bạn uống thuốc hồi phục và cảm thấy sảng khoái!", 5
                    elif "strength" in item.name:
                        self.active_effects["strength"] = 10
                        return "Bạn cảm thấy một luồng sức mạnh dâng lên! Đòn tấn công sẽ mạnh hơn.", 5
                    
                elif item.item_type == ItemType.KEY:
                    # Chìa khóa tự động sử dụng khi di chuyển
                    return f"{item.name} sẽ được tự động sử dụng khi cần thiết.", 0
                    
                else:
                    return f"Bạn không thể sử dụng {item.name} lúc này.", -0.5
        
        return f"Bạn không có {item_name}.", -0.5
    
    def _attack(self, weapon_name: str) -> Tuple[str, float]:
        """Tấn công lính canh bằng vũ khí.
        
        Kiểm tra hiệu quả vũ khí dựa trên bảng weapon_effectiveness (cơ chế ẩn).
        Trong chế độ stochastic: có xác suất đòn chí mạng (10%), 
        thành công thường (85%), và đánh trượt (5%).
        
        Args:
            weapon_name: Tên vũ khí sử dụng để tấn công
            
        Returns:
            Tuple gồm: thông báo kết quả và giá trị reward
        """
        if not self.current_room.has_guard or self.current_room.guard_defeated:
            return "Không có gì để tấn công ở đây.", -1
        
        # Tìm vũ khí trong túi đồ
        weapon = None
        for item in self.inventory:
            if item.name.lower() == weapon_name.lower():
                weapon = item
                break
        
        if not weapon:
            return f"Bạn không có {weapon_name}.", -1
        
        if weapon.item_type != ItemType.WEAPON:
            return f"{weapon_name} không phải là vũ khí!", -1
        
        # Kiểm tra hiệu quả vũ khí (cơ chế ẩn)
        # Trong bản đồ đơn giản này, lính canh ở guard_room là "strong guard"
        guard_type = "strong guard"
        
        if weapon.name in self.weapon_effectiveness:
            if guard_type in self.weapon_effectiveness[weapon.name]:
                # Trong chế độ stochastic, thêm biến thể chiến đấu
                if self.stochastic:
                    roll = self.random_state.random()
                    if roll < 0.1:  # 10% đòn chí mạng
                        self.current_room.guard_defeated = True
                        return f"Đòn chí mạng! Bạn hạ gục {guard_type} bằng {weapon.name}!", 30
                    elif roll < 0.95:  # 85% thành công thường
                        self.current_room.guard_defeated = True
                        return f"Bạn đánh bại {guard_type} bằng {weapon.name}!", 20
                    else:  # 5% đánh trượt
                        return f"Đòn tấn công trượt! {guard_type} vẫn đứng vững.", -0.5
                else:
                    self.current_room.guard_defeated = True
                    return f"Bạn đánh bại {guard_type} bằng {weapon.name}!", 20
            else:
                penalty = -2
                if self.stochastic:
                    penalty += self.random_state.uniform(-0.5, 0.5)
                return f"{weapon.name} của bạn không hiệu quả chống lại {guard_type}!", penalty
        
        return f"{weapon.name} của bạn dường như không có tác dụng.", -1
    
    def _try_crafting(self) -> Tuple[str, float]:
        """Thử chế tạo vật phẩm mới từ các vật phẩm trong túi đồ (cơ chế ẩn).
        
        Duyệt qua tất cả công thức chế tạo và kiểm tra xem túi đồ
        có đủ nguyên liệu không. Trong chế độ stochastic, chế tạo có
        90% tỷ lệ thành công và 10% thất bại (không mất nguyên liệu).
        
        Returns:
            Tuple gồm: thông báo kết quả và giá trị reward
        """
        if len(self.inventory) < 2:
            return "Bạn cần ít nhất hai vật phẩm để chế tạo.", -0.5
        
        # Kiểm tra tất cả công thức có thể
        inventory_names = [item.name for item in self.inventory]
        
        for recipe, result in self.crafting_recipes.items():
            if recipe.issubset(set(inventory_names)):
                # Trong chế độ stochastic, chế tạo có thể có biến thể
                if self.stochastic:
                    if self.random_state.random() < 0.9:  # 90% tỷ lệ thành công
                        # Chế tạo vật phẩm — loại bỏ nguyên liệu khỏi túi đồ
                        for ingredient in recipe:
                            for item in self.inventory[:]:
                                if item.name == ingredient:
                                    self.inventory.remove(item)
                                    break
                        
                        new_item = self._create_item(result)
                        self.inventory.append(new_item)
                        reward = 10 + self.random_state.uniform(-1, 2)
                        return f"Bạn chế tạo thành công {result}!", reward
                    else:
                        # 10% xác suất chế tạo thất bại (nguyên liệu không bị tiêu hao)
                        return "Quá trình chế tạo thất bại. Hãy thử lại!", -0.2
                else:
                    # Chế tạo xác định (không ngẫu nhiên)
                    for ingredient in recipe:
                        for item in self.inventory[:]:
                            if item.name == ingredient:
                                self.inventory.remove(item)
                                break
                    
                    new_item = self._create_item(result)
                    self.inventory.append(new_item)
                    return f"Bạn chế tạo thành công {result}!", 10  # Reward tốt khi khám phá ra chế tạo
        
        penalty = -0.5
        if self.stochastic:
            penalty += self.random_state.uniform(-0.1, 0.1)
        
        return "Những vật phẩm này không thể kết hợp thành thứ gì hữu ích.", penalty
    
    def _create_item(self, item_name: str) -> Item:
        """Tạo một vật phẩm mới theo tên (dùng cho hệ thống chế tạo).
        
        Tra cứu tên vật phẩm và trả về đối tượng Item tương ứng
        với mô tả tiếng Việt.
        
        Args:
            item_name: Tên định danh của vật phẩm cần tạo
            
        Returns:
            Đối tượng Item mới
        """
        if item_name == "silver sword":
            return Item("silver sword", ItemType.WEAPON, "Một thanh kiếm bạc sáng lấp lánh")
        elif item_name == "magic staff":
            return Item("magic staff", ItemType.WEAPON, "Một cây gậy phép lách tách năng lượng ma thuật")
        else:
            return Item(item_name, ItemType.TOOL, "Một vật phẩm được chế tạo")
    
    def _check_victory(self) -> bool:
        """Kiểm tra xem người chơi đã chiến thắng chưa.
        
        Điều kiện thắng: có "dragon's treasure" trong túi đồ.
        """
        for item in self.inventory:
            if item.name == "dragon's treasure":
                return True
        return False
    
    def reset(self, seed: int = None) -> str:
        """Đặt lại trò chơi về trạng thái ban đầu.
        
        Tạo seed mới nếu không được cung cấp, sau đó khởi tạo lại
        toàn bộ thế giới trò chơi.
        
        Args:
            seed: Hạt giống ngẫu nhiên (tùy chọn)
            
        Returns:
            Mô tả trạng thái ban đầu của trò chơi
        """
        if seed is None:
            seed = random.randint(0, 10000)
        self.__init__(seed=seed, stochastic=self.stochastic)
        return self.get_state_description()
    
    def get_hidden_rules(self) -> str:
        """Trả về các luật chơi ẩn (dùng để gỡ lỗi/phân tích).
        
        Tiết lộ toàn bộ cơ chế ẩn bao gồm: cách thắng, cơ chế chìa khóa,
        hiệu quả vũ khí, công thức chế tạo, và giải pháp tối ưu.
        """
        rules = []
        rules.append("Cơ Chế Ẩn Của Trò Chơi (Phiên Bản Đơn Giản):")
        rules.append("\n1. Cách chiến thắng:")
        rules.append("   - Lấy chìa khóa đỏ (red key) từ phòng kho")
        rules.append("   - Dùng nó để mở khóa cửa đến phòng lính canh")
        rules.append("   - Chế tạo kiếm bạc (rusty sword + magic crystal)")
        rules.append("   - Đánh bại lính canh mạnh bằng kiếm bạc")
        rules.append("   - Thu thập kho báu của rồng (dragon's treasure)")
        
        rules.append("\n2. Cơ chế chìa khóa:")
        rules.append("   - Chìa khóa đỏ (red key) mở cánh cửa bị khóa ở hành lang")
        
        rules.append("\n3. Hiệu quả vũ khí:")
        for weapon, targets in self.weapon_effectiveness.items():
            rules.append(f"   - {weapon} đánh bại: {', '.join(targets)}")
        
        rules.append("\n4. Công thức chế tạo:")
        for ingredients, result in self.crafting_recipes.items():
            rules.append(f"   - {' + '.join(ingredients)} = {result}")
        
        rules.append("\n5. Giải pháp tối ưu:")
        rules.append("   - Mất khoảng 10-15 lượt đi nếu thực hiện hiệu quả")
        
        return "\n".join(rules)