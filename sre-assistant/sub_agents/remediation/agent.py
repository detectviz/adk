# sre-assistant/sub_agents/remediation/agent.py
# 說明：(預留位置) 修復專家 (RemediationExpert) 代理。
# 未來的實作將包含執行修復操作 (如重啟服務、回滾配置) 的工具。

from google.adk.agents import LlmAgent
from typing import Optional, Dict, Any

class RemediationAgent(LlmAgent):
    """(預留位置) 修復專家代理"""
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="RemediationExpert", model="gemini-1.5-flash-001")
        # 註：config 參數暫時保留，以備將來擴展。
        # self.config = config
