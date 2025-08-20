
import os, datetime as dt
import types
import pytest

os.environ['PROM_URL'] = 'http://prometheus.local'

from agents.sre_assistant.tools import prometheus_tool as prom

def test_build_query_range_params(monkeypatch):
    class FakeResp:
        def raise_for_status(self): pass
        def json(self): return {"status":"success","data":{"resultType":"matrix","result":[]}}        
    class FakeClient:
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def get(self, url, params=None):
            assert url.endswith('/api/v1/query_range')
            assert 'query' in params and 'start' in params and 'end' in params and 'step' in params
            return FakeResp()
    monkeypatch.setattr(prom, "httpx", types.SimpleNamespace(Client=FakeClient))
    s = dt.datetime(2025,1,1)
    e = dt.datetime(2025,1,1,0,5)
    resp = prom.query_range("up", start=s, end=e, step="15s")
    assert resp["status"] == "success"
