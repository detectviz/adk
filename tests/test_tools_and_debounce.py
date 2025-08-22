# 檔案：tests/test_tools_and_debounce.py
# 產生時間：2025-08-22T03:34:52.621849Z
# 專案：SRE Assistant（對齊 Google ADK），本檔案已補齊繁體中文註解以提升可讀性與可維護性。
# 說明：一般模組或測試檔，已加入中文檔頭說明。

# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient
from sre_assistant.server.app import app

def test_tools_listing():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_tools_listing` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    c = TestClient(app)
    r = c.get("/api/v1/tools", headers={"X-API-Key":"devkey"})
    assert r.status_code == 200
    tools = r.json()["items"]
    assert any(t["name"]=="PromQLQueryTool" for t in tools)

def test_debounce_session_scope():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_debounce_session_scope` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    c = TestClient(app)
    # 同一訊息不同 session 應允許
    p1 = c.post("/api/v1/chat", headers={"X-API-Key":"devkey"}, json={"message":"diagnose cpu", "session_id":"s1"})
    p2 = c.post("/api/v1/chat", headers={"X-API-Key":"devkey"}, json={"message":"diagnose cpu", "session_id":"s2"})
    assert p1.status_code == 200 and p2.status_code == 200
    # 同一 session 立即重送應被去抖
    p3 = c.post("/api/v1/chat", headers={"X-API-Key":"devkey"}, json={"message":"diagnose cpu", "session_id":"s2"})
    assert p3.status_code == 409