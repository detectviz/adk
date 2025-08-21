
# -*- coding: utf-8 -*-
# 向量檢索工具：pgvector 優先，無 PG 則 FTS
from __future__ import annotations
from typing import Dict, Any, List
import os
from ..core.embeddings import get_embedder
from ..core.vectorstore_pg import PgVectorStore
from ..core.rag import rag_retrieve_tool as fts_retrieve

def rag_retrieve_vector_tool(query: str, top_k: int = 5, status_filter: List[str] | None = None) -> Dict[str, Any]:
    dsn = os.getenv("PG_DSN")
    if not dsn:
        return fts_retrieve(query, top_k=top_k, status_filter=status_filter)
    emb = get_embedder()
    qvec = emb.embed_texts([query])[0]
    vs = PgVectorStore(dsn=dsn, dim=len(qvec))
    items = vs.search(qvec, top_k=top_k, status=status_filter)
    return {"query": query, "hits": items, "backend": "pgvector"}
