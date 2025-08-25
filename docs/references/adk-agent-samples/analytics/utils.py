# utils.py

import threading

from typing import Any


class InMemoryCache:
    """無過期時間的簡單執行緒安全記憶體內快取。"""

    def __init__(self):
        self._lock = threading.Lock()
        self._store: dict[str, Any] = {}

    def get(self, key: str) -> Any | None:
        with self._lock:
            return self._store.get(key)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = value

    def delete(self, key: str) -> None:
        with self._lock:
            if key in self._store:
                del self._store[key]

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


# 用於跨模組使用的單例快取實例
cache = InMemoryCache()
