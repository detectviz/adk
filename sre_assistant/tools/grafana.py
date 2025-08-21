
# -*- coding: utf-8 -*-
# Grafana 儀表板工具：支援 Token 驗證與模擬輸出。
from __future__ import annotations
import os, random, string
from typing import Any, Dict
from .common_http import HttpClient
from ..adk_compat.executor import ExecutionError

def _rand_uid(n=8):
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))

def grafana_create_dashboard_tool(service_type: str, title: str | None = None) -> Dict[str, Any]:
    """
    建立 Grafana 儀表板的簡化流程。
    環境變數：
      - GRAFANA_URL
      - GRAFANA_TOKEN（可選）
      - GRAFANA_MOCK=1 時使用模擬輸出
    回傳：{ success: bool, uid: str, url: str }
    """
    if not service_type:
        raise ExecutionError("E_SCHEMA", "service_type 必填")

    base = os.getenv("GRAFANA_URL")
    token = os.getenv("GRAFANA_TOKEN")
    mock = os.getenv("GRAFANA_MOCK", "1") == "1" or not base

    if mock:
        uid = _rand_uid()
        return {"success": True, "uid": uid, "url": f"https://example.grafana.local/d/{uid}", "title": title or f"{service_type}-dashboard"}

    headers = {"Authorization": f"Bearer {token}"} if token else {}
    client = HttpClient(base_url=base, headers=headers)
    # Grafana 建立儀表板 API：POST /api/dashboards/db
    body = {
        "dashboard": {"title": title or f"{service_type}-dashboard", "panels": []},
        "folderId": 0,
        "overwrite": False
    }
    data = client.post("/api/dashboards/db", json_body=body)
    if not data.get("status") == "success":
        raise ExecutionError("E_BACKEND", f"Grafana 建立失敗：{data}")
    return {"success": True, "uid": data.get("uid"), "url": data.get("url"), "title": title or f"{service_type}-dashboard"}
