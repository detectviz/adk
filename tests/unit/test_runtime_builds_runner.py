
# -*- coding: utf-8 -*-
# 驗證 runtime 能讀取 adk.yaml 並建立 Runner
import yaml, pathlib
from sre_assistant.adk_app.runtime import build_runner_from_config

def test_build_runner_from_config_minimal(tmp_path):
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_build_runner_from_config_minimal` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `tmp_path`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    cfg = {
        "agent": {"model": "gemini-2.0-flash", "tools_allowlist": ["rag_search"]},
        "runner": {"max_iterations": 5},
        "experts": {"diagnostic": {"tools_allowlist": ["rag_search"]}}
    }
    r = build_runner_from_config(cfg)
    assert r is not None