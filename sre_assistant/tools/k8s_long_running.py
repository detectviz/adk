
# -*- coding: utf-8 -*-
# Kubernetes 長任務工具（v14.4）：HITL（request_credential）+ 真正 rollout 輪詢
from __future__ import annotations
import os, time, uuid
from typing import Dict, Any, Optional

from google.adk.tools.long_running_tool import LongRunningFunctionTool
from google.adk.tools.tool_context import ToolContext
from ..core.hitl_provider import get_provider
from ..core.persistence import DB
from ..core.errors import HitlRejectedError

from .k8s import rollout_restart_deployment

# 內存暫存操作上下文（示例）；生產請改 DB/Redis
_LR_OPS: Dict[str, Dict[str, Any]] = {}

def _start_restart(ctx: ToolContext, namespace: str, deployment_name: str, reason: str) -> dict: ToolContext, namespace: str, deployment_name: str, reason: str = "") -> Dict[str, Any]:
    """開始重啟流程：prod/production 需 HITL；否則直接觸發短任務並進入輪詢。"""
    op_id = f"op-{int(time.time()*1000)}"
    need_hitl = namespace.lower() in {"prod","production"}
    _LR_OPS[op_id] = {"namespace": namespace, "deployment_name": deployment_name, "reason": reason, "approved": not need_hitl, "progress": 0}
    if need_hitl:
        prov = get_provider('hitl-approval')
        # 可依 provider 定義調整 prompt/欄位
        ctx.request_credential(
            provider_id="hitl-approval",
            prompt=f"批准在 {namespace} 對 {deployment_name} 進行 rollout restart",
            callback={"function_call_id": ctx.function_call_id}
        )
        return {"op_id": op_id, "status": "PENDING_APPROVAL", "message": "已要求人工核可"}
    else:
        return _execute_restart(op_id)

def _execute_restart(op_id: str) -> Dict[str, Any]:
    """實際觸發 rollout 並預設等待完成（300 秒）。"""
    info = _LR_OPS[op_id]
    res = rollout_restart_deployment(info["namespace"], info["deployment_name"], info.get("reason",""), wait=True, timeout_seconds=300)
    info["approved"] = True
    info["result"] = res
    info["progress"] = 100 if res.get("success") else 0
    return {"op_id": op_id, "status": "RUNNING" if res.get("success") else "FAILED", "result": res}

def _poll_restart(ctx: ToolContext, op_id: str) -> Dict[str, Any]:
    # 讀取前端核可回應，若已核可/拒絕則更新 session 狀態
    try:
        auth = ctx.get_auth_response(function_call_id=op_id)
        if auth and isinstance(auth, dict):
            st = ctx.session.state.setdefault('lr_ops', {})
            info = st.setdefault(op_id, {"approved": False, "progress": 0, "result": None})
            if auth.get('approved') is True:
                info['approved'] = True
            if auth.get('rejected') is True:
                info['approved'] = False
                info['result'] = {"success": False, "message": auth.get('reason','HITL 拒絕')}
    except Exception:
        pass
    ops = ctx.session.state.setdefault('lr_ops', {})
    st = ops.get(op_id) or {"approved": False, "progress": 0, "result": None}
    """前端輪詢：若已核可且尚未執行，執行一次；否則回報進度。"""
    info = st
    if not info:
        return {"op_id": op_id, "status": "UNKNOWN", "message": "查無此操作"}
    if info.get("approved") and "result" not in info:
        return _execute_restart(op_id)
    done = info.get("result",{}).get("success", False) and info.get("progress",0) == 100
    return {
        "op_id": op_id,
        "status": "DONE" if done else ("RUNNING" if info.get("approved") else "PENDING_APPROVAL"),
        "progress": info.get("progress", 0),
        "result": info.get("result", {})
    }

k8s_rollout_restart_long_running_tool = LongRunningFunctionTool(
    name="K8sRolloutRestartLongRunningTool",
    description="對 Deployment 進行長任務式 rollout restart；prod/production 需 HITL 才執行。",
    start_func=_start_restart,
    poll_func=_poll_restart,
    timeout_seconds=600
)
