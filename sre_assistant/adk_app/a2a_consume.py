
# -*- coding: utf-8 -*-
# 以 ADK 官方 RemoteA2aAgent 消費遠端 Agent（不要手寫 gRPC）。
from __future__ import annotations

try:
    from google.adk.a2a import RemoteA2aAgent  # 官方 API（以實際版本為準）
except Exception:
    RemoteA2aAgent = None

def get_remote_agent(endpoint: str):
    if RemoteA2aAgent is None:
        raise RuntimeError("缺少 google-adk 套件，無法使用 RemoteA2aAgent")
    return RemoteA2aAgent(endpoint)
