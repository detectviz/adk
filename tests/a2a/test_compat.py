
# -*- coding: utf-8 -*-
# 目的：模擬 ADK 官方樣式的 Execute 互通（訊息欄位/錯誤處理）。
import time, pytest
try:
    from sre_assistant.a2a.server import serve
    from sre_assistant.a2a.client import execute
    HAS=True
except Exception:
    HAS=False

@pytest.mark.skipif(not HAS, reason="缺少 gRPC 產物或依賴")
def test_execute_roundtrip_fields():
    class Dummy: pass
    srv = serve(Dummy(), host="127.0.0.1", port=50060)
    time.sleep(0.2)
    try:
        res = execute("127.0.0.1:50060", agent="SREMainAgent", text="diag")
        assert "output" in res and "trace_id" in res
    finally:
        srv.stop(0)
