
# -*- coding: utf-8 -*-
# 提供 /api/v1/hitl/approve|reject 端點使用之輔助邏輯
from __future__ import annotations
from typing import Dict, Any
from ..tools.k8s_long_running import _LR_OPS  # 簡化示例：真實應改為 DB
from ..core.persistence import DB

def hitl_approve(session_id: str, user_id: str, op_id: str, approver: str, ticket_id: str|None=None) -> Dict[str,Any]:
    """標記指定長任務為已核可。"""
    info = _LR_OPS.get(op_id)
    if not info:
        return {"ok": False, "message": "op_id 不存在"}
    info["approved"] = True
    DB.write_audit(session_id, user_id, "HITL_APPROVE", {"op_id": op_id, "approver": approver, "ticket_id": ticket_id})
    return {"ok": True}

def hitl_reject(session_id: str, user_id: str, op_id: str, reason: str) -> Dict[str,Any]:
    """標記指定長任務為拒絕（不執行）。"""
    info = _LR_OPS.get(op_id)
    if not info:
        return {"ok": False, "message": "op_id 不存在"}
    info["approved"] = False
    info["result"] = {"success": False, "message": f"HITL 拒絕: {reason}"}
    info["progress"] = 0
    DB.write_audit(session_id, user_id, "HITL_REJECT", {"op_id": op_id, "reason": reason})
    return {"ok": True}
