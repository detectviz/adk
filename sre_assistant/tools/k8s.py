
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any

def k8s_rollout_restart_tool(namespace: str, deployment_name: str, reason: str = "manual") -> Dict[str, Any]:
    if namespace in {"prod","production","kube-system"}:
        return {"success": False, "message": "Protected namespace", "error": "E_NAMESPACE_PROTECTED"}
    return {"success": True, "message": f"rollout restart {namespace}/{deployment_name} initiated for {reason}"}
