
# -*- coding: utf-8 -*-
# 工具註冊表：以「工具描述 YAML + Python 函式」顯式註冊，提供查詢與檢索。
from __future__ import annotations
from typing import Dict, Any, Callable
import yaml, os

class ToolRegistry:
    def __init__(self):
        # _tools 映射：name -> {spec: dict, func: callable}
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register_from_yaml(self, yaml_path: str, func: Callable):
        """
        讀取 YAML 規格，與函式成對註冊。
        - 若重複註冊同名工具，後者會覆蓋前者（亦可改為禁止，視需求）。
        """
        with open(yaml_path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
        name = spec.get("name")
        if not name:
            raise ValueError(f"YAML 無 name：{yaml_path}")
        self._tools[name] = {"spec": spec, "func": func}

    def register_dir(self, dir_path: str, mapping: Dict[str, Callable]):
        """
        批次註冊：指定資料夾內的所有 YAML 以檔名推導工具名稱。
        mapping 需提供 name->函式 的對映。
        """
        for fn in os.listdir(dir_path):
            if fn.endswith(".yaml"):
                p = os.path.join(dir_path, fn)
                spec = yaml.safe_load(open(p, "r", encoding="utf-8"))
                name = spec.get("name")
                if name in mapping:
                    self._tools[name] = {"spec": spec, "func": mapping[name]}

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._tools)

    def get_func(self, name: str) -> Callable | None:
        ent = self._tools.get(name)
        return ent["func"] if ent else None

    def require(self, name: str) -> Dict[str, Any]:
        ent = self._tools.get(name)
        if not ent:
            raise KeyError(name)
        return ent
