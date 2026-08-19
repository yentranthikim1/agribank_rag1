"""Streamlit UI for the Buổi 07 RAG pipeline.

This module only coordinates Streamlit controls and the public functions in
``rag.py``. RAG behavior remains in the pipeline module.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import rag


STRATEGIES = ["hierarchical", "semantic", "fixed-size"]
INSUFFICIENT_ANSWER = "Không tìm thấy đủ thông tin liên quan trong tài liệu đã cung cấp."
RETRIEVAL_ONLY_ANSWER = "Đã truy xuất được nguồn nhưng chưa thể tạo câu trả lời tổng hợp."


def _friendly_error(error: Exception) -> str:
    message = str(error).replace("\n", " ").strip()
    if "GEMINI_API_KEY" in message:
        return "Chưa có GEMINI_API_KEY. Hãy điền key trong file .env của Buổi 07."
    if not message:
        return "Đã xảy ra lỗi khi xử lý yêu cầu."
    return message[:300] + ("..." if len(message) > 300 else "")


def _render_status(status: dict[str, Any]) -> None:
    st.sidebar.subheader("Trạng thái hệ thống")
    status_rows = {
        "API key": status["api_key"],
        "Embedding model": status["embedding_model"],
        "Embedding dimension": status["embedding_dim"],
        "Generation model": status.get("generation_model", ""),
        "Strategy": status["strategy"],
        "Collection": status["collection"],
        "Collection tồn tại": "Có" if status["exists"] else "Chưa có",
        "Số chunk": status["count"],
        "RAG_MAX_DISTANCE": status.get("max_distance", ""),
    }
    for label, value in status_rows.items():
        st.sidebar.caption(label)
        st.sidebar.write(value)


def _render_index_result(result: dict[str, Any], before_count: int) -> None:
    stats = result.get("stats", {})
    st.success("Index hoàn tất.")
    st.write(f"Strategy: `{result.get('strategy', 'đã chọn')}`")
    st.write(f"Collection: `{result['collection']}`")
    st.write(f"Số chunk trước/sau: `{before_count}` / `{result['count']}`")
    st.write(f"Text rỗng bỏ qua: `{stats.get('empty_text_skipped', 0)}`")


def _render_citations(citations: list[dict[str, Any]]) -> None:
    if not citations:
        return
    st.markdown("**Citation**")
    for citation in citations:
        st.write(citation["display"])


def _render_evidence(evidence: list[dict[str, Any]]) -> None:
    st.subheader("Nguồn tham khảo")
    if not evidence:
        st.info("Chưa có evidence.")
        return

    st.caption("Distance thấp hơn thường cho thấy kết quả liên quan hơn; đây không phải xác suất.")
    for item in evidence:
        page = str(item["page_start"]) if item["page_start"] == item["page_end"] else f"{item['page_start']}-{item['page_end']}"
        state = "Đạt confidence gate" if item["accepted"] else "Không đạt confidence gate, không dùng để tạo answer"
        title = f"{item['source']} – tr. {page} – {item['chunk_id']}"
        with st.expander(title):
            st.write(f"Evidence ID: `{item['evidence_id']}`")
            st.write(f"Source: `{item['source']}`")
            st.write(f"Page: `{page}`")
            st.write(f"Chunk ID: `{item['chunk_id']}`")
            st.write(f"Distance: `{item['distance']:.4f}`")
            st.write(f"Accepted: `{item['accepted']}`")
            if item["accepted"]:
                st.success(state)
            else:
                st.warning(state)
            st.text(item["text"])


def _render_query_result(result: dict[str, Any]) -> None:
    status = result["status"]
    if status == "answered":
        st.success("answered")
    elif status == "insufficient_evidence":
        st.warning("insufficient_evidence: không tìm thấy đủ thông tin liên quan.")
    else:
        st.warning("retrieval_only: đã retrieve được nguồn nhưng generation chưa tạo được answer.")

    st.markdown("### Answer")
    if status == "insufficient_evidence":
        st.info(INSUFFICIENT_ANSWER)
    elif status == "retrieval_only":
        st.info(RETRIEVAL_ONLY_ANSWER)
    else:
        st.write(result["answer"])

    for warning in result.get("warnings", []):
        st.warning(warning)
    _render_citations(result.get("citations", []))
    _render_evidence(result.get("evidence", []))


def main() -> None:
    st.set_page_config(page_title="Buổi 07 RAG", page_icon="📚", layout="wide")
    st.title("Buổi 07 · Hỏi đáp tài liệu")
    st.caption("Giao diện thử nghiệm semantic retrieval, confidence gate và grounding.")

    try:
        config = rag.load_config()
    except Exception as error:
        st.error(_friendly_error(error))
        st.stop()

    strategy = st.sidebar.selectbox("Strategy", STRATEGIES, index=0)
    top_k = st.sidebar.slider("Top-k", min_value=1, max_value=10, value=min(config["top_k"], 10))
    try:
        current_status = rag.status(strategy, config)
    except Exception as error:
        current_status = None
        st.sidebar.error(_friendly_error(error))
    if current_status is not None:
        current_status["generation_model"] = config["generation_model"]
        current_status["max_distance"] = config["max_distance"]
        _render_status(current_status)

    if "last_index" not in st.session_state:
        st.session_state.last_index = None
    if "last_query" not in st.session_state:
        st.session_state.last_query = None

    st.sidebar.subheader("Index dữ liệu")
    reset = st.sidebar.checkbox("Reset collection trước khi index")
    if st.sidebar.button("Index dữ liệu", type="primary", use_container_width=True):
        if not config["api_key"]:
            st.sidebar.warning("Chưa có API key. Hãy điền GEMINI_API_KEY trong file .env.")
        else:
            before_count = current_status["count"] if current_status else 0
            try:
                with st.spinner("Đang tạo embedding và index dữ liệu..."):
                    result = rag.index(strategy, config, reset=reset)
                st.session_state.last_index = result
                _render_index_result(result, before_count)
            except Exception as error:
                st.error(_friendly_error(error))

    st.header("Đặt câu hỏi")
    question = st.text_area("Câu hỏi", height=120, placeholder="Nhập câu hỏi về tài liệu...")
    if st.button("Gửi câu hỏi", type="primary"):
        if not question.strip():
            st.warning("Hãy nhập câu hỏi trước khi gửi.")
        elif not config["api_key"]:
            st.warning("Chưa có API key. Hãy điền GEMINI_API_KEY trong file .env.")
        elif current_status is None or not current_status["exists"]:
            st.warning("Collection chưa tồn tại. Hãy index dữ liệu trước.")
        elif current_status["count"] < 1:
            st.warning("Collection đang rỗng. Hãy index dữ liệu trước.")
        else:
            try:
                with st.spinner("Đang truy xuất và tổng hợp câu trả lời..."):
                    result = rag.ask(question, strategy, top_k, config)
                st.session_state.last_query = result
            except Exception as error:
                st.error(_friendly_error(error))

    if st.session_state.last_query is not None:
        _render_query_result(st.session_state.last_query)


if __name__ == "__main__":
    main()
