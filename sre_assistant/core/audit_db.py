
# -*- coding: utf-8 -*-
# DB 審計與事件回放（PostgreSQL + JSONB）
# - 表：audits、events；若不存在將自動建立
from __future__ import annotations
from typing import Dict, Any, Iterable
import os, json, time, uuid, contextlib

try:
    import psycopg
    from psycopg.rows import dict_row
except Exception:
    psycopg=None

PG_DSN = os.getenv("PG_DSN","")

@contextlib.contextmanager
def _conn():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`_conn` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    if not psycopg or not PG_DSN:
        raise RuntimeError("缺少 psycopg 或未設定 PG_DSN")
    with psycopg.connect(PG_DSN, row_factory=dict_row) as c:
        yield c

def init_schema() -> None:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`init_schema` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS audits (
          id UUID PRIMARY KEY,
          session_id TEXT,
          user_id TEXT,
          action TEXT,
          tool_name TEXT,
          params JSONB,
          result JSONB,
          risk TEXT,
          require_hitl BOOLEAN,
          created_at TIMESTAMPTZ DEFAULT now()
        );""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
          id BIGSERIAL PRIMARY KEY,
          session_id TEXT NOT NULL,
          user_id TEXT,
          event_type TEXT,
          payload JSONB,
          created_at TIMESTAMPTZ DEFAULT now()
        );""")
        c.commit()

def write_audit_db(event: Dict[str,Any]) -> None:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`write_audit_db` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `event`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    init_schema()
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
        INSERT INTO audits(id, session_id, user_id, action, tool_name, params, result, risk, require_hitl)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);
        """, (
            uuid.uuid4(), event.get("session_id"), event.get("user_id"),
            event.get("action"), event.get("tool_name"), json.dumps(event.get("params",{})),
            json.dumps(event.get("result",{})), event.get("risk"), bool(event.get("require_hitl",False))
        ))
        c.commit()

def record_event(session_id: str, event_type: str, payload: Dict[str,Any], user_id: str | None = None) -> None:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`record_event` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `session_id`：參數用途請描述。
    - `event_type`：參數用途請描述。
    - `payload`：參數用途請描述。
    - `user_id`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    init_schema()
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
        INSERT INTO events(session_id, user_id, event_type, payload) VALUES (%s,%s,%s,%s);
        """, (session_id, user_id, event_type, json.dumps(payload)))
        c.commit()

def load_events(session_id: str, limit: int = 200) -> list[Dict[str,Any]]:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`load_events` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `session_id`：參數用途請描述。
    - `limit`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
        SELECT id, session_id, user_id, event_type, payload, created_at
        FROM events WHERE session_id=%s ORDER BY id ASC LIMIT %s;
        """, (session_id, limit))
        return cur.fetchall()