
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any, List

RAG_STORE: List[Dict[str, Any]] = []

def knowledge_ingestion_tool(title: str, content: str, tags: list[str] | None = None):
    RAG_STORE.append({"title": title, "content": content, "tags": tags or []})
    return {"ok": True, "count": len(RAG_STORE)}

def rag_retrieve_tool(query: str, top_k: int = 3):
    q = query.lower()
    scored = []
    for doc in RAG_STORE:
        score = sum(1 for w in q.split() if w in doc["content"].lower())
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return {"snippets": [d for _, d in scored[:top_k]]}
