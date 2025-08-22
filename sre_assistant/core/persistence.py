
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
    """統一資料介面。根據環境切換 sqlite 或 PostgreSQL。"""
    path = SQLITE_PATH  # 兼容 CLI 參考

    @staticmethod
    def write_audit(session_id: str, user_id: str, action: str, payload: Dict[str,Any]) -> None:
        
        init_schema()
        if USE_SQLITE:
            with _sqlite() as c:
                c.execute("INSERT INTO audits(session_id,user_id,action,payload) VALUES(?,?,?,?)",
                          (session_id, user_id, action, json.dumps(payload, ensure_ascii=False)))
        else:
            with _pg() as c, c.cursor() as cur:
                cur.execute("INSERT INTO audits(session_id,user_id,action,payload) VALUES(%s,%s,%s,%s)",
                            (session_id, user_id, action, json.dumps(payload, ensure_ascii=False)))
                c.commit()

    @staticmethod
    def write_event(session_id: str, user_id: str, event_type: str, event_json: Dict[str,Any]) -> None:
        
        init_schema()
        if USE_SQLITE:
            with _sqlite() as c:
                c.execute("INSERT INTO events(session_id,user_id,event_type,event_json) VALUES(?,?,?,?)",
                          (session_id, user_id, event_type, json.dumps(event_json, ensure_ascii=False)))
        else:
            with _pg() as c, c.cursor() as cur:
                cur.execute("INSERT INTO events(session_id,user_id,event_type,event_json) VALUES(%s,%s,%s,%s)",
                            (session_id, user_id, event_type, json.dumps(event_json, ensure_ascii=False)))
                c.commit()

    @staticmethod
    def write_decision(session_id: str, agent_name: str, decision_type: str,
                       input_json: Dict[str,Any], output_json: Dict[str,Any],
                       confidence: float | None = None, execution_time_ms: int | None = None) -> None:
        """寫入決策記錄（供審計與回放）。"""
        init_schema()
        if USE_SQLITE:
            with _sqlite() as c:
                c.execute("""INSERT INTO decisions(session_id,agent_name,decision_type,input_json,output_json,confidence,execution_time_ms)
                             VALUES(?,?,?,?,?,?,?)""",
                          (session_id, agent_name, decision_type,
                           json.dumps(input_json, ensure_ascii=False),
                           json.dumps(output_json, ensure_ascii=False),
                           confidence, execution_time_ms))
        else:
            with _pg() as c, c.cursor() as cur:
                cur.execute("""INSERT INTO decisions(session_id,agent_name,decision_type,input_json,output_json,confidence,execution_time_ms)
                               VALUES(%s,%s,%s,%s,%s,%s,%s)""",
                            (session_id, agent_name, decision_type,
                             json.dumps(input_json, ensure_ascii=False),
                             json.dumps(output_json, ensure_ascii=False),
                             confidence, execution_time_ms))
                c.commit()

    @staticmethod
    def list_events(session_id: str, limit: int = 100) -> List[Dict[str,Any]]:
        
        init_schema()
        if USE_SQLITE:
            with _sqlite() as c:
                cur=c.cursor()
                cur.execute("SELECT id, event_type, event_json, created_at FROM events WHERE session_id=? ORDER BY id DESC LIMIT ?", (session_id, limit))
                return [{"id":r[0],"type":r[1],"event":json.loads(r[2] or "{}"),"created_at":r[3]} for r in cur.fetchall()]
        else:
            with _pg() as c, c.cursor() as cur:
                cur.execute("SELECT id, event_type, event_json, created_at FROM events WHERE session_id=%s ORDER BY id DESC LIMIT %s", (session_id, limit))
                rows=cur.fetchall()
                return [{"id":r["id"],"type":r["event_type"],"event":r["event_json"],"created_at":r["created_at"].isoformat()} for r in rows]

    @staticmethod
    def list_decisions(limit: int = 50, offset: int = 0) -> List[Dict[str,Any]]:
        
        init_schema()
        if USE_SQLITE:
            with _sqlite() as c:
                cur=c.cursor()
                cur.execute("SELECT id, session_id, agent_name, decision_type, confidence, execution_time_ms, created_at FROM decisions ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
                rows=cur.fetchall()
                return [{"id":r[0],"session_id":r[1],"agent_name":r[2],"decision_type":r[3],"confidence":r[4],"execution_time_ms":r[5],"created_at":r[6]} for r in rows]
        else:
            with _pg() as c, c.cursor() as cur:
                cur.execute("SELECT id, session_id, agent_name, decision_type, confidence, execution_time_ms, created_at FROM decisions ORDER BY id DESC LIMIT %s OFFSET %s", (limit, offset))
                rows=cur.fetchall()
                return [{"id":r["id"],"session_id":r["session_id"],"agent_name":r["agent_name"],"decision_type":r["decision_type"],"confidence":r["confidence"],"execution_time_ms":r["execution_time_ms"],"created_at":r["created_at"].isoformat()} for r in rows]


def list_events_range(session_id: str, since: str|None=None, until: str|None=None, limit: int=100, offset: int=0):
    """以時間範圍與 offset/limit 取回事件（ISO8601字串）。"""
    init_schema()
    if USE_SQLITE:
        q = "SELECT id,event_type,event_json,created_at FROM events WHERE session_id=?"
        args=[session_id]
        if since: q += " AND created_at >= ?"; args.append(since)
        if until: q += " AND created_at <= ?"; args.append(until)
        q += " ORDER BY id DESC LIMIT ? OFFSET ?"; args += [limit, offset]
        with _sqlite() as c:
            cur=c.cursor(); cur.execute(q, args); rows=cur.fetchall()
            return [{"id":r[0],"type":r[1],"event":json.loads(r[2] or "{}"),"created_at":r[3]} for r in rows]
    else:
        with _pg() as c, c.cursor() as cur:
            q = "SELECT id, event_type, event_json, created_at FROM events WHERE session_id=%s"
            args=[session_id]
            if since: q += " AND created_at >= %s"; args.append(since)
            if until: q += " AND created_at <= %s"; args.append(until)
            q += " ORDER BY id DESC LIMIT %s OFFSET %s"; args += [limit, offset]
            cur.execute(q, args); rows=cur.fetchall()
            return [{"id":r["id"],"type":r["event_type"],"event":r["event_json"],"created_at":r["created_at"].isoformat()} for r in rows]

def list_decisions_range(since: str|None=None, until: str|None=None, limit: int=50, offset: int=0):
    
    init_schema()
    if USE_SQLITE:
        q = "SELECT id, session_id, agent_name, decision_type, confidence, execution_time_ms, created_at FROM decisions WHERE 1=1"
        args=[]
        if since: q += " AND created_at >= ?"; args.append(since)
        if until: q += " AND created_at <= ?"; args.append(until)
        q += " ORDER BY id DESC LIMIT ? OFFSET ?"; args += [limit, offset]
        with _sqlite() as c:
            cur=c.cursor(); cur.execute(q, args); rows=cur.fetchall()
            return [{"id":r[0],"session_id":r[1],"agent_name":r[2],"decision_type":r[3],"confidence":r[4],"execution_time_ms":r[5],"created_at":r[6]} for r in rows]
    else:
        with _pg() as c, c.cursor() as cur:
            q = "SELECT id, session_id, agent_name, decision_type, confidence, execution_time_ms, created_at FROM decisions WHERE 1=1"
            args=[]
            if since: q += " AND created_at >= %s"; args.append(since)
            if until: q += " AND created_at <= %s"; args.append(until)
            q += " ORDER BY id DESC LIMIT %s OFFSET %s"; args += [limit, offset]
            cur.execute(q, args); rows=cur.fetchall()
            return [{"id":r["id"],"session_id":r["session_id"],"agent_name":r["agent_name"],"decision_type":r["decision_type"],"confidence":r["confidence"],"execution_time_ms":r["execution_time_ms"],"created_at":r["created_at"].isoformat()} for r in rows]