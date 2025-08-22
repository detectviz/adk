
# -*- coding: utf-8 -*-
# FeedbackAgent：成功處置路徑 → Runbook（寫入向量庫）
from __future__ import annotations
from typing import Dict, Any, List
import datetime
from ..core.vectorstore_pg import init_schema, upsert_documents, upsert_chunks
from ..tools.knowledge_ingestion import _embed_texts

def save_runbook(incident_key: str, steps: List[str], outcome: str, tags: Dict[str,Any] | None = None) -> Dict[str,Any]:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`save_runbook` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `incident_key`：參數用途請描述。
    - `steps`：參數用途請描述。
    - `outcome`：參數用途請描述。
    - `tags`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    init_schema()
    title = f"Runbook:{incident_key}:{datetime.datetime.utcnow().isoformat()}Z"
    body = "\n".join([f"Step {i+1}: {s}" for i,s in enumerate(steps)]) + f"\nOutcome: {outcome}"
    [doc_id] = upsert_documents([{"title": title, "metadata": tags or {}}])
    chunks = [body]
    embeds = _embed_texts(chunks)
    added, skipped = upsert_chunks(doc_id, chunks, embeds)
    return {"doc_id": doc_id, "chunks_added": added, "title": title}