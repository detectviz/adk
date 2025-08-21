
# -*- coding: utf-8 -*-
# 協調器：意圖分類→規劃→政策門關→HITL→執行→知識回寫→持久化→可觀測。
from __future__ import annotations
from typing import Dict, Any, List
import time, json, uuid
from .intents import Intent, Step, StepResult
from .router import simple_intent_classifier
from .policy import SRESecurityPolicy
from .memory import StateStore
from .cache import TTLCache
from .persistence import DB
from .observability import REQUEST_TOTAL, REQUEST_LATENCY, log_event
from .planner import BuiltInPlanner
from ..adk_compat.registry import ToolRegistry
from ..adk_compat.executor import ToolExecutor
from .hitl import APPROVALS
from ..experts.diagnostic import DiagnosticExpert
from ..experts.remediation import RemediationExpert
from ..experts.postmortem import PostmortemExpert
from ..experts.provisioning import ProvisioningExpert
from ..experts.feedback import FeedbackAgent

class SREAssistant:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.executor = ToolExecutor(registry)
        self.policy = SRESecurityPolicy()
        self.state = StateStore()
        self.cache = TTLCache(ttl_seconds=20)
        self.planner = BuiltInPlanner()
        self.feedback = FeedbackAgent(author="SREAssistant")
        self.experts = {
            "diagnostic": DiagnosticExpert(),
            "remediation": RemediationExpert(),
            "postmortem": PostmortemExpert(),
            "provisioning": ProvisioningExpert(),
        }

    def classify(self, text: str) -> Intent:
        return simple_intent_classifier(text)

    def plan(self, intent: Intent) -> List[Step]:
        return self.planner.plan(intent)

    async def execute(self, session_id: str, steps: List[Step]) -> List[StepResult]:
        results: List[StepResult] = []
        for s in steps:
            allowed, reason, risk = self.policy.evaluate_tool_call(s.tool, s.args)
            if not allowed or risk in ("High","Critical"):
                results.append(StepResult(ok=False, data={"reason": reason, "risk": risk}, error_code="E_POLICY", latency_ms=0))
                continue

            if s.require_approval:
                a = APPROVALS.create(tool=s.tool, args=s.args)
                results.append(StepResult(ok=False, data={"approval_id": a.id, "status": "pending"}, error_code="E_REQUIRE_APPROVAL", latency_ms=0))
                continue

            cached = self.cache.get(s.tool, s.args)
            if cached is not None:
                results.append(StepResult(ok=True, data=cached, error_code=None, latency_ms=1))
                continue

            entry = self.registry.require(s.tool)
            spec = entry["spec"]
            t0 = time.time()
            try:
                data = self.executor.invoke(s.tool, spec, **s.args)
                dt = int((time.time()-t0)*1000)
                results.append(StepResult(ok=True, data=data, error_code=None, latency_ms=dt))
                self.cache.set(s.tool, s.args, data)
                DB.insert_tool_execution(None, s.tool, json.dumps(s.args, ensure_ascii=False), json.dumps(data, ensure_ascii=False), "ok", None, dt)
            except Exception as e:
                dt = int((time.time()-t0)*1000)
                results.append(StepResult(ok=False, data={"exception": str(e)}, error_code="E_TOOL", latency_ms=dt))
                DB.insert_tool_execution(None, s.tool, json.dumps(s.args, ensure_ascii=False), json.dumps({"exception": str(e)}, ensure_ascii=False), "error", str(e), dt)
        return results

    async def execute_approval(self, approval_id: int) -> Dict[str, Any]:
        a = APPROVALS.get(approval_id)
        if not a:
            return {"ok": False, "error": "not_found"}
        if a.status != "approved":
            return {"ok": False, "error": f"status={a.status}"}
        allowed, reason, risk = self.policy.evaluate_tool_call(a.tool, a.args)
        if not allowed or risk in ("High","Critical"):
            return {"ok": False, "error": "policy_denied", "reason": reason, "risk": risk}
        entry = self.registry.require(a.tool)
        spec = entry["spec"]
        t0 = time.time()
        try:
            data = self.executor.invoke(a.tool, spec, **a.args)
            dt = int((time.time()-t0)*1000)
            DB.insert_tool_execution(None, a.tool, json.dumps(a.args, ensure_ascii=False), json.dumps(data, ensure_ascii=False), "ok", None, dt)
            return {"ok": True, "data": data, "latency_ms": dt}
        except Exception as e:
            dt = int((time.time()-t0)*1000)
            DB.insert_tool_execution(None, a.tool, json.dumps(a.args, ensure_ascii=False), json.dumps({"exception": str(e)}, ensure_ascii=False), "error", str(e), dt)
            return {"ok": False, "error": "exec_failed", "message": str(e), "latency_ms": dt}

    async def chat(self, message: str) -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        REQUEST_TOTAL.labels(agent="SREAssistant", status="start").inc()
        with REQUEST_LATENCY.labels(agent="SREAssistant").time():
            intent = self.classify(message)
            steps = self.plan(intent)
            t0 = time.time()
            results = await self.execute(session_id, steps)
            dt = int((time.time()-t0)*1000)

            # 知識回寫：若為診斷且工具成功，萃取簡要步驟成 runbook 草稿
            if intent.type == "diagnostic":
                ok_steps = [r for r in results if r.ok]
                if ok_steps:
                    self.feedback.capture_runbook(
                        title=f"初診流程-{time.strftime('%Y%m%d-%H%M%S')}",
                        steps=[f"{s.tool}({s.args})" for s in steps],
                        tags=["diagnostic","auto"]
                    )

            DB.insert_decision(session_id, "SREAssistant", intent.type, json.dumps([s.model_dump() for s in steps], ensure_ascii=False), json.dumps([r.model_dump() for r in results], ensure_ascii=False), intent.confidence, dt)
            REQUEST_TOTAL.labels(agent="SREAssistant", status="ok").inc()
            log_event("assistant.chat", {"intent": intent.type, "duration_ms": dt})
            return {
                "intent": intent.model_dump(),
                "actions_taken": [r.model_dump() for r in results],
                "response": f"為 {intent.type} 規劃 {len(steps)} 個步驟",
                "metrics": {"steps": len(steps), "duration_ms": dt, "tools_available": list(self.registry.list_tools().keys())}
            }
