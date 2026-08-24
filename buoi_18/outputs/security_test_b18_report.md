# Security & Guardrail Test Report

## Test Results

- RBAC Test: PASS - Staff bị từ chối dữ liệu restricted; Risk_Manager nhận đúng dữ liệu được cấp quyền.
- Citation Integrity: PASS - Tất cả conflict/checklist item đều có citation hợp lệ và tồn tại trong dataset.
- Hallucination Check: PASS - Mọi citation và các câu hỏi gốc đều bắt nguồn từ dataset thực.
- Human Review Guardrail: PASS - Mọi output đều có review_status = NEEDS_HUMAN_REVIEW.
- Audit Log Privacy: PASS - Không lưu secret/API key; keyword nhạy cảm phát hiện: không có.
- Unknown Domain Test: PASS - Hệ thống cảnh báo rõ ràng khi domain không có dữ liệu, không tự bịa.
- File Export Verification: PASS - CSV export đúng schema và file tồn tại.

SECURITY & GUARDRAIL TESTS: PASS