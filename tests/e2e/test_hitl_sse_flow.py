
import json
import pytest

try:
    from fastapi.testclient import TestClient
    from sre_assistant.server.app import app
except Exception:
    pytest.skip("FastAPI not available", allow_module_level=True)

client = TestClient(app)

def _read_sse_lines(resp, limit=5):
    chunked = []
    for i, line in enumerate(resp.iter_lines()):
        if i >= limit:
            break
        if line:
            chunked.append(line.decode("utf-8"))
    return chunked

def test_hitl_sse_flow():
    # Start SSE stream
    with client.stream("GET", "/api/v1/events/hitl") as resp:
        assert resp.status_code == 200
        # Trigger mock event
        r = client.post("/api/v1/hitl/mock")
        assert r.status_code == 200
        # Consume a few SSE lines
        lines = _read_sse_lines(resp, limit=3)
        body = "".join(lines)
        assert "adk_request_credential" in body
