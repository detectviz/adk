
# -*- coding: utf-8 -*-
import asyncio
from sre_assistant.core.assistant import SREAssistant
from adk_runtime.main import build_registry
from sre_assistant.core.policy import SRESecurityPolicy

def test_protected_namespace_denied():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_protected_namespace_denied` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    a = SREAssistant(build_registry())
    # 直接呼叫 execute 的規劃步驟由 planner 決定，這裏只檢查 policy 行為
    p = SRESecurityPolicy(registry=a.registry)
    allowed, reason, risk, req = p.evaluate_tool_call("K8sRolloutRestartTool", {"namespace":"prod","deployment_name":"api"})
    assert not allowed and risk in ("High","Critical")

def test_regex_violation():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_regex_violation` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    a = SREAssistant(build_registry())
    p = SRESecurityPolicy(registry=a.registry)
    allowed, reason, risk, req = p.evaluate_tool_call("GrafanaDashboardTool", {"service_type":"INVALID*"})
    assert not allowed

def test_approval_from_yaml_or_window():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_approval_from_yaml_or_window` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    a = SREAssistant(build_registry())
    p = SRESecurityPolicy(registry=a.registry)
    # YAML 已宣告 require_approval=true
    allowed, reason, risk, req = p.evaluate_tool_call("K8sRolloutRestartTool", {"namespace":"staging","deployment_name":"api"})
    assert allowed and req