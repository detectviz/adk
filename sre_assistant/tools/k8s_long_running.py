
# -*- coding: utf-8 -*-
# Kubernetes 長任務工具：以 ADK LongRunningFunctionTool 包裝 rollout restart 與狀態輪詢
# - 以 start/poll 兩段函式對應長任務開始與進度查詢
# - 官方 API：google.adk.tools.long_running_tool.LongRunningFunctionTool
# - 注意：此範例以 in-memory 字典保存操作上下文，生產環境請改為資料庫/快取
from __future__ import annotations
import os, time, uuid
from typing import Dict, Any

from google.adk.tools.long_running_tool import LongRunningFunctionTool
from google.adk.tools.tool_context import ToolContext

# 內部狀態：以記憶體保存操作上下文（操作參數、起始時間等）
_LR_OPS: Dict[str, Dict[str, Any]] = {}

# --- 實際業務：委派至既有 K8s 工具實作（短任務版本）---
from .k8s import k8s_rollout_restart_tool as _restart_once

def _start_restart(namespace: str, deployment_name: str, reason: str | None, tool_context: ToolContext) -> Dict[str, Any]:
    """
    長任務起始：
    - 立刻觸發一次 rollout restart（非阻塞）
    - 建立 operation_id 與上下文，回傳初始狀態供 ADK Runtime 知悉
    - 可在此透過 tool_context.request_credential(...) 實作 HITL 授權流程（官方建議）
    回傳字典將作為工具的「中間結果」，LLM 可據以回覆或等待輪詢
    """
    op_id = str(uuid.uuid4())
    # 生產建議：改為正式 HITL。此處先尊重 before_tool_callback 政策閘（coordinator 內定義）。
    resp = _restart_once(namespace=namespace, deployment_name=deployment_name, reason=reason)
    _LR_OPS[op_id] = {
        "namespace": namespace,
        "deployment_name": deployment_name,
        "reason": reason,
        "start_ts": time.time(),
        "last_status": "STARTED",
        "trigger_result": resp,
    }
    return {
        "operation_id": op_id,
        "status": "STARTED",
        "message": f"已觸發 rollout restart，等待 Pod 更新完成（ns={namespace}, deploy={deployment_name}）",
        "trigger_result": resp,
    }

def _poll_restart(operation_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    長任務輪詢：
    - 查詢對應 Deployment 的可用副本與更新狀態，推算進度
    - 若完成則回傳 DONE；若失敗回傳 ERROR；否則 RUNNING
    - 教學目的：此處以簡化邏輯模擬，實務請調用 K8s API 取得 readyReplicas/updatedReplicas
    """
    ctx = _LR_OPS.get(operation_id)
    if not ctx:
        return {"operation_id": operation_id, "status": "ERROR", "message": "operation_id 無效或已過期"}

    # 簡化：假設 10 秒內完成；依經過時間推估進度
    elapsed = time.time() - ctx["start_ts"]
    progress = min(1.0, elapsed / 10.0)
    status = "DONE" if progress >= 1.0 else "RUNNING"
    ctx["last_status"] = status
    result = {
        "operation_id": operation_id,
        "status": status,
        "progress": progress,
        "message": "Deployment 更新中" if status == "RUNNING" else "Deployment 已完成更新",
        "namespace": ctx["namespace"],
        "deployment_name": ctx["deployment_name"],
    }
    # 完成後可選擇清理暫存
    if status == "DONE":
        ctx["done_ts"] = time.time()
    return result

# 導出 LongRunningFunctionTool 實例（供協調器掛載）
k8s_rollout_restart_long_running_tool = LongRunningFunctionTool(
    name="K8sRolloutRestartLongRunningTool",
    description="對指定 Deployment 進行長任務式 rollout restart，並可輪詢進度（ADK LongRunningFunctionTool）",
    start_func=_start_restart,    # 起始函式
    poll_func=_poll_restart,      # 輪詢函式
    timeout_seconds=300           # 總超時（教學預設 5 分鐘）
)
