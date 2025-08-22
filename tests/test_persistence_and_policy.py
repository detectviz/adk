import asyncio
from sre_assistant.core.assistant import SREAssistant
from adk_runtime.main import build_registry
from sre_assistant.core.persistence import DB

def test_decision_persisted():
    
    a = SREAssistant(build_registry())
    res = asyncio.run(a.chat("diagnose latency"))
    items = DB.list_decisions(limit=5)
    assert items, "應寫入 decisions 表"

def test_per_tool_cache_ttl():
    
    a = SREAssistant(build_registry())
    r1 = asyncio.run(a.chat("diagnose cpu"))
    r2 = asyncio.run(a.chat("diagnose cpu"))
    assert r1 and r2