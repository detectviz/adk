
# -*- coding: utf-8 -*-
# ADK 介面：將 YAML+函式的工具轉換為 ADK 的 FunctionTool，並建立 LoopAgent 協調器。
from __future__ import annotations
from typing import Any, Dict, Callable, List
from ..adk_compat.registry import ToolRegistry

try:
    from google.adk.agents import LoopAgent, LlmAgent
    from google.adk.planners import BuiltInPlanner
    from google.adk.tools.function_tool import FunctionTool as AdkFunctionTool
    ADK_AVAILABLE = True
except Exception:
    ADK_AVAILABLE = False

from ...adk_runtime.main import build_registry

def _build_adk_tools(reg: ToolRegistry) -> List[Any]:
    tools = []
    if not ADK_AVAILABLE:
        return tools
    for name, ent in reg.list_tools().items():
        spec = ent["spec"]
        func = ent["func"]
        # 將 YAML 契約映射為 ADK 的 FunctionTool 參數（示意，實務依 ADK 介面補齊）
        t = AdkFunctionTool(
            name=spec.get("name", name),
            description=spec.get("description",""),
            func=func,
            args_schema=spec.get("args_schema", {"type":"object"}),
            returns_schema=spec.get("returns_schema", {"type":"object"}),
            timeout_seconds=spec.get("timeout_seconds", 30),
        )
        tools.append(t)
    return tools

def build_coordinator(model: str = "gemini-2.5-flash"):
    reg = build_registry()
    if not ADK_AVAILABLE:
        # 回退：回傳本地協調器以維持功能
        from ..core.assistant import SREAssistant
        return SREAssistant(reg)
    adk_tools = _build_adk_tools(reg)
    main = LlmAgent(name="SREMainAgent", model=model, instruction="You are SRE assistant", tools=adk_tools)
    coordinator = LoopAgent(agents=[main], planner=BuiltInPlanner(), max_iterations=10)
    return coordinator
