
import os, types
os.environ['GRAFANA_URL'] = 'http://grafana.local'
from agents.sre_assistant.tools import grafana_tool as graf

def test_annotate(monkeypatch):
    class FakeResp:
        def raise_for_status(self): pass
        def json(self): return {"id": 123}
    class FakeClient:
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def post(self, url, json=None):
            assert url.endswith('/api/annotations')
            assert 'text' in json
            return FakeResp()
    monkeypatch.setattr(graf, "httpx", types.SimpleNamespace(Client=FakeClient))
    out = graf.annotate("incident start")
    assert out["id"] == 123
