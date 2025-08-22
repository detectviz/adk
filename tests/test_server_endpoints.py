# 檔案：tests/test_server_endpoints.py
# 產生時間：2025-08-22T03:34:52.621849Z
# 專案：SRE Assistant（對齊 Google ADK），本檔案已補齊繁體中文註解以提升可讀性與可維護性。
# 說明：一般模組或測試檔，已加入中文檔頭說明。

# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient
from sre_assistant.server.app import app

def test_health_endpoints():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_health_endpoints` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    c = TestClient(app)
    assert c.get("/health/live").status_code == 200
    assert c.get("/health/ready").status_code in (200, 503)

def test_chat_and_list():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_chat_and_list` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    c = TestClient(app)
    r = c.post("/api/v1/chat", headers={"X-API-Key":"devkey"}, json={"message":"diagnose cpu"})
    assert r.status_code == 200
    r2 = c.get("/api/v1/decisions", headers={"X-API-Key":"devkey"})
    assert r2.status_code == 200