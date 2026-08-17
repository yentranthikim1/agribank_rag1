# SPEC - Buổi 6

Đây là tài liệu hướng dẫn AI Agent khi triển khai project Buổi 6.

## Workspace

Chỉ được phép đọc:

- `RAG/rag_foundation/buoi_05/output/chunks/`
- `RAG/rag_foundation/buoi_05/.venv/`
- `RAG/rag_foundation/buoi_06/`

Không đọc:

- Source code của Buổi 5
- README các buổi trước
- Notebook
- Git history
- Các thư mục khác

Buổi 5 là black box. Không reverse engineering. Không phân tích cách Buổi 5 hoạt động.

## Python

Sử dụng đúng interpreter trong:

`RAG/rag_foundation/buoi_05/.venv/`

Không tạo virtual environment mới.

## Package

Chỉ cài:

- `streamlit`
- `google-genai`
- `chromadb`
- `psycopg`
- `python-dotenv`

Không cài framework khác.

## Coding Style

Ưu tiên:

- Ít file
- Ít class
- Ít function
- Code dễ đọc

Không tạo:

- Repository pattern
- Service layer
- Dependency injection
- Factory
- Plugin

## Scope

Chỉ cần triển khai:

- Index
- Retrieval
- Answer
- Streamlit

Không phát triển ngoài yêu cầu.

## Error Handling

Chỉ cần `try/except` tối thiểu.

Không cần:

- Retry
- Logging
- Monitoring

## Security

Không in hoặc lưu:

- API key
- Password
- Secret

## Code Size

Mục tiêu khoảng 300-500 dòng Python.

Nếu vượt khoảng 700 dòng, hãy đơn giản hóa thiết kế.
