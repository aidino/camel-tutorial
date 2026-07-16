# Datagen

Các mô-đun tạo dữ liệu của CAMEL dành cho các bộ dữ liệu chất lượng cao, được tinh chỉnh theo hướng dẫn và giàu khả năng suy luận.

Trang này giới thiệu các mô-đun tạo dữ liệu của CAMEL nhằm tạo ra dữ liệu huấn luyện chất lượng cao với lập luận rõ ràng, hướng dẫn đa dạng và tinh chỉnh tự động nâng cao.

- **Chain of Thought (CoT)**: Tạo ra các đường dẫn lập luận rõ ràng
- **Self-Instruct**: Tạo dữ liệu tuân theo hướng dẫn từ cả con người và máy móc
- **Source2Synth**: Tổng hợp QA đa bước từ văn bản nguồn hoặc mã nguồn
- **Self-Improving CoT**: Cải thiện lặp đi lặp lại khả năng suy luận thông qua việc tự phê bình của agent

## Chain of Thought (CoT) Data Generation

Việc tạo dữ liệu Chain of Thought (CoT) xây dựng các lộ trình suy luận từng bước để giải quyết vấn đề, tận dụng các agent kép và logic tìm kiếm/xác minh nâng cao.

### Key Features 

- Monte Carlo Tree Search (MCTS) để khám phá giải pháp
- Phát hiện lỗi bằng tìm kiếm nhị phân để định vị lỗi chính xác
- Hệ thống xác minh Dual-Agent để đảm bảo chất lượng
- Quản lý Solution Tree để theo dõi các đường dẫn suy luận

#### Core Components

#### `CoTDataGenerator` Class

Lớp chính triển khai hệ thống tạo CoT với các khả năng sau:

- Kiến trúc Dual-Agent: Hỗ trợ cả chế độ single-agent (kế thừa) và dual-agent
- Tạo câu trả lời: Tạo câu trả lời tinh vi với MCTS
- Xác minh câu trả lời: Hệ thống xác minh mạnh mẽ sử dụng golden answers
- Phát hiện lỗi: Phát hiện lỗi dựa trên tìm kiếm nhị phân trong các giải pháp
- Quản lý giải pháp: Quản lý và xuất cây giải pháp toàn diện

#### Quick Start: CoT Data Generation

Triển khai việc tạo dữ liệu chuỗi suy nghĩ với hai tác nhân, câu trả lời chuẩn và quá trình sinh giải pháp theo phương pháp chuỗi suy nghĩ:

```python
from camel.agents import ChatAgent
from camel.datagen import CoTDataGenerator

# Initialize agents
generator_agent = ChatAgent("Generator agent for simple math computation.")
verifier_agent = ChatAgent("Verified agent for simple math computation.")

# Define golden answers
question = "What's the answer of 1 + 2?"

golden_answers = {
    question: "3",
}

# Create generator
cot_generator = CoTDataGenerator(
    generator_agent=generator_agent,
    verifier_agent=verifier_agent,
    golden_answers=golden_answers,
    search_limit=3,
)

# Generate solution
solution = cot_generator.solve(question)
```

#### Data Import/Export for CoT

Dễ dàng nhập các cặp câu hỏi-câu trả lời hoặc xuất các giải pháp đã được tạo ra để sử dụng tiếp theo:

```python
# Import QA pairs from JSON
cot_generator.import_qa_from_json("qa_pairs.json")

# Export solutions
cot_generator.export_solutions("solutions.json")
```

### Solution Generation Process

#### Direct Solution Attempt - Nỗ lực giải quyết trực tiếp

#### MCTS-Based Exploration - Khám phá dựa trên MCTS

#### Error Detection & Correction

#### Solution Verification  

