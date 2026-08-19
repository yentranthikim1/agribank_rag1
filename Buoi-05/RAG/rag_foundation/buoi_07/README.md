# Buổi 07: RAG semantic retrieval

## 1. Mục tiêu

Buổi 07 hoàn thiện pipeline RAG tối giản trên dữ liệu chunk đã chuẩn bị sẵn:

```text
JSON chunks -> validate -> Gemini embedding -> Chroma persistent index
           -> query embedding -> retrieval -> confidence gate
           -> grounded generation -> citation từ metadata thật
```

Ứng dụng có CLI và giao diện Streamlit. Đây là bài thực hành kỹ thuật, không phải hệ thống tư vấn pháp lý.

## 2. Quan hệ với Buổi 05 và Buổi 06

- **Buổi 05** cung cấp dữ liệu JSON chunk tại `rag_foundation/buoi_05/output/chunks/` và virtual environment dùng chung.
- **Buổi 06** là bài liền trước trong workspace; Buổi 07 không sửa code, dữ liệu hoặc storage của Buổi 06.
- Buổi 07 chỉ đọc dữ liệu Buổi 05, validate rồi lập index riêng tại `buoi_07/storage/chroma/`.

## 3. Cấu trúc thư mục

```text
buoi_07/
├── app.py                 # giao diện Streamlit, chỉ gọi API công khai của rag.py
├── rag.py                 # loader, embedding, index, retrieval, generation, citation
├── SPEC_buoi_07.md        # đặc tả kỹ thuật
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── storage/
│   └── .gitkeep
└── tests/
    ├── test_rag.py
    └── fixtures/chunks_sample.json
```

Đường dẫn trong code được suy ra từ `Path(__file__).resolve()`, không phụ thuộc current working directory.

## 4. Điều kiện đầu vào

- Windows, Linux hoặc macOS.
- Python 3.11+.
- Dữ liệu chunk JSON hợp lệ của Buổi 05.
- Virtual environment Buổi 05 đã có các package trong `requirements.txt`.
- Chỉ cần API key Gemini khi index hoặc query bằng embedding/generation thật.

## 5. Dùng virtual environment Buổi 05

Các lệnh dưới đây chạy từ thư mục gốc `RAG`, tức thư mục chứa trực tiếp `rag_foundation/`. Không tạo virtual environment mới cho Buổi 07.

### Windows PowerShell

```powershell
$PY = ".\rag_foundation\buoi_05\.venv\Scripts\python.exe"
```

### Linux/macOS

```bash
PY="./rag_foundation/buoi_05/.venv/bin/python"
```

## 6. Cài requirements

Windows:

```powershell
& $PY -m pip install -r .\rag_foundation\buoi_07\requirements.txt
```

Linux/macOS:

```bash
"$PY" -m pip install -r ./rag_foundation/buoi_07/requirements.txt
```

## 7. Tạo `.env`

Sao chép `.env.example` thành `.env` trong thư mục Buổi 07. Không commit `.env` và không dán API key vào chat.

Windows:

```powershell
Copy-Item .\rag_foundation\buoi_07\.env.example .\rag_foundation\buoi_07\.env
```

Linux/macOS:

```bash
cp ./rag_foundation/buoi_07/.env.example ./rag_foundation/buoi_07/.env
```

Các biến môi trường:

| Biến | Ý nghĩa |
|---|---|
| `GEMINI_API_KEY` | API key local cho Gemini; không in ra output. |
| `GEMINI_EMBEDDING_MODEL` | Model tạo embedding cho document và query. |
| `GEMINI_EMBEDDING_DIM` | Số chiều embedding, từ 128 đến 3072. |
| `GEMINI_GENERATION_MODEL` | Model tổng hợp câu trả lời. |
| `DEFAULT_TOP_K` | Số evidence mặc định, từ 1 đến 20. |
| `RAG_MAX_DISTANCE` | Ngưỡng cosine distance không âm dùng cho confidence gate. Đây không phải xác suất. |

## 8. Các lệnh chính

### Validate

Đọc và validate JSON, không gọi Gemini và không tạo Chroma collection.

Windows:

```powershell
& $PY .\rag_foundation\buoi_07\rag.py validate --strategy hierarchical
```

Linux/macOS:

```bash
"$PY" ./rag_foundation/buoi_07/rag.py validate --strategy hierarchical
```

Có thể thay strategy bằng `semantic` hoặc `fixed-size`.

### Status

`status` là thao tác read-only: không gọi Gemini, không tạo collection rỗng.

Windows:

```powershell
& $PY .\rag_foundation\buoi_07\rag.py status --strategy hierarchical
```

Linux/macOS:

```bash
"$PY" ./rag_foundation/buoi_07/rag.py status --strategy hierarchical
```

### Index

```powershell
& $PY .\rag_foundation\buoi_07\rag.py index --strategy hierarchical
```

```bash
"$PY" ./rag_foundation/buoi_07/rag.py index --strategy hierarchical
```

Index dùng Gemini embedding thật khi có key, sau đó `upsert` vào Chroma persistent. Chạy lại cùng cấu hình không làm tăng số record.

### Reset đúng collection đích

Chỉ xóa collection của strategy, model và dimension hiện tại sau khi toàn bộ embedding mới đã validate thành công:

```powershell
& $PY .\rag_foundation\buoi_07\rag.py index --strategy hierarchical --reset
```

```bash
"$PY" ./rag_foundation/buoi_07/rag.py index --strategy hierarchical --reset
```

### Query CLI

```powershell
& $PY .\rag_foundation\buoi_07\rag.py query --strategy hierarchical --top-k 5 --question "Cơ cấu lại thời hạn trả nợ được quy định như thế nào?"
```

```bash
"$PY" ./rag_foundation/buoi_07/rag.py query --strategy hierarchical --top-k 5 --question "Cơ cấu lại thời hạn trả nợ được quy định như thế nào?"
```

CLI hiển thị status, answer, collection và evidence gồm source, trang, chunk ID, distance và preview; không in raw prompt hoặc API key.

### Test

```powershell
& $PY -m unittest discover -s .\rag_foundation\buoi_07\tests -v
```

```bash
"$PY" -m unittest discover -s ./rag_foundation/buoi_07/tests -v
```

### Streamlit

```powershell
& $PY -m streamlit run .\rag_foundation\buoi_07\app.py
```

```bash
"$PY" -m streamlit run ./rag_foundation/buoi_07/app.py
```

Dừng server bằng `Ctrl+C`. Chỉ giữ một tiến trình Streamlit; nếu có tiến trình cũ, chuyển tới terminal của tiến trình đó và nhấn `Ctrl+C` trước khi chạy lại.

## 9. Khái niệm chính

- **Strategy:** cách chunk dữ liệu, gồm `hierarchical`, `semantic`, `fixed-size`; mỗi strategy có collection riêng.
- **Embedding model:** model Gemini biến text thành vector. Document và query dùng cùng model.
- **Embedding dimension:** số phần tử trong mỗi vector; phải giống nhau khi index và query.
- **Collection identity:** tên gồm strategy, dimension và hash ổn định của model, ví dụ `nhnn-hierarchical-768-...`.
- **Top-k:** số kết quả retrieval tối đa; query thực tế dùng `min(top_k, collection.count())`.
- **Cosine distance:** khoảng cách dùng để sắp xếp độ liên quan; thường càng thấp càng liên quan.
- **`RAG_MAX_DISTANCE`:** ngưỡng demo để đánh dấu evidence được chấp nhận.
- **Confidence gate:** chỉ evidence có `distance <= RAG_MAX_DISTANCE` mới được đưa vào prompt generation. Evidence bị loại vẫn được trả về để kiểm tra.
- **`retrieval_only`:** đã lấy được evidence đạt gate nhưng generation lỗi hoặc trả text rỗng.
- **Citation:** label như `[E1]` trong answer được map bằng code sang source, trang và chunk ID từ metadata Chroma thật; model không tự quyết định metadata citation.

## 10. Manual acceptance plan

Chạy trên dữ liệu thật **sau khi index thành công**. Không khẳng định A hoặc B chắc chắn có answer; kết quả phải dựa trên evidence thật và threshold hiện tại.

### A. Có khả năng thuộc tài liệu

```text
Cơ cấu lại thời hạn trả nợ được quy định như thế nào?
```

### B. Có khả năng thuộc tài liệu

```text
Việc phân loại nợ và trích lập dự phòng được thực hiện như thế nào?
```

### C. Ngoài phạm vi

```text
Ngân hàng nào có lãi suất tiết kiệm cao nhất hôm nay?
```

Kỳ vọng cho C là evidence không đạt gate, không gọi generation, trả:

```text
Không tìm thấy đủ thông tin liên quan trong tài liệu đã cung cấp.
```

Nếu C vẫn đạt threshold, đó là false positive của retrieval/gate và phải ghi nhận, không sửa answer thủ công để che kết quả. Đây là kỳ vọng, không phải kết quả bảo đảm trước khi hiệu chỉnh threshold.

## 11. Troubleshooting

- **Thiếu package:** chạy lại lệnh `pip install -r ...` bằng đúng interpreter Buổi 05.
- **Sai interpreter:** kiểm tra `& $PY --version` hoặc `"$PY" --version`; phải là Python 3.11+ trong `.venv` Buổi 05.
- **Thiếu API key:** điền `GEMINI_API_KEY` trong `.env` local. Không tạo key giả và không dùng vector giả.
- **Collection rỗng/chưa tồn tại:** chạy `validate`, sau đó `index` đúng strategy trước khi `query`.
- **Model/dimension mismatch:** giữ nguyên model và dimension đã index hoặc chạy `index --reset` với cấu hình đúng; code sẽ chặn mismatch thay vì tự ghi đè.
- **JSON lỗi:** chạy `validate`; kiểm tra file JSON trong `buoi_05/output/chunks/`, không sửa dữ liệu nguồn tự động.
- **Embedding lỗi hoặc rate limit:** kiểm tra key, model, quota và kết nối; chạy lại sau khi lỗi được xử lý. Index dừng trước `upsert` một phần.
- **Streamlit đang chạy:** nhấn `Ctrl+C` trong terminal của tiến trình cũ rồi khởi chạy lại một tiến trình duy nhất.

## 12. Giới hạn và cảnh báo

- Đây là demo học tập, chưa có reranker, hybrid search, OCR, RBAC hoặc deployment.
- Retrieval có thể bỏ sót thông tin hoặc trả false positive.
- `RAG_MAX_DISTANCE` cần hiệu chỉnh trên dữ liệu và câu hỏi thực tế; distance không phải xác suất.
- Câu trả lời không phải tư vấn pháp lý và không thay thế việc kiểm tra văn bản gốc.
- Khi embedding hoặc generation thật, nội dung chunk có thể được gửi tới Gemini. Chỉ dùng dữ liệu mà người vận hành được phép gửi tới dịch vụ bên ngoài.
- Không coi answer của model là bằng chứng; hãy kiểm tra evidence, source, trang và chunk ID.

## 13. Checklist cuối

- [ ] Dùng đúng `.venv` Buổi 05.
- [ ] Validate dữ liệu trước khi index.
- [ ] Chỉ index một strategy trong collection tương ứng.
- [ ] Không dùng vector giả.
- [ ] Status không tạo collection.
- [ ] Index lặp không tăng record count.
- [ ] Query trả evidence có source, trang, distance và chunk ID.
- [ ] Evidence yếu không gọi generation.
- [ ] Citation lấy từ metadata thật.
- [ ] Test offline chạy thành công.
- [ ] Không commit `.env` hoặc lộ API key.
- [ ] Kết quả không phải tư vấn pháp lý.
