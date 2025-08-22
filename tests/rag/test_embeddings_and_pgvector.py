
# -*- coding: utf-8 -*-
# 測試：嵌入維度檢查與 pgvector upsert 呼叫行為（以假連線模擬）
import types
from sre_assistant.rag.embeddings import get_embedding, ensure_dimension

def test_embedding_dimension_pad_trunc():
    v = [1.0,2.0,3.0]
    assert len(ensure_dimension(v, 2)) == 2
    assert len(ensure_dimension(v, 5)) == 5

def test_get_embedding_fallback():
    # 在無 Vertex SDK/憑證時應回退 hash，確保可用
    vec = get_embedding("hello", dim=8)
    assert isinstance(vec, list) and len(vec) >= 1

def test_ingest_to_pg_calls_upsert(monkeypatch):
    from sre_assistant.tools import knowledge_ingestion as ki
    called = {}
    def fake_upsert(conn, sid, ver, content, emb):
        called['ok']= (sid, ver, content, emb)
    monkeypatch.setattr(ki, "_upsert_document_pg", fake_upsert, raising=False)
    class C: 
        def cursor(self): 
            return types.SimpleNamespace(execute=lambda *a, **k: None)
    ki.ingest_to_pg(C(), "src", 1, "text", dim=8)
    assert 'ok' in called
