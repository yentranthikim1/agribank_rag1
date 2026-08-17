# SPEC - Buổi 5: OCR và so sánh chiến lược chunking cho PDF tiếng Việt

## 1. Mục tiêu

Mục tiêu của Buổi 5 là xây dựng một demo đơn giản, dễ hiểu, tập trung vào quy trình OCR và đánh giá cách chia văn bản (chunking) cho tài liệu PDF tiếng Việt. Demo này không phát triển full RAG production, không tạo embedding, không lưu vector database, và không gọi LLM.

Nội dung chính:
- Đọc đầu vào từ thư mục datademo/
- OCR các PDF tiếng Việt theo hướng xử lý đơn giản
- Chuẩn hóa text sang Unicode NFC
- Trích xuất metadata tối thiểu: source, page, ocr_used, language
- So sánh 3 chiến lược chunking:
  1. Fixed-size
  2. Semantic
  3. Hierarchical
- Xuất báo cáo so sánh theo từng chiến lược
- Dùng key từ .env trong folder src, nhưng không được phép đọc giá trị thực của key trong mã hay trong output

## 2. Vị trí làm việc

Đảm bảo làm việc chỉ trong thư mục:

- RAG/
  - rag_foundation/
    - buoi_05/
      - datademo/
      - src/
      - storage/
      - tests/

Không được viết code hoặc tài liệu ngoài nhánh Buổi 5 này.

## 3. Đầu vào

### 3.1 Nguồn PDF

Đầu vào là các file PDF tiếng Việt nằm trong:

- RAG/rag_foundation/buoi_05/datademo/

Yêu cầu:
- Chỉ dùng PDF có sẵn trong datademo/
- Không tạo dữ liệu thật mới
- Không sửa PDF gốc
- Không ghi đè file hiện có
- Nếu file đã tồn tại, phải kiểm tra trước và dùng lại nếu cần

### 3.2 Dữ liệu công khai / mô phỏng

PDF đầu vào phải là dữ liệu công khai hoặc dữ liệu mô phỏng đủ dùng cho demo học tập, không có dữ liệu nhạy cảm và không dùng tài liệu nội bộ.

## 4. Đầu ra cần có

Demo phải xuất ra các dữ liệu sau:

1. Text OCR đã chuẩn hóa Unicode NFC
2. Metadata cho mỗi tài liệu / mỗi trang:
   - source
   - page
   - ocr_used
   - language
3. Báo cáo so sánh ba chiến lược chunking

### 4.1 Định dạng text OCR

- Text được OCR phải là dạng Unicode chuẩn NFC
- Không dùng các ký tự không hợp lệ hoặc văn bản lạ ngoài nội dung PDF gốc
- Không biến đổi ngữ nghĩa của văn bản mục tiêu

### 4.2 Metadata bắt buộc

Mỗi bản ghi phải chứa ít nhất:

```json
{
  "source": "path/to/file.pdf",
  "page": 1,
  "ocr_used": "pymupdf|llama_cloud|mock_ocr",
  "language": "vi"
}
```

Yêu cầu:
- source: đường dẫn tệp PDF đầu vào
- page: số trang
- ocr_used: tên công cụ OCR được sử dụng trong demo
- language: ngôn ngữ đầu vào, ví dụ "vi"

## 5. Ba chiến lược chunking cần so sánh

Phải có báo cáo rõ ràng cho ba cách sau:

### 5.1 Fixed-size

Đặc điểm:
- Cắt theo số ký tự hoặc token cố định
- Có overlap giữa các chunk
- Mục tiêu: đánh giá cách cắt đơn giản, dễ implement nhưng có thể cắt ngang câu / đoạn

Yêu cầu so sánh:
- chunk_size
- overlap
- số lượng chunk được sinh ra
- độ dài trung bình
- ưu điểm / nhược điểm

### 5.2 Semantic

Đặc điểm:
- Ưu tiên ranh giới đoạn văn
- Chia dựa trên ngắt đoạn, kết đoạn, cách dòng, hoặc các dấu ngắt ngữ nghĩa
- Mục tiêu: giữ ý nghĩa của đoạn văn hơn là cắt theo độ dài cố định

Yêu cầu so sánh:
- số lượng chunk
- số đoạn / số cú pháp ngắt được giữ nguyên
- độ dài các chunk
- ưu điểm / nhược điểm

### 5.3 Hierarchical

Đặc điểm:
- Chia theo cấu trúc tài liệu:
  - Chương → Mục → Điều / Khoản → Điểm
- Mỗi mốc cấu trúc sẽ thành điểm bắt đầu của một chunk
- Mục tiêu: giữ cấu trúc logic tài liệu pháp lý / hành chính / học thuật

Yêu cầu so sánh:
- số chunk theo cấp độ cấu trúc
- mức độ giữ nguyên phân cấp
- ưu điểm / nhược điểm

## 6. Quy định về key trong .env

### 6.1 Vị trí key

- File key phải nằm trong folder:
  - RAG/rag_foundation/buoi_05/src/.env

Key cần khai báo theo tên:

```env
LLAMA_CLOUD_API_KEY='KEY CỦA BẠN'
```

### 6.2 Quy tắc bảo mật và không đọc giá trị

Yêu cầu bắt buộc:
- Không được phép đọc giá trị thực của key trong mã Python
- Không được phép in key ra console/log/output
- Không được phép lưu key vào báo cáo, file output, hoặc terminal log
- Không được phép đưa key vào commit/ghi chú/README demo
- Chỉ được phép sử dụng key như biến môi trường, nhưng không được truy xuất giá trị để hiển thị

Nói cách khác: mã chỉ có thể kiểm tra biến tồn tại bằng cách đọc tên biến, nhưng tuyệt đối không được đọc hoặc in giá trị thực. Nếu cần, hãy đặt placeholder hoặc xác nhận "key exists without revealing secret".

## 7. Ràng buộc kỹ thuật của Buổi 5

### 7.1 Không tạo embedding

Buổi 5 không được tạo embedding và không được lưu vector database.

### 7.2 Không lưu vector database

- Không khởi tạo FAISS, Chroma, Pinecone, Weaviate, hoặc hệ thống vector nào
- Không lưu chunk vào database dạng vector
- Không chạy query similarity trong demo này

### 7.3 Không gọi LLM

- Không gọi mô hình ngôn ngữ lớn nào trong Buổi 5
- Không dùng LLM để tóm tắt, tạo chunk, hoặc đánh giá văn bản
- Mọi xử lý phải là logic local, dễ hiểu, demo học tập

### 7.4 Mức độ demo đơn giản

- Code không phức tạp hóa
- Không cần thiết kế architecture production
- Tập trung vào việc minh họa quy trình OCR + so sánh chunking
- Tạo function rõ ràng, dễ đọc cho người mới học

## 8. Yêu cầu về OCR và chuẩn hóa

Mỗi bước xử lý phải rõ ràng:

1. Đọc file PDF từ datademo/
2. Trích xuất text từ PDF
3. Chuẩn hóa Unicode NFC
4. Gắn metadata theo trang
5. Tạo báo cáo chunking cho ba chiến lược
6. Xuất kết quả ra file JSON/CSV/text tùy demo đơn giản

### 8.1 Unicode NFC

- Dùng chuẩn Unicode NFC để đảm bảo text ổn định trước khi xử lý
- Tất cả output text phải có dạng chuẩn NFC

### 8.2 Metadata và báo cáo

Báo cáo cuối cùng phải nhấn mạnh:
- source
- page
- ocr_used
- language
- chunk_count
- chunk_strategy
- chunk_preview (nếu cần)

## 9. Kết quả mong đợi

Demo phải đủ để người mới học hiểu được:
- PDF tiếng Việt đầu vào thường là văn bản có cấu trúc
- OCR + chuẩn hóa text là bước cần làm trước khi xử lý
- Chunking ảnh hưởng lớn đến hiệu quả xử lý văn bản
- Fixed-size đơn giản nhưng dễ cắt sai ngữ nghĩa
- Semantic giữ ý nghĩa đoạn văn tốt hơn
- Hierarchical phù hợp với văn bản pháp lý / cấu trúc có cấp bậc

## 10. Quy định kiểm tra cuối cùng

Trước khi hoàn thành, phải đảm bảo:
- file PDF gốc không bị sửa
- không tạo embedding
- không lưu vector database
- không gọi LLM
- code hoạt động ở mức demo đơn giản
- key trong .env ở src được giữ nguyên và không bị in ra output
- các output chứa text OCR/metadata/chunk report có chuẩn Unicode NFC
- báo cáo so sánh 3 chiến lược chunking đã được nêu rõ và đầy đủ

## 11. Tóm tắt yêu cầu bắt buộc

Buổi 5 phải tuân thủ đầy đủ các yêu cầu sau:

- Đầu vào: PDF tiếng Việt trong datademo/
- Đầu ra: text OCR chuẩn Unicode NFC + metadata + báo cáo 3 chiến lược chunking
- So sánh 3 cách: Fixed-size, Semantic, Hierarchical
- Key .env đặt trong src nhưng không được phép đọc giá trị key
- Không tạo embedding
- Không lưu vector database
- Không gọi LLM
- Demo đơn giản, không phức tạp hóa
- Không dùng dữ liệu nội bộ, nhạy cảm hoặc không công khai
