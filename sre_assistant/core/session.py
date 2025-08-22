# 提供 Session 儲存服務的兩種實作（記憶體/資料庫），並以工廠函式依設定載入。
from __future__ import annotations
import os, time
from typing import Dict, Any, Optional

class InMemorySessionService:
    """
    類別用途：以記憶體字典維護 session 狀態（適合本地開發與單機測試）。
    結構：{ session_id: { 'state': dict, 'updated_at': epoch_ms } }
    """
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def get_state(self, session_id: str) -> Dict[str, Any]:
        """取得指定 session 的狀態字典，不存在則建立。"""
        if session_id not in self._store:
            self._store[session_id] = {'state': {}, 'updated_at': int(time.time()*1000)}
        return self._store[session_id]['state']

    def set_state(self, session_id: str, state: Dict[str, Any]) -> None:
        """設定指定 session 的狀態字典。"""
        self._store[session_id] = {'state': dict(state), 'updated_at': int(time.time()*1000)}

class DatabaseSessionService:
    """
    類別用途：以資料庫持久化 session 狀態（需 SQLAlchemy；若無相依則拋出 RuntimeError）。
    資料表建議：sessions(id TEXT PRIMARY KEY, state JSONB/TEXT, updated_at BIGINT)
    """
    def __init__(self, database_url: str):
        try:
            from sqlalchemy import create_engine, text
        except Exception as e:
            raise RuntimeError("需要 SQLAlchemy 以啟用 DatabaseSessionService") from e
        self._engine = create_engine(database_url, future=True)
        # 嘗試建立最小表結構
        with self._engine.begin() as conn:
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                state TEXT,
                updated_at BIGINT
            )"""))

    def get_state(self, session_id: str) -> Dict[str, Any]:
        from sqlalchemy import text
        import json, time
        with self._engine.begin() as conn:
            row = conn.execute(text("SELECT state FROM sessions WHERE id=:id"), {'id': session_id}).fetchone()
            if row is None or not row[0]:
                conn.execute(text("INSERT INTO sessions(id,state,updated_at) VALUES(:id,:s,:t)"),
                             {'id': session_id, 's': '{}', 't': int(time.time()*1000)})
                return {}
            return json.loads(row[0])

    def set_state(self, session_id: str, state: Dict[str, Any]) -> None:
        from sqlalchemy import text
        import json, time
        with self._engine.begin() as conn:
            conn.execute(text("""
            INSERT INTO sessions(id,state,updated_at)
            VALUES(:id,:s,:t)
            ON CONFLICT(id) DO UPDATE SET state=:s, updated_at=:t
            """), {'id': session_id, 's': json.dumps(state), 't': int(time.time()*1000)})

def get_session_service()->object:
    """
    函式用途：依據環境變數 SESSION_BACKEND 選擇實作，預設 InMemory。
    - SESSION_BACKEND=database 且 DATABASE_URL 有值 → DatabaseSessionService
    - 其餘 → InMemorySessionService
    """
    backend = os.getenv('SESSION_BACKEND','memory').lower()
    if backend in ('db','database'):
        url = os.getenv('DATABASE_URL','')
        if not url:
            raise RuntimeError('SESSION_BACKEND=database 但缺少 DATABASE_URL')
        return DatabaseSessionService(url)
    return InMemorySessionService()
