
# -*- coding: utf-8 -*-
# pgvector RAG 煙霧測試（需要 PG_DSN 與 pgvector）
import os, pytest
from sre_assistant.tools.knowledge_ingestion import ingest_text
from sre_assistant.tools.rag_retrieve import rag_search

pytestmark = pytest.mark.skipif(not os.getenv("PG_DSN"), reason="未設定 PG_DSN")

def test_rag_ingest_and_search():
    ingest_text("doc-1", "Kubernetes 是容器編排系統。", {"lang":"zh"})
    res = rag_search("什麼是 Kubernetes？", top_k=3)
    assert "hits" in res
