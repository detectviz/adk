
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
            """
            2025-08-22 03:37:34Z
            函式用途：`_factory` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
            參數說明：
            - `n`：參數用途請描述。
            - `s`：參數用途請描述。
            回傳：請描述回傳資料結構與語義。
            """
            def _call(**kwargs):
                """
                2025-08-22 03:37:34Z
                函式用途：`_call` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
                參數說明：
                - `**kwargs`：參數用途請描述。
                回傳：請描述回傳資料結構與語義。
                """
                return execu.invoke(n, s, **kwargs)
            return _call
        tools.append(AdkFunctionTool(name=name, description=spec.get("description",""), args_schema=spec.get("args_schema",{}), returns_schema=spec.get("returns_schema",{}), func=_factory()))
    return tools