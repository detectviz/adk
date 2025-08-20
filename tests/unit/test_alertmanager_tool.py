
import os, types
os.environ['AM_URL'] = 'http://am.local'
from agents.sre_assistant.tools import alertmanager_tool as am

def test_list_alerts(monkeypatch):
    class FakeResp:
        def raise_for_status(self): pass
        def json(self): return []
    class FakeClient:
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def get(self, url, params=None):
            assert url.endswith('/api/v2/alerts')
            return FakeResp()
    monkeypatch.setattr(am, "httpx", types.SimpleNamespace(Client=FakeClient))
    out = am.list_alerts()
    assert isinstance(out, list)
