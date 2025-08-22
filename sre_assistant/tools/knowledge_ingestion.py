
# -*- coding: utf-8 -*-
# 知識匯入工具：將文字以嵌入後寫入 pgvector
from __future__ import annotations
from typing import Dict, Any
from sentence_transformers import SentenceTransformer
from ..rag.vectorstore_pg import upsert_document

_model = None
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # 正式嵌入模型
    return _model

def ingest_text(doc_id: str, text: str, metadata: Dict[str,Any]|None=None) -> Dict[str,Any]:
    emb = get_model().encode(text).tolist()
    upsert_document(doc_id, text, emb, metadata or {})
    return {"ok": True, "doc_id": doc_id}
