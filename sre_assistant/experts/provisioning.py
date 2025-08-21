
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any
from ..adk_compat.agents import LlmAgent

class ProvisioningExpert(LlmAgent):
    def __init__(self, model: str = "gemini-2.5-flash"):
        super().__init__(name="ProvisioningExpert", instruction="為新服務產生監控儀表板與告警。", tools=["GrafanaDashboardTool"])

    async def onboard(self, service_type: str) -> Dict[str, Any]:
        return {"service_type": service_type}
