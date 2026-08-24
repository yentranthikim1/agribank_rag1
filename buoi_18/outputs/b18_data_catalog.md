# Data Cataloging Report - Buổi 18

## 1) Tổng quan dữ liệu

- File nội bộ chính: `data/agribank_internal_policies.csv`
- File dữ liệu chuẩn hóa: `data/chunks_combined_secure.csv`
- Số dòng nội bộ: 24
- Số tài liệu nội bộ duy nhất: 10
- Số dòng dữ liệu chuẩn hóa: 811
- Số tài liệu duy nhất trong dữ liệu chuẩn hóa: 25
- Tất cả 14 trường metadata đều có đủ dữ liệu: không có missing value.

## 2) Kiểm tra cấu trúc metadata 14 cột

Các cột hiện có trong file nội bộ:

1. `chunk_id`
2. `document_id`
3. `text`
4. `source_file`
5. `title`
6. `so_ky_hieu`
7. `loai_van_ban`
8. `co_quan_ban_hanh`
9. `ngay_ban_hanh`
10. `chapter`
11. `section`
12. `article`
13. `citation`
14. `allowed_roles`

Kết quả kiểm tra:
- `title`: NA = 0
- `so_ky_hieu`: NA = 0
- `loai_van_ban`: NA = 0
- `co_quan_ban_hanh`: NA = 0
- `ngay_ban_hanh`: NA = 0
- `chapter`: NA = 0
- `section`: NA = 0
- `article`: NA = 0
- `citation`: NA = 0
- `allowed_roles`: NA = 0

=> Metadata đầy đủ để phục vụ UC3 & UC4.

## 3) Danh sách văn bản nội bộ Agribank

### 3.1 Document: agr_at01
- Title: Quy định nội bộ số 100/QĐ-NHNO-AT về Giao nhận, bảo quản, vận chuyển tiền mặt và tài sản quý Agribank
- Số ký hiệu: 100/QĐ-NHNO-AT
- Loại văn bản: Quy định nội bộ
- Cơ quan ban hành: Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank)
- Ngày ban hành: 15/03/2024
- Scope: Giao nhận, bảo quản, vận chuyển tiền mặt và tài sản quý; kho tiền; niêm phong; an toàn vận chuyển
- Article sample: Điều 1. Phạm vi và đối tượng tuân thủ; Điều 12. Xe bọc thép và phương án bảo vệ; Điều 25. Kiểm đếm và niêm phong tiền nghi giả; Điều 30. Trách nhiệm của Ban Quản lý kho tiền

### 3.2 Document: agr_car02
- Title: Quy định nội bộ số 250/QĐ-NHNO-QLRR về Quản lý tỷ lệ an toàn vốn và định mức rủi ro Agribank
- Số ký hiệu: 250/QĐ-NHNO-QLRR
- Loại văn bản: Quy định nội bộ
- Cơ quan ban hành: Agribank
- Ngày ban hành: 20/06/2024
- Scope: CAR, tỷ lệ an toàn vốn, định mức rủi ro, trích nộp quỹ đảm bảo an toàn

### 3.3 Document: agr_td03
- Title: Quy chế tín dụng nội bộ số 315/QC-NHNO-TD về Phán quyết và Phân cấp ủy quyền cho vay tại Agribank
- Số ký hiệu: 315/QC-NHNO-TD
- Loại văn bản: Quy chế nội bộ
- Cơ quan ban hành: Agribank
- Ngày ban hành: 10/01/2024
- Scope: Hạn mức phê duyệt tín dụng, phân cấp ủy quyền, cho vay nông nghiệp, giám sát nợ vay

### 3.4 Document: agr_fx04
- Title: Quy định nội bộ số 410/QĐ-NHNO-TTNH về Quản lý trạng thái ngoại tệ và giao dịch ngoại hối Agribank
- Số ký hiệu: 410/QĐ-NHNO-TTNH
- Loại văn bản: Quy định nội bộ
- Cơ quan ban hành: Agribank
- Ngày ban hành: 05/09/2024
- Scope: Ngoại tệ, giao dịch ngoại hối, hạn mức trạng thái ngoại tệ

### 3.5 Document: agr_gp05
- Title: Quy chế số 520/QC-NHNO-MANGLUOI về Mở rộng mạng lưới chi nhánh và phòng giao dịch Agribank
- Số ký hiệu: 520/QC-NHNO-MANGLUOI
- Loại văn bản: Quy chế nội bộ
- Cơ quan ban hành: Agribank
- Ngày ban hành: 18/11/2024
- Scope: Mở rộng mạng lưới, thành lập điểm giao dịch, trình tự phê duyệt

### 3.6 Document: agr_bh06
- Title: Quy định nội bộ số 180/QĐ-NHNO-BH về Mua bảo hiểm rủi ro nghiệp vụ và tài sản Agribank
- Số ký hiệu: 180/QĐ-NHNO-BH
- Loại văn bản: Quy định nội bộ
- Cơ quan ban hành: Agribank
- Ngày ban hành: 14/02/2024
- Scope: Bảo hiểm tiền mặt, kho tiền, đại lý bảo hiểm, đạo đức bán bảo hiểm

### 3.7 Document: agr_it07
- Title: Quy chế bảo mật CNTT số 600/QC-NHNO-CNTT về An toàn thông tin và Quản trị dữ liệu AI Agribank
- Số ký hiệu: 600/QC-NHNO-CNTT
- Loại văn bản: Quy chế nội bộ
- Cơ quan ban hành: Agribank
- Ngày ban hành: 01/03/2025
- Scope: Bảo mật dữ liệu, phân quyền, nhật ký truy cập, AI governance

### 3.8 Document: agr_hr08
- Title: Quy định nội bộ số 88/QĐ-NHNO-NS về Quy hoạch, bổ nhiệm và quản lý nhân sự Agribank
- Số ký hiệu: 88/QĐ-NHNO-NS
- Loại văn bản: Quy định nội bộ
- Cơ quan ban hành: Agribank
- Ngày ban hành: 10/01/2025
- Scope: Bổ nhiệm cán bộ quản lý, đào tạo, nguồn nhân lực

### 3.9 Document: agr_tc09
- Title: Quy chế tài chính số 720/QC-NHNO-TC về Chế độ chi tiêu và mua sắm tài sản nội bộ Agribank
- Số ký hiệu: 720/QC-NHNO-TC
- Loại văn bản: Quy chế nội bộ
- Cơ quan ban hành: Agribank
- Ngày ban hành: 05/12/2024
- Scope: Chi tiêu, mua sắm tài sản, hạch toán dự phòng

### 3.10 Document: agr_xln10
- Title: Quy định nội bộ số 390/QĐ-NHNO-XLN về Phân loại nợ và Xử lý nợ xấu tại Agribank
- Số ký hiệu: 390/QĐ-NHNO-XLN
- Loại văn bản: Quy định nội bộ
- Cơ quan ban hành: Agribank
- Ngày ban hành: 22/07/2024
- Scope: Phân loại nợ, trích lập dự phòng, xử lý nợ xấu

## 4) Phân loại theo Domain / Nhiệm vụ

Các domain gợi ý từ dữ liệu thực tế:

- An toàn kho quỹ
- CAR & Quản lý rủi ro
- Tín dụng
- Ngoại tệ
- Bảo mật CNTT & AI
- Thẩm quyền phê duyệt
- Mua sắm nội bộ

Dựa trên keyword và nội dung văn bản, các tài liệu chủ yếu thuộc các domain sau:
- An toàn kho quỹ: agr_at01
- CAR & Quản lý rủi ro: agr_car02
- Tín dụng: agr_td03
- Ngoại tệ: agr_fx04
- Thẩm quyền phê duyệt / mạng lưới: agr_gp05
- Bảo hiểm / rủi ro nghiệp vụ: agr_bh06
- Bảo mật CNTT & AI: agr_it07
- Nhân sự / thẩm quyền bổ nhiệm: agr_hr08
- Mua sắm nội bộ / ngân sách: agr_tc09
- Xử lý nợ / rủi ro tín dụng: agr_xln10

## 5) Đánh giá tổng kết

- Dữ liệu nội bộ có đủ thông tin để phục vụ cataloging.
- Tất cả 14 trường metadata đều đầy đủ.
- Số lượng tài liệu nội bộ và chunk dữ liệu đủ lớn để phục vụ UC3 và UC4.

DATA CATALOGING: PASS
DOMAINS DETECTED: 7
READY FOR UC3 & UC4: YES
