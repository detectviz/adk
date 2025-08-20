
# -*- coding: utf-8 -*-
# 極簡 KV 儲存（記憶體實作；繁體中文註解）。
from typing import Dict, Optional

class InMemoryKV:
    def __init__(self):
        self._store: Dict[str, str] = {}
    def get(self, key: str) -> Optional[str]:
        return self._store.get(key)
    def set(self, key: str, value: str) -> None:
        self._store[key] = value
    def delete(self, key: str) -> None:
        self._store.pop(key, None)
