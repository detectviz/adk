
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any
from ..adk_compat.agents import LlmAgent

class DiagnosticExpert(LlmAgent):
    def __init__(self, model: str = "gemini-2.5-flash"):
        super().__init__(name="DiagnosticExpert", instruction="使用指標與 Runbook 進行故障初診。", tools=["PromQLQueryTool", "RunbookLookupTool"])

    async def diagnose(self, message: str) -> Dict[str, Any]:
        return {"note": f"Diagnosis plan for: {message}"}
