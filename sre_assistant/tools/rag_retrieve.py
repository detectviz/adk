
# -*- coding: utf-8 -*-
# RAG 檢索工具：pgvector 近鄰查詢 → 引用與信心分數
from __future__ import annotations
from typing import Dict, Any, List
from ..tools.knowledge_ingestion import _embed_texts
from ..core.vectorstore_pg import search_similar

def rag_search(query: str, top_k: int = 6) -> Dict[str, Any]:
    q_emb = _embed_texts([query])[0]
    rows = search_similar(q_emb, top_k=top_k)
    citations=[
        {"doc_id": str(r["doc_id"]), "text": r["content"], "confidence": float(r["score"]), "metadata": r.get("metadata", {})}
        for r in rows
    ]
    return {"query": query, "citations": citations}
