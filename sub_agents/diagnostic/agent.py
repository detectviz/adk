
# -*- coding: utf-8 -*-
# diagnostic 子代理薄封裝，實作仍在 `sre_assistant/experts/diagnostic.py`
from __future__ import annotations
def get_agent():
    """自動產生註解時間：2025-08-22T04:52:51.336960Z
    函式用途：回傳對應專家代理的實例或描述。"""
    try:
        from sre_assistant.experts.diagnostic import AGENT_INSTANCE as agent
        return agent
    except Exception:
        return None
