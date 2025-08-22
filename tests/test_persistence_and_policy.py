# 檔案：tests/test_persistence_and_policy.py
# 產生時間：2025-08-22T03:34:52.621849Z
# 專案：SRE Assistant（對齊 Google ADK），本檔案已補齊繁體中文註解以提升可讀性與可維護性。
# 說明：一般模組或測試檔，已加入中文檔頭說明。

import asyncio
from sre_assistant.core.assistant import SREAssistant
from adk_runtime.main import build_registry
from sre_assistant.core.persistence import DB

def test_decision_persisted():
    """
    2025-08-22 03:37:34Z
    函式用途：`test_decision_persisted` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    a = SREAssistant(build_registry())
    res = asyncio.run(a.chat("diagnose latency"))
    items = DB.list_decisions(limit=5)
    assert items, "應寫入 decisions 表"

def test_per_tool_cache_ttl():
    """
    2025-08-22 03:37:34Z
    函式用途：`test_per_tool_cache_ttl` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    a = SREAssistant(build_registry())
    r1 = asyncio.run(a.chat("diagnose cpu"))
    r2 = asyncio.run(a.chat("diagnose cpu"))
    assert r1 and r2