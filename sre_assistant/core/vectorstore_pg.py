
# -*- coding: utf-8 -*-
# pgvector 向量庫：以文字向量常值 '[1,2,3]'::vector 寫入與查詢，降低驅動適配風險。
from __future__ import annotations
from typing import List, Dict, Any, Optional
import os

try:
    import psycopg
except Exception:
    psycopg = None

def _vec_literal(vec: List[float]) -> str:
    # 產生 pgvector 的文字常值，例如 '[0.1, -0.2, ...]'
    return "[" + ",".join(f"{float(x):.6f}" for x in vec) + "]"

class PgVectorStore:
    def __init__(self, dsn: str, dim: int = 384):
        if psycopg is None:
            raise RuntimeError("未安裝 psycopg，無法使用 pgvector")
        self.dim = dim
        self.conn = psycopg.connect(dsn, autocommit=True)
        self._init_schema()

    def _init_schema(self):
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS rag_chunks (
              id BIGSERIAL PRIMARY KEY,
              doc_id BIGINT,
              content TEXT NOT NULL,
              embedding vector({self.dim}),
              tags TEXT,
              status TEXT,
              created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """)

    def upsert(self, doc_id: int, chunks: List[str], embeddings: List[List[float]], tags: List[str], status: str):
        with self.conn.cursor() as cur:
            for c, e in zip(chunks, embeddings):
                lit = _vec_literal(e)
                cur.execute(
                    "INSERT INTO rag_chunks(doc_id, content, embedding, tags, status) VALUES (%s,%s," + lit + "::vector,%s,%s)",
                    (doc_id, c, ",".join(tags), status)
                )

    def search(self, query_vec: List[float], top_k: int = 5, status: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        lit = _vec_literal(query_vec)
        cond = ""
        args: list[Any] = [top_k]
        if status:
            cond = "WHERE status = ANY(%s)"
            args = [status, top_k]
        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT id, doc_id, content, tags, status, embedding <#> {lit}::vector AS distance FROM rag_chunks {cond} ORDER BY embedding <#> {lit}::vector LIMIT %s",
                args
            )
            rows = cur.fetchall()
        res = []
        for r in rows:
            res.append({"id": r[0], "doc_id": r[1], "content": r[2], "tags": (r[3] or '').split(','), "status": r[4], "distance": float(r[5])})
        return res
