
# -*- coding: utf-8 -*-
# Kubernetes 操作工具（真實客戶端優先）：
# - 若安裝 `kubernetes` 套件且 K8S_MOCK!=1，則使用 AppsV1Api.patch_namespaced_deployment
# - 否則使用模擬輸出
from __future__ import annotations
import os, time
from typing import Any, Dict
from ..adk_compat.executor import ExecutionError

try:
    from kubernetes import client, config
except Exception:
    client = None
    config = None

def _ensure_k8s():
    if client is None or config is None:
        raise ExecutionError("E_BACKEND", "環境未安裝 kubernetes 客戶端")

def k8s_rollout_restart_tool(namespace: str, deployment_name: str, reason: str | None = None) -> Dict[str, Any]:
    if not namespace or not deployment_name:
        raise ExecutionError("E_SCHEMA", "namespace 與 deployment_name 必填")

    protected = {"prod", "production", "kube-system"}
    if namespace in protected:
        raise ExecutionError("E_POLICY", "受保護命名空間禁止直接重啟")

    mock = os.getenv("K8S_MOCK", "1") == "1"
    if mock:
        return {"success": True, "message": f"模擬已排程 rollout restart {namespace}/{deployment_name}"}

    _ensure_k8s()
    # 優先嘗試 in-cluster，失敗落回 kubeconfig
    try:
        config.load_incluster_config()
    except Exception:
        try:
            config.load_kube_config()
        except Exception as e:
            raise ExecutionError("E_BACKEND", f"載入 K8s 設定失敗：{e}")

    api = client.AppsV1Api()
    patch = {
        "spec": {
            "template": {
                "metadata": {"annotations": {"kubectl.kubernetes.io/restartedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ")}}
            }
        }
    }
    try:
        # strategic merge patch
        api.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=patch)
        return {"success": True, "message": f"已觸發 rollout restart {namespace}/{deployment_name}"}
    except client.ApiException as e:
        if e.status == 404:
            raise ExecutionError("E_BACKEND", "Deployment 不存在")
        raise ExecutionError("E_BACKEND", f"K8s API 失敗：{e.status} {e.reason}")
    except Exception as e:
        raise ExecutionError("E_BACKEND", f"未知錯誤：{e}")
