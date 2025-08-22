
# -*- coding: utf-8 -*-
# 測試 coordinator 會從 adk.yaml 讀取模型、迭代上限與工具 allowlist（煙霧）
import os, yaml, pathlib
from adk.registry import ToolRegistry
from sre_assistant.adk_app.coordinator import build_coordinator

def test_coordinator_loads_adk_yaml(tmp_path, monkeypatch):
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_coordinator_loads_adk_yaml` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `tmp_path`：參數用途請描述。
    - `monkeypatch`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    y = {
        "agent": {"model": "gemini-2.0-flash", "tools_allowlist": ["rag_search"]},
        "runner": {"max_iterations": 7},
    }
    p = tmp_path / "adk.yaml"
    p.write_text(yaml.safe_dump(y), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    reg = ToolRegistry()
    # 後備註冊一個工具
    from sre_assistant.tools.rag_retrieve import rag_search
    reg.register("rag_search", rag_search)
    coord = build_coordinator(reg)
    # 僅做基本存在性檢查
    assert coord is not None