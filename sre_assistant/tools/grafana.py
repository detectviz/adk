
# -*- coding: utf-8 -*-
# Grafana 儀表板建立工具（真連接版）
# - 依 service_type 產生最小化儀表板 JSON，並呼叫 /api/dashboards/db
# - 真實專案可改為載入模板檔並套參數
from __future__ import annotations
from typing import Dict, Any
import time, uuid
from ..integrations.grafana_http import GrafanaClient

def _template_dashboard(service_type: str) -> Dict[str, Any]:
    uid = f"sre-{service_type}-{uuid.uuid4().hex[:8]}"
    return {
        "uid": uid,
        "title": f"SRE {service_type} Service Dashboard",
        "timezone": "browser",
        "schemaVersion": 38,
        "refresh": "30s",
        "panels": [
            {
                "type": "timeseries",
                "title": "CPU Usage",
                "gridPos": {"x":0,"y":0,"w":12,"h":8},
                "targets": [{"expr": "rate(container_cpu_usage_seconds_total[5m])"}]
            },
            {
                "type": "timeseries",
                "title": "Memory Usage",
                "gridPos": {"x":12,"y":0,"w":12,"h":8},
                "targets": [{"expr": "container_memory_working_set_bytes"}]
            }
        ]
    }

def grafana_create_dashboard_tool(service_type: str) -> Dict[str, Any]:
    """建立 Grafana 儀表板並回傳 UID（真連接 Grafana）。"""
    t0 = time.time()
    cli = GrafanaClient()
    dash = _template_dashboard(service_type)
    try:
        res = cli.upsert_dashboard(dashboard=dash, folder_id=None, overwrite=False)
        uid = res.get("uid") or res.get("dashboard",{}).get("uid") or dash["uid"]
        return {"success": True, "dashboard_uid": uid, "message": "created", "elapsed_ms": int((time.time()-t0)*1000)}
    except Exception as e:
        return {"success": False, "dashboard_uid": None, "message": f"create failed: {e}", "elapsed_ms": int((time.time()-t0)*1000)}
