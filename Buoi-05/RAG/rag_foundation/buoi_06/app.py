import streamlit as st

import chromadb
import rag


def _postgres_status() -> str:
	connection = rag._postgres()
	if connection is None:
		return "SQLite fallback (.db)"
	connection.close()
	return "Đang chạy"


def _chroma_status() -> str:
	try:
		client = chromadb.PersistentClient(path=str(rag.CHROMA_DIR))
		client.get_or_create_collection(rag.COLLECTION_NAME)
		return "Đang chạy"
	except Exception:
		return "Thiếu"


def _retrieve(question: str, k: int) -> list[tuple[str, str]]:
	client = chromadb.PersistentClient(path=str(rag.CHROMA_DIR))
	collection = client.get_or_create_collection(rag.COLLECTION_NAME)
	if collection.count() == 0:
		return []
	result = collection.query(
		query_embeddings=[rag._embedding(question)],
		n_results=max(1, int(k)),
	)
	ids = result.get("ids", [[]])[0]
	documents = rag._get_texts(ids)
	return list(zip(ids, documents))


st.set_page_config(page_title="Buoi 6 RAG", layout="centered")
st.title("Buoi 6 RAG")

with st.sidebar:
	st.subheader("Trang thai")
	st.write(f"PostgreSQL: {_postgres_status()}")
	st.write(f"ChromaDB: {_chroma_status()}")
	st.write(f"Gemini API Key: {'Có' if rag._api_key() else 'Retrieval-only (Thiếu)'}")

if st.button("Index", type="primary"):
	try:
		st.success(rag.index())
	except Exception as error:
		st.error(str(error))

question = st.text_input("Question")
k = st.number_input("Top-k", min_value=1, max_value=20, value=5, step=1)

if st.button("Ask"):
	if not question.strip():
		st.warning("Vui lòng nhập câu hỏi.")
	else:
		try:
			retrieved = _retrieve(question, int(k))
			st.subheader("Kết quả Top-k")
			if retrieved:
				for position, (chunk_id, text) in enumerate(retrieved, start=1):
					st.markdown(f"**{position}. {chunk_id}**")
					st.write(text)
			else:
				st.info("Chưa có dữ liệu retrieval. Hãy chạy Index trước.")

			st.subheader("Answer")
			if not rag._api_key():
				st.info("Retrieval-only: chưa cấu hình Gemini API Key, không gọi Gemini.")
			else:
				st.write(rag.ask(question, int(k)))
		except Exception as error:
			st.error(str(error))
