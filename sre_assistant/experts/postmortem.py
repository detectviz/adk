
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any, List
from ..adk_compat.agents import LlmAgent

class PostmortemExpert(LlmAgent):
    def __init__(self, model: str = "gemini-2.5-flash"):
        super().__init__(name="PostmortemExpert", instruction="生成事故時間線與 RCA 假設。", tools=[])

    async def summarize(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {"timeline_items": len(events), "summary": "Postmortem summary (mock).", "actions": ["調整告警門檻", "補強 Runbook"]}
