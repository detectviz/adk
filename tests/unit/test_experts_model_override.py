
# -*- coding: utf-8 -*-
# 驗證 runtime 在存在 experts.*.model 配置時仍可建 runner（煙霧）
from sre_assistant.adk_app.runtime import build_runner_from_config

def test_experts_model_override_smoke():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_experts_model_override_smoke` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    cfg = {
        "agent": {"model": "gemini-2.0-flash", "tools_allowlist": ["rag_search"]},
        "experts": {
            "diagnostic": {"model": "gemini-2.0-pro", "tools_allowlist": ["rag_search"]},
            "remediation": {"tools_allowlist": ["K8sRolloutRestartLongRunningTool"]},
        },
        "runner": {"max_iterations": 3}
    }
    r = build_runner_from_config(cfg)
    assert r is not None