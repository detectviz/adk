
# -*- coding: utf-8 -*-
# 診斷專家代理（最小 ADK 化實作）：用於 AgentTool 掛載
from __future__ import annotations
import os
try:
    from google.adk.agents import LlmAgent
except Exception:
    LlmAgent = None

def build_diagnostic_agent(model: str) -> "LlmAgent":
    """建立 LlmAgent 供 AgentTool 包裝。"""
    if LlmAgent is None:
        raise RuntimeError("缺少 google-adk 套件，無法建立 DiagnosticExpert")
    instruction = "你是 SRE 診斷專家，根據指標與日誌推斷可能的根因，輸出可行的驗證步驟與資料依據。"
    return LlmAgent(name="DiagnosticExpert", model=model, instruction=instruction, tools=[])
