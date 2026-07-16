# Introduction

CAMEL-AI là một cộng đồng mã nguồn mở nhằm tìm ra các quy luật mở rộng của AI Agent cho việc tạo dữ liệu, mô phỏng thế giới và tự động hóa tác vụ.

## CAMEL-AI là gì?

CAMEL‑AI là một khung làm việc mã nguồn mở, mô-đun hóa để xây dựng các hệ thống đa tác tử thông minh. Nó cung cấp các thành phần cơ bản để:
- Tạo ra các Agent có khả năng suy luận, lập kế hoạch và hành động
- Xây dựng các Cộng đồng gồm nhiều agent với các vai trò được xác định rõ ràng
- Tích hợp các trình thông dịch (Interpreters) để thực thi và phân tích mã
- Quản lý bộ nhớ cho ngữ cảnh dài hạn và quá trình học tập
- Điều phối các quy trình Retrieval-Augmented Generation (RAG)
- Tạo dữ liệu tổng hợp ở quy mô lớn với các vòng lặp tự hướng dẫn và xác minh
- Mô phỏng các thế giới và tương tác của agent trong các môi trường như mạng xã hội

## Core Components  

- Agents: Các đơn vị suy luận nguyên tử được điều khiển bởi LLMs, có khả năng gọi công cụ và ra quyết định
- Societies: Các lớp điều phối phân công vai trò, ủy nhiệm tác vụ và quản lý sự cộng tác
- Trình thông dịch: Các backend thực thi (Python, shell, trình duyệt) để đánh giá mã trực tiếp và tự động hóa
- Bộ nhớ & Lưu trữ: Các lớp ngữ cảnh bền vững cho lịch sử trò chuyện, đầu ra của công cụ và kiến thức đã học
- Quy trình RAG: Kết hợp phân đoạn, truy xuất và tạo sinh để đưa ra các phản hồi có căn cứ và chính xác
- Công cụ Dữ liệu Tổng hợp: Các quy trình Self-instruct, Chain-of-Thought và Source2Synth kèm theo bộ xác minh
- Mô phỏng thế giới: Các nền tảng như Oasis dành cho các mô phỏng xã hội đa tác nhân quy mô lớn
- Tự động hóa tác vụ: Các bộ chuẩn như CRAB dành cho các quy trình phần mềm nhiều bước trong thực tế

## Ecosystem Highlights 

- [OASIS](https://github.com/camel-ai/oasis): Môi trường mô phỏng xã hội quy mô lớn: mô hình hóa Reddit, Twitter và các tương tác của người dùng
- [CRAB](https://crab.camel-ai.org/) Các tác vụ tự động hóa agent xuyên môi trường trên nền tảng Ubuntu và Android
- [Project Loong](https://github.com/camel-ai/loong): Tạo dữ liệu tổng hợp dựa trên trình xác minh cho hệ thống hỏi đáp chuyên ngành ở quy mô lớn
- [OWL](https://github.com/camel-ai/owl): OWL (Optimized Workforce Learning) là một khung tự động hóa đa tác nhân dành cho các nhiệm vụ thực tế. Được xây dựng trên nền tảng CAMEL-AI, nó cho phép sự cộng tác linh hoạt giữa các AI Agent bằng cách sử dụng các công cụ như trình duyệt, bộ thông dịch mã và các mô hình đa phương thức.

## Installation

Guide: https://docs.camel-ai.org/get_started/installation

