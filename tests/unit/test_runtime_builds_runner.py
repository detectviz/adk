
# 驗證 runtime 能讀取 adk.yaml 並建立 Runner
import yaml, pathlib
from sre_assistant.adk_app.runtime import build_runner_from_config

def test_build_runner_from_config_minimal(tmp_path):
    
    cfg = {
        "agent": {"model": "gemini-2.0-flash", "tools_allowlist": ["rag_search"]},
        "runner": {"max_iterations": 5},
        "experts": {"diagnostic": {"tools_allowlist": ["rag_search"]}}
    }
    r = build_runner_from_config(cfg)
    assert r is not None