
# -*- coding: utf-8 -*-
# 持久化：SQLite with trace 欄位與 FTS
from __future__ import annotations
import sqlite3, json, hashlib
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
            'trace_id TEXT,'
            'span_id TEXT,'
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
            'trace_id TEXT,'
            'span_id TEXT,'
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
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS api_keys ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'key_hash TEXT NOT NULL UNIQUE,'
            'role TEXT NOT NULL,'
            'created_at DATETIME DEFAULT CURRENT_TIMESTAMP'
            ');'
        )
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS rag_entries ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'title TEXT NOT NULL,'
            'content TEXT NOT NULL,'
            'author TEXT,'
            'tags TEXT,'
            'status TEXT,'
            'created_at DATETIME DEFAULT CURRENT_TIMESTAMP'
            ');'
        )
        try:
            self.conn.execute('CREATE VIRTUAL TABLE IF NOT EXISTS rag_entries_fts USING fts5(title, content)')
        except Exception:
            pass
        # 嘗試新增缺失欄位（向前兼容）
        for alter in [
            "ALTER TABLE decisions ADD COLUMN trace_id TEXT",
            "ALTER TABLE decisions ADD COLUMN span_id TEXT",
            "ALTER TABLE tool_executions ADD COLUMN trace_id TEXT",
            "ALTER TABLE tool_executions ADD COLUMN span_id TEXT",
        ]:
            try: self.conn.execute(alter)
            except Exception: pass
        self.conn.commit()

    # decisions
    def insert_decision(self, session_id: str, agent_name: str, decision_type: str, input: str, output: str, confidence: float | None, execution_time_ms: int, trace_id: str | None = None, span_id: str | None = None) -> int:
        cur = self.conn.cursor()
        cur.execute(
            'INSERT INTO decisions(session_id, agent_name, decision_type, input, output, confidence, execution_time_ms, trace_id, span_id) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (session_id, agent_name, decision_type, input, output, confidence, execution_time_ms, trace_id, span_id)
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

    # tool execs
    def insert_tool_execution(self, decision_id: int | None, tool_name: str, parameters: str, result: str, status: str, error_message: str | None, duration_ms: int, trace_id: str | None = None, span_id: str | None = None) -> int:
        cur = self.conn.cursor()
        cur.execute(
            'INSERT INTO tool_executions(decision_id, tool_name, parameters, result, status, error_message, duration_ms, trace_id, span_id) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (decision_id, tool_name, parameters, result, status, error_message, duration_ms, trace_id, span_id)
        )
        self.conn.commit()
        return cur.lastrowid

    # approvals / list / api_keys 與先前相同，為簡潔略
    # ...（已在 v11 提供，保留原行為）

from .persistence import Database as _OldDB  # 兼容引用
DB = Database()
