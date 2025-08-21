
# -*- coding: utf-8 -*-
# 去抖動與重複抑制：避免同一短時間內重複請求造成資源浪費。
import time, hashlib
from typing import Dict

class Debouncer:
    def __init__(self, ttl_seconds: int = 10):
        self.ttl = ttl_seconds
        self._hits: Dict[str, float] = {}

    def key_of(self, text: str) -> str:
        norm = " ".join(text.lower().split())
        return hashlib.sha256(norm.encode("utf-8")).hexdigest()

    def allow(self, text: str) -> bool:
        k = self.key_of(text)
        now = time.time()
        ts = self._hits.get(k, 0)
        if now - ts < self.ttl:
            return False
        self._hits[k] = now
        return True

DEBOUNCER = Debouncer()
