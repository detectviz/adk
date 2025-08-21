
# -*- coding: utf-8 -*-
# 認證與授權：
# - 以 X-API-Key 進行簡易認證（適合內部環境與 PoC）
# - RBAC：使用者金鑰綁定角色（viewer|operator|admin）
# - 速率限制：每 API Key 每分鐘 N 次（Token Bucket 簡化）
import time, threading
from typing import Dict

class AuthError(Exception):
    pass

class ApiKeyStore:
    def __init__(self):
        # 示範：內建一組金鑰；正式環境請改由 DB 或 KMS 提供
        self._keys = {
            "devkey": "admin",
        }
    def role_of(self, key: str) -> str | None:
        return self._keys.get(key)

API_KEYS = ApiKeyStore()

class RateLimiter:
    def __init__(self, capacity: int = 120, refill_per_sec: float = 2.0):
        # 每金鑰一個桶，預設每秒補 2，容量 120
        self.capacity = capacity
        self.refill = refill_per_sec
        self._lock = threading.Lock()
        self._buckets: Dict[str, tuple[float, float]] = {}  # key -> (tokens, last_ts)

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
    # 角色等級：viewer < operator < admin
    levels = {"viewer":0,"operator":1,"admin":2}
    return levels.get(role, -1) >= levels.get(minimum, 9)
