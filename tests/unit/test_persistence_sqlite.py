
# -*- coding: utf-8 -*-
# SQLite 模式：審計/事件/決策 快速測試
import os, json, tempfile, pathlib
from sre_assistant.core import persistence as P

def test_sqlite_audit_event_decision(tmp_path, monkeypatch):
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_sqlite_audit_event_decision` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `tmp_path`：參數用途請描述。
    - `monkeypatch`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    db_path = tmp_path / "sre.db"
    monkeypatch.setenv("DB_PATH", str(db_path))
    monkeypatch.delenv("PG_DSN", raising=False)

    P.init_schema()
    P.DB.write_audit("s1","u1","test",{"a":1})
    P.DB.write_event("s1","u1","evt",{"x":1})
    P.DB.write_decision("s1","agent","AgentFinished",{"q":"hi"},{"a":"ok"},0.9,123)

    evts = P.DB.list_events("s1", limit=10)
    assert len(evts) >= 1
    decs = P.DB.list_decisions(limit=10, offset=0)
    assert any(d["agent_name"]=="agent" for d in decs)