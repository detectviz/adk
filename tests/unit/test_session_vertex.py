import os
from sre_assistant.core.session import pick_session_service
def test_vertex_session_fallback(monkeypatch):
    
    monkeypatch.setenv("SESSION_BACKEND","vertex")
    svc = pick_session_service()
    s = svc.get("s1"); assert isinstance(s, dict)
    svc.set("s1", {"state":{"k":"v"}})