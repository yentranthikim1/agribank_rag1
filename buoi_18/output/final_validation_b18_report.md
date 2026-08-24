# Báo cáo nghiệm thu cuối cùng - Buổi 18

- **Ngày kiểm tra:** 2026-08-24
- **Phạm vi:** `buoi_18/`
- **Kết luận:** Hệ thống đạt điều kiện demo nội bộ cho UC3 và UC4.

## 1. Source Data Integrity

**PASS**

- Nguồn chính: `data/agribank_internal_policies.csv`.
- Dataset được đọc bằng `pandas.read_csv`; không có thao tác ghi đè nguồn trong luồng UC3/UC4.
- Quy mô kiểm tra: 24 dòng, 10 `document_id` duy nhất.
- Metadata catalog ghi nhận đủ 14 trường và không có missing value.
- SHA-256 tại thời điểm nghiệm thu: `71AA62A59D1F8AF6D40145CB7B89823B351F269C9755689C35C6D55DD1086D98`.
- Các file kết quả được ghi riêng vào `outputs/`, không ghi vào thư mục `data/`.

## 2. UC3 - AI Compliance Checker

**PASS**

- Engine: `scripts/compliance_checker.py`.
- Thực hiện lọc domain từ nội dung nguồn, chọn các đoạn quy định và so sánh chéo theo cặp.
- Kết quả có `doc_a_id`, `doc_b_id`, nội dung hai phía, loại xung đột, mô tả, severity, citation, timestamp và request ID.
- Kết quả kiểm tra với role `KiemToanVien`:
  - `An toàn kho quỹ`: 3 conflict.
  - `CAR & Quản lý rủi ro`: 3 conflict.
  - `Tín dụng`: 3 conflict.
- Artifact: `outputs/compliance_conflicts.csv` và `outputs/compliance_conflict_report.md`.

## 3. UC4 - AI Audit Checklist Generator

**PASS**

- Engine: `scripts/audit_checklist_gen.py`.
- Lọc `allowed_roles` trước khi lọc domain và tạo context/checklist.
- Checklist chứa domain, unit scope, câu hỏi kiểm toán, rủi ro, risk level, citation, recommendation và review status.
- Kiểm tra thực tế sinh được checklist cho `An toàn kho quỹ` và `Chi nhánh loại 1`; các item được gắn citation từ dataset.
- Artifact: `outputs/audit_checklist_results.csv` và `outputs/audit_checklist_report.md`.

## 4. Citation & Linking

**PASS**

- Citation giữ đủ số ký hiệu văn bản, điều và mã chunk/document.
- Security suite đã kiểm tra toàn bộ citation của conflict và checklist đối chiếu với cột `citation` trong dataset.
- Kết quả: `Citation Integrity: PASS` và `Hallucination Check: PASS`.

## 5. RBAC & Governance

**PASS**

- Role được chuẩn hóa và kiểm tra bằng `allowed_roles` trước bước domain filtering và sinh output.
- Kiểm thử Staff xác nhận mọi citation trả về đều thuộc tập dữ liệu được phép cho Staff.
- Kết quả: `RBAC Test: PASS`.
- Lưu ý: quyền truy cập hiện là demo RBAC dựa trên CSV role; chưa thay thế IAM/SSO hoặc policy enforcement ở tầng hạ tầng.

## 6. Streamlit Web Interface

**PASS**

- Entry point: `app.py`, chạy bằng `streamlit run app.py`.
- Có tab riêng cho UC3, UC4 và Audit Log/System Trail.
- Có chọn user/role, hiển thị bảng và chi tiết, download CSV/JSON/Markdown, trạng thái human review và giao diện responsive theo layout wide.
- Health check thực tế: `http://localhost:8505/_stcore/health` trả HTTP `200`, body `ok`.

## 7. Audit Log

**PASS**

- Logger: `scripts/audit_logger.py`.
- Artifact thực tế: `outputs/audit_log.jsonl` theo định dạng append-only JSON Lines.
- Mỗi event có timestamp UTC, request ID, user ID, user role, action, query, retrieval method, document/chunk IDs, citation IDs, denied candidate count, status và details.
- Số dòng log tại thời điểm kiểm tra: 275.
- Kiểm thử privacy không phát hiện keyword secret/API key.
- Ghi chú: project hiện không dùng `audit_log.json` hoặc database; JSONL là audit store được triển khai.

## 8. Human Review Guardrail

**PASS**

- UC3 và UC4 đều gắn `review_status = NEEDS_HUMAN_REVIEW` cho output mới.
- Giao diện cho phép kiểm toán viên xem xét trạng thái trước khi sử dụng kết quả.
- Security suite xác nhận `Human Review Guardrail: PASS`.

## 9. Validation Commands & Evidence

- `python -m py_compile app.py scripts/*.py` theo danh sách file Python thực tế: **PASS**.
- `python scripts/security_tests_b18.py`: **PASS** toàn bộ 7 kiểm tra.
- Streamlit health endpoint trên port 8505: **HTTP 200 / ok**.
- Artifact security: `outputs/security_test_b18_report.md`.
- Artifact catalog: `outputs/b18_data_catalog.md`.

## Đánh giá tổng thể

- **UC3 COMPLIANCE CHECKER: PASS**
- **UC4 AUDIT CHECKLIST GEN: PASS**
- **CITATION INTEGRITY: PASS**
- **RBAC & GOVERNANCE: PASS**
- **STREAMLIT DEMO: PASS**
- **AUDIT TRAIL: PASS**
- **SYSTEM READY FOR DEMO: YES**

> Phạm vi kết luận là demo nội bộ dựa trên dataset CSV hiện có. Trước khi đưa vào production cần bổ sung IAM/SSO, phân quyền ở tầng storage, database/audit retention và kiểm thử UI tự động trên các viewport mục tiêu.
