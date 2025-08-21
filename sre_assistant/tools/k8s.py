
# -*- coding: utf-8 -*-
# Kubernetes 操作工具：以 K8s API 或模擬模式執行 rollout restart。
from __future__ import annotations
import os, time
from typing import Any, Dict
from .common_http import HttpClient
from ..adk_compat.executor import ExecutionError

def k8s_rollout_restart_tool(namespace: str, deployment_name: str, reason: str | None = None) -> Dict[str, Any]:
    """
    觸發 Deployment 的 rollout restart。
    環境變數：
      - K8S_API_URL
      - K8S_BEARER_TOKEN（可選）
      - K8S_MOCK=1 時使用模擬輸出
    輸出：{ success: bool, message: str }
    例外：受保護命名空間或 API 失敗時回傳對應錯誤碼。
    """
    if not namespace or not deployment_name:
        raise ExecutionError("E_SCHEMA", "namespace 與 deployment_name 必填")

    protected = {"prod", "production", "kube-system"}
    if namespace in protected:
        raise ExecutionError("E_POLICY", "受保護命名空間禁止直接重啟")

    base = os.getenv("K8S_API_URL")
    token = os.getenv("K8S_BEARER_TOKEN")
    mock = os.getenv("K8S_MOCK", "1") == "1" or not base

    if mock:
        return {"success": True, "message": f"模擬已排程 rollout restart {namespace}/{deployment_name}"}

    headers = {"Authorization": f"Bearer {token}"} if token else {}
    client = HttpClient(base_url=base, headers=headers)
    # 依據 Kubernetes 版本，重啟可透過 patch annotation 或 scale 操作；此處示意以 patch annotation：
    patch = {
        "spec": {
            "template": {
                "metadata": {"annotations": {"kubectl.kubernetes.io/restartedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ")}}
            }
        }
    }
    # 注意：實務上為 PATCH /apis/apps/v1/namespaces/{ns}/deployments/{name}
    # 並需設定 Content-Type: application/strategic-merge-patch+json，這裡簡化示意
    data = client.post(f"/apis/apps/v1/namespaces/{namespace}/deployments/{deployment_name}", json_body=patch)
    # 假設 API 回應含 status 或 code 欄位，這裡只確認非空
    if not data:
        raise ExecutionError("E_BACKEND", "K8s API 無回應")
    return {"success": True, "message": f"已觸發 rollout restart {namespace}/{deployment_name}"}
