
# -*- coding: utf-8 -*-
# 專家子代理：Diagnostic / Remediation / Postmortem / Config，以 LlmAgent 實作並以 AgentTool 掛載
from __future__ import annotations
from typing import List, Any
import os

try:
    from google.adk.agents import LlmAgent
    from google.adk.tools.agent_tool import AgentTool
except Exception:
    LlmAgent = None
    AgentTool = None

def _ensure():
    if LlmAgent is None or AgentTool is None:
        raise RuntimeError("缺少 google-adk 套件，無法建立專家代理與 AgentTool")

def make_diagnostic_expert(tools: List[Any]) -> Any:
    _ensure()
    agent = LlmAgent(
        name="DiagnosticExpert",
        model=os.getenv("ADK_MODEL_DIAG", os.getenv("ADK_MODEL", "gemini-2.0-flash")),
        instruction="你是診斷專家，專注於問題分類、根因假設與資料蒐集。必要時建議後續修復步驟。",
        tools=tools,
    )
    return AgentTool(name="DiagnosticExpertTool", agent=agent)

def make_remediation_expert(tools: List[Any]) -> Any:
    _ensure()
    agent = LlmAgent(
        name="RemediationExpert",
        model=os.getenv("ADK_MODEL_REMED", os.getenv("ADK_MODEL", "gemini-2.0-flash")),
        instruction="你是修復專家，根據診斷結果制定並執行修復計畫，高風險操作需觸發 HITL。",
        tools=tools,
    )
    return AgentTool(name="RemediationExpertTool", agent=agent)

def make_postmortem_expert(tools: List[Any]) -> Any:
    _ensure()
    agent = LlmAgent(
        name="PostmortemExpert",
        model=os.getenv("ADK_MODEL_PM", os.getenv("ADK_MODEL", "gemini-2.0-flash")),
        instruction="你是覆盤專家，負責事件總結、根因分析、改進建議與知識沉澱。",
        tools=tools,
    )
    return AgentTool(name="PostmortemExpertTool", agent=agent)

def make_config_expert(tools: List[Any]) -> Any:
    _ensure()
    agent = LlmAgent(
        name="ConfigExpert",
        model=os.getenv("ADK_MODEL_CFG", os.getenv("ADK_MODEL", "gemini-2.0-flash")),
        instruction="你是配置專家，負責監控儀表板與告警策略的生成與調整。",
        tools=tools,
    )
    return AgentTool(name="ConfigExpertTool", agent=agent)
