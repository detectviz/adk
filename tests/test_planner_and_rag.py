
import asyncio
from sre_assistant.core.assistant import SREAssistant
from adk_runtime.main import build_registry
from sre_assistant.core.rag import rag_create_entry, rag_retrieve_tool, rag_update_status

def test_planner_sequence():
    """
    2025-08-22 03:37:34Z
    函式用途：`test_planner_sequence` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    a = SREAssistant(build_registry())
    # 應至少兩步（PromQL + Runbook）
    res = asyncio.run(a.chat("diagnose anything"))
    assert res["metrics"]["steps"] >= 2

def test_rag_versioning():
    """
    2025-08-22 03:37:34Z
    函式用途：`test_rag_versioning` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    e = rag_create_entry("test", "hello kafka lag", author="tester", tags=["kafka"], status="draft")
    out = rag_retrieve_tool("kafka")
    assert out["snippets"]
    rag_update_status(e["id"], "approved")
    out2 = rag_retrieve_tool("kafka", status_filter=["approved"])
    assert out2["snippets"]