
# -*- coding: utf-8 -*-
from typing import Dict, List
ROLES: Dict[str, List[str]] = {
  "viewer": [],
  "operator": ["rag_search"],
  "sre": ["rag_search","K8sRolloutRestartLongRunningTool","ingest_text"],
  "admin": ["*"],
}
APIKEY_ROLE: Dict[str, str] = {"dev-view":"viewer","dev-op":"operator","dev-sre":"sre","dev-admin":"admin"}
def allowed_tools_for_key(api_key: str)->List[str]:
    role = APIKEY_ROLE.get(api_key, "viewer")
    return ROLES.get(role, [])
