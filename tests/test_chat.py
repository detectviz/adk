
# -*- coding: utf-8 -*-
import asyncio
from sre_assistant.core.assistant import SREAssistant
from adk_runtime.main import build_registry

def test_chat_diagnostic():
    registry = build_registry()
    a = SREAssistant(registry)
    res = asyncio.run(a.chat("diagnose cpu high"))
    assert res["intent"]["type"] == "diagnostic"
    assert res["actions_taken"]
    assert "PromQLQueryTool" in res["metrics"]["tools_available"]
