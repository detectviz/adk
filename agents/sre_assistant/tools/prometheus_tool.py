# 說明：Prometheus HTTP API 包裝，提供即時與區間查詢（繁體中文註解）。

import os
import datetime as _dt
from typing import Dict, Any, Optional
import httpx

PROM_URL = os.getenv("PROM_URL", "").rstrip("/")

def _ts(dt: Optional[_dt.datetime]) -> str:
    if dt is None:
        return str(int(_dt.datetime.now(tz=_dt.timezone.utc).timestamp()))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_dt.timezone.utc)
    return str(int(dt.timestamp()))

def query(promql: str, ts: Optional[_dt.datetime] = None, timeout: float = 10.0) -> Dict[str, Any]:
    assert PROM_URL, "PROM_URL is required"
    params = {"query": promql}
    if ts is not None:
        params["time"] = _ts(ts)
    with httpx.Client(timeout=timeout) as client:
        r = client.get(f"{PROM_URL}/api/v1/query", params=params)
        r.raise_for_status()
        return r.json()

def query_range(promql: str, start: _dt.datetime, end: _dt.datetime, step: str = "30s", timeout: float = 20.0) -> Dict[str, Any]:
    assert PROM_URL, "PROM_URL is required"
    params = {
        "query": promql,
        "start": _ts(start),
        "end": _ts(end),
        "step": step
    }
    with httpx.Client(timeout=timeout) as client:
        r = client.get(f"{PROM_URL}/api/v1/query_range", params=params)
        r.raise_for_status()
        return r.json()
