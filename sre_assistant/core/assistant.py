
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any, List
import time
from .intents import Intent, Step, StepResult
from .router import simple_intent_classifier
from .policy import SRESecurityPolicy
from .memory import StateStore
from ..adk_compat.registry import ToolRegistry
from ..experts.diagnostic import DiagnosticExpert
from ..experts.remediation import RemediationExpert
from ..experts.postmortem import PostmortemExpert
from ..experts.provisioning import ProvisioningExpert

class SREAssistant:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.policy = SRESecurityPolicy()
        self.state = StateStore()
        self.experts = {
            "diagnostic": DiagnosticExpert(),
            "remediation": RemediationExpert(),
            "postmortem": PostmortemExpert(),
            "provisioning": ProvisioningExpert(),
        }

    def classify(self, text: str) -> Intent:
        return simple_intent_classifier(text)

    def plan(self, intent: Intent) -> List[Step]:
        if intent.type == "remediation":
            return [Step(tool="K8sRolloutRestartTool", args={"namespace": "staging", "deployment_name": "orders-api", "reason": "auto"}, require_approval=True)]
        if intent.type == "provisioning":
            return [Step(tool="GrafanaDashboardTool", args={"service_type": "webapi"})]
        if intent.type == "diagnostic":
            return [Step(tool="PromQLQueryTool", args={"query":"up","range":"5m"})]
        return []

    async def execute(self, steps: List[Step]) -> List[StepResult]:
        results: List[StepResult] = []
        for s in steps:
            allowed, reason, risk = self.policy.evaluate_tool_call(s.tool, s.args)
            if not allowed or risk in ("High","Critical"):
                results.append(StepResult(ok=False, data={"reason": reason, "risk": risk}, error_code="E_POLICY", latency_ms=0))
                continue
            t0 = time.time()
            try:
                data = self.registry.invoke(s.tool, **s.args)
                dt = int((time.time()-t0)*1000)
                results.append(StepResult(ok=True, data=data, error_code=None, latency_ms=dt))
            except Exception as e:
                dt = int((time.time()-t0)*1000)
                results.append(StepResult(ok=False, data={"exception": str(e)}, error_code="E_TOOL", latency_ms=dt))
        return results

    async def chat(self, message: str) -> Dict[str, Any]:
        intent = self.classify(message)
        steps = self.plan(intent)
        results = await self.execute(steps)
        return {
            "intent": intent.model_dump(),
            "actions_taken": [r.model_dump() for r in results],
            "response": f"為 {intent.type} 規劃 {len(steps)} 個步驟",
            "metrics": {"steps": len(steps), "tools_available": list(self.registry.list_tools().keys())}
        }
