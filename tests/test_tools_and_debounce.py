
# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient
from sre_assistant.server.app import app

def test_tools_listing():
    c = TestClient(app)
    r = c.get("/api/v1/tools", headers={"X-API-Key":"devkey"})
    assert r.status_code == 200
    tools = r.json()["items"]
    assert any(t["name"]=="PromQLQueryTool" for t in tools)

def test_debounce_session_scope():
    c = TestClient(app)
    # 同一訊息不同 session 應允許
    p1 = c.post("/api/v1/chat", headers={"X-API-Key":"devkey"}, json={"message":"diagnose cpu", "session_id":"s1"})
    p2 = c.post("/api/v1/chat", headers={"X-API-Key":"devkey"}, json={"message":"diagnose cpu", "session_id":"s2"})
    assert p1.status_code == 200 and p2.status_code == 200
    # 同一 session 立即重送應被去抖
    p3 = c.post("/api/v1/chat", headers={"X-API-Key":"devkey"}, json={"message":"diagnose cpu", "session_id":"s2"})
    assert p3.status_code == 409
