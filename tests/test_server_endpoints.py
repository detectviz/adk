
# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient
from sre_assistant.server.app import app

def test_health_endpoints():
    c = TestClient(app)
    assert c.get("/health/live").status_code == 200
    assert c.get("/health/ready").status_code in (200, 503)

def test_chat_and_list():
    c = TestClient(app)
    r = c.post("/api/v1/chat", headers={"X-API-Key":"devkey"}, json={"message":"diagnose cpu"})
    assert r.status_code == 200
    r2 = c.get("/api/v1/decisions", headers={"X-API-Key":"devkey"})
    assert r2.status_code == 200
