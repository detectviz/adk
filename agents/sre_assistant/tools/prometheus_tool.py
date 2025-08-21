# 說明：Prometheus HTTP API 包裝，提供即時與區間查詢。

import os
import datetime as _dt
from typing import Dict, Any, Optional
import httpx
import tenacity
from tenacity import retry, stop_after_attempt, wait_exponential
from cachetools import cached, TTLCache

# --- Cache and Retry Configuration ---

# TTL快取：最多快取 1024 個結果，每個結果存活 60 秒
cache = TTLCache(maxsize=1024, ttl=60)

def _should_retry(retry_state: tenacity.RetryCallState) -> bool:
    """如果例外是網路錯誤或 5xx 伺服器錯誤，則回傳 True。"""
    exception = retry_state.outcome.exception()
    if isinstance(exception, (httpx.RequestError, httpx.TimeoutException)):
        return True
    if isinstance(exception, httpx.HTTPStatusError):
        # 只對伺服器端錯誤 (5xx) 重試
        return exception.response.status_code >= 500
    return False

# 重試策略：最多重試3次，指數退讓（1s, 2s, 4s），僅在網路錯誤或 5xx 錯誤時重試
retry_policy = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=_should_retry
)

# --- Environment Configuration ---

PROM_URL = os.getenv("PROM_URL", "").rstrip("/")

# --- Helper Functions ---

def _ts(dt: Optional[_dt.datetime]) -> str:
    if dt is None:
        return str(int(_dt.datetime.now(tz=_dt.timezone.utc).timestamp()))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_dt.timezone.utc)
    return str(int(dt.timestamp()))

# --- Tool Functions ---

@cached(cache)
@retry_policy
def query(promql: str, ts: Optional[_dt.datetime] = None, timeout: float = 10.0) -> Dict[str, Any]:
    """執行即時查詢，具備快取與重試機制。"""
    assert PROM_URL, "PROM_URL is required"
    params = {"query": promql}
    if ts is not None:
        params["time"] = _ts(ts)
    
    with httpx.Client(timeout=timeout) as client:
        r = client.get(f"{PROM_URL}/api/v1/query", params=params)
        r.raise_for_status()  # httpx 會對 4xx/5xx 拋出 HTTPStatusError
        return r.json()

@cached(cache)
@retry_policy
def query_range(promql: str, start: _dt.datetime, end: _dt.datetime, step: str = "30s", timeout: float = 20.0) -> Dict[str, Any]:
    """執行區間查詢，具備快取與重試機制。"""
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
