
# -*- coding: utf-8 -*-
# 資料層：提供審計/事件/決策儲存（sqlite 預設；PG_DSN 待擴充）
from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
import os, json, sqlite3, contextlib

PG_DSN = os.getenv("PG_DSN","")
USE_SQLITE = not bool(PG_DSN)
SQLITE_PATH = os.getenv("DB_PATH","/mnt/data/sre-assistant.db")

@contextlib.contextmanager
def _sqlite():
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    try:
        yield conn
    finally:
        conn.commit(); conn.close()

def init_schema():
    if USE_SQLITE:
        with _sqlite() as c:
            cur=c.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS audits(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT, user_id TEXT, action TEXT, payload TEXT,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            cur.execute("""CREATE TABLE IF NOT EXISTS events(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT, user_id TEXT, event_type TEXT, event_json TEXT,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            cur.execute("""CREATE TABLE IF NOT EXISTS decisions(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT, agent_name TEXT, decision_type TEXT,
              input_json TEXT, output_json TEXT, confidence REAL,
              execution_time_ms INTEGER,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            cur.execute("""CREATE TABLE IF NOT EXISTS api_keys(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              key TEXT, role TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")

class DB:
    path = SQLITE_PATH

    @staticmethod
    def write_audit(session_id: str, user_id: str, action: str, payload: Dict[str,Any]) -> None:
        init_schema()
        with _sqlite() as c:
            c.execute("INSERT INTO audits(session_id,user_id,action,payload) VALUES(?,?,?,?)",
                      (session_id, user_id, action, json.dumps(payload, ensure_ascii=False)))

    @staticmethod
    def write_event(session_id: str, user_id: str, event_type: str, event_json: Dict[str,Any]) -> None:
        init_schema()
        with _sqlite() as c:
            c.execute("INSERT INTO events(session_id,user_id,event_type,event_json) VALUES(?,?,?,?)",
                      (session_id, user_id, event_type, json.dumps(event_json, ensure_ascii=False)))

    @staticmethod
    def list_events(session_id: str, limit: int = 100) -> List[Dict[str,Any]]:
        init_schema()
        with _sqlite() as c:
            cur=c.cursor()
            cur.execute("SELECT id,event_type,event_json,created_at FROM events WHERE session_id=? ORDER BY id DESC LIMIT ?", (session_id, limit))
            return [{"id":r[0],"type":r[1],"event":json.loads(r[2] or "{}"),"created_at":r[3]} for r in cur.fetchall()]

    @staticmethod
    def list_decisions(limit: int = 50, offset: int = 0) -> List[Dict[str,Any]]:
        init_schema()
        with _sqlite() as c:
            cur=c.cursor()
            cur.execute("SELECT id, session_id, agent_name, decision_type, confidence, execution_time_ms, created_at FROM decisions ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
            rows=cur.fetchall()
            return [{"id":r[0],"session_id":r[1],"agent_name":r[2],"decision_type":r[3],"confidence":r[4],"execution_time_ms":r[5],"created_at":r[6]} for r in rows]
