# Societies - Xã hội

Các khung tác nhân cộng tác trong CAMEL: các hành vi xã hội tự chủ, giải quyết nhiệm vụ dựa trên vai trò và các xã hội tác nhân luân phiên.

> Mô-đun society mô phỏng các hành vi xã hội của tác nhân và các quy trình làm việc cộng tác.
> 
> Nó cung cấp năng lượng cho các tác nhân đa vai trò tự chủ có thể lập kế hoạch, tranh luận, phê bình và cùng nhau giải quyết các nhiệm vụ, giảm thiểu sự can thiệp của con người trong khi tối đa hóa sự phù hợp với các mục tiêu của bạn.

## Society Concepts: How Do AI Agents Interact?

- **Task**: Một mục tiêu hoặc ý tưởng, được đưa ra dưới dạng một lời nhắc đơn giản.
- **AI User:** Vai trò chịu trách nhiệm cung cấp các hướng dẫn hoặc thách thức.
- **AI Assistant:** Vai trò được giao nhiệm vụ tạo ra các giải pháp, kế hoạch hoặc phản hồi từng bước.
- **Critic (tùy chọn):** Một agent xem xét hoặc phê bình các phản hồi của assistant để kiểm soát chất lượng.

## RolePlaying

Sự hợp tác giữa các agent theo lượt, được thiết kế qua prompt, không đảo ngược vai trò.

- Ngăn chặn việc đảo ngược vai trò, vòng lặp vô hạn và các phản hồi mơ hồ.
- Luân phiên có cấu trúc và nghiêm ngặt—người dùng và trợ lý không bao giờ hoán đổi vai trò
- Hỗ trợ các bộ lập kế hoạch tác vụ, nhà phê bình và suy luận meta tùy chọn
- Mọi tin nhắn đều tuân theo một cấu trúc được hệ thống bắt buộc

### Built-in Prompt Rules:  

- Không bao giờ quên rằng bạn là `<ASSISTANT_ROLE>` , tôi là `<USER_ROLE>`
- Không bao giờ đảo ngược vai trò hoặc chỉ đạo tôi
- Từ chối các yêu cầu không thể thực hiện hoặc không an toàn, giải thích lý do
- Luôn trả lời với tư cách: `Solution: <YOUR_SOLUTION>`
- Luôn kết thúc bằng: `Next request`


### 🧩 RolePlaying Attributes

| Attribute                       | Type               | Description                                              |
| :------------------------------ | :----------------- | :------------------------------------------------------- |
| `assistant_role_name`           | `str`              | Tên vai trò của trợ lý                                   |
| `user_role_name`                | `str`              | Tên vai trò của người dùng                               |
| `critic_role_name`              | `str`              | Tên vai trò của người phản biện (tùy chọn)               |
| `task_prompt`                   | `str`              | Lời nhắc cho nhiệm vụ chính                              |
| `with_task_specify`             | `bool`             | Kích hoạt tác nhân xác định nhiệm vụ                     |
| `with_task_planner`             | `bool`             | Bật tác nhân lập kế hoạch nhiệm vụ                       |
| `with_critic_in_the_loop`       | `bool`             | Bao gồm critic trong vòng lặp hội thoại                  |
| `critic_criteria`               | `str`              | Cách thức nhà phê bình chấm điểm/đánh giá các đầu ra     |
| `model`                         | `BaseModelBackend` | Model backend for responses                              |
| `task_type`                     | `TaskType`         | Type/category of the task                                |
| `assistant_agent_kwargs`        | `Dict`             | Tùy chọn bổ sung cho trợ lý agent                        |
| `user_agent_kwargs`             | `Dict`             | Tùy chọn bổ sung cho user agent                          |
| `task_specify_agent_kwargs`     | `Dict`             | Các tùy chọn bổ sung cho tác nhân xác định nhiệm vụ      |
| `task_planner_agent_kwargs`     | `Dict`             | Các tùy chọn bổ sung cho tác nhân lập kế hoạch nhiệm vụ  |
| `critic_kwargs`                 | `Dict`             | Các tùy chọn bổ sung cho agent phản biện                 |
| `sys_msg_generator_kwargs`      | `Dict`             | Các tùy chọn cho trình tạo thông điệp hệ thống           |
| `extend_sys_msg_meta_dicts`     | `List[Dict]`       | Extra metadata for system messages                       |
| `extend_task_specify_meta_dict` | `Dict`             | Extra metadata for task specification                    |
| `output_language`               | `str`              | Ngôn ngữ đầu ra mục tiêu                                 |
| `assistant_agent`               | `ChatAgent`        | ChatAgent tùy chỉnh để sử dụng làm trợ lý (tùy chọn)     |
| `user_agent`                    | `ChatAgent`        | ChatAgent tùy chỉnh để sử dụng làm người dùng (tùy chọn) |
|                                 |                    |                                                          |

### Get Started: RolePlaying in Action

Ví dụ: Trò chuyện đa tác nhân theo lượt với các vai trò tùy chỉnh và màu sắc đầu ra trực tiếp.

```python
from colorama import Fore
from camel.societies import RolePlaying
from camel.utils import print_text_animated

def main(model=None, chat_turn_limit=50) -> None:
  # Initialize a session for developing a trading bot
  task_prompt = "Develop a trading bot for the stock market"
  role_play_session = RolePlaying(
      assistant_role_name="Python Programmer",
      assistant_agent_kwargs=dict(model=model),
      user_role_name="Stock Trader",
      user_agent_kwargs=dict(model=model),
      task_prompt=task_prompt,
      with_task_specify=True,
      task_specify_agent_kwargs=dict(model=model),
  )

  # Print initial system messages
  print(
      Fore.GREEN
      + f"AI Assistant sys message:\\n{role_play_session.assistant_sys_msg}\\n"
  )
  print(
      Fore.BLUE + f"AI User sys message:\\n{role_play_session.user_sys_msg}\\n"
  )

  print(Fore.YELLOW + f"Original task prompt:\\n{task_prompt}\\n")
  print(
      Fore.CYAN
      + "Specified task prompt:"
      + f"\\n{role_play_session.specified_task_prompt}\\n"
  )
  print(Fore.RED + f"Final task prompt:\\n{role_play_session.task_prompt}\\n")

  n = 0
  input_msg = role_play_session.init_chat()

  # Turn-based simulation
  while n < chat_turn_limit:
      n += 1
      assistant_response, user_response = role_play_session.step(input_msg)

      if assistant_response.terminated:
          print(
              Fore.GREEN
              + (
                  "AI Assistant terminated. Reason: "
                  f"{assistant_response.info['termination_reasons']}."
              )
          )
          break
      if user_response.terminated:
          print(
              Fore.GREEN
              + (
                  "AI User terminated. "
                  f"Reason: {user_response.info['termination_reasons']}."
              )
          )
          break

      print_text_animated(
          Fore.BLUE + f"AI User:\\n\\n{user_response.msg.content}\\n"
      )
      print_text_animated(
          Fore.GREEN + "AI Assistant:\\n\\n"
          f"{assistant_response.msg.content}\\n"
      )

      if "CAMEL_TASK_DONE" in user_response.msg.content:
          break

      input_msg = assistant_response.msg

if __name__ == "__main__":
  main()
```

## Tips & Best Practices

- Sử dụng `RolePlaying` cho hầu hết các cuộc hội thoại multi-agent, có hoặc không có critic.
- Xác định các vai trò cụ thể và prompt-guardrails cho các agent của bạn—cấu trúc là tất cả!
- Hãy thử BabyAGI khi bạn muốn thực hiện các dự án mang tính mở, hướng nghiên cứu hoặc tự chủ.
- Tận dụng các tùy chọn `with_task_specify` và `with_task_planner` cho các tác vụ cực kỳ phức tạp.
- Giám sát các vòng lặp vô hạn—mỗi phản hồi của agent phải có bước tiếp theo rõ ràng hoặc kết thúc.

## More Examples & Advanced Use

- Kiểm tra `examples/society/` trong kho lưu trữ CAMEL để xem các demo xã hội tác nhân nâng cao.
- Khám phá các thiết lập có sự tham gia của nhà phê bình (`critic-in-the-loop`) để đạt độ chính xác và an toàn cao hơn.
- Tích hợp các bộ công cụ hoặc API bên ngoài vào các vòng lặp của xã hội Agent nhằm hỗ trợ các quy trình làm việc trong thực tế.
