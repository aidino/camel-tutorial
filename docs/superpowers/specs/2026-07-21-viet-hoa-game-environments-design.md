# Việt hóa `game_environments.py`

**Ngày:** 2026-07-21
**File mục tiêu:** `agent-books/chapter1/learning-from-experience/game_environments.py`

## Mục tiêu

Việt hóa toàn diện file `game_environments.py` — một trò chơi săn tìm kho báu dựa trên text (~504 dòng Python). Mục đích giúp người đọc Việt Nam hiểu được code và trải nghiệm game bằng tiếng Việt.

## Phạm vi thay đổi

| Thành phần | Xử lý | Lý do |
|---|---|---|
| Comments & docstrings | Dịch sang tiếng Việt, giữ thuật ngữ kỹ thuật (Agent, stochastic, reward, seed) | Giúp người đọc VN hiểu code |
| `ItemType` enum values | Dịch: `"key"` → `"chìa khóa"`, `"weapon"` → `"vũ khí"`, `"treasure"` → `"kho báu"`, `"tool"` → `"công cụ"`, `"potion"` → `"thuốc"` | Hiển thị tiếng Việt khi xem inventory |
| Room descriptions | Dịch sang tiếng Việt | Trải nghiệm game bằng tiếng Việt |
| Item descriptions | Dịch sang tiếng Việt | Trải nghiệm game bằng tiếng Việt |
| Feedback messages (tất cả strings trả về từ các hàm) | Dịch sang tiếng Việt | Trải nghiệm game bằng tiếng Việt |
| Hidden rules output (`get_hidden_rules`) | Dịch sang tiếng Việt | Nhất quán |
| Tên biến, tên hàm, tên class | **Giữ nguyên tiếng Anh** | Đảm bảo logic code không đổi |
| `item.name` (tên vật phẩm) | **Giữ nguyên tiếng Anh** | Dùng làm keys trong dict matching, crafting recipes, weapon effectiveness |

## Nguyên tắc an toàn

1. **Không thay đổi `item.name`**: Các tên `"rusty sword"`, `"red key"`, `"golden key"`, `"blue key"`, `"magic crystal"`, `"silver sword"`, `"dragon's treasure"` đều tham gia logic matching trong:
   - `self.color_key_mapping`
   - `self.weapon_effectiveness`
   - `self.crafting_recipes`
   - `self._check_victory()`
   - Các phép so sánh `item.name.lower() == ...`

   Thay đổi sẽ phá vỡ game.

2. **Không thay đổi tên phòng (`room.name`)**: Các tên `"entrance"`, `"storage"`, `"hallway"`, `"guard_room"`, `"treasure_room"` dùng làm dictionary keys trong `self.rooms` và trong `exits` mapping.

3. **Không thay đổi tên direction**: `"north"`, `"south"`, `"east"`, `"west"` dùng trong logic parsing action `"go {direction}"`.

4. **Không thay đổi action keywords**: `"go "`, `"take "`, `"use "`, `"drop "`, `"attack with "`, `"look around"`, `"check inventory"`, `"try crafting"` — đây là các lệnh mà agent/player nhập vào.

## Chi tiết dịch từng phần

### Module docstring
```
Trò chơi săn tìm kho báu dựa trên văn bản với các cơ chế ẩn.
Lấy cảm hứng từ những hiểu biết của Shunyu Yao về lý luận và khả năng tổng quát hóa trong AI.
```
(Đã dịch sẵn — giữ nguyên)

### Class `ItemType`
- Thêm docstring tiếng Việt
- Dịch enum values

### Class `Item`
- Thêm docstring tiếng Việt giải thích dataclass

### Class `Room`
- Thêm docstring tiếng Việt
- Dịch inline comments

### Class `TreasureHuntGame`
- Dịch class docstring
- Mỗi method: dịch docstring + thêm comment giải thích logic

### Feedback messages (ví dụ)
| Tiếng Anh | Tiếng Việt |
|---|---|
| `"You stand in a dimly lit entrance hall."` | `"Bạn đứng trong sảnh lối vào mờ tối. Bức tường đá vọng lại tiếng bước chân."` |
| `"A guard blocks your way!"` | `"Một lính canh chặn đường bạn!"` |
| `"You take the {item.name}."` | `"Bạn nhặt {item.name}."` |
| `"Game is already over."` | `"Trò chơi đã kết thúc."` |
| `"VICTORY! You've collected the dragon's treasure!"` | `"CHIẾN THẮNG! Bạn đã thu thập được kho báu của rồng!"` |

## Ngoài phạm vi

- Không tách strings ra file i18n riêng (chỉ inline trong code)
- Không thay đổi logic game
- Không thêm/bớt tính năng
- Không refactor cấu trúc code
