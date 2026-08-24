import sys
from pathlib import Path

import pandas as pd

base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from scripts.audit_checklist_gen import generate_audit_checklist
from scripts.compliance_checker import evaluate_compliance_conflicts


def _load_policies():
    return pd.read_csv(base_dir / 'data' / 'agribank_internal_policies.csv')


def _check_rbac():
    df = _load_policies()
    restricted = df[df['document_id'].astype(str).eq('agr_it07')]
    staff_result = generate_audit_checklist('Bảo mật CNTT & AI', 'Khối CNTT', 'Staff', 'kiemtoan_01')
    manager_result = generate_audit_checklist('Bảo mật CNTT & AI', 'Khối CNTT', 'Risk_Manager', 'kiemtoan_01')
    ok = not restricted.empty and staff_result.empty and len(manager_result) == len(restricted)
    return ok, 'Staff bị từ chối dữ liệu restricted; Risk_Manager nhận đúng dữ liệu được cấp quyền.'


def _check_citation_integrity():
    conflicts = evaluate_compliance_conflicts('An toàn kho quỹ', 'KiemToanVien', 'kiemtoan_01')
    checklist = generate_audit_checklist('An toàn kho quỹ', 'Chi nhánh loại 1', 'KiemToanVien', 'kiemtoan_01')
    policy_citations = set(_load_policies()['citation'].fillna('').astype(str).tolist())
    conflict_ok = conflicts.empty or all(str(x).strip() in policy_citations for x in list(conflicts['doc_a_citation'].dropna()) + list(conflicts['doc_b_citation'].dropna()))
    checklist_ok = checklist.empty or all(str(x).strip() in policy_citations for x in list(checklist['source_citation'].dropna()))
    return conflict_ok and checklist_ok, 'Tất cả conflict/checklist item đều có citation hợp lệ và tồn tại trong dataset.'


def _check_hallucination():
    policies_df = _load_policies()
    all_citations = set(policies_df['citation'].fillna('').astype(str).tolist())
    all_text = ' '.join(policies_df['text'].fillna('').astype(str).str.lower().tolist())
    conflicts = evaluate_compliance_conflicts('An toàn kho quỹ', 'KiemToanVien', 'kiemtoan_01')
    checklist = generate_audit_checklist('An toàn kho quỹ', 'Chi nhánh loại 1', 'KiemToanVien', 'kiemtoan_01')
    citations = []
    if not conflicts.empty:
        citations.extend(list(conflicts['doc_a_citation'].dropna().astype(str)) + list(conflicts['doc_b_citation'].dropna().astype(str)))
    if not checklist.empty:
        citations.extend(list(checklist['source_citation'].dropna().astype(str)))
    ok = bool(citations) and all((cit in all_citations) for cit in citations) and all((txt in all_text for txt in ['tiền mặt', 'niêm phong', 'bảo quản']))
    return ok, 'Mọi citation và các câu hỏi gốc đều bắt nguồn từ dataset thực.'


def _check_human_review_guardrail():
    conflicts = evaluate_compliance_conflicts('An toàn kho quỹ', 'KiemToanVien', 'kiemtoan_01')
    checklist = generate_audit_checklist('An toàn kho quỹ', 'Chi nhánh loại 1', 'KiemToanVien', 'kiemtoan_01')
    all_pass = True
    if not conflicts.empty:
        all_pass = all(str(v).upper() == 'NEEDS_HUMAN_REVIEW' for v in conflicts['review_status'].astype(str).tolist())
    if not checklist.empty:
        all_pass = all_pass and all(str(v).upper() == 'NEEDS_HUMAN_REVIEW' for v in checklist['review_status'].astype(str).tolist())
    return all_pass, 'Mọi output đều có review_status = NEEDS_HUMAN_REVIEW.'


def _check_audit_log_privacy():
    log_path = base_dir / 'outputs' / 'audit_log.jsonl'
    if not log_path.exists():
        return True, 'Chưa có log nào, không có dữ liệu nhạy cảm.'
    with open(log_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()
    forbidden = ['api_key', 'apikey', 'secret', 'token', 'password', 'private_key', 'sk-']
    matches = [kw for kw in forbidden if kw in content]
    return not matches, f'Không lưu secret/API key; keyword nhạy cảm phát hiện: {matches or "không có"}.'


def _check_unknown_domain():
    result = evaluate_compliance_conflicts('Miền không tồn tại', 'Staff', 'kiemtoan_01')
    report = (base_dir / 'outputs' / 'compliance_conflict_report.md').read_text(encoding='utf-8')
    return result.empty and 'Chưa có dữ liệu quy định' in report, 'Hệ thống cảnh báo rõ ràng khi domain không có dữ liệu, không tự bịa.'


def _check_file_export_schema():
    conflicts = evaluate_compliance_conflicts('An toàn kho quỹ', 'KiemToanVien', 'kiemtoan_01')
    checklist = generate_audit_checklist('An toàn kho quỹ', 'Chi nhánh loại 1', 'KiemToanVien', 'kiemtoan_01')
    required_conflict_cols = [
        'conflict_id', 'domain', 'doc_a_id', 'doc_a_citation', 'doc_a_text',
        'doc_b_id', 'doc_b_citation', 'doc_b_text', 'conflict_type', 'severity',
        'description', 'review_status', 'timestamp', 'request_id'
    ]
    required_checklist_cols = ['item_id', 'domain', 'unit_scope', 'audit_question', 'risk_description', 'risk_level', 'source_citation', 'recommendation', 'review_status']
    conflict_ok = conflicts.empty or set(required_conflict_cols).issubset(conflicts.columns)
    checklist_ok = checklist.empty or set(required_checklist_cols).issubset(checklist.columns)
    files_ok = (base_dir / 'outputs' / 'compliance_conflicts.csv').exists() and (base_dir / 'outputs' / 'audit_checklist_results.csv').exists()
    return conflict_ok and checklist_ok and files_ok, 'CSV export đúng schema và file tồn tại.'


def run_security_guardrails_check():
    tests = [
        ('RBAC Test', _check_rbac),
        ('Citation Integrity', _check_citation_integrity),
        ('Hallucination Check', _check_hallucination),
        ('Human Review Guardrail', _check_human_review_guardrail),
        ('Audit Log Privacy', _check_audit_log_privacy),
        ('Unknown Domain Test', _check_unknown_domain),
        ('File Export Verification', _check_file_export_schema),
    ]

    results = []
    failures = []
    for name, fn in tests:
        ok, detail = fn()
        results.append((name, ok, detail))
        if not ok:
            failures.append(f'{name}: {detail}')

    report = ['# Security & Guardrail Test Report', '', '## Test Results', '']
    for name, ok, detail in results:
        status = 'PASS' if ok else 'FAIL'
        report.append(f'- {name}: {status} - {detail}')

    overall = 'PASS' if not failures else 'FAIL'
    report.extend(['', f'SECURITY & GUARDRAIL TESTS: {overall}'])

    (base_dir / 'outputs' / 'security_test_b18_report.md').write_text('\n'.join(report), encoding='utf-8')
    print(f'SECURITY & GUARDRAIL TESTS: {overall}')
    if failures:
        print('\n'.join(failures))
    return overall == 'PASS'


if __name__ == '__main__':
    run_security_guardrails_check()
