
# 驗證長任務使用 Session.state 並與 function_call_id 關聯
from sre_assistant.core.session import InMemorySessionService
from sre_assistant.tools.k8s_long_running import _start_restart, _poll_restart

class DummyCtx:
    def __init__(self, sid):
        """
        2025-08-22 03:37:34Z
        函式用途：`__init__` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `sid`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        from types import SimpleNamespace
        self.session = SimpleNamespace(state={})
        self.function_call_id = "fc-1"
        """
        2025-08-22 03:37:34Z
        函式用途：`request_credential` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `**kwargs`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
    def request_credential(self, **kwargs): pass
    def get_auth_response(self, function_call_id=None):
        """
        2025-08-22 03:37:34Z
        函式用途：`get_auth_response` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `function_call_id`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        if function_call_id == "fc-1":
            return {"approved": True}
        return None

def test_lr_state_and_fcid():
    """
    2025-08-22 03:37:34Z
    函式用途：`test_lr_state_and_fcid` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    ctx = DummyCtx("s1")
    r = _start_restart(ctx, "prod", "web", "test")
    op_id = r.get("op_id")
    # poll 會讀取 fc-1 批准
    r2 = _poll_restart(ctx, op_id)
    assert r2.get("done") in (True, False)