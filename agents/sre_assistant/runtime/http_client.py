
# -*- coding: utf-8 -*-
# 簡單 HTTP Client 包裝（集中重試與逾時設定；繁體中文註解）。
import httpx
from typing import Any, Dict, Optional

class HttpClient:
    def __init__(self, timeout: float = 20.0, retries: int = 2):
        self.timeout = timeout
        self.retries = retries

    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        last_exc = None
        for _ in range(self.retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    return client.request(method, url, **kwargs)
            except Exception as e:
                last_exc = e
        raise last_exc
