
# -*- coding: utf-8 -*-
# 用途：以官方 RemoteA2aAgent 消費遠端 Agent（占位）。
from __future__ import annotations

def remote_agent(endpoint: str):
    """
    函式用途：建立指向遠端 A2A Agent 的代理。
    參數說明：`endpoint` 遠端 A2A 端點 URL。
    回傳：RemoteA2aAgent 實例或 None。
    """
    try:
        from google.adk.a2a import RemoteA2aAgent  # type: ignore
        return RemoteA2aAgent(endpoint)
    except Exception:
        return None
