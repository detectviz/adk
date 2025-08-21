
# -*- coding: utf-8 -*-
# ADK 工具橋接：將本專案的 YAML+函式工具映射為 ADK 的 FunctionTool/AgentTool。
from __future__ import annotations
from typing import Any, Dict, Callable, List

try:
    from google.adk.tools import FunctionTool as AdkFunctionTool
    ADK_OK = True
except Exception:
    ADK_OK = False

from ..adk_compat.registry import ToolRegistry
from ..adk_compat.executor import ToolExecutor

def build_adk_tools_from_registry(registry: ToolRegistry) -> List[Any]:
    if not ADK_OK:
        return []
    execu = ToolExecutor(registry)
    tools: List[Any] = []
    for name, entry in registry.list_tools().items():
        spec = entry["spec"]
        def _factory(n=name, s=spec):
            def _call(**kwargs):
                return execu.invoke(n, s, **kwargs)
            return _call
        tools.append(AdkFunctionTool(name=name, description=spec.get("description",""), args_schema=spec.get("args_schema",{}), returns_schema=spec.get("returns_schema",{}), func=_factory()))
    return tools
