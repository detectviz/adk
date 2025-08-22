
# -*- coding: utf-8 -*-
# 政策閘（最小實作）：根據 adk.yaml 中 allowlist 與 require_approval 控制工具執行
from __future__ import annotations
from typing import Dict, Any, Tuple
import os, yaml

class RiskLevel:
    Low="Low"; Medium="Medium"; High="High"; Critical="Critical"

def _load_cfg(path: str="adk.yaml") -> Dict[str,Any]:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`_load_cfg` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `path`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    if not os.path.exists(path): return {}
    return yaml.safe_load(open(path,"r",encoding="utf-8").read()) or {}

def evaluate_tool_call(tool_name: str, kwargs: Dict[str,Any]) -> Tuple[bool, str, str, bool]:
    """回傳：(allowed, reason, risk_level, require_approval)"""
    cfg = _load_cfg()
    allow = set((cfg.get("agent",{}).get("tools_allowlist") or []))
    req = set((cfg.get("agent",{}).get("tools_require_approval") or []))
    if allow and tool_name not in allow:
        return False, "Not in allowlist", RiskLevel.High, False
    require_approval = tool_name in req
    # 粗略風險評級（示例）：含 delete/patch/exec 字樣者高風險
    name = tool_name.lower()
    risk = RiskLevel.Medium
    if any(x in name for x in ["delete","patch","exec","restart"]):
        risk = RiskLevel.High
    return True, "ok", risk, require_approval