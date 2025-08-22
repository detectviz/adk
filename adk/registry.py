
# -*- coding: utf-8 -*-
# 工具註冊表：以 YAML 描述 + 明確函式註冊，避免魔法裝飾器
from __future__ import annotations
from typing import Dict, Callable, Any
import yaml, importlib

class ToolRegistry:
    def __init__(self):
        self._map: Dict[str, Callable[..., Any]] = {}
    def register(self, name: str, func: Callable[..., Any]):
        self._map[name] = func
    def register_from_yaml(self, path: str, func: Callable[..., Any] = None):
        data = yaml.safe_load(open(path, "r", encoding="utf-8").read())
        for item in data.get("tools", []):
            mod = item["module"]; fn = item["callable"]; name = item.get("name") or fn
            if func and fn == func.__name__:
                self.register(name, func)
            else:
                f = getattr(importlib.import_module(mod), fn)
                self.register(name, f)
    def get(self, name: str):
        return self._map[name]
    def list(self):
        return list(self._map.keys())
