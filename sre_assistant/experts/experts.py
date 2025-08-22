
# 專家子代理：Diagnostic / Remediation / Postmortem / Config，以 LlmAgent 實作並以 AgentTool 掛載
from __future__ import annotations
from typing import List, Any
import os
from ..core.config import load_adk_config

try:
    from google.adk.agents import LlmAgent
    from google.adk.tools.agent_tool import AgentTool
except Exception:
    LlmAgent = None
    AgentTool = None

def _ensure():
    
    if LlmAgent is None or AgentTool is None:
        raise RuntimeError("缺少 google-adk 套件，無法建立專家代理與 AgentTool")

def make_diagnostic_expert(registry) -> Any:
    
    _ensure()
    agent = LlmAgent(
        name="DiagnosticExpert",
        model=os.getenv("ADK_MODEL_DIAG", os.getenv("ADK_MODEL", "gemini-2.0-flash")),
        instruction="你是診斷專家，專注於問題分類、根因假設與資料蒐集。必要時建議後續修復步驟。",
        tools=_select_tools(registry, 'diagnostic', ['rag_search']) ,
    )
    return AgentTool(name="DiagnosticExpertTool", agent=agent)

def make_remediation_expert(registry) -> Any:
    
    _ensure()
    agent = LlmAgent(
        name="RemediationExpert",
        model=os.getenv("ADK_MODEL_REMED", os.getenv("ADK_MODEL", "gemini-2.0-flash")),
        instruction="你是修復專家，根據診斷結果制定並執行修復計畫，高風險操作需觸發 HITL。",
        tools=_select_tools(registry, 'diagnostic', ['rag_search']) ,
    )
    return AgentTool(name="RemediationExpertTool", agent=agent)

def make_postmortem_expert(registry) -> Any:
    
    _ensure()
    agent = LlmAgent(
        name="PostmortemExpert",
        model=os.getenv("ADK_MODEL_PM", os.getenv("ADK_MODEL", "gemini-2.0-flash")),
        instruction="你是覆盤專家，負責事件總結、根因分析、改進建議與知識沉澱。",
        tools=_select_tools(registry, 'diagnostic', ['rag_search']) ,
    )
    return AgentTool(name="PostmortemExpertTool", agent=agent)

def make_config_expert(registry) -> Any:
    
    _ensure()
    agent = LlmAgent(
        name="ConfigExpert",
        model=os.getenv("ADK_MODEL_CFG", os.getenv("ADK_MODEL", "gemini-2.0-flash")),
        instruction="你是配置專家，負責監控儀表板與告警策略的生成與調整。",
        tools=_select_tools(registry, 'diagnostic', ['rag_search']) ,
    )
    return AgentTool(name="ConfigExpertTool", agent=agent)


def _select_tools(registry, section: str, default: list[str]) -> list[Any]:
    
    cfg = load_adk_config()
    allow = (((cfg.get("experts",{}) or {}).get(section, {}) or {}).get("tools_allowlist")) or default
    out = []
    for n in allow:
        try: out.append(registry.get(n))
        except Exception: pass
    return out