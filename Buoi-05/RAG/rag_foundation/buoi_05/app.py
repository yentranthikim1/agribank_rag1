from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_CANDIDATES = [
    ROOT_DIR / "output",
    ROOT_DIR / "storage" / "output",
]


@st.cache_data
def list_json_outputs() -> List[Path]:
    files: List[Path] = []
    seen: set[Path] = set()
    for folder in OUTPUT_CANDIDATES:
        if not folder.exists():
            continue
        for item in sorted(folder.glob("*_result.json")):
            if item not in seen:
                seen.add(item)
                files.append(item)
    return files


@st.cache_data
def load_output(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def doc_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    records = payload.get("records", [])
    strategies = payload.get("strategies", {})
    chunks = payload.get("chunks", [])
    return {
        "filename": Path(safe_text(payload.get("source", ""))).name,
        "pages": len(records),
        "warnings": payload.get("warnings", []),
        "strategies": strategies,
        "total_chunks": len(chunks),
    }


def build_strategy_table(payload: Dict[str, Any]) -> pd.DataFrame:
    strategies = payload.get("strategies", {})
    rows: List[Dict[str, Any]] = []
    for strategy, stats in strategies.items():
        rows.append(
            {
                "Chiến lược": strategy,
                "Số chunk": stats.get("count", 0),
                "Min length": stats.get("min", 0),
                "Max length": stats.get("max", 0),
                "Avg length": stats.get("avg", 0),
            }
        )
    return pd.DataFrame(rows)


def render_chunk_list(chunks: List[Dict[str, Any]], selected_strategy: str) -> None:
    if not chunks:
        st.info("Không có chunk nào cho chiến lược này.")
        return

    for idx, chunk in enumerate(chunks, start=1):
        with st.container():
            st.markdown(f"### Chunk {idx}")
            meta = chunk.get("metadata", {})
            st.caption(
                f"chunk_id: {chunk.get('chunk_id', '-')} | "
                f"page: {chunk.get('page_start', '')} | "
                f"length: {len(safe_text(chunk.get('text', '')))} | "
                f"strategy: {selected_strategy}"
            )
            if "heading_hint" in meta:
                st.write(f"**Heading hint:** {meta.get('heading_hint', '')}")
            text = safe_text(chunk.get("text", ""))
            st.code(text[:2000] + ("..." if len(text) > 2000 else ""), language="text")
            st.markdown("---")


def render_strategy_comparison(payload: Dict[str, Any]) -> None:
    strategy_table = build_strategy_table(payload)
    if strategy_table.empty:
        st.info("Chưa có dữ liệu so sánh chiến lược cho tài liệu này.")
        return

    st.subheader("📊 So sánh trực quan 3 chiến lược")
    chart_df = strategy_table[["Chiến lược", "Số chunk", "Avg length"]].copy()
    chart_df = chart_df.rename(columns={"Avg length": "Avg length (chars)"})

    st.bar_chart(chart_df.set_index("Chiến lược"), use_container_width=True)

    st.subheader("📋 Bảng so sánh chi tiết")
    st.dataframe(strategy_table, use_container_width=True)

    st.caption("So sánh nhanh: fixed-size dễ cắt ngang, semantic giữ đoạn nghĩa, hierarchical giữ cấu trúc văn bản.")


st.set_page_config(page_title="Buổi 5 - Chunk Viewer", page_icon="📄", layout="wide")
st.title("📄 Buổi 5 - Visualize Chunking cho PDF tiếng Việt")

outputs = list_json_outputs()
if not outputs:
    st.warning("Chưa có file JSON output nào được tìm thấy trong các thư mục output hoặc storage/output.")
    st.stop()

selected_path = st.sidebar.selectbox(
    "Chọn file JSON",
    options=outputs,
    format_func=lambda p: p.name,
)

payload = load_output(selected_path)
summary = doc_summary(payload)

st.sidebar.markdown("## Thông tin tài liệu")
st.sidebar.write(f"Tệp: {summary['filename']}")
st.sidebar.write(f"Số trang: {summary['pages']}")
st.sidebar.write(f"Số chunk tổng: {summary['total_chunks']}")

if summary["warnings"]:
    st.sidebar.warning("Cảnh báo:")
    for warn in summary["warnings"]:
        st.sidebar.write(f"- {warn}")

strategy_names = ["fixed_size", "semantic", "hierarchical"]
selected_strategy = st.selectbox(
    "Chọn chiến lược chunking",
    strategy_names,
    index=0,
)

st.subheader("Tổng quan")
col1, col2, col3 = st.columns(3)
for idx, key in enumerate(strategy_names):
    stats = summary["strategies"].get(key, {})
    with col1 if idx == 0 else col2 if idx == 1 else col3:
        st.metric(label=key, value=str(stats.get("count", 0)))

render_strategy_comparison(payload)

strategy_chunks = [
    chunk for chunk in payload.get("chunks", []) if chunk.get("strategy") == selected_strategy
]

st.subheader(f"Chi tiết chiến lược: {selected_strategy}")
if summary["strategies"].get(selected_strategy):
    st.json(summary["strategies"][selected_strategy], expanded=False)

render_chunk_list(strategy_chunks, selected_strategy)

st.subheader("Bản ghi theo trang")
records = payload.get("records", [])
for rec in records:
    with st.expander(f"Trang {rec.get('page', '-')} — {rec.get('ocr_used', 'unknown')}", expanded=False):
        st.write(f"Source: {rec.get('source', '')}")
        st.write(f"Language: {rec.get('language', '')}")
        st.write(f"Status: {rec.get('status', '')}")
        if rec.get("warning"):
            st.warning(rec.get("warning"))
        text = safe_text(rec.get("text", ""))
        if text:
            st.code(text[:1500] + ("..." if len(text) > 1500 else ""), language="text")
        else:
            st.info("Trang này không có text layer hợp lệ; cần fallback hoặc warning.")

st.subheader("JSON gốc")
st.json(payload, expanded=False)
