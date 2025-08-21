
# -*- coding: utf-8 -*-
# 整合測試（需 PostgreSQL + pgvector）：未提供 DSN 時自動跳過。
import os, pytest
from adk_runtime.main import build_registry
from sre_assistant.tools.knowledge_ingestion import knowledge_ingestion_tool
from sre_assistant.tools.rag_retrieve import rag_retrieve_vector_tool

pytestmark = pytest.mark.integration

def test_pgvector_ingest_and_retrieve(monkeypatch):
    dsn = os.getenv("PG_DSN")
    if not dsn:
        pytest.skip("PG_DSN 未設定，略過整合測試")
    monkeypatch.setenv("EMBEDDER", "st")  # 若未安裝會自動回退 hash
    r = knowledge_ingestion_tool("測試文件", "這是一段可被檢索的內容，用於驗證向量檢索是否生效。", tags=["test"], status="approved")
    assert r["ok"]
    res = rag_retrieve_vector_tool("檢索 向量 生效")
    assert res.get("hits") is not None
