
# -*- coding: utf-8 -*-
# 去抖動：短時間內抑制相同語句觸發重複執行
import time, hashlib
from typing import Dict
from .config import Config

class Debouncer:
    def __init__(self, ttl_seconds: int | None = None):
        self.ttl = ttl_seconds if ttl_seconds is not None else Config.DEBOUNCE_TTL
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
