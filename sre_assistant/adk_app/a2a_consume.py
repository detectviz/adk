
# -*- coding: utf-8 -*-
# 從主協調器消費遠端 A2A 代理
from __future__ import annotations
import os
try:
    from google.adk.a2a.remote_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
except Exception as e:
    raise RuntimeError("缺少 google-adk[a2a] 依賴，請先安裝：pip install 'google-adk[a2a]'") from e

A2A_BASE = os.getenv("A2A_REMOTE_BASE","http://localhost:8001")
REMOTE_CARD = f"{A2A_BASE}{AGENT_CARD_WELL_KNOWN_PATH}"

def get_remote_diagnostic() -> RemoteA2aAgent:
    return RemoteA2aAgent(
        name="remote_diagnostic",
        description="Remote Diagnostic Expert via A2A",
        agent_card=REMOTE_CARD,
    )
