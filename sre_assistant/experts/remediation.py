
# -*- coding: utf-8 -*-
# 修復專家代理（最小 ADK 化實作）：用於 AgentTool 掛載
from __future__ import annotations
import os
try:
    from google.adk.agents import LlmAgent
except Exception:
    LlmAgent = None

def build_remediation_agent(model: str) -> "LlmAgent":
    if LlmAgent is None:
        raise RuntimeError("缺少 google-adk 套件，無法建立 RemediationExpert")
    instruction = "你是 SRE 修復專家，在風險可控前提下提出修復方案，必要時要求 HITL 核可後再執行。"
    return LlmAgent(name="RemediationExpert", model=model, instruction=instruction, tools=[])
