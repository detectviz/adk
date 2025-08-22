# -*- coding: utf-8 -*-
# 注意：此檔為「非 ADK 模式」的備援協調器，預設不在生產中使用。
# 正式協調器實作請參考：sre_assistant/adk_app/coordinator.py（LoopAgent + BuiltInPlanner）


# -*- coding: utf-8 -*-
# 協調器：建立決策→執行步驟→關聯工具記錄→更新決策輸出。
from __future__ import annotations
from typing import Dict, Any, List
import time, json, uuid
from .intents import Intent, Step, StepResult, SCHEMA_VERSION
from .router import simple_intent_classifier
from .policy import SRESecurityPolicy
from .memory import StateStore
from .cache import TTLCache
from .persistence import DB
from .observability import REQUEST_TOTAL, REQUEST_LATENCY, log_event
from .planner import BuiltInPlanner
from ..adk_compat.registry import ToolRegistry
from ..adk_compat.executor import ToolExecutor, ExecutionError
from .hitl import APPROVALS
from ..experts.diagnostic import DiagnosticExpert
from ..experts.remediation import RemediationExpert
from ..experts.postmortem import PostmortemExpert
from ..experts.provisioning import ProvisioningExpert
from ..experts.feedback import FeedbackAgent
from .config import Config

class SREAssistant:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.executor = ToolExecutor(registry)
        self.policy = SRESecurityPolicy(registry=registry)
        self.state = StateStore()
        self.cache = TTLCache(default_ttl_seconds=Config.CACHE_TTL_DEFAULT)
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

    async def _execute_steps(self, decision_id: int, steps: List[Step]) -> List[StepResult]:
        results: List[StepResult] = []
        for s in steps:
            allowed, reason, risk, req_from_spec = self.policy.evaluate_tool_call(s.tool, s.args)
            if not allowed or risk in ("High","Critical"):
                r = StepResult(schema_version=SCHEMA_VERSION, ok=False, data={"reason": reason, "risk": risk}, error_code="E_POLICY", latency_ms=0)
                results.append(r)
                continue

            require_approval = s.require_approval or req_from_spec
            if require_approval:
                a = APPROVALS.create(tool=s.tool, args=s.args)
                r = StepResult(schema_version=SCHEMA_VERSION, ok=False, data={"approval_id": a.id, "status": "pending"}, error_code="E_REQUIRE_APPROVAL", latency_ms=0)
                results.append(r)
                continue

            ttl = None
            try:
                spec = self.registry.require(s.tool)["spec"]
                ttl = int(spec.get("cache_ttl_seconds", 0)) or None
            except Exception:
                spec = self.registry.require(s.tool)["spec"]

            cached = self.cache.get(s.tool, s.args)
            if cached is not None:
                r = StepResult(schema_version=SCHEMA_VERSION, ok=True, data=cached, error_code=None, latency_ms=1)
                results.append(r)
                continue

            t0 = time.time()
            try:
                data = self.executor.invoke(s.tool, spec, **s.args)
                dt = int((time.time()-t0)*1000)
                r = StepResult(schema_version=SCHEMA_VERSION, ok=True, data=data, error_code=None, latency_ms=dt)
                results.append(r)
                self.cache.set(s.tool, s.args, data, ttl=ttl)
                DB.insert_tool_execution(decision_id, s.tool, json.dumps(s.args, ensure_ascii=False), json.dumps(data, ensure_ascii=False), "ok", None, dt)
            except ExecutionError as e:
                dt = int((time.time()-t0)*1000)
                r = StepResult(schema_version=SCHEMA_VERSION, ok=False, data={"exception": str(e)}, error_code=e.code, latency_ms=dt)
                results.append(r)
                DB.insert_tool_execution(decision_id, s.tool, json.dumps(s.args, ensure_ascii=False), json.dumps({"exception": str(e)}, ensure_ascii=False), "error", str(e), dt)
            except Exception as e:
                dt = int((time.time()-t0)*1000)
                r = StepResult(schema_version=SCHEMA_VERSION, ok=False, data={"exception": str(e)}, error_code="E_UNKNOWN", latency_ms=dt)
                results.append(r)
                DB.insert_tool_execution(decision_id, s.tool, json.dumps(s.args, ensure_ascii=False), json.dumps({"exception": str(e)}, ensure_ascii=False), "error", str(e), dt)
        return results

    async def execute_approval(self, approval_id: int) -> Dict[str, Any]:
        a = APPROVALS.get(approval_id)
        if not a:
            return {"ok": False, "error": "not_found"}
        if a.status != "approved":
            return {"ok": False, "error": f"status={a.status}"}
        allowed, reason, risk, _ = self.policy.evaluate_tool_call(a.tool, a.args)
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
        except ExecutionError as e:
            dt = int((time.time()-t0)*1000)
            DB.insert_tool_execution(None, a.tool, json.dumps(a.args, ensure_ascii=False), json.dumps({"exception": str(e)}, ensure_ascii=False), "error", str(e), dt)
            return {"ok": False, "error": e.code, "message": str(e), "latency_ms": dt}
        except Exception as e:
            dt = int((time.time()-t0)*1000)
            DB.insert_tool_execution(None, a.tool, json.dumps(a.args, ensure_ascii=False), json.dumps({"exception": str(e)}, ensure_ascii=False), "error", str(e), dt)
            return {"ok": False, "error": "E_UNKNOWN", "message": str(e), "latency_ms": dt}

    async def chat(self, message: str) -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        REQUEST_TOTAL.labels(agent="SREAssistant", status="start").inc()
        with REQUEST_LATENCY.labels(agent="SREAssistant").time():
            intent = self.classify(message)
            steps = self.plan(intent)

            # 先寫入一筆 decision（輸出暫時為空陣列），取得 decision_id
            decision_id = DB.insert_decision(session_id, "SREAssistant", intent.type, json.dumps([s.model_dump() for s in steps], ensure_ascii=False), "[]", intent.confidence, 0)

            t0 = time.time()
            results = await self._execute_steps(decision_id, steps)
            dt = int((time.time()-t0)*1000)

            if intent.type == "diagnostic":
                ok_steps = [r for r in results if r.ok]
                if ok_steps:
                    self.feedback.capture_runbook(
                        title=f"初診流程-{time.strftime('%Y%m%d-%H%M%S')}",
                        steps=[f"{s.tool}({s.args})" for s in steps],
                        tags=["diagnostic","auto"]
                    )

            # 更新 decision 的 output 與耗時
            DB.update_decision_output(decision_id, json.dumps([r.model_dump() for r in results], ensure_ascii=False), execution_time_ms=dt)

            REQUEST_TOTAL.labels(agent="SREAssistant", status="ok").inc()
            log_event("assistant.chat", {"intent": intent.type, "duration_ms": dt})
            return {
                "schema_version": SCHEMA_VERSION,
                "intent": intent.model_dump(),
                "actions_taken": [r.model_dump() for r in results],
                "response": f"為 {intent.type} 規劃 {len(steps)} 個步驟",
                "metrics": {"steps": len(steps), "duration_ms": dt, "decision_id": decision_id, "tools_available": list(self.registry.list_tools().keys())}
            }
