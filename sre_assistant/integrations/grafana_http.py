
# -*- coding: utf-8 -*-
# Grafana HTTP 整合客戶端
# - 依環境變數 GRAFANA_URL 與 GRAFANA_TOKEN 呼叫 Grafana API
# - 實作最小集合：建立/更新儀表板
from __future__ import annotations
from typing import Dict, Any, Optional
import os, requests
from ._retry import session_with_retry

GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN", "")  # 需有適當權限

class GrafanaClient:
    def __init__(self, base_url: str | None = None, token: str | None = None):
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`__init__` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `base_url`：參數用途請描述。
        - `token`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        self.base_url = (base_url or GRAFANA_URL).rstrip('/')
        self.token = token or GRAFANA_TOKEN
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}" if self.token else ""
        }

    def upsert_dashboard(self, dashboard: Dict[str, Any], folder_id: Optional[int] = None, overwrite: bool = True) -> Dict[str, Any]:
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`upsert_dashboard` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `dashboard`：參數用途請描述。
        - `folder_id`：參數用途請描述。
        - `overwrite`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        payload = { "dashboard": dashboard, "folderId": folder_id, "overwrite": overwrite }
        url = f"{self.base_url}/api/dashboards/db"
        r = session_with_retry().post(url, headers=self.headers, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()