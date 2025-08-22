# 測試：Session 雙實作可用（資料庫模式僅在裝有 SQLAlchemy 且設 DATABASE_URL 時測）
import os
from sre_assistant.core.session import InMemorySessionService

def test_inmemory_session_basic():
    svc = InMemorySessionService()
    st = svc.get_state("s1")
    assert isinstance(st, dict) and st == {}
    st['x']=1
    svc.set_state("s1", st)
    assert svc.get_state("s1")['x']==1
