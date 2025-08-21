
# -*- coding: utf-8 -*-
# 安全策略（強化版）：支援 policy.d/*.yaml 熱載入，合併 YAML 與動態規則。
from __future__ import annotations
from typing import Dict, Literal, Any
import os, re, time, glob, yaml

from ..adk_compat.registry import ToolRegistry

RiskLevel = Literal["Low","Medium","High","Critical"]

class SRESecurityPolicy:
    def __init__(self, registry: ToolRegistry | None = None, policy_dir: str | None = None):
        self.registry = registry
        self.policy_dir = policy_dir or os.getenv("POLICY_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "policy.d"))
        self._mtime = 0.0
        # 內建規則
        self.defaults = {
            "protected_namespaces": ["prod","production","kube-system"],
            "maintenance_window": os.getenv("MAINT_WINDOW","00:00-06:00"),
            "param_limits": {
                "GrafanaDashboardTool": {"service_type": {"max_len": 32, "regex": r"^[a-z0-9\-]+$"}},
                "K8sRolloutRestartTool": {"namespace": {"enum": ["dev","staging","qa","prod","production","kube-system"]}},
            },
            "deny_tools": [],
            "allow_tools": []
        }
        self.runtime = dict(self.defaults)
        self._load_if_needed()

    def _load_if_needed(self):
        # 每次調用時，若 policy.d 有更新則重新載入
        try:
            newest = 0.0
            files = glob.glob(os.path.join(self.policy_dir, "*.yaml"))
            for f in files:
                newest = max(newest, os.path.getmtime(f))
            if newest <= self._mtime:
                return
            self._mtime = newest
            rt = dict(self.defaults)
            for f in files:
                try:
                    doc = yaml.safe_load(open(f, "r", encoding="utf-8"))
                    for k, v in (doc or {}).items():
                        rt[k] = v
                except Exception:
                    continue
            self.runtime = rt
        except Exception:
            # 安全起見，保留上次設定
            pass

    def _in_window(self) -> bool:
        w = self.runtime.get("maintenance_window","00:00-06:00")
        try:
            start, end = w.split("-")
            h1, m1 = map(int, start.split(":"))
            h2, m2 = map(int, end.split(":"))
            now = time.localtime()
            cur = now.tm_hour * 60 + now.tm_min
            s = h1 * 60 + m1
            e = h2 * 60 + m2
            if s <= e:
                return s <= cur <= e
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

    def evaluate_tool_call(self, tool_name: str, kwargs: Dict[str, Any]) -> tuple[bool, str, RiskLevel, bool]:
        self._load_if_needed()
        deny = set(self.runtime.get("deny_tools", []))
        allow = set(self.runtime.get("allow_tools", []))
        protected = set(self.runtime.get("protected_namespaces", []))
        limits = self.runtime.get("param_limits", {})

        if tool_name in deny:
            return False, "Tool denied", "Critical", True
        if allow and tool_name not in allow:
            return False, "Not in allowlist", "High", True

        if tool_name.lower().startswith("k8s") and kwargs.get("namespace") in protected:
            return False, "Protected namespace", "High", True

        limit = limits.get(tool_name, {})
        for k, rule in limit.items():
            if k in kwargs and isinstance(kwargs[k], str):
                if "max_len" in rule and len(kwargs[k]) > rule["max_len"]:
                    return False, f"Param {k} exceeds max_len", "Medium", False
                if "regex" in rule and not re.match(rule["regex"], kwargs[k]):
                    return False, f"Param {k} regex mismatch", "Medium", False
                if "enum" in rule and kwargs[k] not in rule["enum"]:
                    return False, f"Param {k} not in enum", "Medium", False

        req_from_spec, base_risk = self._spec_flags(tool_name)
        change_tool = tool_name.lower().startswith(("k8s","grafana"))
        req_from_window = (not self._in_window()) and change_tool
        return True, "Allowed", base_risk, (req_from_spec or req_from_window)
