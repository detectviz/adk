
# -*- coding: utf-8 -*-
# 檔案：sre_assistant/core/policy.py
# 角色：載入靜態策略（如 require_approval 清單），供工具內自行判斷是否觸發 HITL。
from __future__ import annotations
import yaml, os
from typing import Dict, Any

def load_policy(path: str = "adk.yaml") -> Dict[str, Any]:
    """
    函式用途：載入策略設定。
    參數說明：`path` 設定檔路徑。
    回傳：字典，至少包含 `agent.tools_require_approval`（若有）。
    """
    if not os.path.exists(path): return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
