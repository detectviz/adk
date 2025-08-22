
# 去抖動：在短時間內抑制相同訊息重複觸發；新增 session 維度避免跨會話誤殺。
import time, hashlib
from typing import Dict, Optional
from .config import Config

class Debouncer:
    def __init__(self, ttl_seconds: int | None = None):
        """
        2025-08-22 03:37:34Z
        函式用途：`__init__` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `ttl_seconds`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        self.ttl = ttl_seconds if ttl_seconds is not None else Config.DEBOUNCE_TTL
        # _hits 儲存 key->timestamp，key 包含訊息內容與可選的 session_id
        self._hits: Dict[str, float] = {}

    def _hash(self, text: str, session_id: Optional[str]) -> str:
        """
        2025-08-22 03:37:34Z
        函式用途：`_hash` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `text`：參數用途請描述。
        - `session_id`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        norm = " ".join((text or "").lower().split())
        base = norm + "|" + (session_id or "")
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    def allow_msg(self, text: str, session_id: Optional[str] = None) -> bool:
        """
        2025-08-22 03:37:34Z
        函式用途：`allow_msg` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `text`：參數用途請描述。
        - `session_id`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        k = self._hash(text, session_id)
        now = time.time()
        ts = self._hits.get(k, 0)
        if now - ts < self.ttl:
            return False
        self._hits[k] = now
        return True

# 單例
DEBOUNCER = Debouncer()