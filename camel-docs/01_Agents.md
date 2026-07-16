# Agents

Tìm hiểu về các loại agent của CAMEL, tập trung vào ChatAgent và các kiến trúc agent tiên tiến để tự động hóa bằng AI.

## Concept

Các Agent trong CAMEL là các thực thể tự trị có khả năng thực hiện các nhiệm vụ cụ thể thông qua tương tác với các mô hình ngôn ngữ và các thành phần khác. Mỗi agent được thiết kế với một vai trò và năng lực riêng biệt, cho phép chúng hoạt động độc lập hoặc cộng tác để đạt được các mục tiêu phức tạp.

> Hãy nghĩ về một agent như một đồng đội được hỗ trợ bởi AI, mang đến một vai trò xác định, bộ nhớ và khả năng sử dụng công cụ cho mọi quy trình làm việc. Các agent của CAMEL có tính lắp ghép cao, mạnh mẽ và có thể được mở rộng với logic tùy chỉnh.

## Base Agent Architecture  

Tất cả các agent CAMEL đều kế thừa từ lớp trừu tượng BaseAgent , lớp này định nghĩa hai phương thức thiết yếu:

- `reset()`: 
- `step()`

| Method   | Purpose            | Description                                            |
| -------- | ------------------ | ------------------------------------------------------ |
| `reset`  | Quản lý trạng thái | Đặt lại tác nhân về trạng thái ban đầu                 |
| `step()` | Thực thi nhiệm vụ  | Thực hiện một bước đơn lẻ trong hoạt động của tác nhân |
|          |                    |                                                        |

## Types

### ChatAgent

`ChatAgent` là triển khai chính xử lý các cuộc hội thoại với các mô hình ngôn ngữ. Nó hỗ trợ:

- Cấu hình thông điệp hệ thống để định nghĩa vai trò
- Quản lý bộ nhớ cho lịch sử hội thoại
- Khả năng gọi công cụ/chức năng
- Định dạng phản hồi và đầu ra có cấu trúc
- Hỗ trợ nhiều backend mô hình với các chiến lược lập lịch
- Hỗ trợ thao tác không đồng bộ

**Other Agent Types (When to Use)**
- `CriticAgent` Tác nhân chuyên biệt để đánh giá và phê bình các phản hồi hoặc giải pháp. Được sử dụng trong các kịch bản yêu cầu đánh giá chất lượng hoặc xác thực.
- `DeductiveReasonerAgent` Tập trung vào lập luận logic và suy diễn. Phân tích các vấn đề phức tạp thành các bước nhỏ hơn, dễ quản lý.
- `EmbodiedAgent` Được thiết kế cho các kịch bản AI thể xác (embodied AI), có khả năng hiểu và phản hồi các ngữ cảnh trong thế giới thực.
- `KnowledgeGraphAgent` Chuyên xây dựng và sử dụng knowledge graphs để nâng cao khả năng lập luận và quản lý thông tin.
- `MultiHopGeneratorAgent` Xử lý các tác vụ lập luận đa bước (multi-hop reasoning), tạo ra các bước trung gian để đi đến kết luận.
- `SearchAgent` Tập trung vào các tác vụ truy xuất thông tin và tìm kiếm trên nhiều nguồn dữ liệu khác nhau.
- `TaskAgent` Xử lý việc phân tách và quản lý tác vụ, chia nhỏ các tác vụ phức tạp thành các tác vụ con dễ quản lý.

## Usage

### Basic ChatAgent Usage 

```python
from camel.agents import ChatAgent

# Create a chat agent with a system message
agent = ChatAgent(system_message="You are a helpful assistant.")

# Step through a conversation
response = agent.step("Hello, can you help me?")
```

### Simplified Agent Creation

ChatAgent hỗ trợ nhiều cách để chỉ định mô hình:

```python
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

# Method 1: Using just a string for the model name (default model platform is used)
agent_1 = ChatAgent("You are a helpful assistant.", model="gpt-4o-mini")

# Method 2: Using a ModelType enum (default model platform is used)
agent_2 = ChatAgent("You are a helpful assistant.", model=ModelType.GPT_4O_MINI)

# Method 3: Using a tuple of strings (platform, model)
agent_3 = ChatAgent("You are a helpful assistant.", model=("openai", "gpt-4o-mini"))

# Method 4: Using a tuple of enums
agent_4 = ChatAgent(
    "You are a helpful assistant.",
    model=(ModelPlatformType.ANTHROPIC, ModelType.CLAUDE_HAIKU_4_5),
)

# Method 5: Using default model platform and default model type when none is specified
agent_5 = ChatAgent("You are a helpful assistant.")

# Method 6: Using a pre-created model with ModelFactory (original approach)
model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI,  # Using enum
    model_type=ModelType.GPT_4O_MINI,         # Using enum
)
agent_6 = ChatAgent("You are a helpful assistant.", model=model)

# Method 7: Using ModelFactory with string parameters
model = ModelFactory.create(
    model_platform="openai",     # Using string
    model_type="gpt-4o-mini",    # Using string
)
agent_7 = ChatAgent("You are a helpful assistant.", model=model)
```

### Using Tools with Chat Agent

```python
from camel.agents import ChatAgent
from camel.toolkits import FunctionTool

# Define a tool
def calculator(a: int, b: int) -> int:
    return a + b

# Create agent with tool
agent = ChatAgent(tools=[calculator])

# The agent can now use the calculator tool in conversations
response = agent.step("What is 5 + 3?")
```

### Structured Output

`ChatAgent` của CAMEL có thể tạo ra đầu ra có cấu trúc bằng cách tận dụng các mô hình `Pydantic`. Tính năng này đặc biệt hữu ích khi bạn cần agent trả về dữ liệu theo một định dạng cụ thể, chẳng hạn như `JSON`. Bằng cách xác định một mô hình `Pydantic`, bạn có thể đảm bảo rằng đầu ra của agent là dễ dự đoán và dễ phân tích cú pháp.

#### Simple object

Dưới đây là cách bạn có thể nhận được phản hồi có cấu trúc từ một `ChatAgent` . Trước tiên, hãy định nghĩa một `BaseModel` chỉ rõ các trường đầu ra mong muốn. Bạn có thể thêm mô tả cho từng trường để hướng dẫn mô hình.

```python
from pydantic import BaseModel, Field
from typing import List

class JokeResponse(BaseModel):
    joke: str = Field(description="A joke")
    funny_level: int = Field(description="Funny level, from 1 to 10")

# Create agent with structured output
agent = ChatAgent(model="gpt-4o-mini")
response = agent.step("Tell me a joke.", response_format=JokeResponse)

# The response content is a JSON string
print(response.msgs[0].content)
# '{"joke": "Why don't scientists trust atoms? Because they make up everything!", "funny_level": 8}'

# Access the parsed Pydantic object
parsed_response = response.msgs[0].parsed
print(parsed_response.joke)
# "Why don't scientists trust atoms? Because they make up everything!"
print(parsed_response.funny_level)
# 8
```

#### Nested Objects and Lists

Bạn cũng có thể sử dụng các mô hình `Pydantic` lồng nhau và danh sách để định nghĩa các cấu trúc phức tạp hơn. Trong ví dụ này, chúng ta định nghĩa một `StudentList` chứa danh sách các đối tượng `Student` .

```python
from pydantic import BaseModel
from typing import List

class Student(BaseModel):
    name: str
    age: str
    email: str

class StudentList(BaseModel):
    students: List[Student]

# Create agent with structured output
agent = ChatAgent(model="gpt-4o-mini")
response = agent.step(
    "Create a list of two students with their names, ages, and email addresses.",
    response_format=StudentList,
)

# Access the parsed Pydantic object
parsed_response = response.msgs[0].parsed
for student in parsed_response.students:
    print(f"Name: {student.name}, Age: {student.age}, Email: {student.email}")
# Name: Alex, Age: 22, Email: alex@example.com
# Name: Beth, Age: 25, Email: beth@example.com
```

## Best Practices  

- **Memory Management:** 
  - Sử dụng kích thước cửa sổ phù hợp để quản lý lịch sử hội thoại
  - Xem xét giới hạn token khi xử lý các cuộc hội thoại dài
  - Sử dụng hệ thống bộ nhớ để duy trì ngữ cảnh
- **Tool Integration:**
  - Giữ cho các hàm công cụ tập trung và được ghi chép đầy đủ
  - Xử lý lỗi công cụ một cách linh hoạt
  - Sử dụng các công cụ bên ngoài cho các thao tác cần được người dùng xử lý
- **Response Handling:**
  - Triển khai các bộ kết thúc phản hồi phù hợp để kiểm soát hội thoại
  - Sử dụng đầu ra có cấu trúc khi cần các định dạng phản hồi cụ thể
  - Xử lý đúng cách các thao tác bất đồng bộ khi làm việc với các tác vụ chạy dài hạn
- **Model Specification:**
  - Sử dụng các phương thức đặc tả mô hình đơn giản hóa để có mã nguồn sạch hơn
  - Đối với các mô hình nền tảng mặc định, chỉ cần chỉ định tên mô hình dưới dạng chuỗi
  - Đối với các nền tảng cụ thể, sử dụng định dạng tuple `(platform, model)`
  - Sử dụng enums để đảm bảo an toàn kiểu dữ liệu tốt hơn và hỗ trợ IDE

## Advanced Features

Bạn có thể linh hoạt chọn mô hình mà một agent sử dụng cho từng bước bằng cách thêm chiến lược lập lịch của riêng bạn.

```python
def custom_strategy(models):
    # Custom model selection logic
    return models[0]

agent.add_model_scheduling_strategy("custom", custom_strategy)
```

Các Agent có thể phản hồi bằng bất kỳ ngôn ngữ nào. Hãy thiết lập ngôn ngữ đầu ra ngay trong lúc trò chuyện.

```python
agent.set_output_language("Spanish")
```