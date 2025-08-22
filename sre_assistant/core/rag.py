
# RAG：以 SQLite FTS5 優先檢索，無 FTS 時落回 LIKE 檢索。
from __future__ import annotations
from typing import Any, Dict, List
from .persistence import DB

def rag_create_entry(title: str, content: str, author: str, tags: List[str], status: str = "draft") -> Dict[str, Any]:
    """
    2025-08-22 03:37:34Z
    函式用途：`rag_create_entry` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `title`：參數用途請描述。
    - `content`：參數用途請描述。
    - `author`：參數用途請描述。
    - `tags`：參數用途請描述。
    - `status`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    return DB.rag_insert(title, content, author, tags, status)

def rag_update_status(entry_id: int, status: str) -> Dict[str, Any] | None:
    """
    2025-08-22 03:37:34Z
    函式用途：`rag_update_status` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `entry_id`：參數用途請描述。
    - `status`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    return DB.rag_update_status(entry_id, status)

def rag_retrieve_tool(query: str, top_k: int = 5, status_filter: List[str] | None = None) -> Dict[str, Any]:
    """
    2025-08-22 03:37:34Z
    函式用途：`rag_retrieve_tool` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `query`：參數用途請描述。
    - `top_k`：參數用途請描述。
    - `status_filter`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    items = DB.rag_search(query, top_k, status_filter)
    return {"query": query, "hits": items}