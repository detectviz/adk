
# -*- coding: utf-8 -*-
# 認證與授權：API Key + RBAC + Token Bucket
import time, threading
from typing import Dict
from .config import Config

class AuthError(Exception):
    pass

class ApiKeyStore:
    def __init__(self):
        self._keys = {"devkey": "admin"}
    def role_of(self, key: str) -> str | None:
        return self._keys.get(key)

API_KEYS = ApiKeyStore()

class RateLimiter:
    def __init__(self, capacity: int | None = None, refill_per_sec: float | None = None):
        self.capacity = capacity if capacity is not None else Config.RATE_CAPACITY
        self.refill = refill_per_sec if refill_per_sec is not None else Config.RATE_REFILL
        self._lock = threading.Lock()
        self._buckets: Dict[str, tuple[float, float]] = {}

    def allow(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            tokens, last = self._buckets.get(key, (self.capacity, now))
            tokens = min(self.capacity, tokens + (now - last) * self.refill)
            if tokens >= 1.0:
                tokens -= 1.0
                self._buckets[key] = (tokens, now)
                return True
            self._buckets[key] = (tokens, now)
            return False

LIMITER = RateLimiter()

def require_api_key(key: str) -> str:
    role = API_KEYS.role_of(key or "")
    if not role:
        raise AuthError("invalid api key")
    if not LIMITER.allow(key):
        raise AuthError("rate_limited")
    return role

def require_role(role: str, minimum: str) -> bool:
    levels = {"viewer":0,"operator":1,"admin":2}
    return levels.get(role, -1) >= levels.get(minimum, 9)
