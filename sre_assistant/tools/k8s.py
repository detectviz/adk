
# -*- coding: utf-8 -*-
# Kubernetes 重啟工具（真連接版，短任務）
# - 以 kubernetes 官方 client 連線；支援 InCluster 與本機 kubeconfig
# - 以 patch annotations 方式觸發 rollout restart
from __future__ import annotations
from typing import Dict, Any, Optional
import os, time, datetime

try:
    from kubernetes import client, config
except Exception:
    client = None
    config = None

def _load_k8s_config():
    if config is None:
        raise RuntimeError("未安裝 kubernetes 套件")
    if os.getenv("K8S_IN_CLUSTER","").lower() in {"1","true","yes"}:
        config.load_incluster_config()
    else:
        kubeconfig = os.getenv("KUBECONFIG")
        if kubeconfig and os.path.exists(kubeconfig):
            config.load_kube_config(config_file=kubeconfig)
        else:
            config.load_kube_config()

def k8s_rollout_restart_tool(namespace: str, deployment_name: str, reason: Optional[str] = None) -> Dict[str, Any]:
    """對指定 Deployment 進行 rollout restart（以 annotation 方式觸發）。"""
    t0 = time.time()
    try:
        _load_k8s_config()
        api = client.AppsV1Api()
        now = datetime.datetime.utcnow().isoformat() + "Z"
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
        api.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=patch)
        return {"success": True, "message": f"rollout restart triggered at {now}", "elapsed_ms": int((time.time()-t0)*1000)}
    except Exception as e:
        return {"success": False, "message": f"restart failed: {e}", "elapsed_ms": int((time.time()-t0)*1000)}
