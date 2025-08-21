
# -*- coding: utf-8 -*-
# RAG（示範版）升級：
# - 版本化：每個條目有自增 id、version 與狀態（draft|approved|archived）
# - 建立/檢索/審核 API（程式內函式）
from __future__ import annotations
from typing import Dict, Any, List, Optional
import itertools, time

_id = itertools.count(1)

class RagEntry(dict):
    pass

RAG_STORE: List[RagEntry] = []

def rag_create_entry(title: str, content: str, author: str = "unknown", tags: list[str] | None = None, status: str = "draft") -> RagEntry:
    eid = next(_id)
    entry = RagEntry({
        "id": eid,
        "version": 1,
        "title": title,
        "content": content,
        "author": author,
        "tags": tags or [],
        "status": status,
        "created_at": time.time(),
        "updated_at": time.time(),
    })
    RAG_STORE.append(entry)
    return entry

def rag_update_status(entry_id: int, status: str) -> Optional[RagEntry]:
    for e in RAG_STORE:
        if e["id"] == entry_id:
            e["status"] = status
            e["updated_at"] = time.time()
            return e
    return None

def rag_retrieve_tool(query: str, top_k: int = 3, status_filter: list[str] | None = None):
    q = query.lower()
    stat = set(status_filter or ["approved","draft"])
    scored = []
    for doc in RAG_STORE:
        if doc["status"] not in stat: continue
        score = sum(1 for w in q.split() if w in doc["content"].lower() or w in doc.get("title","").lower())
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return {"snippets": [d for _, d in scored[:top_k]]}

def knowledge_ingestion_tool(title: str, content: str, tags: list[str] | None = None):
    e = rag_create_entry(title=title, content=content, tags=tags or [], author="api", status="draft")
    return {"ok": True, "id": e["id"]}
