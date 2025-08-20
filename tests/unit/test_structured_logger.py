
# -*- coding: utf-8 -*-
# 測試結構化日誌輸出（繁體中文註解）。
import io, sys, json
from agents.sre_assistant.runtime.structured_logger import info

def test_logger_outputs_json(monkeypatch):
    buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buf)
    info("unit_test", foo="bar", n=1)
    line = buf.getvalue().strip()
    rec = json.loads(line)
    assert rec["event"] == "unit_test"
    assert rec["foo"] == "bar"
    assert rec["n"] == 1
    assert "ts" in rec and "level" in rec
