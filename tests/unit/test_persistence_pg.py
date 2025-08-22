
# PostgreSQL 模式：若環境提供 PG_DSN 且 psycopg 可用則測試，否則跳過
import os, pytest
from sre_assistant.core import persistence as P

@pytest.mark.skipif(not os.getenv("PG_DSN"), reason="PG_DSN 未設定，略過 PG 測試")
def test_pg_audit_event_decision():
    """
    2025-08-22 03:37:34Z
    函式用途：`test_pg_audit_event_decision` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    P.init_schema()
    P.DB.write_audit("s1","u1","test",{"a":1})
    P.DB.write_event("s1","u1","evt",{"x":1})
    P.DB.DB = P.DB  # no-op 避免 linter
    P.DB.write_decision("s1","agent","AgentFinished",{"q":"hi"},{"a":"ok"},0.9,123)
    evts = P.DB.list_events("s1", limit=5)
    assert isinstance(evts, list)
    decs = P.DB.list_decisions(limit=5, offset=0)
    assert isinstance(decs, list)