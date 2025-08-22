
# 驗證長任務狀態存放於 Session.state['lr_ops'] 並可由 HITL API 更新
import os
from sre_assistant.core.session import InMemorySessionService
from sre_assistant.server.hitl_api import hitl_approve, hitl_reject

def test_lr_ops_in_session_and_hitl_update(monkeypatch):
    """
    2025-08-22 03:37:34Z
    函式用途：`test_lr_ops_in_session_and_hitl_update` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `monkeypatch`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    svc = InMemorySessionService()
    sid = "s1"; uid="u1"; op_id="op-123"
    st = svc.get(sid)
    st.setdefault("lr_ops", {})[op_id] = {"approved": False, "progress": 0, "result": None}
    # monkeypatch pick_session_service 以回傳本地 svc
    import sre_assistant.server.hitl_api as H
    H.pick_session_service = lambda: svc

    r1 = hitl_approve(sid, uid, op_id, approver="dev")
    assert r1["ok"] is True
    assert svc.get(sid)["lr_ops"][op_id]["approved"] is True

    r2 = hitl_reject(sid, uid, op_id, reason="no window")
    assert r2["ok"] is True
    assert svc.get(sid)["lr_ops"][op_id]["result"]["success"] is False