import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

base_dir = Path(__file__).resolve().parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from scripts.audit_checklist_gen import generate_audit_checklist
from scripts.audit_logger import log_audit_event
from scripts.compliance_checker import evaluate_compliance_conflicts

st.set_page_config(page_title='Buổi 18 - AI Compliance & Audit', page_icon='🧾', layout='wide')
st.markdown(
    """
    <style>
        .main > div {
            padding-top: 1.2rem;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
        }
        .stApp {
            background: linear-gradient(180deg, #fff6f5 0%, #fff1f1 100%);
        }
        div[data-testid="stWarning"] {
            background: #fff0ef;
            border-left: 5px solid #a40000;
            color: #6b1111;
            font-weight: 700;
            border-radius: 12px;
            padding: 0.9rem 1rem;
            box-shadow: 0 5px 18px rgba(164, 0, 0, 0.08);
        }
        h1 {
            color: #a40000;
            font-weight: 800;
            letter-spacing: 0.02em;
        }
        h2, h3 {
            color: #7d0a0a;
        }
        .card {
            background: white;
            border: 1px solid #f2d3d3;
            border-radius: 16px;
            padding: 1rem 1.2rem;
            box-shadow: 0 6px 18px rgba(164, 0, 0, 0.08);
            margin-bottom: 1rem;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #7d0a0a 0%, #a40000 100%);
            color: white;
        }
        [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stTextInput label {
            color: white !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            background: #ffe5e5;
            color: #700d0d;
            border: none;
            border-radius: 10px;
            font-weight: 700;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: #ffd0d0;
        }
        .stDataFrame {
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid #f2d3d3;
        }
        .stTabs [role="tablist"] {
            gap: 0.5rem;
        }
        .stTabs [role="tab"] {
            border-radius: 10px 10px 0 0;
            padding: 0.7rem 1.1rem;
            background: #fff0f0;
            border: 1px solid #f2d3d3;
            color: #7d0a0a;
        }
        .stTabs [role="tab"][aria-selected="true"] {
            background: #a40000;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.warning('Demo sản phẩm AI Kiểm toán - Kết quả gợi ý cần kiểm toán viên xác minh trước khi ban hành.')
st.title('Hệ thống AI Kiểm toán nội bộ Agribank')
st.caption('AI Compliance Checker & Audit Checklist Generator | Buổi 18')

with st.sidebar:
    st.header('Thông tin người dùng & phân quyền')
    user_id = st.text_input('ID người dùng demo:', value='kiemtoan_01')
    role = st.selectbox('Vai trò người dùng:', ['Admin', 'Risk_Manager', 'KiemToanVien', 'Staff', 'Guest'])
    st.markdown('### Trạng thái nguồn dữ liệu')
    st.caption('Internal Policies: READY')
    st.caption('External Legal Docs: READY')

    if st.button('Reset Session / Clean Audit Log'):
        log_path = base_dir / 'outputs' / 'audit_log.jsonl'
        if log_path.exists():
            log_path.unlink()
        st.success('Audit log đã được xóa.')

    st.markdown('---')
    st.caption(f'Người dùng đang đăng nhập: {user_id}')
    st.caption(f'Vai trò hiện tại: {role}')



def _severity_color(severity: str) -> str:
    if severity == 'HIGH':
        return 'background: #fdd4d4; color: #7a0d0d; font-weight: 700;'
    if severity == 'MEDIUM':
        return 'background: #fff0bf; color: #7a5200; font-weight: 700;'
    return 'background: #d9f7d9; color: #0c5a2c; font-weight: 700;'



def _render_conflict_cards(df: pd.DataFrame):
    if df.empty:
        st.info('Không phát hiện xung đột quy định rõ ràng trong phạm vi dữ liệu hiện có.')
        return

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(
        df[['conflict_id', 'domain', 'conflict_type', 'severity', 'review_status']].style.apply(
            lambda x: [_severity_color(x['severity']) for _ in x], axis=1
        ),
        use_container_width=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    for _, row in df.iterrows():
        status_key = f"review_{row['conflict_id']}"
        if status_key not in st.session_state:
            st.session_state[status_key] = row.get('review_status', 'NEEDS_HUMAN_REVIEW')

        with st.expander(f"{row['conflict_id']} - {row['conflict_type']} ({row['severity']})", expanded=True):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown('### Văn bản A')
                st.caption(row['doc_a_citation'])
                st.write(row['doc_a_text'])
            with col_right:
                st.markdown('### Văn bản B')
                st.caption(row['doc_b_citation'])
                st.write(row['doc_b_text'])

            st.info(f"**Phân tích AI:** {row['description']}")

            st.markdown('#### Phê duyệt của Kiểm toán viên')
            review_value = st.selectbox(
                'Trạng thái xem xét',
                ['NEEDS_HUMAN_REVIEW', 'APPROVED', 'REJECTED'],
                index=['NEEDS_HUMAN_REVIEW', 'APPROVED', 'REJECTED'].index(st.session_state[status_key]),
                key=f"select_{row['conflict_id']}",
            )
            st.session_state[status_key] = review_value
            st.caption(f'Trạng thái hiện tại: {review_value}')
            st.markdown('</div>', unsafe_allow_html=True)



def _download_button(df: pd.DataFrame, label: str, mime: str, filename: str):
    return st.download_button(
        label=label,
        data=df.to_csv(index=False, encoding='utf-8') if mime == 'text/csv' else df.to_json(orient='records', force_ascii=False, indent=2).encode('utf-8'),
        file_name=filename,
        mime=mime,
    )



tab1, tab2, tab3 = st.tabs(['UC3 - AI Compliance Checker', 'UC4 - AI Audit Checklist Generator', 'Audit Log & System Trail'])

with tab1:
    st.subheader('Kiểm tra xung đột & mâu thuẫn quy định nội bộ')
    domain_options = ['An toàn kho quỹ & Vận chuyển tiền', 'Quản lý CAR', 'An toàn kho quỹ', 'CAR & Quản lý rủi ro', 'Tín dụng', 'Quét toàn bộ văn bản']
    domain = st.selectbox('Miền kiểm toán / quét toàn bộ', domain_options)

    if st.button('Kiểm tra tuân thủ & phát hiện mâu thuẫn'):
        with st.spinner('Đang so sánh chéo quy định nội bộ...'):
            if domain == 'Quét toàn bộ văn bản':
                domains = ['An toàn kho quỹ', 'CAR & Quản lý rủi ro', 'Tín dụng']
                frames = []
                for item in domains:
                    df_item = evaluate_compliance_conflicts(domain=item, user_role=role, user_id_demo=user_id)
                    if not df_item.empty:
                        frames.append(df_item)
                df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
            else:
                df = evaluate_compliance_conflicts(domain=domain, user_role=role, user_id_demo=user_id)

            _render_conflict_cards(df)

            if not df.empty:
                col_csv, col_md = st.columns(2)
                with col_csv:
                    _download_button(df, 'Tải CSV kết quả', 'text/csv', 'compliance_conflicts.csv')
                with col_md:
                    report_path = base_dir / 'outputs' / 'compliance_conflict_report.md'
                    md_content = report_path.read_text(encoding='utf-8') if report_path.exists() else '# Compliance Conflict Report\n\nNo report generated.'
                    st.download_button('Tải Markdown báo cáo', md_content, file_name='compliance_conflict_report.md', mime='text/markdown')

with tab2:
    st.subheader('Tạo bản nháp checklist kiểm toán nội bộ')
    domain2 = st.selectbox('Phạm vi kiểm toán', ['Bảo mật CNTT & AI', 'An toàn kho quỹ', 'Tín dụng', 'Quản lý CAR'])
    unit = st.selectbox('Đơn vị kiểm toán', ['Chi nhánh loại 1', 'Phòng giao dịch', 'Khối CNTT', 'Phòng Kế toán'])

    if st.button('Tạo bản nháp Checklist kiểm toán'):
        with st.spinner('Đang sinh danh mục mục kiểm toán...'):
            df = generate_audit_checklist(domain2, unit, role, user_id)
            st.dataframe(df[['item_id', 'audit_question', 'risk_level', 'source_citation']], use_container_width=True)

            for _, row in df.iterrows():
                with st.expander(f"{row['item_id']} | {row['risk_level']}"):
                    st.markdown(f"**Câu hỏi kiểm toán:** {row['audit_question']}")
                    st.markdown(f"**Rủi ro tiềm ẩn:** {row['risk_description']}")
                    st.markdown(f"**Khuyến nghị kiểm toán:** {row['recommendation']}")
                    st.caption(f"**Văn bản gốc / Citation:** {row['source_citation']}")

            col_csv, col_json = st.columns(2)
            with col_csv:
                _download_button(df, 'Tải Checklist CSV', 'text/csv', 'audit_checklist_results.csv')
            with col_json:
                _download_button(df, 'Tải Checklist JSON', 'application/json', 'audit_checklist_results.json')

with tab3:
    st.subheader('Nhật ký hệ thống & hành vi kiểm toán')
    log_path = base_dir / 'outputs' / 'audit_log.jsonl'
    rows = []
    if log_path.exists():
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))

    if rows:
        log_df = pd.DataFrame(rows)
        role_filter = st.selectbox('Lọc theo vai trò', ['All'] + sorted(log_df['user_role'].dropna().unique().tolist()))
        action_filter = st.selectbox('Lọc theo hành động', ['All'] + sorted(log_df['action'].dropna().unique().tolist()))

        filtered = log_df.copy()
        if role_filter != 'All':
            filtered = filtered[filtered['user_role'] == role_filter]
        if action_filter != 'All':
            filtered = filtered[filtered['action'] == action_filter]

        st.dataframe(
            filtered[['timestamp_utc', 'request_id', 'user_id_demo', 'user_role', 'action', 'status', 'query']].sort_values('timestamp_utc', ascending=False),
            use_container_width=True,
        )
    else:
        st.info('Chưa có log nào được ghi trong hệ thống.')
