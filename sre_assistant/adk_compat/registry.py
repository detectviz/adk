
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Dict, Callable
import yaml

class ToolSpecError(Exception):
    '''工具規格錯誤（參數缺失或描述有誤）'''
    pass

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register_from_yaml(self, yaml_path: str, func: Callable[..., Any]) -> None:
        with open(yaml_path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
        required_keys = ["name", "description", "args_schema", "returns_schema"]
        for k in required_keys:
            if k not in spec:
                raise ToolSpecError(f"工具規格缺少必要欄位: {k} in {yaml_path}")
        name = spec["name"]
        self._tools[name] = {"spec": spec, "func": func}

    def require(self, name: str) -> Dict[str, Any]:
        if name not in self._tools:
            raise KeyError(f"工具未註冊: {name}")
        return self._tools[name]

    def invoke(self, name: str, **kwargs):
        entry = self.require(name)
        spec = entry["spec"]
        func = entry["func"]
        args_schema = spec.get("args_schema", {})
        required = args_schema.get("required", [])
        for r in required:
            if r not in kwargs:
                raise ToolSpecError(f"缺少必要參數: {r} for tool {name}")
        return func(**kwargs)

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        return {n: {"description": t["spec"].get("description", "")} for n, t in self._tools.items()}
