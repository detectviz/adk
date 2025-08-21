
# -*- coding: utf-8 -*-
# HITL 流程測試：K8s 工具 require_approval=true → 產生審批 → 核准後執行。
import asyncio
from sre_assistant.core.assistant import SREAssistant
from adk_runtime.main import build_registry
from sre_assistant.core.hitl import APPROVALS

def test_hitl_restart_flow():
    a = SREAssistant(build_registry())
    res = asyncio.run(a.chat("please restart service"))
    pend = [s for s in res["actions_taken"] if s.get("error_code")=="E_REQUIRE_APPROVAL"]
    assert pend, "應產生審批步驟"
    aid = pend[0]["data"]["approval_id"]
    APPROVALS.decide(aid, status="approved", decided_by="test", reason="ok")
    res2 = asyncio.run(a.execute_approval(aid))
    assert res2.get("ok"), "審批後應可執行"
