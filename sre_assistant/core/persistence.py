
# -*- coding: utf-8 -*-
# 持久化：SQLite 實作 decisions/tool_executions/approvals 三張表，並提供更新介面。
from __future__ import annotations
import sqlite3, json
from typing import Any, Dict, List, Optional, Tuple
from .config import Config

class Database:
    def __init__(self):
        self.path = Config.SQLITE_PATH
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self._init_schema()

    def _init_schema(self):
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS decisions ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'session_id TEXT NOT NULL,'
            'agent_name TEXT NOT NULL,'
            'decision_type TEXT NOT NULL,'
            'input TEXT NOT NULL,'
            'output TEXT NOT NULL,'
            'confidence REAL,'
            'execution_time_ms INTEGER,'
            'created_at DATETIME DEFAULT CURRENT_TIMESTAMP'
            ');'
        )
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS tool_executions ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'decision_id INTEGER,'
            'tool_name TEXT NOT NULL,'
            'parameters TEXT,'
            'result TEXT,'
            'status TEXT NOT NULL,'
            'error_message TEXT,'
            'duration_ms INTEGER,'
            'executed_at DATETIME DEFAULT CURRENT_TIMESTAMP'
            ');'
        )
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS approvals ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'tool TEXT NOT NULL,'
            'args TEXT NOT NULL,'
            'status TEXT NOT NULL,'
            'created_at DATETIME DEFAULT CURRENT_TIMESTAMP,'
            'decided_at DATETIME,'
            'decided_by TEXT,'
            'reason TEXT'
            ');'
        )
        self.conn.commit()

    def insert_decision(self, session_id: str, agent_name: str, decision_type: str, input: str, output: str, confidence: float | None, execution_time_ms: int) -> int:
        cur = self.conn.cursor()
        cur.execute(
            'INSERT INTO decisions(session_id, agent_name, decision_type, input, output, confidence, execution_time_ms) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (session_id, agent_name, decision_type, input, output, confidence, execution_time_ms)
        )
        self.conn.commit()
        return cur.lastrowid

    def update_decision_output(self, decision_id: int, output: str, execution_time_ms: int | None = None):
        cur = self.conn.cursor()
        if execution_time_ms is None:
            cur.execute('UPDATE decisions SET output=? WHERE id=?', (output, decision_id))
        else:
            cur.execute('UPDATE decisions SET output=?, execution_time_ms=? WHERE id=?', (output, execution_time_ms, decision_id))
        self.conn.commit()

    def insert_tool_execution(self, decision_id: int | None, tool_name: str, parameters: str, result: str, status: str, error_message: str | None, duration_ms: int) -> int:
        cur = self.conn.cursor()
        cur.execute(
            'INSERT INTO tool_executions(decision_id, tool_name, parameters, result, status, error_message, duration_ms) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (decision_id, tool_name, parameters, result, status, error_message, duration_ms)
        )
        self.conn.commit()
        return cur.lastrowid

    def insert_approval(self, tool: str, args: Dict[str, Any]) -> int:
        cur = self.conn.cursor()
        cur.execute('INSERT INTO approvals(tool, args, status) VALUES (?, ?, "pending")', (tool, json.dumps(args, ensure_ascii=False)))
        self.conn.commit()
        return cur.lastrowid

    def get_approval(self, aid: int) -> Optional[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute('SELECT id, tool, args, status, created_at, decided_at, decided_by, reason FROM approvals WHERE id=?', (aid,))
        r = cur.fetchone()
        if not r: return None
        return {"id": r[0], "tool": r[1], "args": json.loads(r[2]), "status": r[3], "created_at": r[4], "decided_at": r[5], "decided_by": r[6], "reason": r[7]}

    def decide_approval(self, aid: int, status: str, decided_by: str, reason: str | None) -> Optional[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute('UPDATE approvals SET status=?, decided_at=CURRENT_TIMESTAMP, decided_by=?, reason=? WHERE id=?', (status, decided_by, reason, aid))
        self.conn.commit()
        return self.get_approval(aid)

    def list_decisions(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(
            'SELECT id, session_id, agent_name, decision_type, input, output, confidence, execution_time_ms, created_at '
            'FROM decisions ORDER BY id DESC LIMIT ? OFFSET ?',
            (limit, offset)
        )
        rows = cur.fetchall()
        out = []
        for r in rows:
            out.append({
                "id": r[0], "session_id": r[1], "agent_name": r[2], "decision_type": r[3],
                "input": r[4], "output": r[5], "confidence": r[6], "execution_time_ms": r[7], "created_at": r[8]
            })
        return out

    def list_tool_execs(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(
            'SELECT id, decision_id, tool_name, parameters, result, status, error_message, duration_ms, executed_at '
            'FROM tool_executions ORDER BY id DESC LIMIT ? OFFSET ?',
            (limit, offset)
        )
        rows = cur.fetchall()
        res = []
        for r in rows:
            res.append({
                "id": r[0], "decision_id": r[1], "tool_name": r[2], "parameters": r[3],
                "result": r[4], "status": r[5], "error_message": r[6], "duration_ms": r[7], "executed_at": r[8]
            })
        return res

DB = Database()
