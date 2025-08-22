
# -*- coding: utf-8 -*-
# 角色：RBAC 讀自 adk.yaml 的 roles 映射；若缺省則回退內建預設。
from __future__ import annotations
import yaml, os
from typing import Dict, List

DEFAULT = {
  "roles": {
    "viewer": [],
    "operator": ["rag_search"],
    "sre": ["rag_search","K8sRolloutRestartLongRunningTool","ingest_text"],
    "admin": ["*"]
  },
  "apikey_role": {"dev-view":"viewer","dev-op":"operator","dev-sre":"sre","dev-admin":"admin"}
}

def _load()->dict:
    p = "adk.yaml"
    if os.path.exists(p):
        try:
            with open(p,"r",encoding="utf-8") as f:
                y = yaml.safe_load(f) or {}
            roles = (y.get("rbac") or {}).get("roles") or DEFAULT["roles"]
            apir = (y.get("rbac") or {}).get("apikey_role") or DEFAULT["apikey_role"]
            return {"roles": roles, "apikey_role": apir}
        except Exception:
            return DEFAULT
    return DEFAULT

_CFG = _load()

def allowed_tools_for_key(api_key: str)->List[str]:
    role = _CFG["apikey_role"].get(api_key, "viewer")
    return _CFG["roles"].get(role, [])
