"""
Bản demo nhanh — Minh họa toàn bộ hệ thống Săn Tìm Kho Báu.

Tệp lệnh này chạy 3 phần demo:
1. Demo môi trường trò chơi (game_environments.py) — chơi thủ công theo giải pháp tối ưu
2. Demo LLM Agent (llm_agent.py) — cho AI chơi 1 episode
3. Demo đánh giá — thống kê hiệu suất

Chạy: python quick_demo.py
"""

import os
import sys
from dotenv import load_dotenv

# Tải biến môi trường từ .env
load_dotenv()

from game_environments import TreasureHuntGame, ItemType
from llm_agent import LLMAgent


def demo_game_environment():
    """Demo 1: Môi trường trò chơi — chơi thủ công theo giải pháp tối ưu.
    
    Minh họa cách tương tác với TreasureHuntGame:
    - Khởi tạo game, xem trạng thái, thực thi hành động
    - Chạy toàn bộ giải pháp tối ưu từ đầu đến chiến thắng
    """
    print("\n" + "="*70)
    print("📦 DEMO 1: MÔI TRƯỜNG TRÒ CHƠI (game_environments.py)")
    print("="*70)
    
    # Khởi tạo trò chơi với seed cố định để tái lập kết quả
    game = TreasureHuntGame(seed=42)
    
    # Hiển thị trạng thái ban đầu
    print("\n📍 Trạng thái ban đầu:")
    print(game.get_state_description())
    
    # Hiển thị ItemType tiếng Việt
    print("\n🏷️  Các loại vật phẩm:")
    for item_type in ItemType:
        print(f"  {item_type.name:10s} = \"{item_type.value}\"")
    
    # Chạy giải pháp tối ưu
    print("\n" + "-"*70)
    print("🗺️  CHẠY GIẢI PHÁP TỐI ƯU")
    print("-"*70)
    
    optimal_actions = [
        "take rusty sword",          # Nhặt kiếm rỉ sét
        "go east",                   # Đến phòng kho
        "take red key",              # Nhặt chìa khóa đỏ
        "take magic crystal",        # Nhặt pha lê ma thuật
        "try crafting",              # Chế tạo: rusty sword + magic crystal → silver sword
        "go west",                   # Quay về sảnh lối vào
        "go north",                  # Đến hành lang (tự động mở khóa bằng red key)
        "go north",                  # Đến phòng lính canh
        "attack with silver sword",  # Đánh bại strong guard
        "go east",                   # Đến phòng kho báu
        "take dragon's treasure",    # Thu thập kho báu → CHIẾN THẮNG!
    ]
    
    total_reward = 0
    for i, action in enumerate(optimal_actions, 1):
        feedback, reward, done = game.execute_action(action)
        total_reward += reward
        
        # Biểu tượng dựa trên reward
        icon = "✨" if reward > 0 else "📉"
        print(f"  Bước {i:2d}: {action:30s} → {icon} reward={reward:+.1f} | {feedback[:70]}")
        
        if done:
            break
    
    # Kết quả
    print(f"\n{'🎉' if game.victory else '💀'} Kết quả: {'CHIẾN THẮNG' if game.victory else 'THẤT BẠI'}")
    print(f"  Tổng reward: {total_reward:.1f}")
    print(f"  Số bước: {game.moves}")
    
    # Hiển thị luật ẩn
    print("\n" + "-"*70)
    print("🔮 LUẬT ẨN CỦA TRÒ CHƠI")
    print("-"*70)
    print(game.get_hidden_rules())
    
    return game.victory


def demo_llm_agent():
    """Demo 2: LLM Agent chơi trò chơi — 1 episode với In-Context Learning.
    
    Minh họa cách LLMAgent:
    - Khởi tạo với OpenAI API (đọc từ .env)
    - Quan sát trạng thái, suy luận, chọn hành động
    - Tích lũy kinh nghiệm cho các lượt sau
    """
    print("\n" + "="*70)
    print("🤖 DEMO 2: LLM AGENT CHƠI TRÒ CHƠI (llm_agent.py)")
    print("="*70)
    
    # Kiểm tra API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Bỏ qua demo LLM Agent: OPENAI_API_KEY chưa được đặt trong .env")
        print("   Hãy thêm OPENAI_API_KEY vào file .env để chạy demo này.")
        return None
    
    # Khởi tạo Agent
    agent = LLMAgent()
    
    # Tạo trò chơi
    game = TreasureHuntGame(seed=42)
    
    # Chơi 1 episode
    print("\n🎮 Bắt đầu episode...")
    total_reward, steps, victory = agent.play_episode(game, verbose=True)
    
    # Thống kê
    print(f"\n📊 Thống kê Agent:")
    print(f"  Kinh nghiệm tích lũy: {len(agent.experiences)}")
    print(f"  Số lần gọi API: {agent.api_calls}")
    print(f"  Tổng token sử dụng: {agent.total_tokens}")
    
    return victory


def demo_stochastic():
    """Demo 3: So sánh chế độ Deterministic và Stochastic.
    
    Chạy cùng một chuỗi hành động trên cả hai chế độ
    để minh họa sự khác biệt về reward.
    """
    print("\n" + "="*70)
    print("🎲 DEMO 3: SO SÁNH DETERMINISTIC vs STOCHASTIC")
    print("="*70)
    
    test_actions = ["take rusty sword", "go east", "take red key"]
    
    # Chế độ Deterministic
    print("\n📐 Chế độ Deterministic (seed=42):")
    game_det = TreasureHuntGame(seed=42, stochastic=False)
    for action in test_actions:
        feedback, reward, done = game_det.execute_action(action)
        print(f"  {action:25s} → reward={reward:+.1f}")
    
    # Chế độ Stochastic — chạy 3 lần với seed khác nhau
    print("\n🎲 Chế độ Stochastic (3 lần chạy):")
    for seed in [1, 2, 3]:
        game_sto = TreasureHuntGame(seed=seed, stochastic=True)
        rewards = []
        for action in test_actions:
            feedback, reward, done = game_sto.execute_action(action)
            rewards.append(reward)
        print(f"  Seed {seed}: rewards = [{', '.join(f'{r:+.2f}' for r in rewards)}]")
    
    print("\n💡 Nhận xét: Stochastic thêm biến động nhỏ vào reward,")
    print("   giúp Agent học cách xử lý tình huống không chắc chắn.")


def main():
    """Hàm chính — chạy tuần tự tất cả các phần demo."""
    print("╔" + "═"*68 + "╗")
    print("║" + " BẢN DEMO NHANH — HỆ THỐNG SĂN TÌM KHO BÁU VỚI AI AGENT ".center(68) + "║")
    print("║" + " Chapter 1: Learning from Experience ".center(68) + "║")
    print("╚" + "═"*68 + "╝")
    
    # Demo 1: Môi trường trò chơi (không cần API)
    demo_game_environment()
    
    # Demo 3: So sánh Deterministic vs Stochastic (không cần API)
    demo_stochastic()
    
    # Demo 2: LLM Agent (cần OPENAI_API_KEY)
    print("\n" + "─"*70)
    print("💡 Demo LLM Agent cần OPENAI_API_KEY trong .env.")
    
    if os.getenv("OPENAI_API_KEY"):
        # Hỏi người dùng có muốn chạy demo LLM không (tốn token)
        print("   API key đã được tìm thấy!")
        print("   ⚠️  Demo LLM Agent sẽ gọi API và tốn token.")
        
        try:
            answer = input("   Bạn có muốn chạy demo LLM Agent? (y/N): ").strip().lower()
            if answer in ('y', 'yes'):
                demo_llm_agent()
            else:
                print("   Đã bỏ qua demo LLM Agent.")
        except (EOFError, KeyboardInterrupt):
            print("\n   Đã bỏ qua demo LLM Agent.")
    else:
        print("   ⚠️  OPENAI_API_KEY chưa được đặt. Bỏ qua demo LLM Agent.")
    
    # Kết thúc
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " ✅ DEMO HOÀN TẤT! ".center(68) + "║")
    print("╚" + "═"*68 + "╝")


if __name__ == "__main__":
    main()
