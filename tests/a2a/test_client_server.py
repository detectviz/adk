
# -*- coding: utf-8 -*-
import time, pytest
try:
    from sre_assistant.a2a.server import serve
    from sre_assistant.a2a.client import execute
    HAS=True
except Exception:
    HAS=False

@pytest.mark.skipif(not HAS, reason="缺少 gRPC 產物或依賴")
def test_a2a_execute_smoke():
    class Dummy: pass
    srv = serve(Dummy(), host="127.0.0.1", port=50059)
    time.sleep(0.5)
    try:
        res = execute("127.0.0.1:50059", "SREMainAgent", "ping")
        assert "ping" in res.get("output","")
    finally:
        srv.stop(0)
