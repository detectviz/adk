
# -*- coding: utf-8 -*-
# A2A TLS 測試骨架（若無憑證與環境，跳過）
import os, pytest
from sre_assistant.adk_app.a2a_client import relay

pytestmark = pytest.mark.skip(reason="需要本地 TLS 憑證與 server 進程")

def test_relay_tls():
    out = relay("localhost:50052","s1","diag","hello",{"x":1}, use_tls=True, traceparent="00-...")
    assert isinstance(out, dict)
