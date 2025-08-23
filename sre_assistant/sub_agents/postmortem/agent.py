# sre_assistant/sub_agents/postmortem/agent.py
# 說明：(預留位置) 覆盤專家 (PostmortemExpert) 代理。
# 未來的實作將包含生成結構化事後檢討報告的工具。

from google.adk.agents import LlmAgent
from typing import Optional, Dict, Any

class PostmortemAgent(LlmAgent):
    """(預留位置) 覆盤專家代理"""
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="PostmortemExpert", model="gemini-1.5-flash-001")
        # 註：config 參數暫時保留，以備將來擴展。
        # self.config = config
