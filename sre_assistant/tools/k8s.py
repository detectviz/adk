
# -*- coding: utf-8 -*-
# Kubernetes 工具（真連接）：RBAC 權限預檢 + rollout restart + 完成輪詢
from __future__ import annotations
from typing import Dict, Any, Optional
import os, time, datetime

try:
    from kubernetes import client, config
except Exception:
    client = None
    config = None

def _load_k8s_config() -> None:
    """載入 K8s 設定（InCluster 優先，否則回退本機 kubeconfig）。"""
    if not config:
        raise RuntimeError("未安裝 kubernetes 套件，請先安裝 kubernetes")
    try:
        config.load_incluster_config()
    except Exception:
        config.load_kube_config()

def _check_rbac(namespace: str, verb: str, resource: str = "deployments", group: str = "apps") -> bool:
    """使用 SelfSubjectAccessReview 進行 RBAC 預檢，避免執行期才 403。"""
    _load_k8s_config()
    auth = client.AuthorizationV1Api()
    review = client.V1SelfSubjectAccessReview(
        spec=client.V1SelfSubjectAccessReviewSpec(
            resource_attributes=client.V1ResourceAttributes(
                namespace=namespace, verb=verb, resource=resource, group=group
            )
        )
    )
    try:
        resp = auth.create_self_subject_access_review(review)
        return bool(resp.status and resp.status.allowed)
    except Exception:
        return False

def _wait_rollout_complete(namespace: str, deployment_name: str, timeout_seconds: int = 300, poll_interval: float = 2.0) -> Dict[str, Any]:
    """輪詢 Deployment 是否完成更新：updated/ready/available 達到目標；逾時則失敗。"""
    _load_k8s_config()
    apps = client.AppsV1Api()
    start = time.time()
    while time.time() - start < timeout_seconds:
        dep = apps.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        status = dep.status or client.V1DeploymentStatus()
        desired = (dep.spec.replicas or 0)
        updated = status.updated_replicas or 0
        ready = status.ready_replicas or 0
        available = status.available_replicas or 0
        if updated >= desired and ready >= desired and available >= desired:
            return {"done": True, "desired": desired, "updated": updated, "ready": ready, "available": available}
        time.sleep(poll_interval)
    return {"done": False, "reason": "timeout", "last_status": {"updated": status.updated_replicas or 0, "ready": status.ready_replicas or 0}}

def rollout_restart_deployment(namespace: str, deployment_name: str, reason: Optional[str] = None, wait: bool = True, timeout_seconds: int = 300) -> Dict[str, Any]:
    """
    觸發 Deployment 的 rollout restart，並可選擇等待完成。
    - RBAC 預檢：確認對 deployments 的 get/patch 權限。
    - 以 patch annotations（kubectl.kubernetes.io/restartedAt）方式觸發。
    - wait=True 時輪詢直到完成或逾時。
    """
    if not client:
        return {"success": False, "message": "未安裝 kubernetes 套件"}
    if not _check_rbac(namespace, "get") or not _check_rbac(namespace, "patch"):
        return {"success": False, "message": "RBAC 權限不足，缺少 get/patch deployments 權限"}

    _load_k8s_config()
    apps = client.AppsV1Api()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    t0 = time.time()
    try:
        patch = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": now,
                            **({"sre.reason": reason} if reason else {})
                        }
                    }
                }
            }
        }
        apps.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=patch)
        if wait:
            status = _wait_rollout_complete(namespace, deployment_name, timeout_seconds=timeout_seconds)
            if not status.get("done"):
                return {"success": False, "message": f"restart issued but not completed: {status}", "elapsed_ms": int((time.time()-t0)*1000)}
        return {"success": True, "message": f"rollout restart triggered at {now}", "elapsed_ms": int((time.time()-t0)*1000)}
    except Exception as e:
        return {"success": False, "message": f"restart failed: {e}", "elapsed_ms": int((time.time()-t0)*1000)}
