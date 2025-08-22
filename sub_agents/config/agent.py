
# config 子代理薄封裝，實作仍在 `sre_assistant/experts/config.py`
from __future__ import annotations
def get_agent():
    """2025-08-22T04:52:51.338139Z
    函式用途：回傳對應專家代理的實例或描述。"""
    try:
        from sre_assistant.experts.config import AGENT_INSTANCE as agent
        return agent
    except Exception:
        return None
