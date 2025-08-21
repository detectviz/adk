
# -*- coding: utf-8 -*-
# 安全策略：結合 YAML 規格推導預設風險與審批需求，並加入維護時窗與值域限制。
from __future__ import annotations
from typing import Dict, Literal
import os, re, time

from ..adk_compat.registry import ToolRegistry

RiskLevel = Literal["Low","Medium","High","Critical"]

class SRESecurityPolicy:
    def __init__(self, registry: ToolRegistry | None = None):
        self.registry = registry
        self.protected_namespaces = {"prod","production","kube-system"}
        self.deny_tools = set()
        self.allow_tools = set()
        self.param_limits = {
            "GrafanaDashboardTool": {"service_type": {"max_len": 32, "regex": r"^[a-z0-9\-]+$"}},
            "K8sRolloutRestartTool": {"namespace": {"enum": ["dev","staging","qa","prod","production","kube-system"]}},
        }
        # 維護時窗（24h，例：00:00-06:00），非時窗內對變更類工具要求審批
        self.maintenance_window = os.getenv("MAINT_WINDOW", "00:00-06:00")

    def _in_window(self) -> bool:
        try:
            start, end = self.maintenance_window.split("-")
            h1, m1 = map(int, start.split(":"))
            h2, m2 = map(int, end.split(":"))
            now = time.localtime()
            cur = now.tm_hour * 60 + now.tm_min
            s = h1 * 60 + m1
            e = h2 * 60 + m2
            if s <= e:
                return s <= cur <= e
            # 跨日
            return cur >= s or cur <= e
        except Exception:
            return False

    def _spec_flags(self, tool_name: str) -> tuple[bool, RiskLevel]:
        req = False
        risk: RiskLevel = "Low"
        if self.registry:
            try:
                spec = self.registry.require(tool_name)["spec"]
                req = bool(spec.get("require_approval", False))
                risk = spec.get("risk_level", risk) or risk
            except Exception:
                pass
        return req, risk

    def evaluate_tool_call(self, tool_name: str, kwargs: Dict) -> tuple[bool, str, RiskLevel, bool]:
        # 1) 黑白名單
        if tool_name in self.deny_tools:
            return False, "Tool denied", "Critical", True
        if self.allow_tools and tool_name not in self.allow_tools:
            return False, "Not in allowlist", "High", True
        # 2) 受保護命名空間
        if tool_name.lower().startswith("k8s") and kwargs.get("namespace") in self.protected_namespaces:
            return False, "Protected namespace", "High", True
        # 3) 值域限制
        limits = self.param_limits.get(tool_name, {})
        for k, rule in limits.items():
            if k in kwargs and isinstance(kwargs[k], str):
                if "max_len" in rule and len(kwargs[k]) > rule["max_len"]:
                    return False, f"Param {k} exceeds max_len", "Medium", False
                if "regex" in rule and not re.match(rule["regex"], kwargs[k]):
                    return False, f"Param {k} regex mismatch", "Medium", False
                if "enum" in rule and kwargs[k] not in rule["enum"]:
                    return False, f"Param {k} not in enum", "Medium", False
        # 4) YAML 預設審批與風險
        req_from_spec, base_risk = self._spec_flags(tool_name)
        # 5) 維護時窗：對變更類工具（k8s/grafana）在非時窗強制審批
        change_tool = tool_name.lower().startswith(("k8s","grafana"))
        req_from_window = (not self._in_window()) and change_tool
        return True, "Allowed", base_risk, (req_from_spec or req_from_window)
