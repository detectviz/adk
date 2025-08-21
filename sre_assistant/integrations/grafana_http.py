
# -*- coding: utf-8 -*-
# Grafana HTTP 整合客戶端
# - 依環境變數 GRAFANA_URL 與 GRAFANA_TOKEN 呼叫 Grafana API
# - 實作最小集合：建立/更新儀表板
from __future__ import annotations
from typing import Dict, Any, Optional
import os, requests

GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN", "")  # 需有適當權限

class GrafanaClient:
    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.base_url = (base_url or GRAFANA_URL).rstrip('/')
        self.token = token or GRAFANA_TOKEN
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}" if self.token else ""
        }

    def upsert_dashboard(self, dashboard: Dict[str, Any], folder_id: Optional[int] = None, overwrite: bool = True) -> Dict[str, Any]:
        payload = { "dashboard": dashboard, "folderId": folder_id, "overwrite": overwrite }
        url = f"{self.base_url}/api/dashboards/db"
        r = requests.post(url, headers=self.headers, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
