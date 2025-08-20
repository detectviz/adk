
import os, datetime as dt, types
os.environ['LOKI_URL'] = 'http://loki.local'
from agents.sre_assistant.tools import loki_tool as loki

def test_query_range(monkeypatch):
    class FakeResp:
        def raise_for_status(self): pass
        def json(self): return {"status":"success","data":{"resultType":"streams","result":[]}}        
    class FakeClient:
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def get(self, url, params=None):
            assert url.endswith('/loki/api/v1/query_range')
            assert 'query' in params and 'start' in params and 'end' in params and 'limit' in params
            return FakeResp()
    monkeypatch.setattr(loki, "httpx", types.SimpleNamespace(Client=FakeClient))
    s = dt.datetime(2025,1,1)
    e = dt.datetime(2025,1,1,0,5)
    resp = loki.query_range("{app=\"web\"}", start=s, end=e, limit=10)
    assert resp["status"] == "success"
