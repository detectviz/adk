
# -*- coding: utf-8 -*-
import pytest
from sre_assistant.a2a.client import execute

def test_execute_server_unavailable():
    # 連不上服務時應丟出例外（由 gRPC channel 錯誤產生），測試方捕捉即可。
    with pytest.raises(Exception):
        execute("127.0.0.1:59999", "SREMainAgent", "hello")
