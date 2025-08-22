
# TTL 快取：每鍵獨立到期
import time, json, hashlib
from typing import Any, Dict

class TTLCache:
    def __init__(self, default_ttl_seconds: int = 20):
        """
        2025-08-22 03:37:34Z
        函式用途：`__init__` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `default_ttl_seconds`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        self.default_ttl = default_ttl_seconds
        self._data: Dict[str, tuple[float, Any]] = {}

    def _key(self, tool: str, kwargs: Dict[str, Any]) -> str:
        """
        2025-08-22 03:37:34Z
        函式用途：`_key` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `tool`：參數用途請描述。
        - `kwargs`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        body = json.dumps({k: kwargs[k] for k in sorted(kwargs)}, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(f"{tool}:{body}".encode("utf-8")).hexdigest()

    def get(self, tool: str, kwargs: Dict[str, Any]):
        """
        2025-08-22 03:37:34Z
        函式用途：`get` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `tool`：參數用途請描述。
        - `kwargs`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        k = self._key(tool, kwargs)
        v = self._data.get(k)
        if not v: return None
        exp, val = v
        if time.time() <= exp:
            return val
        self._data.pop(k, None)
        return None

    def set(self, tool: str, kwargs: Dict[str, Any], value: Any, ttl: int | None = None):
        """
        2025-08-22 03:37:34Z
        函式用途：`set` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `tool`：參數用途請描述。
        - `kwargs`：參數用途請描述。
        - `value`：參數用途請描述。
        - `ttl`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        k = self._key(tool, kwargs)
        exp = time.time() + (ttl if ttl is not None else self.default_ttl)
        self._data[k] = (exp, value)