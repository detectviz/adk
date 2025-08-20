
# -*- coding: utf-8 -*-
# 測試 ToolRunner 的允許清單與錯誤處理（繁體中文註解）。
import os, pytest
from agents.sre_assistant.runtime.tool_runner import ToolRunner
from contracts.messages.sre_messages import ToolRequest

def test_deny_unknown_tool(monkeypatch):
    runner = ToolRunner(allowed={"prom.query"})  # 僅允許 prom.query
    with pytest.raises(ValueError) as ei:
        runner.invoke("loki.query_range", ToolRequest(name="loki.query_range"))
    assert "工具未允許" in str(ei.value)
