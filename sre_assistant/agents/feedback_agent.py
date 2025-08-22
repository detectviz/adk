
# -*- coding: utf-8 -*-
# FeedbackAgent：成功處置路徑 → Runbook（寫入向量庫）
from __future__ import annotations
from typing import Dict, Any, List
import datetime
from ..core.vectorstore_pg import init_schema, upsert_documents, upsert_chunks
from ..tools.knowledge_ingestion import _embed_texts

def save_runbook(incident_key: str, steps: List[str], outcome: str, tags: Dict[str,Any] | None = None) -> Dict[str,Any]:
    init_schema()
    title = f"Runbook:{incident_key}:{datetime.datetime.utcnow().isoformat()}Z"
    body = "\n".join([f"Step {i+1}: {s}" for i,s in enumerate(steps)]) + f"\nOutcome: {outcome}"
    [doc_id] = upsert_documents([{"title": title, "metadata": tags or {}}])
    chunks = [body]
    embeds = _embed_texts(chunks)
    added, skipped = upsert_chunks(doc_id, chunks, embeds)
    return {"doc_id": doc_id, "chunks_added": added, "title": title}
