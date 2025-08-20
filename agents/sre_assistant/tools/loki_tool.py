# 說明：Loki HTTP API 包裝，提供區間查詢（繁體中文註解）。

import os
import datetime as _dt
from typing import Dict, Any, Optional
import httpx

LOKI_URL = os.getenv("LOKI_URL", "").rstrip("/")

def _ts(dt: _dt.datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_dt.timezone.utc)
    # Loki expects nanoseconds since epoch
    return str(int(dt.timestamp() * 1_000_000_000))

def query_range(logql: str, start: _dt.datetime, end: _dt.datetime, limit: int = 500, direction: str = "backward", timeout: float = 20.0) -> Dict[str, Any]:
    assert LOKI_URL, "LOKI_URL is required"
    params = {
        "query": logql,
        "start": _ts(start),
        "end": _ts(end),
        "limit": str(limit),
        "direction": direction,
    }
    with httpx.Client(timeout=timeout) as client:
        r = client.get(f"{LOKI_URL}/loki/api/v1/query_range", params=params)
        r.raise_for_status()
        return r.json()
