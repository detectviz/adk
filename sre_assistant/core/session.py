
# -*- coding: utf-8 -*-
# Session 服務：優先採用官方 google.adk.sessions，若不可用再回退到本地最小實作
from __future__ import annotations
from typing import Dict, Any
import os, time

try:
    # 官方 ADK SessionService（建議在生產使用）
    from google.adk.sessions import InMemorySessionService as _AdkMem
    from google.adk.sessions import DatabaseSessionService as _AdkDB
except Exception:
    _AdkMem = None
    _AdkDB = None

# --- 本地 fallback（僅當無法使用官方時） ---
class _LocalInMemorySessionService:
    """以記憶體保存 Session 狀態的最小實作（開發用途）。"""
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`__init__` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
    def __init__(self): self._store: Dict[str, Dict[str, Any]] = {}
    def get(self, session_id: str) -> Dict[str, Any]:
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`get` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `session_id`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        return self._store.setdefault(session_id, {"created_at": time.time(), "state": {}})
    def set(self, session_id: str, state: Dict[str, Any]) -> None:
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`set` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `session_id`：參數用途請描述。
        - `state`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        self._store.setdefault(session_id, {"created_at": time.time(), "state": {}})["state"] = state

class _LocalDatabaseSessionService:
    """以事件表持久化 Session 狀態的最小實作（非官方）。建議改用官方 _AdkDB。"""
    KEY = "__session_state__"
    def get(self, session_id: str) -> Dict[str, Any]:
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`get` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `session_id`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        try:
            from .persistence import DB
            events = DB.list_events(session_id, limit=200)
            for e in events:
                if e.get("type") == self.KEY:
                    return e.get("event") or {}
        except Exception:
            pass
        return {"state": {}}
    def set(self, session_id: str, state: Dict[str, Any]) -> None:
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`set` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `session_id`：參數用途請描述。
        - `state`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        try:
            from .persistence import DB
            DB.write_event(session_id, "system", self.KEY, state)
        except Exception:
            pass

# --- 對外導出：優先官方，否則回退 ---
class InMemorySessionService(_AdkMem if _AdkMem else _LocalInMemorySessionService): pass
class DatabaseSessionService(_AdkDB if _AdkDB else _LocalDatabaseSessionService): pass

def pick_session_service():
    """依環境變數 SESSION_BACKEND 選擇服務：memory | db | vertex(保留)。"""
    be = (os.getenv("SESSION_BACKEND","memory") or "memory").lower()
    if be == "db":
        return DatabaseSessionService()
    if be == "vertex":
        # 若有自定 Vertex 實作可在此導向；否則回退為 DB 或 Memory
        return DatabaseSessionService() if _AdkDB else InMemorySessionService()
    return InMemorySessionService()