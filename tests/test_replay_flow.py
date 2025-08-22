# 檔案：tests/test_replay_flow.py
# 產生時間：2025-08-22T03:34:52.621849Z
# 專案：SRE Assistant（對齊 Google ADK），本檔案已補齊繁體中文註解以提升可讀性與可維護性。
# 說明：一般模組或測試檔，已加入中文檔頭說明。

import asyncio, json
from sre_assistant.core.assistant import SREAssistant
from adk_runtime.main import build_registry
from sre_assistant.core.persistence import DB
from fastapi.testclient import TestClient
from sre_assistant.server.app import app

def test_replay_endpoint():
    """
    2025-08-22 03:37:34Z
    函式用途：`test_replay_endpoint` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    c = TestClient(app)
    r = c.post("/api/v1/chat", headers={"X-API-Key":"devkey"}, json={"message":"diagnose cpu"})
    assert r.status_code == 200
    decisions = c.get("/api/v1/decisions", headers={"X-API-Key":"devkey"}).json()["items"]
    assert decisions
    did = decisions[0]["id"]
    rr = c.post("/api/v1/replay", headers={"X-API-Key":"devkey"}, json={"decision_id": did})
    assert rr.status_code == 200
    assert rr.json()["ok"]