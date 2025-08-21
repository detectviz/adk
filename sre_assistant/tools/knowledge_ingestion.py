
# -*- coding: utf-8 -*-
# 知識匯入工具：支援 pgvector 與正式嵌入器
from __future__ import annotations
from typing import Dict, Any, List
import os, textwrap
from ..core.embeddings import get_embedder
from ..core.vectorstore_pg import PgVectorStore
from ..core.rag import rag_create_entry

def _chunk(text: str, size: int = 600) -> List[str]:
    # 簡化切片：固定寬度
    return textwrap.wrap(text, width=size)

def knowledge_ingestion_tool(title: str, content: str, tags: list[str] | None = None, status: str = "draft") -> Dict[str, Any]:
    entry = rag_create_entry(title, content, author="ingestion-tool", tags=tags or [], status=status)
    dsn = os.getenv("PG_DSN")
    chunks = _chunk(content)
    if dsn and chunks:
        emb = get_embedder()
        vecs = emb.embed_texts(chunks)
        vs = PgVectorStore(dsn=dsn, dim=len(vecs[0]))
        vs.upsert(entry["id"], chunks, vecs, tags or [], status)
        return {"ok": True, "entry_id": entry["id"], "chunks": len(chunks), "vectorized": True, "backend": "pgvector"}
    return {"ok": True, "entry_id": entry["id"], "chunks": len(chunks), "vectorized": False, "backend": "fts"}
