
import types, datetime as dt, os
from agents.sre_assistant.runtime.tool_runner import ToolRunner
from contracts.messages.sre_messages import ToolRequest, MetricQuery, TimeRange, LogQuery

def test_prom_query_range(monkeypatch):
    # Fake prom module behavior via monkeypatch inside runner namespace
    import agents.sre_assistant.runtime.tool_runner as tr
    class FakeProm:
        def query_range(self, *a, **kw): pass
    def fake_query_range(query, start, end, step):
        return {"status":"success","data":{"result":[],"sampled":True}}
    monkeypatch.setattr(tr.prom, "query_range", fake_query_range)

    runner = ToolRunner()
    trng = TimeRange(start_ms=1700000000000, end_ms=1700000030000)
    req = ToolRequest(name="prom.query_range", metric=MetricQuery(promql="up", range=trng), params={"step":"30s"})
    resp = runner.invoke("prom.query_range", req)
    assert resp.success and resp.status == "ok"

def test_loki_query_range(monkeypatch):
    import agents.sre_assistant.runtime.tool_runner as tr
    def fake_query_range(logql, start, end, limit, direction):
        return {"status":"success","data":{"resultType":"streams","result":[]}}
    monkeypatch.setattr(tr.loki, "query_range", fake_query_range)
    runner = ToolRunner()
    trng = TimeRange(start_ms=1700000000000, end_ms=1700000030000)
    req = ToolRequest(name="loki.query_range", log=LogQuery(logql="{app=\"web\"}", range=trng, limit=10))
    resp = runner.invoke("loki.query_range", req)
    assert resp.success

def test_graf_annotate(monkeypatch):
    import agents.sre_assistant.runtime.tool_runner as tr
    def fake_annotate(text, dashboard_uid=None, panel_id=None, tags=None, time_ms=None, time_end_ms=None, timeout=10.0):
        return {"id": 123}
    monkeypatch.setattr(tr.graf, "annotate", fake_annotate)
    runner = ToolRunner()
    req = ToolRequest(name="graf.annotate", params={"text":"incident start"})
    resp = runner.invoke("graf.annotate", req)
    assert resp.success and resp.data["id"] == 123
