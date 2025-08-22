
# PostgreSQL DB 實作（pg + pgvector 已於其他檔案使用）：此處提供 decisions/tool_executions/approvals/api_keys 對等欄位。
from __future__ import annotations
from typing import Any, Dict, List, Optional
import os
try:
    import psycopg
except Exception:
    psycopg = None

class PgDatabase:
    def __init__(self, dsn: str):
        
        if psycopg is None:
            raise RuntimeError("未安裝 psycopg，無法使用 PostgreSQL")
        self.conn = psycopg.connect(dsn, autocommit=True)
        self._init_schema()

    def _init_schema(self):
        
        with self.conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS decisions(
              id BIGSERIAL PRIMARY KEY,
              session_id TEXT NOT NULL,
              agent_name TEXT NOT NULL,
              decision_type TEXT NOT NULL,
              input JSONB NOT NULL,
              output JSONB NOT NULL,
              confidence REAL,
              execution_time_ms INT,
              trace_id TEXT,
              span_id TEXT,
              created_at TIMESTAMPTZ DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS tool_executions(
              id BIGSERIAL PRIMARY KEY,
              decision_id BIGINT,
              tool_name TEXT NOT NULL,
              parameters JSONB,
              result JSONB,
              status TEXT NOT NULL,
              error_message TEXT,
              duration_ms INT,
              trace_id TEXT,
              span_id TEXT,
              executed_at TIMESTAMPTZ DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS approvals(
              id BIGSERIAL PRIMARY KEY,
              tool TEXT NOT NULL,
              args JSONB NOT NULL,
              status TEXT NOT NULL,
              created_at TIMESTAMPTZ DEFAULT NOW(),
              decided_at TIMESTAMPTZ,
              decided_by TEXT,
              reason TEXT
            );
            CREATE TABLE IF NOT EXISTS api_keys(
              id BIGSERIAL PRIMARY KEY,
              key_hash TEXT NOT NULL UNIQUE,
              role TEXT NOT NULL,
              created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """)

    # 其餘方法與 SQLite 版本等價，為簡潔此處省略，實務請補齊 CRUD 與查詢。