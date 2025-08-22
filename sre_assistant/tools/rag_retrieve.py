
# -*- coding: utf-8 -*-
# RAG 檢索工具：以向量近鄰搜尋回傳前 K 筆
from __future__ import annotations
from typing import Dict, Any, List
from sentence_transformers import SentenceTransformer
from ..rag.vectorstore_pg import search_similar

_model = None
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model

def rag_search(question: str, top_k: int = 5) -> Dict[str,Any]:
    emb = get_model().encode(question).tolist()
    return {"hits": search_similar(emb, top_k=top_k)}
