
import sre_assistant.server.app as appmod
from sre_assistant.core.persistence import DB, init_schema
def test_events_api_sqlite(monkeypatch):
    monkeypatch.delenv("PG_DSN", raising=False)
    init_schema()
    DB.write_event("sessX","user","Dummy",{"a":1})
    DB.write_decision("sessX","agent","DecisionType",{"q":"x"},{"a":"y"},0.5,10)
    ev = appmod.get_session_events.__wrapped__("sessX", limit=10, _=None)
    dc = appmod.get_session_decisions.__wrapped__("sessX", limit=10, offset=0, _=None)
    assert "events" in ev and "decisions" in dc
