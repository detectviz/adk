import asyncio, json
from sre_assistant.core.assistant import SREAssistant
from adk_runtime.main import build_registry
from sre_assistant.core.persistence import DB
from fastapi.testclient import TestClient
from sre_assistant.server.app import app

def test_replay_endpoint():
    
    c = TestClient(app)
    r = c.post("/api/v1/chat", headers={"X-API-Key":"devkey"}, json={"message":"diagnose cpu"})
    assert r.status_code == 200
    decisions = c.get("/api/v1/decisions", headers={"X-API-Key":"devkey"}).json()["items"]
    assert decisions
    did = decisions[0]["id"]
    rr = c.post("/api/v1/replay", headers={"X-API-Key":"devkey"}, json={"decision_id": did})
    assert rr.status_code == 200
    assert rr.json()["ok"]