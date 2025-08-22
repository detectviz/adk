
# 檔案：sub_agents/remediation/tools.py
# 角色：由 experts/remediation.yaml 讀取並導出工具白名單，供 Dev UI 與組裝使用。
from __future__ import annotations
from typing import List
from sre_assistant.sub_agents._loader import get_tools_allowlist

TOOLS_ALLOWLIST: List[str] = get_tools_allowlist("remediation")

def list_tools() -> List[str]:
    """
    2025-08-22T05:02:00.890560Z
    函式用途：回傳此子代理可使用的工具名稱清單。
    參數說明：無。
    回傳：工具名稱陣列。
    """
    return list(TOOLS_ALLOWLIST)
