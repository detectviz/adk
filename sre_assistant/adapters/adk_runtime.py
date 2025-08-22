
# -*- coding: utf-8 -*-
# 工具適配層：將專案中的明確 Python 函式工具轉為 ADK 的 Tool 物件（FunctionTool / LongRunningFunctionTool）
from __future__ import annotations
from typing import List, Dict, Callable, Any

try:
    from google.adk.tools.function_tool import FunctionTool
    from google.adk.tools.long_running_tool import LongRunningFunctionTool
except Exception:
    FunctionTool = None
    LongRunningFunctionTool = None

def _is_long_running(name: str) -> bool:
    # 約定：名稱或 __name__ 含 long_running 即視為長任務工具（可依 YAML/標記改進）
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`_is_long_running` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `name`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    return "long_running" in name.lower()

def build_adk_tools(tool_map: Dict[str, Callable[..., Any]]) -> List[Any]:
    """將 registry 中的函式轉為 ADK 工具物件；若無 ADK 套件，回傳原函式清單。"""
    out = []
    for name, fn in tool_map.items():
        if FunctionTool is None:
            out.append(fn)
            continue
        if _is_long_running(getattr(fn, "__name__", name)):
            if LongRunningFunctionTool:
                out.append(LongRunningFunctionTool(name=name, func=fn))
            else:
                out.append(FunctionTool(name=name, func=fn))
        else:
            out.append(FunctionTool(name=name, func=fn))
    return out