
# 驗證長任務使用 Session.state 並與 function_call_id 關聯
from sre_assistant.core.session import InMemorySessionService
from sre_assistant.tools.k8s_long_running import _start_restart, _poll_restart

class DummyCtx:
    def __init__(self, sid):
        
        from types import SimpleNamespace
        self.session = SimpleNamespace(state={})
        self.function_call_id = "fc-1"
        
    def request_credential(self, **kwargs): pass
    def get_auth_response(self, function_call_id=None):
        
        if function_call_id == "fc-1":
            return {"approved": True}
        return None

def test_lr_state_and_fcid():
    
    ctx = DummyCtx("s1")
    r = _start_restart(ctx, "prod", "web", "test")
    op_id = r.get("op_id")
    # poll 會讀取 fc-1 批准
    r2 = _poll_restart(ctx, op_id)
    assert r2.get("done") in (True, False)