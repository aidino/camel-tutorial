# 🏴‍☠️ Trò Chơi Săn Tìm Kho Báu — Môi Trường Học Tập Cho AI Agent

> **Chapter 1: Learning from Experience**
> Môi trường trò chơi dựa trên văn bản, thiết kế để AI Agent tự khám phá các cơ chế ẩn thông qua thử-sai và lý luận.

---

## 📖 Mục Lục

- [Tổng Quan](#-tổng-quan)
- [Kiến Trúc (Architecture)](#-kiến-trúc-architecture)
- [Cấu Trúc Thư Mục](#-cấu-trúc-thư-mục)
- [Chi Tiết Các Thành Phần](#-chi-tiết-các-thành-phần)
- [Bản Đồ Trò Chơi](#-bản-đồ-trò-chơi)
- [Cơ Chế Ẩn](#-cơ-chế-ẩn)
- [Hướng Dẫn Sử Dụng](#-hướng-dẫn-sử-dụng)
- [Hướng Dẫn Test](#-hướng-dẫn-test)
- [Tham Khảo](#-tham-khảo)

---

## 🎯 Tổng Quan

Đây là một **trò chơi săn tìm kho báu dựa trên văn bản** được thiết kế làm môi trường thí nghiệm cho AI Agent. Lấy cảm hứng từ nghiên cứu của Shunyu Yao về lý luận và khả năng tổng quát hóa trong AI.

### Mục tiêu chính

- **Cho Agent**: Tự khám phá các cơ chế ẩn (chìa khóa, chế tạo, chiến đấu) thông qua tương tác
- **Cho Người học**: Hiểu cách xây dựng môi trường reinforcement learning cho LLM Agent
- **Cho Nghiên cứu**: So sánh khả năng học tập giữa các mô hình AI trong môi trường có cơ chế ẩn

### Đặc điểm nổi bật

| Đặc điểm | Mô tả |
|---|---|
| **Cơ chế ẩn** | Agent phải tự khám phá luật chơi (chìa khóa, chế tạo, vũ khí) |
| **Hai chế độ** | Deterministic (xác định) và Stochastic (ngẫu nhiên) |
| **Reward system** | Hệ thống điểm thưởng/phạt khuyến khích chiến lược hiệu quả |
| **Giới hạn lượt** | Tối đa 50 lượt đi, buộc agent phải lên kế hoạch |
| **Việt hóa** | Toàn bộ mô tả, phản hồi, giao diện bằng tiếng Việt |

---

## 🏗 Kiến Trúc (Architecture)

### Sơ đồ tổng quan

```
┌──────────────────────────────────────────────────────┐
│                   TreasureHuntGame                   │
│                  (Class điều khiển chính)             │
│                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  Game State  │  │Hidden Mechanics│ │  Action     │ │
│  │  (Trạng thái)│  │ (Cơ chế ẩn)  │  │  Parser     │ │
│  │             │  │              │  │ (Phân tích) │ │
│  │ - rooms     │  │- color_key   │  │             │ │
│  │ - inventory │  │  _mapping    │  │ go/take/use │ │
│  │ - score     │  │- weapon      │  │ drop/attack │ │
│  │ - moves     │  │  _effective  │  │ craft/look  │ │
│  │ - effects   │  │- crafting    │  │             │ │
│  │             │  │  _recipes    │  │             │ │
│  └──────┬──────┘  └──────┬───────┘  └──────┬──────┘ │
│         │               │                 │         │
│         └───────────┬────┘─────────────────┘         │
│                     ▼                                │
│          ┌─────────────────────┐                     │
│          │   execute_action()  │                     │
│          │  (Vòng lặp chính)  │                     │
│          │                     │                     │
│          │ Input:  action str  │                     │
│          │ Output: (feedback,  │                     │
│          │          reward,    │                     │
│          │          done)      │                     │
│          └─────────────────────┘                     │
└──────────────────────────────────────────────────────┘
         ▲                              │
         │ action (str)                 │ (feedback, reward, done)
         │                              ▼
┌──────────────────────────────────────────────────────┐
│              AI Agent / Người Chơi                   │
│                                                      │
│  Quan sát trạng thái → Quyết định hành động →        │
│  Nhận phản hồi → Học hỏi → Lặp lại                  │
└──────────────────────────────────────────────────────┘
```

### Luồng dữ liệu (Data Flow)

```
Agent gửi action (str)
        │
        ▼
execute_action(action)
        │
        ├── Kiểm tra game_over?
        ├── Tính reward cơ bản (-0.5/lượt)
        ├── Kiểm tra giới hạn lượt đi
        │
        ├── Phân tích action:
        │   ├── "go {direction}"     → _move()
        │   ├── "take {item}"        → _take_item()
        │   ├── "use {item}"         → _use_item()
        │   ├── "drop {item}"        → _drop_item()
        │   ├── "attack with {item}" → _attack()
        │   ├── "look around"        → get_state_description()
        │   ├── "check inventory"    → hiển thị túi đồ
        │   └── "try crafting"       → _try_crafting()
        │
        ├── Kiểm tra điều kiện chiến thắng
        │
        └── Trả về (feedback: str, reward: float, done: bool)
```

### Mô hình Class

```
ItemType (Enum)
├── KEY      = "chìa khóa"
├── WEAPON   = "vũ khí"
├── TREASURE = "kho báu"
├── TOOL     = "công cụ"
└── POTION   = "thuốc"

Item (dataclass)
├── name: str            # Tên định danh (tiếng Anh, dùng trong logic)
├── item_type: ItemType  # Loại vật phẩm
├── description: str     # Mô tả (tiếng Việt)
└── properties: Dict     # Thuộc tính bổ sung

Room (dataclass)
├── name: str                    # Tên phòng (tiếng Anh, dùng làm key)
├── description: str             # Mô tả phòng (tiếng Việt)
├── items: List[Item]            # Vật phẩm trong phòng
├── exits: Dict[str, str]        # Lối ra: hướng → tên phòng
├── locked_exits: Dict[str, str] # Lối khóa: hướng → chìa khóa cần
├── has_guard: bool              # Có lính canh?
└── guard_defeated: bool         # Đã đánh bại?

TreasureHuntGame
├── __init__(seed, stochastic)   # Khởi tạo trò chơi
├── _initialize_world()          # Tạo bản đồ & vật phẩm
├── get_state_description()      # Mô tả trạng thái hiện tại
├── get_available_actions()      # Danh sách hành động khả dụng
├── execute_action(action)       # Thực thi hành động (API chính)
├── _move(direction)             # Di chuyển giữa các phòng
├── _take_item(item_name)        # Nhặt vật phẩm
├── _drop_item(item_name)        # Bỏ vật phẩm
├── _use_item(item_name)         # Sử dụng vật phẩm
├── _attack(weapon_name)         # Tấn công lính canh
├── _try_crafting()              # Chế tạo vật phẩm
├── _create_item(item_name)      # Tạo vật phẩm mới (nội bộ)
├── _check_victory()             # Kiểm tra thắng/thua
├── reset(seed)                  # Đặt lại trò chơi
└── get_hidden_rules()           # Xem luật ẩn (debug)
```

---

## 📁 Cấu Trúc Thư Mục

```
learning-from-experience/
├── game_environments.py   # Module chính — môi trường trò chơi
├── quick_demo.py          # Bản demo nhanh
├── requirements.txt       # Các thư viện phụ thuộc
├── .env                   # Cấu hình API key và model
└── README.md              # Tài liệu này
```

---

## 🔍 Chi Tiết Các Thành Phần

### 1. `ItemType` — Phân loại vật phẩm

| Enum | Giá trị | Ý nghĩa | Cách tương tác |
|---|---|---|---|
| `KEY` | `"chìa khóa"` | Mở cửa bị khóa | Tự động dùng khi `go` qua cửa khóa |
| `WEAPON` | `"vũ khí"` | Dùng để chiến đấu | `attack with {name}` |
| `TREASURE` | `"kho báu"` | Mục tiêu cuối cùng | `take {name}` để chiến thắng |
| `TOOL` | `"công cụ"` | Nguyên liệu chế tạo | Dùng trong `try crafting` |
| `POTION` | `"thuốc"` | Hiệu ứng tạm thời | `use {name}` |

### 2. `Item` — Vật phẩm

Mỗi vật phẩm có:
- **`name`** (tiếng Anh): Dùng làm ID trong logic matching — **không được thay đổi**
- **`description`** (tiếng Việt): Hiển thị cho người chơi
- **`properties`**: Dict tùy chỉnh (ví dụ: `{"value": 1000}` cho kho báu)

### 3. `Room` — Phòng

Mỗi phòng là một node trong đồ thị bản đồ:
- **`exits`**: Các cạnh nối đến phòng khác
- **`locked_exits`**: Cạnh bị khóa, cần chìa khóa cụ thể
- **`has_guard`**: Phòng có lính canh chặn → phải đánh bại trước khi đi tiếp

### 4. `TreasureHuntGame` — Lớp điều khiển chính

#### API công khai (Public Methods)

| Method | Mô tả | Trả về |
|---|---|---|
| `__init__(seed, stochastic)` | Khởi tạo game | — |
| `get_state_description()` | Mô tả trạng thái hiện tại | `str` |
| `get_available_actions()` | Danh sách hành động có thể thực hiện | `List[str]` |
| `execute_action(action)` | Thực thi hành động | `Tuple[str, float, bool]` |
| `reset(seed)` | Đặt lại game | `str` |
| `get_hidden_rules()` | Xem cơ chế ẩn (debug) | `str` |

#### Hệ thống Reward

| Hành động | Reward | Ghi chú |
|---|---|---|
| Mỗi lượt đi | `-0.5` | Khuyến khích hiệu quả |
| Nhặt kho báu | `+100` | Reward lớn nhất |
| Nhặt chìa khóa | `+5` | |
| Nhặt vũ khí | `+3` | |
| Nhặt công cụ | `+2` | |
| Mở khóa cửa | `+5` | Dùng chìa khóa thành công |
| Đánh bại lính canh | `+20` (thường) / `+30` (chí mạng) | |
| Chế tạo thành công | `+10` | Khám phá cơ chế ẩn |
| Di chuyển thành công | `+1` | |
| Hành động không hợp lệ | `-1` | |
| Hết lượt đi | `-10` | Game over |
| Chiến thắng | `+100` | Cộng thêm khi có dragon's treasure |

---

## 🗺 Bản Đồ Trò Chơi

```
                    ┌─────────────────┐
                    │  treasure_room  │
                    │  (Phòng kho báu)│
                    │                 │
                    │ 🐉 dragon's    │
                    │    treasure     │
                    └────────┬────────┘
                             │ west
                             │
                    ┌────────┴────────┐
                    │   guard_room    │
                    │ (Phòng lính canh)│
                    │                 │
                    │ ⚔️  Lính canh  │
                    │   (strong guard)│
                    └────────┬────────┘
                             │ south
                     🔒 red key
                             │ north
                    ┌────────┴────────┐
                    │    hallway      │
                    │   (Hành lang)   │
                    │                 │
                    │  Cửa khóa ở    │
                    │  phía bắc       │
                    └────────┬────────┘
                             │ south
                             │
         ┌───────────────────┴───────────────────┐
         │                                       │
         │ north                           east  │
┌────────┴────────┐                   ┌──────────┴──────┐
│    entrance     │ ←───── west ────→ │    storage      │
│  (Sảnh lối vào) │                   │  (Phòng kho)    │
│                 │                   │                 │
│ ⚔️ rusty sword │                   │ 🔑 red key     │
│                 │                   │ 💎 magic crystal│
│ ★ ĐIỂM XUẤT   │                   │                 │
│   PHÁT          │                   │                 │
└─────────────────┘                   └─────────────────┘
```

---

## 🔮 Cơ Chế Ẩn

Đây là các cơ chế mà **Agent không được cho biết trước** — phải tự khám phá:

### 1. Hệ thống Chìa Khóa — Màu Sắc

| Chìa khóa | Mở cửa |
|---|---|
| `red key` | Cửa khóa ở hành lang (đến guard_room) |
| `blue key` | `blue door` (dự phòng, chưa dùng) |
| `golden key` | `golden door` (dự phòng, chưa dùng) |

### 2. Hiệu Quả Vũ Khí

| Vũ khí | Đánh bại được |
|---|---|
| `rusty sword` | weak guard |
| `silver sword` | weak guard, strong guard, dragon |

> ⚠️ **Lưu ý**: Lính canh trong `guard_room` là **strong guard** → chỉ `silver sword` mới đánh bại được!

### 3. Công Thức Chế Tạo

| Nguyên liệu | Kết quả |
|---|---|
| `rusty sword` + `magic crystal` | `silver sword` |

### 4. Giải Pháp Tối Ưu (10-12 lượt)

```
1. take rusty sword          # Nhặt kiếm rỉ sét
2. go east                   # Đến phòng kho
3. take red key              # Nhặt chìa khóa đỏ
4. take magic crystal        # Nhặt pha lê ma thuật
5. try crafting              # Chế tạo: rusty sword + magic crystal → silver sword
6. go west                   # Quay về sảnh
7. go north                  # Đến hành lang (tự động mở khóa bằng red key)
8. go north                  # Đến phòng lính canh
9. attack with silver sword  # Đánh bại strong guard
10. go east                  # Đến phòng kho báu
11. take dragon's treasure   # 🎉 CHIẾN THẮNG!
```

---

## 🚀 Hướng Dẫn Sử Dụng

### Cài đặt

```bash
# Cài đặt thư viện phụ thuộc
pip install -r requirements.txt
```

### Sử dụng cơ bản

```python
from game_environments import TreasureHuntGame

# Khởi tạo trò chơi (deterministic)
game = TreasureHuntGame(seed=42)

# Xem trạng thái hiện tại
print(game.get_state_description())

# Xem danh sách hành động khả dụng
actions = game.get_available_actions()
print(actions)

# Thực thi hành động
feedback, reward, done = game.execute_action("take rusty sword")
print(f"Phản hồi: {feedback}")
print(f"Reward: {reward}")
print(f"Kết thúc: {done}")
```

### Chế độ Stochastic (Ngẫu nhiên)

```python
# Bật chế độ stochastic — thêm yếu tố may rủi
game = TreasureHuntGame(seed=42, stochastic=True)

# Trong chế độ này:
# - Reward có biến động nhỏ ngẫu nhiên (±0.1 đến ±0.5)
# - 3% xác suất hành động thất bại
# - Chiến đấu: 10% chí mạng, 85% thành công, 5% trượt
# - Chế tạo: 90% thành công, 10% thất bại (không mất nguyên liệu)
```

### Tích hợp với AI Agent

```python
from game_environments import TreasureHuntGame

def run_agent_episode(agent, seed=42):
    """Chạy một episode với AI Agent."""
    game = TreasureHuntGame(seed=seed)
    
    total_reward = 0
    state = game.get_state_description()
    
    while not game.game_over:
        # Agent quan sát trạng thái và chọn hành động
        available_actions = game.get_available_actions()
        action = agent.choose_action(state, available_actions)
        
        # Thực thi hành động
        feedback, reward, done = game.execute_action(action)
        total_reward += reward
        
        # Agent học từ kết quả
        state = game.get_state_description()
        agent.learn(feedback, reward)
    
    return total_reward, game.victory, game.moves
```

### Đặt lại trò chơi

```python
# Đặt lại với seed mới
state = game.reset(seed=123)

# Đặt lại với seed ngẫu nhiên
state = game.reset()
```

### Xem luật ẩn (Debug)

```python
# Hữu ích khi phân tích hành vi Agent
print(game.get_hidden_rules())
```

---

## 🧪 Hướng Dẫn Test

### 1. Test nhanh — Kiểm tra import và khởi tạo

```bash
python3 -c "
from game_environments import TreasureHuntGame, ItemType, Item, Room
game = TreasureHuntGame(seed=42)
print('✅ Import và khởi tạo thành công')
print(f'  Phòng hiện tại: {game.current_room.name}')
print(f'  Số phòng: {len(game.rooms)}')
print(f'  Vật phẩm trong phòng: {[i.name for i in game.current_room.items]}')
"
```

### 2. Test ItemType — Kiểm tra giá trị tiếng Việt

```bash
python3 -c "
from game_environments import ItemType

expected = {
    'KEY': 'chìa khóa',
    'WEAPON': 'vũ khí',
    'TREASURE': 'kho báu',
    'TOOL': 'công cụ',
    'POTION': 'thuốc'
}

for name, value in expected.items():
    actual = ItemType[name].value
    assert actual == value, f'❌ {name}: expected \"{value}\", got \"{actual}\"'
    print(f'✅ ItemType.{name} = \"{actual}\"')

print('✅ Tất cả ItemType values đúng!')
"
```

### 3. Test bản đồ — Kiểm tra cấu trúc phòng

```bash
python3 -c "
from game_environments import TreasureHuntGame

game = TreasureHuntGame(seed=42)

# Kiểm tra số phòng
assert len(game.rooms) == 5, f'❌ Expected 5 rooms, got {len(game.rooms)}'

# Kiểm tra các phòng tồn tại
expected_rooms = ['entrance', 'storage', 'hallway', 'guard_room', 'treasure_room']
for room_name in expected_rooms:
    assert room_name in game.rooms, f'❌ Missing room: {room_name}'
    print(f'✅ Phòng \"{room_name}\" tồn tại')

# Kiểm tra phòng bắt đầu
assert game.current_room.name == 'entrance', '❌ Phòng bắt đầu sai'
print('✅ Phòng bắt đầu: entrance')

# Kiểm tra lối ra
assert 'north' in game.rooms['entrance'].exits, '❌ entrance thiếu lối ra north'
assert 'east' in game.rooms['entrance'].exits, '❌ entrance thiếu lối ra east'
print('✅ Lối ra entrance: north, east')

# Kiểm tra cửa khóa
assert 'north' in game.rooms['hallway'].locked_exits, '❌ hallway thiếu cửa khóa'
assert game.rooms['hallway'].locked_exits['north'] == 'red key', '❌ Chìa khóa sai'
print('✅ Cửa khóa hallway cần: red key')

# Kiểm tra lính canh
assert game.rooms['guard_room'].has_guard == True, '❌ guard_room thiếu lính canh'
print('✅ guard_room có lính canh')

print('\\n✅ Tất cả test bản đồ đều đúng!')
"
```

### 4. Test luồng chơi hoàn chỉnh — Giải pháp tối ưu

```bash
python3 -c "
from game_environments import TreasureHuntGame

game = TreasureHuntGame(seed=42)
total_reward = 0

# Giải pháp tối ưu
optimal_solution = [
    'take rusty sword',
    'go east',
    'take red key',
    'take magic crystal',
    'try crafting',
    'go west',
    'go north',
    'go north',
    'attack with silver sword',
    'go east',
    'take dragon\\'s treasure',
]

print('=== Chạy giải pháp tối ưu ===')
for i, action in enumerate(optimal_solution, 1):
    feedback, reward, done = game.execute_action(action)
    total_reward += reward
    print(f'  Lượt {i:2d}: {action:30s} → reward={reward:+.1f} | {feedback[:60]}')
    
    if done:
        break

# Kiểm tra kết quả
assert game.victory == True, '❌ Chưa chiến thắng!'
assert game.game_over == True, '❌ Game chưa kết thúc!'
print(f'\\n✅ CHIẾN THẮNG! Tổng reward: {total_reward:.1f}, Số lượt: {game.moves}')
"
```

### 5. Test chế độ Stochastic

```bash
python3 -c "
from game_environments import TreasureHuntGame

# Chạy nhiều lần để kiểm tra tính ngẫu nhiên
rewards = []
for seed in range(10):
    game = TreasureHuntGame(seed=seed, stochastic=True)
    feedback, reward, done = game.execute_action('take rusty sword')
    rewards.append(reward)

# Trong stochastic, reward phải có biến động
unique_rewards = len(set(rewards))
assert unique_rewards > 1, '❌ Stochastic nhưng reward không thay đổi!'
print(f'✅ Stochastic mode: {unique_rewards} giá trị reward khác nhau trong 10 lần chạy')
print(f'  Rewards: {[round(r, 2) for r in rewards]}')

# Kiểm tra action failure (3% xác suất)
failures = 0
for seed in range(1000):
    game = TreasureHuntGame(seed=seed, stochastic=True)
    feedback, reward, done = game.execute_action('look around')
    if 'lóng ngóng' in feedback:
        failures += 1

print(f'✅ Tỷ lệ thất bại: {failures}/1000 ({failures/10:.1f}%) — kỳ vọng ~3%')
"
```

### 6. Test xử lý lỗi — Hành động không hợp lệ

```bash
python3 -c "
from game_environments import TreasureHuntGame

game = TreasureHuntGame(seed=42)

# Đi hướng không tồn tại
feedback, reward, done = game.execute_action('go west')
assert reward < 0, '❌ Đi hướng sai phải bị phạt'
print(f'✅ Đi hướng sai: reward={reward}, feedback=\"{feedback}\"')

# Nhặt vật phẩm không tồn tại
feedback, reward, done = game.execute_action('take golden key')
assert reward < 0, '❌ Nhặt đồ không có phải bị phạt'
print(f'✅ Nhặt đồ không có: reward={reward}, feedback=\"{feedback}\"')

# Hành động hoàn toàn vô nghĩa
feedback, reward, done = game.execute_action('fly away')
assert reward < 0, '❌ Hành động vô nghĩa phải bị phạt'
assert 'không xác định' in feedback.lower(), '❌ Thiếu thông báo lỗi'
print(f'✅ Hành động vô nghĩa: reward={reward}, feedback=\"{feedback}\"')

# Tấn công khi không có lính canh
feedback, reward, done = game.execute_action('take rusty sword')
feedback, reward, done = game.execute_action('attack with rusty sword')
assert 'Không có gì để tấn công' in feedback, '❌ Thiếu thông báo'
print(f'✅ Tấn công không lính canh: feedback=\"{feedback}\"')

print('\\n✅ Tất cả test xử lý lỗi đều đúng!')
"
```

### 7. Test reset — Đặt lại trò chơi

```bash
python3 -c "
from game_environments import TreasureHuntGame

game = TreasureHuntGame(seed=42)

# Thay đổi trạng thái
game.execute_action('take rusty sword')
assert len(game.inventory) == 1, '❌ Inventory sai'

# Reset
game.reset(seed=42)
assert len(game.inventory) == 0, '❌ Reset không xóa inventory'
assert game.current_room.name == 'entrance', '❌ Reset không về entrance'
assert game.moves == 0, '❌ Reset không đặt lại moves'
assert game.score == 0, '❌ Reset không đặt lại score'
assert game.game_over == False, '❌ Reset không đặt lại game_over'

print('✅ Reset hoạt động đúng!')
"
```

### 8. Chạy tất cả test cùng lúc

```bash
# Chạy tuần tự tất cả test ở trên
python3 -c "
from game_environments import TreasureHuntGame, ItemType

print('=' * 60)
print('  CHẠY TOÀN BỘ TEST SUITE')
print('=' * 60)

# --- Test 1: Import ---
game = TreasureHuntGame(seed=42)
print('\\n[1/7] ✅ Import và khởi tạo thành công')

# --- Test 2: ItemType ---
expected_types = {'KEY': 'chìa khóa', 'WEAPON': 'vũ khí', 'TREASURE': 'kho báu', 'TOOL': 'công cụ', 'POTION': 'thuốc'}
for name, value in expected_types.items():
    assert ItemType[name].value == value
print('[2/7] ✅ ItemType values đúng')

# --- Test 3: Bản đồ ---
assert len(game.rooms) == 5
assert game.current_room.name == 'entrance'
assert game.rooms['guard_room'].has_guard
print('[3/7] ✅ Cấu trúc bản đồ đúng')

# --- Test 4: Giải pháp tối ưu ---
game = TreasureHuntGame(seed=42)
for action in ['take rusty sword', 'go east', 'take red key', 'take magic crystal',
               'try crafting', 'go west', 'go north', 'go north',
               'attack with silver sword', 'go east', \"take dragon's treasure\"]:
    game.execute_action(action)
assert game.victory
print('[4/7] ✅ Giải pháp tối ưu hoạt động')

# --- Test 5: Stochastic ---
rewards = set()
for s in range(10):
    g = TreasureHuntGame(seed=s, stochastic=True)
    _, r, _ = g.execute_action('take rusty sword')
    rewards.add(round(r, 4))
assert len(rewards) > 1
print('[5/7] ✅ Stochastic mode hoạt động')

# --- Test 6: Xử lý lỗi ---
game = TreasureHuntGame(seed=42)
f, r, _ = game.execute_action('go west')
assert r < 0
f, r, _ = game.execute_action('fly away')
assert r < 0
print('[6/7] ✅ Xử lý lỗi đúng')

# --- Test 7: Reset ---
game = TreasureHuntGame(seed=42)
game.execute_action('take rusty sword')
game.reset(seed=42)
assert len(game.inventory) == 0
assert game.moves == 0
print('[7/7] ✅ Reset hoạt động đúng')

print('\\n' + '=' * 60)
print('  ✅ TẤT CẢ 7/7 TEST ĐỀU THÀNH CÔNG!')
print('=' * 60)
"
```

---

## 📚 Tham Khảo

- **Shunyu Yao** — [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- **Reinforcement Learning từ text games** — Cách thiết kế môi trường cho LLM Agent
- **CAMEL Framework** — [camel-ai.org](https://www.camel-ai.org/)
