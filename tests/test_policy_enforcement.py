
# -*- coding: utf-8 -*-
import asyncio
from sre_assistant.core.assistant import SREAssistant
from adk_runtime.main import build_registry
from sre_assistant.core.policy import SRESecurityPolicy

def test_protected_namespace_denied():
    a = SREAssistant(build_registry())
    # 直接呼叫 execute 的規劃步驟由 planner 決定，這裏只檢查 policy 行為
    p = SRESecurityPolicy(registry=a.registry)
    allowed, reason, risk, req = p.evaluate_tool_call("K8sRolloutRestartTool", {"namespace":"prod","deployment_name":"api"})
    assert not allowed and risk in ("High","Critical")

def test_regex_violation():
    a = SREAssistant(build_registry())
    p = SRESecurityPolicy(registry=a.registry)
    allowed, reason, risk, req = p.evaluate_tool_call("GrafanaDashboardTool", {"service_type":"INVALID*"})
    assert not allowed

def test_approval_from_yaml_or_window():
    a = SREAssistant(build_registry())
    p = SRESecurityPolicy(registry=a.registry)
    # YAML 已宣告 require_approval=true
    allowed, reason, risk, req = p.evaluate_tool_call("K8sRolloutRestartTool", {"namespace":"staging","deployment_name":"api"})
    assert allowed and req
