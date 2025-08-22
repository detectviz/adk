import os
from importlib import reload
import sre_assistant.core.config as cfg

def test_get_and_get_list_env_override(monkeypatch, tmp_path):
    # 以環境變數覆寫
    monkeypatch.setenv("ADK_AGENT_NAME","override-name")
    monkeypatch.setenv("ADK_POLICY_HIGH_RISK_NAMESPACES","ns1, ns2 ,ns3")
    reload(cfg)
    assert cfg.get("agent.name")=="override-name"
    lst = cfg.get_list("policy.high_risk_namespaces", [])
    assert lst==["ns1","ns2","ns3"]
