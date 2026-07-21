"""
Agent dựa trên LLM sử dụng Học Tập Trong Ngữ Cảnh (In-Context Learning) với OpenAI API.
Minh họa cách LLM có thể tổng quát hóa thông qua lý luận mà không cần huấn luyện chuyên sâu.

Mô hình mặc định: gpt-4o-mini (cấu hình trong .env).
Có thể ghi đè bằng tham số `model` hoặc biến môi trường DEFAULT_MODEL_TYPE.
"""

import os
import json
import time
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
import openai
from dotenv import load_dotenv
from game_environments import TreasureHuntGame

# Tải biến môi trường từ file .env (OPENAI_API_KEY, DEFAULT_MODEL_TYPE)
load_dotenv()


# === Dataclass lưu trữ kinh nghiệm tương tác ===

@dataclass
class GameExperience:
    """Đại diện cho một lần tương tác trong trò chơi.
    
    Mỗi kinh nghiệm ghi lại: trạng thái trước khi hành động, hành động đã thực hiện,
    phản hồi từ môi trường, reward nhận được, và kết quả (thành công/thất bại).
    Dùng để xây dựng context cho LLM trong các lượt chơi tiếp theo.
    
    Attributes:
        state_description: Mô tả trạng thái trò chơi lúc đó
        action: Hành động đã thực hiện
        feedback: Phản hồi từ môi trường
        reward: Giá trị reward nhận được
        success: Hành động có dẫn đến kết quả tích cực không
    """
    state_description: str
    action: str
    feedback: str
    reward: float
    success: bool  # Hành động có dẫn đến kết quả tích cực không


# === Class Agent chính ===

class LLMAgent:
    """
    Agent dựa trên LLM sử dụng In-Context Learning để chơi trò chơi.
    
    Agent lưu trữ các kinh nghiệm từ những lượt chơi trước và sử dụng chúng
    làm ngữ cảnh để LLM lý luận và đưa ra quyết định tốt hơn trong tương lai.
    Không cần huấn luyện trọng số — chỉ tích lũy kinh nghiệm trong prompt.
    """
    
    def __init__(self,
                 api_key: str = None,
                 model: str = None,
                 temperature: float = 0.7,
                 max_experiences: int = 50):
        """
        Khởi tạo LLM Agent với OpenAI API.
        
        Tự động đọc OPENAI_API_KEY và DEFAULT_MODEL_TYPE từ file .env.
        Có thể ghi đè bằng tham số truyền vào.
        
        Args:
            api_key: OpenAI API key (hoặc đặt OPENAI_API_KEY trong .env)
            model: Tên mô hình (mặc định: đọc từ DEFAULT_MODEL_TYPE trong .env, 
                   nếu không có thì dùng gpt-4o-mini)
            temperature: Nhiệt độ lấy mẫu cho việc sinh text (0.0-2.0)
            max_experiences: Số lượng kinh nghiệm tối đa lưu trữ trong bộ nhớ
        """
        # Thiết lập API key — ưu tiên tham số truyền vào, sau đó đọc từ .env
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Không tìm thấy API key. Đặt OPENAI_API_KEY trong file .env "
                "hoặc truyền tham số api_key khi khởi tạo."
            )
        
        # Xác định mô hình sử dụng
        self.model = model or os.getenv("DEFAULT_MODEL_TYPE", "gpt-4o-mini")
        
        # Khởi tạo OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        self.temperature = temperature
        
        # Bộ nhớ kinh nghiệm cho In-Context Learning
        self.experiences: List[GameExperience] = []
        self.max_experiences = max_experiences
        
        # Thống kê hiệu suất
        self.episode_rewards = []   # Reward mỗi episode
        self.episode_lengths = []   # Số bước mỗi episode
        self.victories = 0          # Tổng số lần chiến thắng
        self.total_episodes = 0     # Tổng số episode đã chơi
        self.api_calls = 0          # Tổng số lần gọi API
        self.total_tokens = 0       # Tổng số token đã sử dụng
        
        print(f"🤖 LLM Agent khởi tạo thành công!")
        print(f"   Mô hình: {self.model}")
        print(f"   Nhiệt độ: {self.temperature}")
        print(f"   Bộ nhớ tối đa: {self.max_experiences} kinh nghiệm")
    
    def _build_context(self, current_state: str, available_actions: List[str]) -> str:
        """
        Xây dựng ngữ cảnh cho LLM bao gồm mô tả nhiệm vụ và kinh nghiệm trước đó.
        
        Đây là phần cốt lõi của In-Context Learning: cung cấp cho LLM các kinh nghiệm
        thành công và thất bại từ quá khứ để nó tự rút ra bài học và chiến lược.
        
        Args:
            current_state: Mô tả trạng thái hiện tại của trò chơi
            available_actions: Danh sách hành động khả dụng
            
        Returns:
            Chuỗi ngữ cảnh hoàn chỉnh để đưa vào prompt
        """
        context = []
        
        # Mô tả nhiệm vụ — giúp LLM hiểu mục tiêu và cơ chế trò chơi
        context.append("""Bạn đang chơi một trò chơi săn tìm kho báu dựa trên văn bản. Mục tiêu là tìm và thu thập kho báu của rồng (dragon's treasure).

Trò chơi có các cơ chế ẩn mà bạn cần khám phá qua kinh nghiệm:
- Một số vật phẩm có thể cần để mở khóa cửa hoặc đánh bại lính canh
- Các vật phẩm có thể kết hợp để tạo vật phẩm tốt hơn
- Các vũ khí khác nhau có hiệu quả khác nhau

Bạn nên suy luận từ những kinh nghiệm trước đó để đưa ra quyết định tốt hơn.""")
        
        # Thêm kinh nghiệm từ quá khứ — phân loại thành công/thất bại
        if self.experiences:
            context.append("\n=== KINH NGHIỆM TRƯỚC ĐÓ ===")
            context.append("Dưới đây là một số kinh nghiệm từ các lượt chơi trước có thể giúp bạn:")
            
            # Phân loại kinh nghiệm thành mẫu thành công và thất bại
            successful_patterns = []
            failed_patterns = []
            
            for exp in self.experiences[-self.max_experiences:]:
                exp_text = f"Trạng thái: {exp.state_description[:200]}...\nHành động: {exp.action}\nKết quả: {exp.feedback}\nReward: {exp.reward:.1f}"
                
                if exp.success:
                    successful_patterns.append(exp_text)
                else:
                    failed_patterns.append(exp_text)
            
            if successful_patterns:
                context.append("\n** Hành động thành công:")
                for pattern in successful_patterns[-10:]:  # 10 mẫu thành công gần nhất
                    context.append(pattern)
            
            if failed_patterns:
                context.append("\n** Hành động thất bại cần tránh:")
                for pattern in failed_patterns[-5:]:  # 5 mẫu thất bại gần nhất
                    context.append(pattern)
        
        # Tình huống hiện tại
        context.append("\n=== TÌNH HUỐNG HIỆN TẠI ===")
        context.append(current_state)
        context.append(f"\nHành động khả dụng: {', '.join(available_actions)}")
        
        return "\n".join(context)
    
    def _build_prompt(self, context: str) -> str:
        """Xây dựng prompt hoàn chỉnh cho LLM.
        
        Yêu cầu LLM suy luận từng bước (chain-of-thought) trước khi chọn hành động.
        Kết quả phải kết thúc bằng dòng "ACTION:" theo đúng format.
        
        Args:
            context: Chuỗi ngữ cảnh đã xây dựng từ _build_context()
            
        Returns:
            Prompt hoàn chỉnh sẵn sàng gửi cho LLM
        """
        prompt = f"""{context}

Dựa trên hiểu biết về cơ chế trò chơi từ kinh nghiệm trước đó và tình huống hiện tại, hãy suy luận từng bước về hành động cần thực hiện:

1. Bạn đã học được gì từ kinh nghiệm trước đó áp dụng được ở đây?
2. Mục tiêu hoặc mục tiêu phụ hiện tại của bạn là gì?
3. Hành động nào trong danh sách khả dụng giúp đạt mục tiêu tốt nhất?

Hãy suy nghĩ kỹ, sau đó đưa ra hành động đã chọn.

QUAN TRỌNG: Phản hồi của bạn PHẢI kết thúc bằng đúng một dòng bắt đầu với "ACTION:" theo sau là một trong các hành động khả dụng đã liệt kê ở trên.

Ví dụ format:
[Lý luận của bạn ở đây...]
ACTION: take red key
"""
        return prompt
    
    def choose_action(self, game: TreasureHuntGame, verbose: bool = True) -> str:
        """
        Chọn hành động sử dụng lý luận LLM kết hợp In-Context Learning.
        
        Xây dựng prompt từ kinh nghiệm tích lũy + trạng thái hiện tại,
        gọi API LLM, phân tích phản hồi để trích xuất hành động.
        Có cơ chế fallback nếu không parse được hành động hợp lệ.
        
        Args:
            game: Instance trò chơi hiện tại
            verbose: Có hiển thị chi tiết quá trình suy luận không
            
        Returns:
            Chuỗi hành động đã chọn
        """
        # Lấy trạng thái hiện tại và danh sách hành động khả dụng
        state_description = game.get_state_description()
        available_actions = game.get_available_actions()
        
        if not available_actions:
            return "look around"
        
        # Xây dựng ngữ cảnh với kinh nghiệm trước đó
        context = self._build_context(state_description, available_actions)
        prompt = self._build_prompt(context)
        
        if verbose:
            print("\n" + "="*60)
            print("QUÁ TRÌNH QUYẾT ĐỊNH CỦA LLM")
            print("="*60)
            print(f"📊 Kinh nghiệm trong bộ nhớ: {len(self.experiences)}")
            print(f"🎮 Phòng hiện tại: {game.current_room.name}")
            print(f"🎯 Số hành động khả dụng: {len(available_actions)}")
            
            # Hiển thị một số kinh nghiệm thành công gần đây
            successful = [e for e in self.experiences if e.success]
            if successful:
                print(f"\n💡 Mẫu thành công gần đây đã học được:")
                for exp in successful[-3:]:
                    print(f"   • {exp.action} → +{exp.reward:.1f} reward")
        
        try:
            print("\n🤔 LLM đang suy luận...")
            
            # Gọi OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Bạn là một agent thông minh chơi trò chơi, có khả năng học hỏi từ kinh nghiệm."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=2048
            )
            
            # Cập nhật thống kê API
            self.api_calls += 1
            if hasattr(response.usage, 'total_tokens'):
                self.total_tokens += response.usage.total_tokens
            
            # Trích xuất hành động từ phản hồi LLM
            response_text = response.choices[0].message.content or ""
            
            if verbose:
                print("\n📝 Lý luận của LLM:")
                print("-" * 40)
                # Hiển thị phần lý luận (trước ACTION:)
                reasoning_lines = []
                for line in response_text.split('\n'):
                    if line.startswith("ACTION:"):
                        break
                    if line.strip():
                        reasoning_lines.append(line)
                
                # Hiển thị vài dòng cuối của lý luận
                for line in reasoning_lines[-5:]:
                    print(f"  {line[:100]}...")  # Cắt ngắn dòng dài
                print("-" * 40)
            
            # Phân tích hành động từ phản hồi — tìm dòng "ACTION:" từ cuối lên
            lines = response_text.strip().split('\n')
            for line in reversed(lines):
                if line.startswith("ACTION:"):
                    action = line[7:].strip()
                    
                    # Xác thực hành động — kiểm tra trong danh sách khả dụng
                    if action in available_actions:
                        if verbose:
                            print(f"\n✅ Hành động đã chọn: {action}")
                        return action
                    else:
                        # Thử tìm hành động khớp (không phân biệt hoa thường)
                        action_lower = action.lower()
                        for available in available_actions:
                            if available.lower() == action_lower:
                                if verbose:
                                    print(f"\n✅ Hành động đã chọn (đã sửa): {available}")
                                return available
            
            # Fallback — không tìm thấy hành động hợp lệ
            print(f"⚠️ Cảnh báo: Không thể phân tích hành động hợp lệ từ phản hồi LLM. Dùng hành động mặc định.")
            return available_actions[0]
            
        except Exception as e:
            print(f"❌ Lỗi khi gọi LLM API: {e}")
            # Fallback — dùng hành động đầu tiên trong danh sách
            return available_actions[0]
    
    def update_experience(self, state: str, action: str, feedback: str, reward: float):
        """
        Lưu một kinh nghiệm vào bộ nhớ cho In-Context Learning trong tương lai.
        
        Tự động phân loại kinh nghiệm là thành công (reward > 0) hoặc thất bại.
        Khi bộ nhớ đầy, giữ lại hỗn hợp kinh nghiệm thành công và thất bại gần nhất
        để đảm bảo LLM học được cả điều nên làm và điều nên tránh.
        
        Args:
            state: Mô tả trạng thái trước khi hành động
            action: Hành động đã thực hiện
            feedback: Phản hồi từ môi trường
            reward: Giá trị reward nhận được
        """
        # Xác định thành công dựa trên reward
        success = reward > 0
        
        experience = GameExperience(
            state_description=state,
            action=action,
            feedback=feedback,
            reward=reward,
            success=success
        )
        
        self.experiences.append(experience)
        
        # Quản lý bộ nhớ — giữ kích thước hợp lý để không vượt context length
        if len(self.experiences) > self.max_experiences * 2:
            # Giữ hỗn hợp kinh nghiệm thành công và thất bại
            successful = [e for e in self.experiences if e.success]
            failed = [e for e in self.experiences if not e.success]
            
            # Giữ lại các kinh nghiệm gần đây và một số kinh nghiệm cũ đa dạng
            self.experiences = (
                successful[-self.max_experiences:] + 
                failed[-self.max_experiences//2:]
            )[-self.max_experiences:]
    
    def play_episode(self, game: TreasureHuntGame, verbose: bool = True) -> Tuple[float, int, bool]:
        """
        Chơi một episode (ván) của trò chơi.
        
        Vòng lặp chính: quan sát trạng thái → LLM chọn hành động → thực thi →
        lưu kinh nghiệm → lặp lại cho đến khi game over.
        
        Args:
            game: Instance trò chơi
            verbose: Có hiển thị chi tiết không
            
        Returns:
            Tuple gồm: tổng reward, số bước, có chiến thắng không
        """
        game.reset()
        total_reward = 0
        steps = 0
        trajectory = []  # Lưu lại toàn bộ quỹ đạo hành động
        
        if verbose:
            print("\n" + "🎮"*30)
            print("BẮT ĐẦU EPISODE MỚI")
            print("🎮"*30)
        
        while not game.game_over:
            if verbose:
                print(f"\n{'='*60}")
                print(f"BƯỚC {steps + 1}")
                print(f"{'='*60}")
                
                # Hiển thị trạng thái trò chơi hiện tại
                print("\n📍 Trạng thái hiện tại:")
                state_lines = game.get_state_description().split('\n')
                for line in state_lines:
                    if line.strip():
                        print(f"  {line}")
            
            # Ghi lại trạng thái trước khi hành động
            state_before = game.get_state_description()
            
            # LLM chọn hành động
            action = self.choose_action(game, verbose=verbose)
            
            # Thực thi hành động trong môi trường
            feedback, reward, done = game.execute_action(action)
            
            # Lưu kinh nghiệm vào bộ nhớ
            self.update_experience(state_before, action, feedback, reward)
            
            # Ghi lại quỹ đạo
            trajectory.append({
                "step": steps + 1,
                "action": action,
                "reward": reward,
                "feedback": feedback
            })
            
            total_reward += reward
            steps += 1
            
            if verbose:
                print(f"\n🎯 Kết quả hành động:")
                print(f"  Phản hồi: {feedback}")
                if reward > 0:
                    print(f"  Reward: ✨ +{reward:.1f}")
                else:
                    print(f"  Reward: 📉 {reward:.1f}")
                print(f"  Tổng reward hiện tại: {total_reward:.1f}")
                
                # Thêm khoảng dừng giữa các bước để dễ đọc
                if not done:
                    print("\n" + "."*60)
        
        # Cập nhật thống kê tổng
        self.episode_rewards.append(total_reward)
        self.episode_lengths.append(steps)
        if game.victory:
            self.victories += 1
        self.total_episodes += 1
        
        if verbose:
            print("\n" + "🏁"*30)
            if game.victory:
                print("🎉 CHIẾN THẮNG! LLM đã tìm thấy kho báu!")
            else:
                print("💀 THUA CUỘC! Chúc may mắn lần sau.")
            print(f"  Điểm cuối cùng: {total_reward:.1f}")
            print(f"  Tổng số bước: {steps}")
            print(f"  Số lần gọi API: {self.api_calls}")
            print("🏁"*30)
        
        return total_reward, steps, game.victory
    
    def train(self, num_episodes: int = 20, verbose: bool = True, stochastic: bool = False) -> Dict[str, Any]:
        """
        'Huấn luyện' Agent thông qua In-Context Learning qua nhiều episode.
        
        Lưu ý: Khác với RL truyền thống, ở đây không có huấn luyện trọng số —
        chỉ tích lũy kinh nghiệm vào bộ nhớ để LLM tham khảo trong prompt.
        
        Args:
            num_episodes: Số episode cần chơi
            verbose: Có hiển thị chi tiết không
            stochastic: Có dùng môi trường ngẫu nhiên không
            
        Returns:
            Dict chứa thống kê: tổng episode, chiến thắng, tỷ lệ thắng, 
            API calls, tokens, kinh nghiệm, rewards, và số bước mỗi episode
        """
        game = TreasureHuntGame(stochastic=stochastic)
        
        print("\n" + "🚀"*30)
        print("THÍ NGHIỆM IN-CONTEXT LEARNING VỚI LLM")
        print("🚀"*30)
        print(f"\n📝 Sẽ chơi {num_episodes} episode để học trò chơi")
        print("🧠 LLM học bằng cách tích lũy kinh nghiệm trong ngữ cảnh")
        print("⚡ Mỗi quyết định hiển thị toàn bộ quá trình suy luận")
        
        for episode in range(num_episodes):
            print(f"\n\n{'🎯'*30}")
            print(f"EPISODE {episode + 1} / {num_episodes}")
            print(f"{'🎯'*30}")
            print(f"📚 Kinh nghiệm đã tích lũy: {len(self.experiences)}")
            
            # Hiển thị đầy đủ cho 3 episode đầu và episode cuối, rút gọn cho phần giữa
            show_full = verbose and (episode < 3 or episode == num_episodes - 1)
            
            if not show_full and verbose:
                print("\n(Rút gọn hiển thị cho các episode giữa để tiết kiệm không gian...)")
            
            reward, steps, victory = self.play_episode(game, verbose=show_full)
            
            if not show_full:
                # Vẫn hiển thị tóm tắt dù không hiển thị đầy đủ
                print(f"\n📊 Tóm tắt Episode {episode + 1}:")
                print(f"  Kết quả: {'🎉 Chiến thắng!' if victory else '💀 Thất bại'}")
                print(f"  Tổng Reward: {reward:.2f}")
                print(f"  Số bước: {steps}")
                print(f"  Tổng lần gọi API: {self.api_calls}")
            
            # Hiển thị tiến trình học tập
            if len(self.episode_rewards) >= 3:
                recent_victories = sum(1 for r in self.episode_rewards[-3:] if r > 50)
                recent_avg = sum(self.episode_rewards[-3:]) / 3
                print(f"\n📈 Hiệu suất gần đây (3 episode cuối):")
                print(f"  Chiến thắng: {recent_victories}/3")
                print(f"  Reward trung bình: {recent_avg:.2f}")
            
            # Tạm dừng giữa các episode để tôn trọng giới hạn tốc độ API
            if episode < num_episodes - 1:
                print("\n⏳ Đợi 1 giây cho giới hạn tốc độ API...")
                time.sleep(1)
        
        return {
            "total_episodes": self.total_episodes,
            "total_victories": self.victories,
            "victory_rate": self.victories / self.total_episodes if self.total_episodes > 0 else 0,
            "total_api_calls": self.api_calls,
            "total_tokens": self.total_tokens,
            "experiences_collected": len(self.experiences),
            "episode_rewards": self.episode_rewards,
            "episode_lengths": self.episode_lengths
        }
    
    def evaluate(self, num_episodes: int = 10, verbose: bool = False, stochastic: bool = False) -> Dict[str, Any]:
        """
        Đánh giá hiệu suất Agent sử dụng kinh nghiệm đã tích lũy.
        
        Chạy nhiều episode đánh giá và trả về thống kê tổng hợp.
        Kinh nghiệm mới vẫn được tích lũy trong quá trình đánh giá.
        
        Args:
            num_episodes: Số episode để đánh giá
            verbose: Có hiển thị chi tiết không
            stochastic: Có dùng môi trường ngẫu nhiên không
            
        Returns:
            Dict chứa thống kê đánh giá: số episode, chiến thắng, 
            tỷ lệ thắng, reward trung bình, số bước trung bình
        """
        game = TreasureHuntGame(stochastic=stochastic)
        eval_rewards = []
        eval_lengths = []
        eval_victories = 0
        
        for episode in range(num_episodes):
            reward, steps, victory = self.play_episode(game, verbose=verbose)
            
            eval_rewards.append(reward)
            eval_lengths.append(steps)
            if victory:
                eval_victories += 1
            
            if verbose:
                print(f"Episode {episode + 1}: Reward={reward:.2f}, Bước={steps}, Chiến thắng={victory}")
        
        return {
            "num_episodes": num_episodes,
            "victories": eval_victories,
            "victory_rate": eval_victories / num_episodes if num_episodes else 0.0,
            "avg_reward": sum(eval_rewards) / len(eval_rewards) if eval_rewards else 0.0,
            "avg_length": sum(eval_lengths) / len(eval_lengths) if eval_lengths else 0.0,
            "total_api_calls": self.api_calls,
            "experiences_used": len(self.experiences)
        }
    
    def save_experiences(self, filepath: str):
        """Lưu kinh nghiệm ra file JSON để phân tích.
        
        Lưu cả danh sách kinh nghiệm lẫn thống kê tổng hợp.
        
        Args:
            filepath: Đường dẫn file JSON đích
        """
        data = {
            "experiences": [asdict(exp) for exp in self.experiences],
            "statistics": {
                "total_episodes": self.total_episodes,
                "victories": self.victories,
                "api_calls": self.api_calls,
                "total_tokens": self.total_tokens
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_experiences(self, filepath: str):
        """Tải kinh nghiệm từ file JSON.
        
        Khôi phục danh sách kinh nghiệm và thống kê từ file đã lưu trước đó.
        
        Args:
            filepath: Đường dẫn file JSON nguồn
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.experiences = [
            GameExperience(**exp) for exp in data["experiences"]
        ]
        
        stats = data.get("statistics", {})
        self.total_episodes = stats.get("total_episodes", 0)
        self.victories = stats.get("victories", 0)
        self.api_calls = stats.get("api_calls", 0)
        self.total_tokens = stats.get("total_tokens", 0)