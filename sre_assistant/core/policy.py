
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Literal

RiskLevel = Literal["Low","Medium","High","Critical"]

class SRESecurityPolicy:
    def __init__(self):
        self.protected_namespaces = {"prod", "production", "kube-system"}

    def evaluate_tool_call(self, tool_name: str, kwargs: Dict) -> tuple[bool, str, RiskLevel]:
        if tool_name.lower().startswith("k8s") and kwargs.get("namespace") in self.protected_namespaces:
            return False, "Protected namespace", "High"
        return True, "Allowed", "Low"
