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
            工廠函式：為每個工具動態建立一個執行閉包 (closure)。
            用途：
            透過閉包捕獲當前迴圈中的工具名稱(n)與規格(s)，
            確保後續生成的 _call 函式能正確地與其對應的工具綁定。
            若不使用工廠函式，所有 _call 都會引用到迴圈最後一個工具的資訊。
            參數說明：
            - `n`：工具的唯一名稱 (str)。
            - `s`：工具的規格定義 (dict)。
            回傳：一個已綁定特定工具資訊的可呼叫函式 (_call)。
            """
            def _call(**kwargs):
                """
                工具執行函式 (由 _factory 產生)。
                用途：
                此函式是最終傳遞給 ADK FunctionTool 的 `func` 參數。
                當 ADK 執行此工具時，會呼叫這個函式，
                它會利用閉包中捕獲的工具名稱(n)與規格(s)，
                透過 ToolExecutor 實際觸發工具邏輯。
                參數說明：
                - `**kwargs`：ADK 傳遞的工具執行參數。
                回傳：工具執行的結果。
                """
                return execu.invoke(n, s, **kwargs)
            return _call
        tools.append(AdkFunctionTool(name=name, description=spec.get("description",""), args_schema=spec.get("args_schema",{}), returns_schema=spec.get("returns_schema",{}), func=_factory()))
    return tools
