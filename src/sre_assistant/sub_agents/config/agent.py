# src/sre_assistant/sub_agents/config/agent.py
# 說明：(預留位置) 配置專家 (ConfigExpert) 代理。
# 未來的實作將包含生成和優化監控儀表板、警報規則等配置的工具。

from google.adk.agents import LlmAgent
from typing import Optional, Dict, Any

class ConfigAgent(LlmAgent):
    """(預留位置) 配置專家代理"""
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="ConfigExpert", model="gemini-1.5-flash-001")
        # 註：config 參數暫時保留，以備將來擴展。
        # self.config = config
