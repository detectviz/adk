
# -*- coding: utf-8 -*-
# 測試：HITL 審計寫入點在無 db 時不丟例外，且在有 db.execute 時會被呼叫
from sre_assistant.core.audit import write_hitl_audit

class DummyDB:
    def __init__(self): self.calls=[]
    def execute(self, sql, params): self.calls.append((sql, params))

def test_write_hitl_audit_no_db():
    # 無 db 物件，應靜默跳過
    write_hitl_audit(None, "fc1", True, "alice", "ok")

def test_write_hitl_audit_with_db():
    db = DummyDB()
    write_hitl_audit(db, "fc1", False, "bob", "deny")
    assert len(db.calls)==1
