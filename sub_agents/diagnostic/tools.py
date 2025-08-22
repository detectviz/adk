
# -*- coding: utf-8 -*-
# 檔案：sub_agents/diagnostic/tools.py
# 角色：由 experts/diagnostic.yaml 讀取並導出工具白名單，供 Dev UI 與組裝使用。
from __future__ import annotations
from typing import List
from sre_assistant.sub_agents._loader import get_tools_allowlist

TOOLS_ALLOWLIST: List[str] = get_tools_allowlist("diagnostic")

def list_tools() -> List[str]:
    """
    自動產生註解時間：2025-08-22T05:02:00.890231Z
    函式用途：回傳此子代理可使用的工具名稱清單。
    參數說明：無。
    回傳：工具名稱陣列。
    """
    return list(TOOLS_ALLOWLIST)
