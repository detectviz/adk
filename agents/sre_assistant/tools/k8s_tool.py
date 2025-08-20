# 說明：Kubernetes Python Client 包裝，提供 Pods/Events/Logs 基本能力（繁體中文註解）。

from typing import Dict, Any, Optional
from dataclasses import dataclass
import os

try:
    from kubernetes import client, config
except Exception:
    client = None
    config = None

@dataclass
class K8sConfig:
    context: Optional[str] = None
    in_cluster: bool = False

def _ensure_client(cfg: Optional[K8sConfig] = None):
    if cfg is None:
        cfg = K8sConfig()
    if cfg.in_cluster:
        assert config is not None, "kubernetes client not installed"
        config.load_incluster_config()
    else:
        assert config is not None, "kubernetes client not installed"
        context = cfg.context or os.getenv("K8S_CONTEXT") or None
        config.load_kube_config(context=context)
    return client.CoreV1Api(), client.AppsV1Api()

def list_pods(namespace: str = "default", label_selector: Optional[str] = None, cfg: Optional[K8sConfig] = None) -> Dict[str, Any]:
    v1, _ = _ensure_client(cfg)
    resp = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
    return resp.to_dict()

def get_events(namespace: str = "default", field_selector: Optional[str] = None, cfg: Optional[K8sConfig] = None) -> Dict[str, Any]:
    v1, _ = _ensure_client(cfg)
    resp = v1.list_namespaced_event(namespace=namespace, field_selector=field_selector)
    return resp.to_dict()

def get_pod_logs(name: str, namespace: str = "default", tail_lines: int = 200, container: Optional[str] = None, cfg: Optional[K8sConfig] = None) -> str:
    v1, _ = _ensure_client(cfg)
    return v1.read_namespaced_pod_log(name=name, namespace=namespace, tail_lines=tail_lines, container=container or None)
