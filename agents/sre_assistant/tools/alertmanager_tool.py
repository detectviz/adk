# 說明：Alertmanager API 包裝，提供告警查詢與靜默建立（繁體中文註解）。

import os
from typing import Dict, Any, List
import httpx

AM_URL = os.getenv("AM_URL", "").rstrip("/")

def list_alerts(filter_expr: str = "", timeout: float = 10.0) -> List[Dict[str, Any]]:
    assert AM_URL, "AM_URL is required"
    params = {"filter": filter_expr} if filter_expr else {}
    with httpx.Client(timeout=timeout) as client:
        r = client.get(f"{AM_URL}/api/v2/alerts", params=params)
        r.raise_for_status()
        return r.json()

def create_silence(matchers: Dict[str, str], created_by: str, comment: str, starts_at: str, ends_at: str, timeout: float = 10.0) -> Dict[str, Any]:
    assert AM_URL, "AM_URL is required"
    payload = {
        "matchers": [{"name": k, "value": v, "isRegex": False} for k, v in matchers.items()],
        "startsAt": starts_at,
        "endsAt": ends_at,
        "createdBy": created_by,
        "comment": comment
    }
    with httpx.Client(timeout=timeout) as client:
        r = client.post(f"{AM_URL}/api/v2/silences", json=payload)
        r.raise_for_status()
        return r.json()
