
# -*- coding: utf-8 -*-
# pgvector 最小向量儲存（需 PG + pgvector 擴充）；支援 upsert、相似度查詢
from __future__ import annotations
from typing import List, Dict, Any, Tuple
import os, json
from ..core.persistence import PG_DSN, psycopg

def init_pgvector_schema():
    if not psycopg: raise RuntimeError("需要 psycopg 套件")
    if not PG_DSN: raise RuntimeError("未設定 PG_DSN")
    with psycopg.connect(PG_DSN) as conn, conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
CREATE TABLE IF NOT EXISTS rag_docs(
  id BIGSERIAL PRIMARY KEY,
  doc_id TEXT UNIQUE,
  text TEXT NOT NULL,
  metadata JSONB,
  embedding vector(768)
);
"""
)
        conn.commit()

def upsert_document(doc_id: str, text: str, embedding: List[float], metadata: Dict[str,Any]|None=None):
    init_pgvector_schema()
    with psycopg.connect(PG_DSN) as conn, conn.cursor() as cur:
        cur.execute("""INSERT INTO rag_docs(doc_id,text,metadata,embedding)
VALUES(%s,%s,%s,%s)
ON CONFLICT (doc_id) DO UPDATE SET text=EXCLUDED.text, metadata=EXCLUDED.metadata, embedding=EXCLUDED.embedding;""",
            (doc_id, text, json.dumps(metadata or {}, ensure_ascii=False), embedding)
        )
        conn.commit()

def search_similar(query_embedding: List[float], top_k: int=5) -> List[Dict[str,Any]]:
    init_pgvector_schema()
    with psycopg.connect(PG_DSN) as conn, conn.cursor() as cur:
        cur.execute("""SELECT doc_id, text, metadata, 1 - (embedding <#> %s) AS score FROM rag_docs ORDER BY embedding <#> %s ASC LIMIT %s;""",
                    (query_embedding, query_embedding, top_k))
        rows=cur.fetchall()
        return [{"doc_id":r[0],"text":r[1],"metadata":r[2],"score":float(r[3])} for r in rows]
