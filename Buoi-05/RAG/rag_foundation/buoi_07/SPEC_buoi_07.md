# Agent Specification Buoi 07

## Workspace
- Vùng được đọc: `../buoi_05/output/chunks/`, `../buoi_05/.venv/`, `../buoi_06/`, và `./` khi file Buổi 07 đã tồn tại.
- Vùng được ghi: `./` trong `rag_foundation/buoi_07/`.
- Không sửa code, dữ liệu hoặc output của Buổi 05 và Buổi 06.

## Python
- Dùng interpreter của Buổi 05: `rag_foundation/buoi_05/.venv`.
- Không tạo venv mới cho Buổi 07.
- Tất cả script phải dùng `Path(__file__).resolve()` khi cần xây dựng đường dẫn.

## Input
- Dữ liệu đầu vào là JSON trong `rag_foundation/buoi_05/output/chunks/`.
- Buổi 05 là nguồn dữ liệu đã chuẩn bị sẵn.
- Không OCR, không parse PDF, không chunk lại dữ liệu mới.
- Chỉ đọc và validate các chunk đã có.

## Packages
- Chỉ dùng các package bắt buộc theo quy định: `streamlit`, `google-genai`, `chromadb`, `python-dotenv`.
- Không thêm gói trực tiếp khác nếu không cần thiết cho bài.

## Pipeline
1. Validate JSON từ Buổi 05.
2. Kiểm tra format và schema của chunk.
3. Tạo embedding với Gemini theo model cấu hình.
4. Lưu persistent ChromaDB theo strategy, model và dimension.
5. Query semantic retrieval theo top-k.
6. Kiểm tra confidence gate theo `RAG_MAX_DISTANCE`.
7. Chỉ gửi evidence đạt ngưỡng cho generation.
8. Gemini tổng hợp câu trả lời dựa trên evidence.
9. Gắn citation từ metadata thật của Chroma.
10. Hiển thị nguồn, trang và `chunk_id`.
11. Chạy `unittest` offline bằng mock/temporary storage.
12. Streamlit là giao diện cuối cùng nếu cần demo.

## Data Contract
Các field bắt buộc của mỗi chunk:
- `chunk_id`
- `strategy`
- `source`
- `page_start`
- `page_end`
- `text`

Mỗi chunk phải là JSON object hợp lệ, không rỗng, không có `bool` ở page, không có `text` trống.

## Index Contract
- Mỗi `strategy` phải có collection riêng.
- Collection identity phải dựa trên `strategy`, model embedding và dimension.
- Query và index phải dùng cùng model và dimension.
- Không dùng vector giả, default Chroma embeddings hoặc metadata do LLM tạo.
- Chặn `NaN`, `Infinity`, `bool`, và zero vector.
- Chroma dùng cosine distance, `embedding_function=None`.
- Index phải idempotent.
- `status()` phải read-only khi storage rỗng.
- Validate embedding phải thành công trước khi reset/upsert.

## Retrieval Contract
- Trả về evidence thật từ Chroma.
- Mỗi evidence phải có `distance`.
- Chỉ evidence dưới ngưỡng `RAG_MAX_DISTANCE` mới được đưa vào generation.
- Nếu không đủ evidence, không gọi generation.
- Kết quả trả về nên có `evidence`, `citations`, `warnings`.

## Citation Contract
- Citations phải lấy từ metadata thật trong Chroma.
- Không tin source/page/chunk_id do LLM tự tạo.
- `result["citations"]` phải chứa mapping hợp lệ.
- `result["warnings"]` phải ghi các citation không hợp lệ hoặc bị loại.
- Code cần thay label `[E1]`, `[E2]` bằng nhãn nguồn thật theo metadata.

## Security
- Không lộ secret hoặc API key trong output.
- Không tạo `.env` có key thật ở bước này.
- Chỉ dùng key từ file môi trường local khi thật sự cần.

## Testing
- Dùng `unittest`.
- Mock API/Gemini ở mức phù hợp.
- Dùng temporary storage cho Chroma.
- Không cần Internet và không dùng key thật trong test.

## Coding Style
- Giữ số file ít, chức năng tập trung.
- Ít class, ít function, ít layer phức tạp.
- Chỉ code cần thiết cho từng bước.
- Không viết kiến trúc quá mức khi mục tiêu mới chỉ là học.

---

Mục tiêu của Buổi 07 là xây dựng pipeline RAG đúng nguyên tắc: valid -> embed -> index -> retrieve -> gate -> generate -> cite -> demo.
