# sre_assistant/sub_agents/postmortem/agent.py
# 說明：(預留位置) 覆盤專家 (PostmortemExpert) 代理。
# 未來的實作將包含生成結構化事後檢討報告的工具。

from google.adk.agents import LlmAgent
from typing import Optional, Dict, Any

class PostmortemAgent(LlmAgent):
    """(預留位置) 覆盤專家代理"""
    def __init__(self, **kwargs: Any):
        # 說明：修改 __init__ 以接受 **kwargs，使其與 Pydantic 模型的行為一致。
        # 這樣可以從外部傳入 'name', 'config' 等參數，同時提供預設值。
        kwargs.setdefault("name", "PostmortemExpert")
        kwargs.setdefault("model", "gemini-1.5-flash-001")
        super().__init__(**kwargs)
