
# 驗證 runtime 在存在 experts.*.model 配置時仍可建 runner（煙霧）
from sre_assistant.adk_app.runtime import build_runner_from_config

def test_experts_model_override_smoke():
    
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