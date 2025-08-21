
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any

RUNBOOKS = {
    "orders": {"steps": ["檢查 DB 延遲","查看 Pod 日誌","必要時滾動重啟"], "version":"1.0"}
}

def runbook_lookup_tool(service: str) -> Dict[str, Any]:
    return RUNBOOKS.get(service, {"steps": [], "version": "unknown"})
