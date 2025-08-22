
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
        
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout

    def _ensure(self):
        
        if httpx is None:
            raise ExecutionError("E_BACKEND", "httpx 未安裝，請於環境中安裝依賴")

    def _full(self, path: str) -> str:
        
        path = path if path.startswith("/") else f"/{path}"
        return f"{self.base_url}{path}"

    def get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        
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