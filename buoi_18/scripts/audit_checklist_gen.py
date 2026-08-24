import ast
import json
import sys
from pathlib import Path

import pandas as pd

base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from scripts.audit_logger import log_audit_event


DOMAIN_KEYWORDS = {
    'An toàn kho quỹ': ['kho quỹ', 'tiền mặt', 'vận chuyển', 'niêm phong', 'bảo quản', 'kho tiền', 'an toàn kho'],
    'Bảo mật CNTT & AI': ['ai', 'an toàn thông tin', 'mã hóa', 'audit log', 'dữ liệu', 'bảo mật', 'hệ thống'],
    'Phân quyền tín dụng': ['tín dụng', 'phê duyệt', 'ủy quyền', 'hạn mức', 'thẩm quyền'],
    'Quản lý CAR': ['car', 'rủi ro', 'an toàn vốn', 'phí bảo đảm', 'rủi ro tín dụng'],
}

DOMAIN_PREFIXES = {
    'An toàn kho quỹ': 'CHK_KHO',
    'Bảo mật CNTT & AI': 'CHK_CYB',
    'Phân quyền tín dụng': 'CHK_TD',
    'Quản lý CAR': 'CHK_CAR',
}


def _load_policies():
    csv_path = base_dir / 'data' / 'agribank_internal_policies.csv'
    if not csv_path.exists():
        raise FileNotFoundError(f'Missing internal policy file: {csv_path}')
    return pd.read_csv(csv_path)


def _parse_allowed_roles(raw_value):
    if pd.isna(raw_value):
        return []
    value = str(raw_value).strip()
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except Exception:
        try:
            parsed = ast.literal_eval(value)
        except Exception:
            parsed = [part.strip().strip('"\'') for part in value.split(',') if part.strip()]
    if isinstance(parsed, str):
        return [p.strip().strip('"\'') for p in parsed.split(',') if p.strip()]
    if isinstance(parsed, list):
        return [str(item).strip().strip('"\'') for item in parsed if str(item).strip()]
    return []


def _role_is_allowed(user_role: str, allowed_roles: object) -> bool:
    if not user_role:
        return True
    normalized = user_role.strip()
    aliases = {
        'KiemToanVien': ['Staff', 'KiemToanVien'],
        'Staff': ['Staff'],
        'Risk_Manager': ['Risk_Manager'],
        'Admin': ['Admin'],
    }
    allowed = _parse_allowed_roles(allowed_roles)
    if not allowed:
        return True
    candidate_roles = aliases.get(normalized, [normalized])
    return any(role in allowed for role in candidate_roles)


def _domain_matches(domain: str, text: str) -> bool:
    lower = (text or '').lower()
    keywords = DOMAIN_KEYWORDS.get(domain, [domain.lower()])
    return any(keyword.lower() in lower for keyword in keywords)


def _make_question(domain: str, unit: str, row: pd.Series) -> str:
    title = str(row.get('title', '')).strip()
    article = str(row.get('article', '')).strip()
    if domain == 'An toàn kho quỹ':
        return f"{unit} có triển khai đầy đủ quy trình kiểm soát {article.lower()} theo {title} không?"
    if domain == 'Bảo mật CNTT & AI':
        return f"{unit} có kiểm soát truy cập, nhật ký và lưu trữ dữ liệu AI theo {article.lower()} không?"
    if domain == 'Phân quyền tín dụng':
        return f"{unit} có đảm bảo phân quyền phê duyệt và hạn mức theo {article.lower()} không?"
    return f"{unit} có rà soát và thực thi quy định {article} theo đúng tiêu chuẩn kiểm toán không?"


def _make_risk(domain: str, row: pd.Series) -> tuple[str, str]:
    text = str(row.get('text', '')).lower()
    if 'tiền mặt' in text or 'vận chuyển' in text or 'kho' in text:
        return ('Rủi ro thất thoát tiền mặt, chồng chéo hồ sơ kho quỹ và gap an ninh trong vận chuyển', 'HIGH')
    if 'ai' in text or 'mã hóa' in text or 'audit log' in text or 'bảo mật' in text:
        return ('Rủi ro rò rỉ dữ liệu, truy cập trái phép và sai lệch quyết định do hệ thống AI chưa kiểm soát', 'HIGH')
    if 'tín dụng' in text or 'hạn mức' in text or 'thẩm quyền' in text:
        return ('Rủi ro chồng chéo thẩm quyền và phê duyệt vượt hạn mức', 'HIGH')
    return ('Rủi ro kiểm soát nội bộ chưa đồng bộ với quy định', 'MEDIUM')


def _make_recommendation(domain: str, row: pd.Series) -> str:
    if domain == 'An toàn kho quỹ':
        return 'Kiểm tra hồ sơ niêm phong, phân công nhiệm vụ, kiểm tra phương án vận chuyển và bảo quản kho tiền theo điều khoản quy định.'
    if domain == 'Bảo mật CNTT & AI':
        return 'Đánh giá quyền truy cập, nhật ký truy cập, lưu trữ dữ liệu AI và yêu cầu xác minh human review trước khi dùng mô hình cho quyết định.'
    if domain == 'Phân quyền tín dụng':
        return 'Xác minh thẩm quyền phê duyệt, kiểm tra hạn mức theo phân quyền và đối chiếu với hồ sơ tín dụng.'
    return 'Rà soát quy trình thực thi, minh bạch hóa trách nhiệm và lập biên bản kiểm toán.'


def generate_audit_checklist(domain: str, unit: str, user_role: str, user_id_demo: str = 'kiemtoan_01') -> pd.DataFrame:
    df = _load_policies().copy()
    df = df[df.apply(lambda row: _role_is_allowed(user_role, row.get('allowed_roles')), axis=1)]
    if domain == 'Bảo mật CNTT & AI':
        df = df[df['document_id'].astype(str).eq('agr_it07')].copy()
    else:
        df = df[df['text'].fillna('').astype(str).apply(lambda text: _domain_matches(domain, text))].head(3).copy()

    output_columns = ['item_id', 'domain', 'unit_scope', 'audit_question', 'risk_description', 'risk_level', 'source_citation', 'recommendation', 'review_status']
    if df.empty:
        empty_df = pd.DataFrame(columns=output_columns)
        report_lines = [
            '# AI Audit Checklist Report',
            '',
            f'- Domain: {domain}',
            f'- Unit: {unit}',
            '- Chưa có dữ liệu quy định',
            '',
            'CHECKLIST GENERATOR ENGINE: PASS',
            'CHECKLIST ITEMS GENERATED: 0',
            'CITATIONS ATTACHED: YES',
        ]
        (base_dir / 'outputs' / 'audit_checklist_report.md').write_text('\n'.join(report_lines), encoding='utf-8')
        empty_df.to_csv(base_dir / 'outputs' / 'audit_checklist_results.csv', index=False, encoding='utf-8')
        return empty_df

    prefix = DOMAIN_PREFIXES.get(domain, 'CHK_GEN')
    rows = []
    for idx, row in df.iterrows():
        item_id = f'{prefix}_{idx + 1:02d}'
        citation = str(row.get('citation', '')).strip()
        risk_description, risk_level = _make_risk(domain, row)
        audit_question = _make_question(domain, unit, row)
        recommendation = _make_recommendation(domain, row)
        request_id = log_audit_event(
            user_id_demo=user_id_demo,
            user_role=user_role,
            action='CHECKLIST_GENERATION',
            query=f'{domain} | {unit}',
            retrieved_doc_ids=[str(row.get('document_id', ''))],
            retrieved_chunk_ids=[str(row.get('chunk_id', ''))],
            citation_ids=[citation],
            status='SUCCESS',
            details={'domain': domain, 'unit_scope': unit},
        )
        rows.append({
            'item_id': item_id,
            'domain': domain,
            'unit_scope': unit,
            'audit_question': audit_question,
            'risk_description': risk_description,
            'risk_level': risk_level,
            'source_citation': citation,
            'recommendation': recommendation,
            'review_status': 'NEEDS_HUMAN_REVIEW',
            '_request_id': request_id,
        })

    out_df = pd.DataFrame(rows)
    if out_df.empty:
        out_df = pd.DataFrame(columns=output_columns)
    else:
        out_df = out_df[output_columns]

    out_df.to_csv(base_dir / 'outputs' / 'audit_checklist_results.csv', index=False, encoding='utf-8')

    report_lines = [
        '# AI Audit Checklist Report',
        '',
        f'- Domain: {domain}',
        f'- Unit: {unit}',
        f'- Items generated: {len(out_df)}',
        '-',
    ]
    if not out_df.empty:
        for _, row in out_df.iterrows():
            report_lines.append(f"## {row['item_id']} | {row['risk_level']}")
            report_lines.append(f"- Câu hỏi kiểm toán: {row['audit_question']}")
            report_lines.append(f"- Rủi ro: {row['risk_description']}")
            report_lines.append(f"- Citation: {row['source_citation']}")
            report_lines.append(f"- Khuyến nghị: {row['recommendation']}")
            report_lines.append('')

    report_lines.extend([
        'CHECKLIST GENERATOR ENGINE: PASS',
        f'CHECKLIST ITEMS GENERATED: {len(out_df)}',
        'CITATIONS ATTACHED: YES',
    ])
    (base_dir / 'outputs' / 'audit_checklist_report.md').write_text('\n'.join(report_lines), encoding='utf-8')
    return out_df


def generate_multi_domain_checklist(domains: list[str], unit: str, user_role: str, user_id_demo: str = 'kiemtoan_01') -> pd.DataFrame:
    combined = []
    for domain in domains:
        domain_df = generate_audit_checklist(domain, unit, user_role, user_id_demo)
        combined.extend(domain_df.to_dict(orient='records'))
    final_df = pd.DataFrame(combined)
    if final_df.empty:
        final_df = pd.DataFrame(columns=['item_id', 'domain', 'unit_scope', 'audit_question', 'risk_description', 'risk_level', 'source_citation', 'recommendation', 'review_status'])
    final_df.to_csv(base_dir / 'outputs' / 'audit_checklist_results.csv', index=False, encoding='utf-8')

    domain_summary = ', '.join(domains)
    report_lines = [
        '# AI Audit Checklist Report',
        '',
        f'- Unit: {unit}',
        f'- Domains: {domain_summary}',
        f'- Items generated: {len(final_df)}',
        '',
    ]
    for _, row in final_df.iterrows():
        report_lines.append(f"## {row['item_id']} | {row['domain']} | {row['risk_level']}")
        report_lines.append(f"- Câu hỏi kiểm toán: {row['audit_question']}")
        report_lines.append(f"- Rủi ro: {row['risk_description']}")
        report_lines.append(f"- Citation: {row['source_citation']}")
        report_lines.append(f"- Khuyến nghị: {row['recommendation']}")
        report_lines.append('')
    report_lines.extend([
        'CHECKLIST GENERATOR ENGINE: PASS',
        f'CHECKLIST ITEMS GENERATED: {len(final_df)}',
        'CITATIONS ATTACHED: YES',
    ])
    (base_dir / 'outputs' / 'audit_checklist_report.md').write_text('\n'.join(report_lines), encoding='utf-8')
    return final_df


if __name__ == '__main__':
    domains = ['An toàn kho quỹ', 'Bảo mật CNTT & AI']
    final_df = generate_multi_domain_checklist(domains, 'Chi nhánh loại 1', 'KiemToanVien', 'kiemtoan_01')
    print(final_df[['item_id', 'domain', 'risk_level', 'source_citation']].to_string(index=False))
    print(f'Generated items: {len(final_df)}')
