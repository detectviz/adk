
# 共用 HTTP 客戶端：以 httpx 實作，並將常見錯誤映射為標準化錯誤碼。
from __future__ import annotations
import os
from typing import Any, Dict, Optional
try:
    import httpx
except Exception:
    httpx = None

from ..adk_compat.executor import ExecutionError

class HttpClient:
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 15):
        """
        2025-08-22 03:37:34Z
        函式用途：`__init__` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `base_url`：參數用途請描述。
        - `headers`：參數用途請描述。
        - `timeout`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout

    def _ensure(self):
        """
        2025-08-22 03:37:34Z
        函式用途：`_ensure` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        if httpx is None:
            raise ExecutionError("E_BACKEND", "httpx 未安裝，請於環境中安裝依賴")

    def _full(self, path: str) -> str:
        """
        2025-08-22 03:37:34Z
        函式用途：`_full` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `path`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        path = path if path.startswith("/") else f"/{path}"
        return f"{self.base_url}{path}"

    def get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        2025-08-22 03:37:34Z
        函式用途：`get` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `path`：參數用途請描述。
        - `params`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        self._ensure()
        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
                r = client.get(self._full(path), params=params or {})
            if r.status_code >= 500:
                raise ExecutionError("E_BACKEND", f"上游 5xx：{r.status_code}")
            if r.status_code == 404:
                raise ExecutionError("E_NOT_FOUND", "資源不存在")
            if r.status_code == 401 or r.status_code == 403:
                raise ExecutionError("E_AUTH", "未授權或權限不足")
            return r.json()
        except httpx.ReadTimeout:
            raise ExecutionError("E_TIMEOUT", "HTTP 逾時")
        except httpx.ConnectError as e:
            raise ExecutionError("E_BACKEND", f"連線錯誤：{e}")
        except ValueError as e:
            raise ExecutionError("E_SCHEMA", f"JSON 解析失敗：{e}")

    def post(self, path: str, json_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        2025-08-22 03:37:34Z
        函式用途：`post` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `path`：參數用途請描述。
        - `json_body`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        self._ensure()
        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
                r = client.post(self._full(path), json=json_body)
            if r.status_code >= 500:
                raise ExecutionError("E_BACKEND", f"上游 5xx：{r.status_code}")
            if r.status_code == 404:
                raise ExecutionError("E_NOT_FOUND", "資源不存在")
            if r.status_code == 401 or r.status_code == 403:
                raise ExecutionError("E_AUTH", "未授權或權限不足")
            return r.json()
        except httpx.ReadTimeout:
            raise ExecutionError("E_TIMEOUT", "HTTP 逾時")
        except httpx.ConnectError as e:
            raise ExecutionError("E_BACKEND", f"連線錯誤：{e}")
        except ValueError as e:
            raise ExecutionError("E_SCHEMA", f"JSON 解析失敗：{e}")