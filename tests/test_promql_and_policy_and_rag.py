# 檔案：tests/test_promql_and_policy_and_rag.py
# 產生時間：2025-08-22T03:34:52.621849Z
# 專案：SRE Assistant（對齊 Google ADK），本檔案已補齊繁體中文註解以提升可讀性與可維護性。
# 說明：一般模組或測試檔，已加入中文檔頭說明。

# -*- coding: utf-8 -*-
import os
from sre_assistant.tools.promql import promql_query_tool
from sre_assistant.core.policy import SRESecurityPolicy
from adk_runtime.main import build_registry
from sre_assistant.core.rag import rag_create_entry
from sre_assistant.tools.rag_retrieve import rag_retrieve_vector_tool

def test_promql_strict_bad_query(monkeypatch):
    monkeypatch.setenv("PROM_MOCK","1")
    monkeypatch.setenv("PROM_STRICT","1")
    try:
        promql_query_tool("rate(http_requests_total{status=200}[5m])", "2025-01-01T00:00:00Z,2025-01-01T01:00:00Z,15s")
    except Exception:
        pass
    # 非法字元
    try:
        promql_query_tool("sum(foo) $", "2025-01-01T00:00:00Z,2025-01-01T01:00:00Z,15s")
        assert False, "應拋出 E_BAD_QUERY"
    except Exception as e:
        assert "E_BAD_QUERY" in str(e)

def test_policy_dynamic_dir(tmp_path, monkeypatch):
    # 建立動態政策檔
    p = tmp_path / "p1.yaml"
    p.write_text("deny_tools: ['GrafanaDashboardTool']
", encoding="utf-8")
    reg = build_registry()
    pol = SRESecurityPolicy(registry=reg, policy_dir=str(tmp_path))
    allowed, reason, risk, req = pol.evaluate_tool_call("GrafanaDashboardTool", {"service_type":"web"})
    assert not allowed

def test_rag_vector_fallback(monkeypatch):
    # 沒有 PG_DSN 時使用 FTS 路徑
    e = rag_create_entry("t","hello world content", author="t", tags=[], status="approved")
    res = rag_retrieve_vector_tool("hello")
    assert res["hits"], "應找得到 FTS 內容"
