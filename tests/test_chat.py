# 檔案：tests/test_chat.py
# 產生時間：2025-08-22T03:34:52.621849Z
# 專案：SRE Assistant（對齊 Google ADK），本檔案已補齊繁體中文註解以提升可讀性與可維護性。
# 說明：一般模組或測試檔，已加入中文檔頭說明。

# -*- coding: utf-8 -*-
import asyncio
from sre_assistant.core.assistant import SREAssistant
from adk_runtime.main import build_registry

def test_chat_diagnostic():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_chat_diagnostic` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    registry = build_registry()
    a = SREAssistant(registry)
    res = asyncio.run(a.chat("diagnose cpu high"))
    assert res["intent"]["type"] == "diagnostic"
    assert res["actions_taken"]
    assert "PromQLQueryTool" in res["metrics"]["tools_available"]