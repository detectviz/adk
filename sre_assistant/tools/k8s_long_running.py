
# -*- coding: utf-8 -*-
# Kubernetes 長任務工具（v14）：HITL 以 request_credential 互動流實作
# - start_func：若 namespace 為 prod/production，觸發 request_credential，等待前端提交憑證（核可）
# - poll_func：輪詢是否已取得核可；核可後才實際觸發 rollout restart，並持續回報進度
from __future__ import annotations
import os, time, uuid
from typing import Dict, Any, Optional

from google.adk.tools.long_running_tool import LongRunningFunctionTool
from google.adk.tools.tool_context import ToolContext

# 內存暫存操作上下文（教學用；生產應改用共享儲存如 DB/Redis）
_LR_OPS: Dict[str, Dict[str, Any]] = {}

# 既有短任務版本：實際執行 restart 一次（此函式內含真正業務邏輯）
from .k8s import k8s_rollout_restart_tool as _restart_once

def _start_restart(namespace: str, deployment_name: str, reason: Optional[str], tool_context: ToolContext) -> Dict[str, Any]:
    """
    長任務起始：
    1) 若目標 namespace 屬高風險（prod/production），先觸發 HITL：
       - 透過 tool_context.request_credential(auth_config) 要求前端互動（adk_request_credential 事件）
       - 前端完成核可後，將以 FunctionResponse 再次呼叫 runner.run_async 恢復流程
    2) 尚未核可時，start 僅建立 operation_id 並回報 WAITING_APPROVAL 狀態
    3) 非高風險環境則直接建立 operation 並交由 poll 追蹤
    備註：此處將實際觸發 restart 延後到 poll 階段，以配合 HITL 回補。
    """
    op_id = str(uuid.uuid4())
    _LR_OPS[op_id] = {
        "namespace": namespace,
        "deployment_name": deployment_name,
        "reason": reason,
        "start_ts": time.time(),
        "approved": False,
        "started": False,   # 是否已真正觸發 restart
        "progress": 0.0,
        "last_status": "INIT",
    }

    # 高風險命名空間：要求核可（HITL）
    if namespace in {"prod", "production"}:
        # 以「核可請求」為名的 AuthConfig（簡化示例）：前端只需回傳一段 callback URI 表示核可
        auth_config = {
            "exchanged_auth_credential": {
                "oauth2": {
                    # 在真實 OAuth2 場景，這裡會是供跳轉的 auth_uri；此處以內部核可頁路徑示意
                    "auth_uri": "/ui/approve.html"
                }
            }
        }
        # 觸發互動事件（adk_request_credential）；ADK 會在 Event 流拋出 function_call 供前端處理
        tool_context.request_credential(auth_config)  # 依官方 API

        return {
            "operation_id": op_id,
            "status": "WAITING_APPROVAL",
            "message": "高風險操作，已請求人工核可，請於前端完成核可後續執行。",
            "namespace": namespace,
            "deployment_name": deployment_name,
        }

    # 低風險：直接進入待執行狀態，由 poll 負責觸發與追蹤
    return {
        "operation_id": op_id,
        "status": "PENDING",
        "message": "已建立長任務，準備開始滾動重啟。",
        "namespace": namespace,
        "deployment_name": deployment_name,
    }

def _poll_restart(operation_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    輪詢進度：
    - 若尚未核可且屬高風險操作，持續回報 WAITING_APPROVAL
    - 若已核可且尚未觸發，立即執行一次真正的 rollout restart（委派 _restart_once）
    - 之後以簡化時間推進進度（教學用）；實務應查詢 K8s ready/updated replicas
    """
    ctx = _LR_OPS.get(operation_id)
    if not ctx:
        return {"operation_id": operation_id, "status": "ERROR", "message": "operation_id 無效或已過期"}

    # 高風險情境：檢查是否收到核可回應
    if ctx["namespace"] in {"prod", "production"} and not ctx["approved"]:
        # 嘗試取得核可回傳（依官方：get_auth_response(auth_config)）；此處以相同 auth_config 索取
        auth_config = {"exchanged_auth_credential": {"oauth2": {}}}
        auth_resp = tool_context.get_auth_response(auth_config)
        if auth_resp:
            # 收到核可（此處僅檢查是否有 auth_response_uri/redirect_uri 等欄位，實務可檢查更嚴格）
            ctx["approved"] = True
        else:
            return {
                "operation_id": operation_id,
                "status": "WAITING_APPROVAL",
                "message": "等待人工核可中…",
                "progress": 0.0,
                "namespace": ctx["namespace"],
                "deployment_name": ctx["deployment_name"],
            }

    # 若尚未觸發實際重啟，現在執行一次
    if not ctx["started"]:
        _ = _restart_once(namespace=ctx["namespace"], deployment_name=ctx["deployment_name"], reason=ctx["reason"])
        ctx["started"] = True
        ctx["progress"] = 0.1
        ctx["last_status"] = "RUNNING"
        return {
            "operation_id": operation_id,
            "status": "RUNNING",
            "message": "已觸發 rollout restart，開始追蹤 Pod 更新。",
            "progress": ctx["progress"],
            "namespace": ctx["namespace"],
            "deployment_name": ctx["deployment_name"],
        }

    # 簡化：經過數次輪詢後視為完成
    ctx["progress"] = min(1.0, ctx["progress"] + 0.2)
    done = ctx["progress"] >= 1.0
    ctx["last_status"] = "DONE" if done else "RUNNING"
    return {
        "operation_id": operation_id,
        "status": ctx["last_status"],
        "message": "Deployment 已完成更新" if done else "Deployment 更新中",
        "progress": ctx["progress"],
        "namespace": ctx["namespace"],
        "deployment_name": ctx["deployment_name"],
    }

# 導出 LongRunningFunctionTool 實例
k8s_rollout_restart_long_running_tool = LongRunningFunctionTool(
    name="K8sRolloutRestartLongRunningTool",
    description="對 Deployment 進行長任務式 rollout restart，必要時觸發 HITL（request_credential）再執行。",
    start_func=_start_restart,
    poll_func=_poll_restart,
    timeout_seconds=600
)
