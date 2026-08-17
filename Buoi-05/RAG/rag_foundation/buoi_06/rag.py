"""Small RAG pipeline for Buoi 6."""

from __future__ import annotations

import hashlib
import json
import math
import os
import sqlite3
from pathlib import Path
from typing import Any

import chromadb
from dotenv import dotenv_values


ROOT = Path(__file__).resolve().parent
CHUNKS_DIR = ROOT.parent / "buoi_05" / "output" / "chunks"
LOCAL_DB = ROOT / ".db"
CHROMA_DIR = ROOT / "storage" / "chroma"
COLLECTION_NAME = "buoi_06_chunks"
EMBEDDING_MODEL = "gemini-embedding-2"
ANSWER_MODEL = "gemini-flash-lite-latest"
EMBEDDING_DIMENSION = 384
ENV = dotenv_values(ROOT / ".env")


def _api_key() -> str:
	return os.getenv("GEMINI_API_KEY") or str(ENV.get("GEMINI_API_KEY") or "")


def _text_from_item(item: Any) -> str | None:
	if isinstance(item, str):
		return item.strip() or None
	if not isinstance(item, dict):
		return None
	for key in ("text", "content", "chunk_text", "page_content"):
		value = item.get(key)
		if isinstance(value, str) and value.strip():
			return value.strip()
	return None


def _read_chunks() -> list[dict[str, Any]]:
	if not CHUNKS_DIR.exists():
		raise FileNotFoundError(f"Không tìm thấy thư mục JSON: {CHUNKS_DIR}")

	chunks: list[dict[str, Any]] = []
	for path in sorted(CHUNKS_DIR.glob("*.json")):
		data = json.loads(path.read_text(encoding="utf-8"))
		items = data if isinstance(data, list) else data.get("chunks", data) if isinstance(data, dict) else []
		if isinstance(items, dict):
			items = [items]
		for position, item in enumerate(items):
			text = _text_from_item(item)
			if text:
				chunks.append({"id": f"{path.stem}-{position}", "text": text, "source": path.name})
	return chunks


def _config() -> dict[str, str]:
	return {
		"host": os.getenv("POSTGRES_HOST") or str(ENV.get("POSTGRES_HOST") or "localhost"),
		"port": os.getenv("POSTGRES_PORT") or str(ENV.get("POSTGRES_PORT") or "5432"),
		"dbname": os.getenv("POSTGRES_DB") or str(ENV.get("POSTGRES_DB") or "rag_db"),
		"user": os.getenv("POSTGRES_USER") or str(ENV.get("POSTGRES_USER") or "postgres"),
		"password": os.getenv("POSTGRES_PASSWORD") or str(ENV.get("POSTGRES_PASSWORD") or ""),
	}


def _postgres():
	try:
		import psycopg

		return psycopg.connect(**_config())
	except Exception:
		return None


def _local_connection() -> sqlite3.Connection:
	connection = sqlite3.connect(LOCAL_DB)
	connection.execute("CREATE TABLE IF NOT EXISTS chunks (id TEXT PRIMARY KEY, text TEXT NOT NULL, source TEXT NOT NULL)")
	connection.commit()
	return connection


def _embedding(text: str) -> list[float]:
	api_key = _api_key()
	if api_key:
		from google import genai
		from google.genai import types

		client = genai.Client(api_key=api_key)
		response = client.models.embed_content(
			model=EMBEDDING_MODEL,
			contents=text,
			config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSION),
		)
		return list(response.embeddings[0].values)

	vector = [0.0] * EMBEDDING_DIMENSION
	words = text.lower().split()
	for word in words:
		digest = hashlib.sha256(word.encode("utf-8")).digest()
		index = int.from_bytes(digest[:4], "big") % EMBEDDING_DIMENSION
		vector[index] += 1.0 if digest[4] % 2 else -1.0
	length = math.sqrt(sum(value * value for value in vector)) or 1.0
	return [value / length for value in vector]


def _save_texts(chunks: list[dict[str, Any]]) -> str:
	connection = _postgres()
	if connection:
		try:
			with connection, connection.cursor() as cursor:
				cursor.execute("CREATE TABLE IF NOT EXISTS rag_chunks (id TEXT PRIMARY KEY, text TEXT NOT NULL, source TEXT NOT NULL)")
				cursor.execute("DELETE FROM rag_chunks")
				cursor.executemany("INSERT INTO rag_chunks (id, text, source) VALUES (%s, %s, %s)", [(c["id"], c["text"], c["source"]) for c in chunks])
			connection.close()
			return "PostgreSQL"
		except Exception:
			connection.close()

	with _local_connection() as connection:
		connection.execute("DELETE FROM chunks")
		connection.executemany("INSERT INTO chunks (id, text, source) VALUES (?, ?, ?)", [(c["id"], c["text"], c["source"]) for c in chunks])
	return "SQLite local (.db)"


def _get_texts(ids: list[str]) -> list[str]:
	connection = _postgres()
	if connection:
		try:
			with connection, connection.cursor() as cursor:
				cursor.execute("SELECT id, text FROM rag_chunks WHERE id = ANY(%s)", (ids,))
				values = dict(cursor.fetchall())
			connection.close()
			return [values[item] for item in ids if item in values]
		except Exception:
			connection.close()

	with _local_connection() as connection:
		placeholders = ",".join("?" for _ in ids)
		rows = connection.execute(f"SELECT id, text FROM chunks WHERE id IN ({placeholders})", ids).fetchall() if ids else []
	values = dict(rows)
	return [values[item] for item in ids if item in values]


def index() -> dict[str, Any]:
	"""Index JSON chunks in Chroma and text storage."""
	chunks = _read_chunks()
	storage = _save_texts(chunks)
	CHROMA_DIR.mkdir(parents=True, exist_ok=True)
	client = chromadb.PersistentClient(path=str(CHROMA_DIR))
	collection = client.get_or_create_collection(COLLECTION_NAME)
	old_ids = collection.get().get("ids", [])
	if old_ids:
		collection.delete(ids=old_ids)
	if chunks:
		collection.upsert(
			ids=[chunk["id"] for chunk in chunks],
			documents=[chunk["text"] for chunk in chunks],
			metadatas=[{"source": chunk["source"]} for chunk in chunks],
			embeddings=[_embedding(chunk["text"]) for chunk in chunks],
		)
	return {"documents": len({chunk["source"] for chunk in chunks}), "chunks": len(chunks), "text_storage": storage}


def ask(question: str, k: int = 5) -> str:
	"""Retrieve the nearest chunks and optionally ask Gemini for an answer."""
	if not question.strip():
		return "Vui lòng nhập câu hỏi."
	collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_or_create_collection(COLLECTION_NAME)
	if collection.count() == 0:
		return "Chưa có dữ liệu. Hãy chạy index() trước."
	result = collection.query(query_embeddings=[_embedding(question)], n_results=max(1, int(k)))
	ids = result.get("ids", [[]])[0]
	context = "\n\n".join(_get_texts(ids))
	api_key = _api_key()
	if not api_key:
		return context or "Không tìm thấy thông tin phù hợp."

	from google import genai

	client = genai.Client(api_key=api_key)
	prompt = f"Dựa chỉ trên ngữ cảnh sau, hãy trả lời bằng tiếng Việt.\n\nNgữ cảnh:\n{context}\n\nCâu hỏi: {question}"
	return client.models.generate_content(model=ANSWER_MODEL, contents=prompt).text or "Không có câu trả lời."


def status() -> dict[str, int]:
	"""Return the number of indexed documents and chunks."""
	connection = _postgres()
	if connection:
		try:
			with connection, connection.cursor() as cursor:
				cursor.execute("SELECT COUNT(*) FROM rag_chunks")
				chunks = int(cursor.fetchone()[0])
				cursor.execute("SELECT COUNT(DISTINCT source) FROM rag_chunks")
				documents = int(cursor.fetchone()[0])
			connection.close()
			return {"documents": documents, "chunks": chunks}
		except Exception:
			connection.close()
	with _local_connection() as connection:
		chunks = int(connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])
		documents = int(connection.execute("SELECT COUNT(DISTINCT source) FROM chunks").fetchone()[0])
	return {"documents": documents, "chunks": chunks}
