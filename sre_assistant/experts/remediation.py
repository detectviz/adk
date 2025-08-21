
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any
from ..adk_compat.agents import LlmAgent

class RemediationExpert(LlmAgent):
    def __init__(self, model: str = "gemini-2.5-flash"):
        super().__init__(name="RemediationExpert", instruction="安全執行修復並預設 HITL。", tools=["K8sRolloutRestartTool"])

    async def remediate(self, namespace: str, deployment_name: str, require_approval: bool = True) -> Dict[str, Any]:
        return {"require_approval": require_approval, "target": f"{namespace}/{deployment_name}"}
