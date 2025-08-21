
# -*- coding: utf-8 -*-
# 整合測試：需設定 PG_DSN 才執行，否則自動跳過。
import os, pytest
from sre_assistant.core.vectorstore_pg import PgVectorStore
from sre_assistant.core.embeddings import Embedder

pg_dsn = os.getenv("PG_DSN", None)
pytestmark = pytest.mark.skipif(not pg_dsn, reason="PG_DSN 未設定，跳過 pgvector 整合測試")

def test_pgvector_roundtrip():
    vs = PgVectorStore(dsn=pg_dsn, dim=384)
    text = "可觀測性是可靠性的基石"
    emb = Embedder().embed_texts([text])[0]
    vs.upsert(doc_id=123, chunks=[text], embeddings=[emb], tags=["test"], status="approved")
    hits = vs.search(emb, top_k=1)
    assert hits and hits[0]["doc_id"] == 123
