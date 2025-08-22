
# -*- coding: utf-8 -*-
# Session 服務：支援 InMemory、Database、Vertex 三種後端
from __future__ import annotations
from typing import Dict, Any
import os, time
from .persistence import DB, init_schema

class InMemorySessionService:
    """以記憶體保存 Session 狀態的最小實作。"""
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
    def get(self, session_id: str) -> Dict[str, Any]:
        return self._store.setdefault(session_id, {"created_at": time.time(), "state": {}})
    def set(self, session_id: str, state: Dict[str, Any]) -> None:
        self._store.setdefault(session_id, {"created_at": time.time(), "state": {}})["state"] = state

class DatabaseSessionService:
    """以資料庫事件表（events）持久化 Session 狀態。"""
    KEY = "__session_state__"
    def __init__(self):
        init_schema()
    def get(self, session_id: str) -> Dict[str, Any]:
        events = DB.list_events(session_id, limit=200)
        for e in events:
            if e.get("type") == self.KEY:
                return e.get("event") or {}
        return {"state": {}}
    def set(self, session_id: str, state: Dict[str, Any]) -> None:
        DB.write_event(session_id, "system", self.KEY, state)

class VertexAiSessionService:
    """Vertex AI Agent Engine 專用 Session 服務占位符。
    - 真實實作應透過官方 SDK/REST 讀寫 session state。
    - 目前回退為 no-op 並以 DB 記錄 session_state 以便觀察。
    """
    def get(self, session_id: str) -> dict:
        return {"state": {"_backend": "vertex"}}
    def set(self, session_id: str, state: dict) -> None:
        DB.write_event(session_id, "vertex", "__session_state__", state)

def pick_session_service():
    """依環境變數 SESSION_BACKEND 選擇服務：memory | db | vertex。"""
    be = (os.getenv("SESSION_BACKEND","memory") or "memory").lower()
    if be == "db":
        return DatabaseSessionService()
    if be == "vertex":
        return VertexAiSessionService()
    return InMemorySessionService()
