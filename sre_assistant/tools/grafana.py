
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any

def grafana_create_dashboard_tool(service_type: str) -> Dict[str, Any]:
    return {"dashboard_id": f"dash-{service_type}", "url": f"https://grafana.local/d/{service_type}"}
