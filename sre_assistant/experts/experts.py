
# -*- coding: utf-8 -*-
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
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`_ensure` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    if LlmAgent is None or AgentTool is None:
        raise RuntimeError("缺少 google-adk 套件，無法建立專家代理與 AgentTool")

def make_diagnostic_expert(registry) -> Any:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`make_diagnostic_expert` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `registry`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    _ensure()
    agent = LlmAgent(
        name="DiagnosticExpert",
        model=os.getenv("ADK_MODEL_DIAG", os.getenv("ADK_MODEL", "gemini-2.0-flash")),
        instruction="你是診斷專家，專注於問題分類、根因假設與資料蒐集。必要時建議後續修復步驟。",
        tools=_select_tools(registry, 'diagnostic', ['rag_search']) ,
    )
    return AgentTool(name="DiagnosticExpertTool", agent=agent)

def make_remediation_expert(registry) -> Any:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`make_remediation_expert` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `registry`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    _ensure()
    agent = LlmAgent(
        name="RemediationExpert",
        model=os.getenv("ADK_MODEL_REMED", os.getenv("ADK_MODEL", "gemini-2.0-flash")),
        instruction="你是修復專家，根據診斷結果制定並執行修復計畫，高風險操作需觸發 HITL。",
        tools=_select_tools(registry, 'diagnostic', ['rag_search']) ,
    )
    return AgentTool(name="RemediationExpertTool", agent=agent)

def make_postmortem_expert(registry) -> Any:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`make_postmortem_expert` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `registry`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    _ensure()
    agent = LlmAgent(
        name="PostmortemExpert",
        model=os.getenv("ADK_MODEL_PM", os.getenv("ADK_MODEL", "gemini-2.0-flash")),
        instruction="你是覆盤專家，負責事件總結、根因分析、改進建議與知識沉澱。",
        tools=_select_tools(registry, 'diagnostic', ['rag_search']) ,
    )
    return AgentTool(name="PostmortemExpertTool", agent=agent)

def make_config_expert(registry) -> Any:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`make_config_expert` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `registry`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    _ensure()
    agent = LlmAgent(
        name="ConfigExpert",
        model=os.getenv("ADK_MODEL_CFG", os.getenv("ADK_MODEL", "gemini-2.0-flash")),
        instruction="你是配置專家，負責監控儀表板與告警策略的生成與調整。",
        tools=_select_tools(registry, 'diagnostic', ['rag_search']) ,
    )
    return AgentTool(name="ConfigExpertTool", agent=agent)


def _select_tools(registry, section: str, default: list[str]) -> list[Any]:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`_select_tools` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `registry`：參數用途請描述。
    - `section`：參數用途請描述。
    - `default`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    cfg = load_adk_config()
    allow = (((cfg.get("experts",{}) or {}).get(section, {}) or {}).get("tools_allowlist")) or default
    out = []
    for n in allow:
        try: out.append(registry.get(n))
        except Exception: pass
    return out