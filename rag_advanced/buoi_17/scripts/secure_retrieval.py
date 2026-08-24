import os
import sys
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple

base_dir = Path(__file__).resolve().parent.parent

class SecureRetrievalAdapter:
    def __init__(self):
        csv_path = base_dir / "data" / "chunks_combined_secure.csv"
        if not csv_path.exists():
            csv_path = base_dir / "data" / "agribank_internal_policies.csv"
        self.chunks_df = pd.read_csv(csv_path)

    @staticmethod
    def _normalize_role_name(value: str) -> str:
        return str(value or "").strip().replace("-", "_").replace(" ", "_").upper()

    @staticmethod
    def _parse_allowed_roles(raw_value) -> list[str]:
        if raw_value is None or (isinstance(raw_value, float) and pd.isna(raw_value)):
            return []
        text = str(raw_value)
        if text.startswith("[") and text.endswith("]"):
            text = text.strip("[]")
        cleaned = text.replace('"', "").replace("'", "").replace(";", ",")
        roles = [r.strip() for r in cleaned.split(",") if r.strip()]
        return [SecureRetrievalAdapter._normalize_role_name(r) for r in roles]

    def retrieve_with_rbac(
        self,
        query: str,
        user_role: str,
        method: str = "hybrid_rerank",
        top_k: int = 3
    ) -> Tuple[List[Dict], int, str]:
        if user_role in ["Guest", "Unknown", None, ""]:
            return [], len(self.chunks_df), "DENIED"

        normalized_user_role = self._normalize_role_name(user_role)
        role_access = {
            "ADMIN": ["ADMIN", "HR", "RISK", "STAFF", "COMMON", "PUBLIC", "ALL"],
            "KIEMTOANVIEN": ["ADMIN", "HR", "RISK", "STAFF", "COMMON", "PUBLIC", "ALL"],
            "HR": ["HR", "STAFF", "COMMON", "PUBLIC", "ALL"],
            "RISK_MANAGER": ["RISK", "STAFF", "COMMON", "PUBLIC", "ALL"],
            "STAFF": ["STAFF", "COMMON", "PUBLIC", "ALL"]
        }
        allowed_set = set(role_access.get(normalized_user_role, ["COMMON", "PUBLIC", "ALL"]))

        allowed_rows = []
        denied_count = 0
        for _, row in self.chunks_df.iterrows():
            chunk_roles = self._parse_allowed_roles(row.get("allowed_roles", "Common"))
            if any(r in allowed_set for r in chunk_roles):
                allowed_rows.append(row)
            else:
                denied_count += 1

        if not allowed_rows:
            return [], denied_count, "DENIED"

        filtered_df = pd.DataFrame(allowed_rows)
        query_words = [w.lower() for w in query.replace("?", "").replace(",", "").split() if len(w) > 1]

        def calc_score(row):
            txt = " ".join([str(val) for val in row.values]).lower()
            return sum(txt.count(w) for w in query_words)

        filtered_df["score"] = filtered_df.apply(calc_score, axis=1)
        scored_df = filtered_df.sort_values(by="score", ascending=False)
        top_df = scored_df.head(top_k)

        standardized_docs = []
        for rank, (_, doc) in enumerate(top_df.iterrows(), 1):
            text_val = str(doc.get("text") or doc.get("content") or doc.get("noi_dung") or "")
            if len(text_val) < 20:
                text_val = " ".join([str(v) for k, v in doc.items() if k not in ["chunk_id", "document_id", "allowed_roles"]])
            doc_id = str(doc.get("document_id") or doc.get("so_ky_hieu") or "DOC_REF")
            citation = str(doc.get("citation") or doc.get("title") or f"Văn bản {doc_id}")
            standardized_docs.append({
                "rank": rank,
                "chunk_id": str(doc.get("chunk_id", f"chk_{rank}")),
                "document_id": doc_id,
                "title": str(doc.get("title", citation)),
                "citation": citation,
                "text": text_val,
                "allowed_roles": str(doc.get("allowed_roles", "Common")),
                "access_decision": "ALLOWED"
            })
        return standardized_docs, denied_count, "SUCCESS"
