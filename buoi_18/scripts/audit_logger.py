import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

log_file = base_dir / 'outputs' / 'audit_log.jsonl'


def ensure_parent_dir():
    log_file.parent.mkdir(parents=True, exist_ok=True)


def log_audit_event(
    user_id_demo: str,
    user_role: str,
    action: str,
    query: str,
    retrieval_method: str = 'Hybrid_Rerank',
    retrieved_doc_ids: list | None = None,
    retrieved_chunk_ids: list | None = None,
    citation_ids: list | None = None,
    denied_candidates_count: int = 0,
    status: str = 'SUCCESS',
    details: dict | None = None,
) -> str:
    ensure_parent_dir()
    request_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
    event = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'request_id': request_id,
        'user_id_demo': user_id_demo,
        'user_role': user_role,
        'action': action,
        'query': query,
        'retrieval_method': retrieval_method,
        'retrieved_doc_ids': retrieved_doc_ids or [],
        'retrieved_chunk_ids': retrieved_chunk_ids or [],
        'citation_ids': citation_ids or [],
        'denied_candidates_count': denied_candidates_count,
        'status': status,
        'details': details or {},
    }
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')
    return request_id
