
# -*- coding: utf-8 -*-
# Prometheus HTTP 整合客戶端
# - 依環境變數 PROM_URL 指向 Prometheus，例如 http://prometheus:9090
# - 以 requests 呼叫 /api/v1/query_range 與 /api/v1/query
# - 提供簡易重試與逾時；統一錯誤代碼供工具層回報
from __future__ import annotations
from typing import Dict, Any, Tuple
import os, time, requests
from ._retry import session_with_retry

DEFAULT_TIMEOUT = float(os.getenv("PROM_TIMEOUT", "8"))
PROM_URL = os.getenv("PROM_URL", "http://localhost:9090")

class PrometheusClient:
    """Prometheus 簡易 HTTP 客戶端。"""
    def __init__(self, base_url: str | None = None, timeout: float = DEFAULT_TIMEOUT):
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`__init__` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `base_url`：參數用途請描述。
        - `timeout`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        self.base_url = (base_url or PROM_URL).rstrip('/')
        self.timeout = timeout

    def _get(self, path: str, params: Dict[str, Any]) -> Tuple[Dict[str, Any] | None, str | None]:
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`_get` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `path`：參數用途請描述。
        - `params`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        url = f"{self.base_url}{path}"
        try:
            r = session_with_retry().get(url, params=params, timeout=self.timeout)
            if r.status_code != 200:
                return None, f"E_HTTP_{r.status_code}"
            data = r.json()
            if data.get("status") != "success":
                return None, "E_BACKEND"
            return data, None
        except requests.Timeout:
            return None, "E_TIMEOUT"
        except Exception:
            return None, "E_HTTP"

    def query_range(self, query: str, start: str, end: str, step: str) -> Tuple[Dict[str, Any] | None, str | None]:
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`query_range` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `query`：參數用途請描述。
        - `start`：參數用途請描述。
        - `end`：參數用途請描述。
        - `step`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        params = {"query": query, "start": start, "end": end, "step": step}
        return self._get("/api/v1/query_range", params)

    def query_instant(self, query: str, ts: str | None = None) -> Tuple[Dict[str, Any] | None, str | None]:
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`query_instant` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `query`：參數用途請描述。
        - `ts`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        params = {"query": query}
        if ts: params["time"] = ts
        return self._get("/api/v1/query", params)