
# -*- coding: utf-8 -*-
import subprocess
from agents.sre_assistant.runtime.bridge_client import BridgeClient

def test_bridge_client_parse(monkeypatch):
    class P:
        def __init__(self): self.stdout='{"status":"ok","message":"","data":{"echo":true}}'; self.stderr=''
    def fake_run(cmd, stdout, stderr, text): return P()
    monkeypatch.setattr(subprocess, "run", fake_run)
    bc = BridgeClient(bin_path="/nonexistent")
    out = bc.exec("diagnostic","check_disk","80")
    assert out["status"] == "ok" and out["data"]["echo"] is True
