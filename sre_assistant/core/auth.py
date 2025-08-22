
# -*- coding: utf-8 -*-
# 認證與授權：DB 支援的 API Key 檢查（SHA-256 雜湊），RBAC 與 Token Bucket。
import time, threading, hashlib
from typing import Dict
from .config import Config
from .persistence import DB

class AuthError(Exception):
    pass

class RateLimiter:
    def __init__(self, capacity: int | None = None, refill_per_sec: float | None = None):
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`__init__` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `capacity`：參數用途請描述。
        - `refill_per_sec`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        self.capacity = capacity if capacity is not None else Config.RATE_CAPACITY
        self.refill = refill_per_sec if refill_per_sec is not None else Config.RATE_REFILL
        self._lock = threading.Lock()
        self._buckets: Dict[str, tuple[float, float]] = {}

    def allow(self, key: str) -> bool:
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`allow` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `key`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
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
    # 先從 DB 查角色，若無則允許 devkey 後門（開發環境）
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`require_api_key` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `key`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    role = DB.get_role_by_key(key or "")
    if not role and (key or "") == "devkey":
        role = "admin"
    if not role:
        raise AuthError("invalid api key")
    if not LIMITER.allow(key):
        raise AuthError("rate_limited")
    return role

def require_role(role: str, minimum: str) -> bool:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`require_role` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `role`：參數用途請描述。
    - `minimum`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    levels = {"viewer":0,"operator":1,"admin":2}
    return levels.get(role, -1) >= levels.get(minimum, 9)