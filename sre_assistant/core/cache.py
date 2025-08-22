
# TTL 快取：每鍵獨立到期
import time, json, hashlib
from typing import Any, Dict

class TTLCache:
    def __init__(self, default_ttl_seconds: int = 20):
        
        self.default_ttl = default_ttl_seconds
        self._data: Dict[str, tuple[float, Any]] = {}

    def _key(self, tool: str, kwargs: Dict[str, Any]) -> str:
        
        body = json.dumps({k: kwargs[k] for k in sorted(kwargs)}, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(f"{tool}:{body}".encode("utf-8")).hexdigest()

    def get(self, tool: str, kwargs: Dict[str, Any]):
        
        k = self._key(tool, kwargs)
        v = self._data.get(k)
        if not v: return None
        exp, val = v
        if time.time() <= exp:
            return val
        self._data.pop(k, None)
        return None

    def set(self, tool: str, kwargs: Dict[str, Any], value: Any, ttl: int | None = None):
        
        k = self._key(tool, kwargs)
        exp = time.time() + (ttl if ttl is not None else self.default_ttl)
        self._data[k] = (exp, value)