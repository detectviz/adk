
# -*- coding: utf-8 -*-
# 用途：將 ADK Agent 以官方 A2A 方式暴露（占位）。
# 真正實作需依官方套件 `google.adk.a2a`，此處僅保留明確對齊接口。
from __future__ import annotations
from typing import Any

def to_a2a_app(agent: Any):
    """
    函式用途：把本地 agent 轉為可被 A2A 訪問的 ASGI/WSGI 應用。
    參數說明：`agent` ADK Agent 實例。
    回傳：ASGI 應用或佔位 None（若未安裝官方套件）。
    """
    try:
        from google.adk.a2a import to_a2a  # type: ignore
        return to_a2a(agent)
    except Exception:
        return None
