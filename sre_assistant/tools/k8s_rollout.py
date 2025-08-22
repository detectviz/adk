# Kubernetes Rolling Restart 與 RBAC 預檢（顯式工具模組）
# - 以官方 kubernetes-client 連線；支援 KUBECONFIG 或 InCluster
# - 先以 SelfSubjectAccessReview 檢查 patch deployments 權限
# - 以 annotation 滾動重啟；輪詢直到 updatedReplicas==replicas 且 availableReplicas==replicas 或逾時
from __future__ import annotations
from typing import Dict, Any
import os, time, datetime

from kubernetes import client, config
from kubernetes.client import ApiException

def _load_kube():
    """載入客戶端配置。"""
    if os.getenv("K8S_IN_CLUSTER","").lower() in {"1","true","yes"}:
        config.load_incluster_config()
    else:
        kubeconfig = os.getenv("KUBECONFIG")
        config.load_kube_config(config_file=kubeconfig)

def _rbac_check(namespace: str, verb: str = "patch", group: str="apps", resource: str="deployments") -> bool:
    """使用 authorization.k8s.io SelfSubjectAccessReview 進行 RBAC 預檢。"""
    auth = client.AuthorizationV1Api()
    sar = client.V1SelfSubjectAccessReview(
        spec=client.V1SelfSubjectAccessReviewSpec(
            resource_attributes=client.V1ResourceAttributes(
                namespace=namespace, verb=verb, group=group, resource=resource
            )
        )
    )
    resp = auth.create_self_subject_access_review(sar)
    return bool(resp and resp.status and resp.status.allowed)

def rollout_restart(namespace: str, deployment: str, timeout_seconds: int = 300) -> Dict[str,Any]:
    """對 Deployment 觸發滾動重啟並輪詢狀態直到完成或逾時。"""
    _load_kube()
    if not _rbac_check(namespace, "patch", "apps", "deployments"):
        return {"ok": False, "error": "E_RBAC", "message": "無 patch deployments 權限"}
    api = client.AppsV1Api()
    # 觸發 rollout restart：更新 annotation
    now = datetime.datetime.utcnow().isoformat() + "Z"
    body = {
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {"kubectl.kubernetes.io/restartedAt": now}
                }
            }
        }
    }
    try:
        api.patch_namespaced_deployment(name=deployment, namespace=namespace, body=body)
    except ApiException as e:
        return {"ok": False, "error": "E_PATCH", "message": f"部署補丁失敗: {e}"}
    # 讀取 replicas 期望值
    try:
        dep = api.read_namespaced_deployment_status(name=deployment, namespace=namespace)
        desired = dep.spec.replicas or 1
    except ApiException as e:
        return {"ok": False, "error": "E_READ", "message": f"讀取狀態失敗: {e}"}
    # 輪詢直到完成
    start=time.time()
    while time.time()-start < timeout_seconds:
        try:
            st = api.read_namespaced_deployment_status(name=deployment, namespace=namespace).status
            up = st.updated_replicas or 0
            av = st.available_replicas or 0
            rr = st.replicas or 0
            if up==desired and av==desired and rr==desired:
                return {"ok": True, "updated": up, "available": av, "replicas": rr, "message": "Rollout 完成"}
        except ApiException as e:
            return {"ok": False, "error": "E_STATUS", "message": f"查詢狀態失敗: {e}"}
        time.sleep(2)
    return {"ok": False, "error": "E_TIMEOUT", "message": f"超時未完成，目標 replicas={desired}"}
