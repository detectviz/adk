# 說明：Grafana 註記 API 包裝，支援 dashboard/panel 附註（繁體中文註解）。

import os
from typing import Dict, Any, Optional
import httpx

GRAFANA_URL = os.getenv("GRAFANA_URL", "").rstrip("/")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN", "")

def annotate(text: str, dashboard_uid: Optional[str] = None, panel_id: Optional[int] = None, tags=None, time_ms: Optional[int] = None, time_end_ms: Optional[int] = None, timeout: float = 10.0) -> Dict[str, Any]:
    assert GRAFANA_URL, "GRAFANA_URL is required"
    headers = {"Authorization": f"Bearer {GRAFANA_TOKEN}"} if GRAFANA_TOKEN else {}
    payload: Dict[str, Any] = {"text": text, "tags": tags or []}
    if time_ms is not None:
        payload["time"] = time_ms
    if time_end_ms is not None:
        payload["timeEnd"] = time_end_ms
    if dashboard_uid:
        payload["dashboardUID"] = dashboard_uid
    if panel_id is not None:
        payload["panelId"] = panel_id
    with httpx.Client(timeout=timeout, headers=headers) as client:
        r = client.post(f"{GRAFANA_URL}/api/annotations", json=payload)
        r.raise_for_status()
        return r.json()
