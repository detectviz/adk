# Kubernetes 長時任務工具：使用標準 ADK Approval Framework
from __future__ import annotations
import time
import uuid
from typing import Dict, Any

from google.adk.tools.long_running_tool import LongRunningFunctionTool
from google.adk.tools.tool_context import ToolContext

# 匯入標準審批框架和風險等級定義
from ..core.adk_approval import request_approval, RiskLevel
from ..core.errors import HitlRejectedError

# 匯入實際的 k8s 操作函式
from .k8s import rollout_restart_deployment, check_rollout_status

def _start_restart(namespace: str, deployment_name: str, reason: str = "") -> Dict[str, Any]:
    """開始一項重啟 Kubernetes Deployment 的長時任務。

    流程：
    1. 觸發標準 HITL (Human-in-the-Loop) 審批流程。
    2. 若獲批准，則執行 k8s rollout restart 並回傳操作 ID。
    3. 若被拒絕或審批失敗，則拋出 HitlRejectedError。
    """
    # 步驟 1: 使用標準審批框架請求高風險操作的權限。
    # 注意：ToolContext 是由 ADK 執行環境在呼叫時自動傳入的，簽章中不應宣告。
    ctx = ToolContext.get_current()
    approval_result = request_approval(
        action="k8s.rollout.restart",
        resource=f"{namespace}/{deployment_name}",
        risk_level=RiskLevel.HIGH,
        context={"reason": reason, "user": ctx.session.state.get("user_id")}
    )

    # 步驟 2: 檢查審批結果。
    if not approval_result.get("approved"):
        raise HitlRejectedError(
            f"操作 {approval_result.get('request_id')} 被拒絕，原因: {approval_result.get('reason')}"
        )

    # 步驟 3: 審批通過，執行非同步的 k8s 操作。
    op_id = f"op-k8s-restart-{uuid.uuid4().hex[:8]}"
    result = rollout_restart_deployment(
        namespace=namespace, 
        deployment_name=deployment_name, 
        reason=reason,
        wait=False  # 設定為非阻塞，由 poll 函式接手輪詢狀態。
    )

    # 在 session state 中儲存操作狀態，以便後續輪詢。
    ops = ctx.session.state.setdefault("lr_ops", {})
    ops[op_id] = {
        "namespace": namespace,
        "deployment_name": deployment_name,
        "start_time": time.time(),
        "status": "RUNNING",
        "progress": 5, # 賦予一個初始進度值。
        "result": result
    }

    return {"op_id": op_id, "status": "RUNNING", "message": "操作已啟動，正在等待審批。"}

def _poll_restart(op_id: str) -> Dict[str, Any]:
    """輪詢指定操作 ID 的 k8s rollout 狀態。"""
    ctx = ToolContext.get_current()
    ops = ctx.session.state.setdefault("lr_ops", {})
    op_info = ops.get(op_id)

    if not op_info:
        return {"op_id": op_id, "status": "UNKNOWN", "message": "查無此操作 ID。"}

    # 如果任務已回報終態（完成或失敗），直接回傳儲存的結果。
    if op_info.get("status") in ("DONE", "FAILED"):
        return op_info

    # 呼叫 k8s 狀態檢查函式。
    status_result = check_rollout_status(
        namespace=op_info["namespace"],
        deployment_name=op_info["deployment_name"]
    )

    # 更新操作資訊於 session state。
    op_info["progress"] = status_result.get("progress", op_info["progress"])
    op_info["status"] = status_result.get("status", op_info["status"])
    op_info["result"] = status_result

    return {
        "op_id": op_id,
        "status": op_info["status"],
        "progress": op_info["progress"],
        "result": op_info["result"]
    }

# 注意：長時任務工具的實例化與註冊已移至 adk_app/runtime.py 中統一管理，
# 以確保所有工具都透過標準的 ToolRegistry 進行註冊。
