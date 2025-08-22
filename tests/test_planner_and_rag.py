
import asyncio
from sre_assistant.core.assistant import SREAssistant
from adk_runtime.main import build_registry
from sre_assistant.core.rag import rag_create_entry, rag_retrieve_tool, rag_update_status

def test_planner_sequence():
    
    a = SREAssistant(build_registry())
    # 應至少兩步（PromQL + Runbook）
    res = asyncio.run(a.chat("diagnose anything"))
    assert res["metrics"]["steps"] >= 2

def test_rag_versioning():
    
    e = rag_create_entry("test", "hello kafka lag", author="tester", tags=["kafka"], status="draft")
    out = rag_retrieve_tool("kafka")
    assert out["snippets"]
    rag_update_status(e["id"], "approved")
    out2 = rag_retrieve_tool("kafka", status_filter=["approved"])
    assert out2["snippets"]