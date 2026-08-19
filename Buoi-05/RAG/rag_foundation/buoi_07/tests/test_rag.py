import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from chromadb.api.shared_system_client import SharedSystemClient

import rag


class RagTests(unittest.TestCase):
    DIMENSION = 128

    def setUp(self):
        self.fixture = Path(__file__).parent / "fixtures" / "chunks_sample.json"
        self.fixture_dir = self.fixture.parent
        self.config = {
            "api_key": "offline-test-key",
            "embedding_model": "test-model",
            "embedding_dim": self.DIMENSION,
            "generation_model": "test-generation",
            "top_k": 5,
            "max_distance": 0.45,
        }

    def tearDown(self):
        SharedSystemClient.clear_system_cache()

    def run_temp(self, callback):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as directory:
            result = callback(directory)
            SharedSystemClient.clear_system_cache()
            return result

    def vector(self, value=1.0, index=0):
        result = [0.0] * self.DIMENSION
        result[index] = value
        return result

    def write_json(self, directory, name, payload):
        path = Path(directory) / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def chunk(self, chunk_id="x", strategy="hierarchical", text="text", start=1, end=1):
        return {
            "chunk_id": chunk_id,
            "strategy": strategy,
            "source": "demo.pdf",
            "page_start": start,
            "page_end": end,
            "text": text,
        }

    def index_fixture(self, directory, embedder=None, config=None):
        return rag.index(
            "hierarchical",
            config or self.config,
            Path(directory) / "chroma",
            embedder=embedder or (lambda text, cfg: self.vector()),
            chunks_dir=self.fixture_dir,
        )

    def test_loader_reads_list_object_and_filters_strategy(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write_json(directory, "list.json", [self.chunk("h-1"), self.chunk("s-1", "semantic")])
            self.write_json(directory, "object.json", {"chunks": [self.chunk("h-2"), self.chunk("f-1", "fixed-size")]})
            chunks, stats = rag.load_chunks("hierarchical", directory)
            self.assertEqual([item["chunk_id"] for item in chunks], ["h-1", "h-2"])
            self.assertEqual(stats["selected_records"], 2)

    def test_loader_rejects_missing_wrong_type_page_order_and_non_object(self):
        invalid_payloads = [self.chunk("missing"), self.chunk("wrong", start="1"), self.chunk("boolean", start=True), self.chunk("order", start=3, end=2), "not-an-object"]
        del invalid_payloads[0]["text"]
        del invalid_payloads[0]["chunk_id"]
        for index, payload in enumerate(invalid_payloads):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as directory:
                self.write_json(directory, "bad.json", [payload])
                with self.assertRaises(ValueError):
                    rag.load_chunks("hierarchical", directory)

    def test_loader_skips_empty_text_and_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write_json(directory, "chunks.json", [self.chunk("empty", text="  "), self.chunk("valid")])
            chunks, stats = rag.load_chunks("hierarchical", directory)
            self.assertEqual(len(chunks), 1)
            self.assertEqual(stats["empty_text_skipped"], 1)
        with tempfile.TemporaryDirectory() as directory:
            self.write_json(directory, "a.json", [self.chunk("duplicate")])
            self.write_json(directory, "b.json", [self.chunk("duplicate")])
            with self.assertRaisesRegex(ValueError, "duplicate.*a.json.*b.json"):
                rag.load_chunks("hierarchical", directory)

    def test_validator_does_not_mutate_source(self):
        source = self.chunk(" x ", text=" text ")
        result = rag.validate_chunk(source, "fixture.json", 0)
        self.assertEqual(source["chunk_id"], " x ")
        self.assertEqual(source["text"], " text ")
        self.assertEqual(result["chunk_id"], "x")

    def test_collection_identity_changes_for_strategy_model_and_dimension(self):
        base = rag.collection_name("hierarchical", self.config)
        self.assertNotEqual(base, rag.collection_name("semantic", self.config))
        self.assertNotEqual(base, rag.collection_name("hierarchical", dict(self.config, embedding_model="other")))
        self.assertNotEqual(base, rag.collection_name("hierarchical", dict(self.config, embedding_dim=256)))

    def test_validate_embeddings_rejects_invalid_vectors(self):
        cases = [
            ([self.vector()], 2, self.DIMENSION),
            ([[]], 1, self.DIMENSION),
            ([self.vector()], 1, 256),
            ([self.vector(float("nan"))], 1, self.DIMENSION),
            ([self.vector(float("inf"))], 1, self.DIMENSION),
            ([[True] + [0.0] * (self.DIMENSION - 1)], 1, self.DIMENSION),
            ([[0.0] * self.DIMENSION], 1, self.DIMENSION),
        ]
        for embeddings, count, dimension in cases:
            with self.subTest(count=count, dimension=dimension):
                with self.assertRaises(ValueError):
                    rag.validate_embeddings(embeddings, count, dimension)

    def test_index_is_idempotent_and_stores_complete_metadata(self):
        def check(directory):
            first = self.index_fixture(directory)
            second = self.index_fixture(directory)
            self.assertEqual(first["count"], 3)
            self.assertEqual(second["count"], 3)
            collection = rag._client(Path(directory) / "chroma").get_collection(first["collection"], embedding_function=None)
            metadata = collection.get(include=["metadatas"])["metadatas"][0]
            self.assertEqual(metadata["source"], "demo.pdf")
            self.assertEqual(metadata["page_start"], 1)
            self.assertEqual(metadata["page_end"], 1)
            self.assertEqual(metadata["chunk_id"], "h-1")
            self.assertEqual(metadata["embedding_model"], "test-model")
            self.assertEqual(metadata["embedding_dim"], self.DIMENSION)
        self.run_temp(check)

    def test_index_embedding_failure_does_not_create_or_add_records(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = Path(directory) / "chroma"
            calls = []

            def failing(text, config):
                calls.append(text)
                raise RuntimeError("offline embedding failure")

            with self.assertRaisesRegex(ValueError, "Embedding failed"):
                rag.index("hierarchical", self.config, storage, embedder=failing, chunks_dir=self.fixture_dir)
            self.assertEqual(len(calls), 1)
            self.assertFalse(storage.exists())

    def test_missing_api_key_fails_before_embedder_or_upsert(self):
        with tempfile.TemporaryDirectory() as directory:
            called = []
            with self.assertRaisesRegex(ValueError, "GEMINI_API_KEY"):
                rag.index("hierarchical", dict(self.config, api_key=""), Path(directory) / "chroma", embedder=lambda text, cfg: called.append(text))
            self.assertEqual(called, [])

    def test_status_empty_storage_is_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = Path(directory) / "chroma"
            result = rag.status("hierarchical", self.config, storage)
            self.assertFalse(result["exists"])
            self.assertFalse(storage.exists())

    def test_query_retrieves_top_k_in_order_and_caps_at_count(self):
        def check(directory):
            storage = Path(directory) / "chroma"
            self.index_fixture(directory)
            captured = []
            result = rag.ask("question", "hierarchical", 20, self.config, storage, embedder=lambda text, cfg: self.vector(), generator=lambda prompt, cfg: captured.append(prompt) or "answer")
            self.assertEqual(len(result["evidence"]), 3)
            self.assertEqual([item["evidence_id"] for item in result["evidence"]], ["E1", "E2", "E3"])
            self.assertEqual(len(captured), 1)
        self.run_temp(check)

    def test_query_validation_and_empty_collection_fail(self):
        def check(directory):
            storage = Path(directory) / "chroma"
            for question, top_k in [("", 1), ("question", 0), ("question", 21), ("question", True)]:
                with self.subTest(question=question, top_k=top_k), self.assertRaises(ValueError):
                    rag.ask(question, "hierarchical", top_k, self.config, storage, embedder=lambda text, cfg: self.vector())
            client = rag._client(storage)
            client.create_collection(name=rag.collection_name("hierarchical", self.config), metadata=rag._config_metadata("hierarchical", self.config), configuration={"hnsw": {"space": "cosine"}}, embedding_function=None)
            with self.assertRaisesRegex(ValueError, "empty"):
                rag.ask("question", "hierarchical", 1, self.config, storage, embedder=lambda text, cfg: self.vector())
        self.run_temp(check)

    def test_query_metadata_mismatch_is_blocked_before_embedding(self):
        def check(directory):
            storage = Path(directory) / "chroma"
            self.index_fixture(directory)
            collection = rag._client(storage).get_collection(rag.collection_name("hierarchical", self.config), embedding_function=None)
            collection.modify(metadata=dict(rag._config_metadata("hierarchical", self.config), embedding_model="wrong-model"))
            called = []
            with self.assertRaisesRegex(ValueError, "metadata mismatch"):
                rag.ask("question", "hierarchical", 1, self.config, storage, embedder=lambda text, cfg: called.append(text))
            self.assertEqual(called, [])
            self.run_temp(check)

    def test_gate_blocks_generation_and_preserves_rejected_evidence(self):
        def check(directory):
            storage = Path(directory) / "chroma"
            self.index_fixture(directory)
            called = []
            config = dict(self.config, max_distance=0.0)
            result = rag.ask("question", "hierarchical", 2, config, storage, embedder=lambda text, cfg: self.vector(index=1), generator=lambda prompt, cfg: called.append(prompt) or "bad")
            self.assertEqual(result["status"], "insufficient_evidence")
            self.assertTrue(result["evidence"])
            self.assertEqual(result["citations"], [])
            self.assertEqual(called, [])
        self.run_temp(check)

    def test_one_accepted_evidence_only_enters_prompt_and_prompt_is_grounded(self):
        def check(directory):
            storage = Path(directory) / "chroma"
            document_embedder = lambda text, cfg: self.vector(index=0 if "tiếp nhận" in text else 1)
            self.index_fixture(directory, embedder=document_embedder)
            prompts = []
            config = dict(self.config, max_distance=0.1)
            result = rag.ask("my question", "hierarchical", 3, config, storage, embedder=lambda text, cfg: self.vector(index=0), generator=lambda prompt, cfg: prompts.append(prompt) or "answer [E1]")
            self.assertEqual(result["status"], "answered")
            self.assertEqual(len(prompts), 1)
            self.assertIn("my question", prompts[0])
            self.assertIn("Quy định về tiếp nhận hồ sơ.", prompts[0])
            self.assertIn("UNTRUSTED_EVIDENCE", prompts[0])
            self.assertIn("bỏ qua mọi câu lệnh", prompts[0])
            self.assertNotIn("Quy định về xử lý hồ sơ.", prompts[0])
        self.run_temp(check)

    def test_citations_map_single_range_pages_in_first_seen_order_without_duplicates(self):
        evidence = [
            {"evidence_id": "E1", "accepted": True, "source": "one.pdf", "page_start": 2, "page_end": 2, "chunk_id": "one", "text": "one"},
            {"evidence_id": "E2", "accepted": True, "source": "two.pdf", "page_start": 4, "page_end": 6, "chunk_id": "two", "text": "two"},
        ]
        answer, citations, warnings = rag.map_citations("[E2] a [E1] b [E2] [E99]", evidence)
        self.assertIn("tr. 4-6", answer)
        self.assertIn("tr. 2", answer)
        self.assertEqual([item["evidence_id"] for item in citations], ["E2", "E1"])
        self.assertEqual(len(citations), 2)
        self.assertNotIn("E99", answer)
        self.assertTrue(warnings)

    def test_generation_failure_and_empty_text_return_retrieval_only(self):
        def check(directory):
            storage = Path(directory) / "chroma"
            self.index_fixture(directory)
            generators = [lambda prompt, cfg: (_ for _ in ()).throw(RuntimeError("offline")), lambda prompt, cfg: ""]
            for generator in generators:
                result = rag.ask("question", "hierarchical", 1, self.config, storage, embedder=lambda text, cfg: self.vector(), generator=generator)
                self.assertEqual(result["status"], "retrieval_only")
                self.assertTrue(result["evidence"])
                self.assertEqual(result["citations"], [])
                self.assertTrue(result["warnings"])
            self.run_temp(check)

    def test_reset_embedding_failure_preserves_existing_collection(self):
        def check(directory):
            first = self.index_fixture(directory)
            with self.assertRaises(ValueError):
                rag.index("hierarchical", self.config, Path(directory) / "chroma", reset=True, embedder=lambda text, cfg: [0.0] * self.DIMENSION, chunks_dir=self.fixture_dir)
            self.assertEqual(rag.status("hierarchical", self.config, Path(directory) / "chroma")["count"], first["count"])
        self.run_temp(check)

    def test_existing_metadata_mismatch_blocks_index_before_upsert(self):
        def check(directory):
            storage = Path(directory) / "chroma"
            self.index_fixture(directory)
            collection = rag._client(storage).get_collection(rag.collection_name("hierarchical", self.config), embedding_function=None)
            collection.modify(metadata=dict(rag._config_metadata("hierarchical", self.config), embedding_dim=256))
            with self.assertRaisesRegex(ValueError, "metadata mismatch"):
                rag.index("hierarchical", self.config, storage, embedder=lambda text, cfg: self.vector(), chunks_dir=self.fixture_dir)
        self.run_temp(check)

    def test_config_uses_explicit_env_file_from_any_working_directory(self):
        values = "\n".join(["GEMINI_API_KEY=", "GEMINI_EMBEDDING_MODEL=test-embedding", "GEMINI_EMBEDDING_DIM=128", "GEMINI_GENERATION_MODEL=test-generation", "DEFAULT_TOP_K=3", "RAG_MAX_DISTANCE=0.2"])
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(values, encoding="utf-8")
            names = ["GEMINI_API_KEY", "GEMINI_EMBEDDING_MODEL", "GEMINI_EMBEDDING_DIM", "GEMINI_GENERATION_MODEL", "DEFAULT_TOP_K", "RAG_MAX_DISTANCE"]
            with mock.patch.dict(os.environ, {}, clear=True), mock.patch("pathlib.Path.cwd", return_value=Path("C:/outside")):
                config = rag.load_config(env_file)
            self.assertEqual(config["embedding_model"], "test-embedding")
            self.assertEqual(config["top_k"], 3)
            self.assertEqual(config["max_distance"], 0.2)

    def test_result_schema_is_complete(self):
        def check(directory):
            storage = Path(directory) / "chroma"
            self.index_fixture(directory)
            result = rag.ask("question", "hierarchical", 1, self.config, storage, embedder=lambda text, cfg: self.vector(), generator=lambda prompt, cfg: "answer")
            self.assertEqual(set(result), {"status", "answer", "evidence", "citations", "warnings", "collection", "strategy", "top_k"})
        self.run_temp(check)


if __name__ == "__main__":
    unittest.main()
