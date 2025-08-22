
# -*- coding: utf-8 -*-
# 協調器：對齊 ADK，使用 LoopAgent + BuiltInPlanner + LlmAgent，並掛載顯式工具註冊表
from __future__ import annotations
from typing import List
import os, yaml, pathlib

# 備援：若缺官方套件，給出明確錯誤
try:
    from google.adk.agents import LlmAgent, LoopAgent
    from google.adk.planners import BuiltInPlanner
except Exception as e:
    LlmAgent = None
    LoopAgent = None
    BuiltInPlanner = None

from adk.registry import ToolRegistry
from ..core.policy_gate import wrap_tools_allowlist
from ..adapters.adk_runtime import build_adk_tools

def build_coordinator(registry: ToolRegistry, cfg: dict|None=None) -> "LoopAgent":
    """建立協調器 Agent。
    - LlmAgent 作為主代理，負責規劃與提出工具呼叫。
    - BuiltInPlanner 執行規劃步驟。
    - LoopAgent 迴圈運行直到達成目標或達到迭代上限。
    """
    if LlmAgent is None or LoopAgent is None or BuiltInPlanner is None:
        raise RuntimeError("缺少 google-adk 套件，無法建立協調器；請依官方文件安裝。")

    cfg = cfg or {}
    model = (cfg.get('agent',{}) or {}).get('model') or os.getenv('ADK_MODEL','gemini-2.0-flash')
    instruction = (
        "你是 SREAssistant 主協調器。根據使用者意圖選用合適工具，先規劃再執行，"
        "高風險操作應觸發 request_credential 事件。所有輸出需附帶關鍵依據與建議後續行動。"
    )

    main_llm = LlmAgent(
        name="SREMainAgent",
        model=model,
        instruction=instruction,
        tools=wrap_tools_allowlist({n: t for n,t in zip(registry.list(), build_adk_tools(registry))}, (cfg.get('agent',{}) or {}).get('tools_allowlist')),  # 以顯式註冊表掛載工具
    )
    planner = BuiltInPlanner()

    # 掛載子專家（Diagnostic/Remediation）為 AgentTool
    try:
        from google.adk.tools.agent_tool import AgentTool
        from ..experts.diagnostic import build_diagnostic_agent
        from ..experts.remediation import build_remediation_agent
        diag = build_diagnostic_agent(model)
        remed = build_remediation_agent(model)
        agent_tools = [AgentTool(agent=diag, name="DiagnosticExpert"), AgentTool(agent=remed, name="RemediationExpert")]
        main_llm.tools.extend(agent_tools)
    except Exception:
        # 若缺官方套件則略過子專家掛載
        pass

    max_iter = int((cfg.get('runner',{}) or {}).get('max_iterations') or os.getenv('ADK_MAX_ITER','10'))
    coordinator = LoopAgent(agents=[main_llm], planner=planner, max_iterations=max_iter)
    return coordinator
