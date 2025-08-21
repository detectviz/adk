
# -*- coding: utf-8 -*-
# RAG：以 SQLite FTS5 優先檢索，無 FTS 時落回 LIKE 檢索。
from __future__ import annotations
from typing import Any, Dict, List
from .persistence import DB

def rag_create_entry(title: str, content: str, author: str, tags: List[str], status: str = "draft") -> Dict[str, Any]:
    return DB.rag_insert(title, content, author, tags, status)

def rag_update_status(entry_id: int, status: str) -> Dict[str, Any] | None:
    return DB.rag_update_status(entry_id, status)

def rag_retrieve_tool(query: str, top_k: int = 5, status_filter: List[str] | None = None) -> Dict[str, Any]:
    items = DB.rag_search(query, top_k, status_filter)
    return {"query": query, "hits": items}
