
# -*- coding: utf-8 -*-
# 政策引擎（簡版）：白名單/風險分級/HITL 標記
from __future__ import annotations
from typing import Dict, Any, Tuple

class RiskLevel:
    LOW="Low"; MEDIUM="Medium"; HIGH="High"; CRITICAL="Critical"

def evaluate_tool_call(tool_name: str, kwargs: Dict[str,Any]) -> Tuple[bool, str, str, bool]:
    ns = (kwargs.get("namespace") or "").lower()
    destructive = any(k in tool_name.lower() for k in ["restart","delete","scale","patch"])
    if destructive and ns in {"prod","production"}:
        return (True, "高風險操作，需要 HITL", RiskLevel.CRITICAL, True)
    if destructive:
        return (True, "破壞性操作，風險中等", RiskLevel.HIGH, False)
    return (True, "允許", RiskLevel.LOW, False)
