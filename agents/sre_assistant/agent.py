from sre_adk import Agent, tool
from diagnostic_expert import DiagnosticExpert
from config_expert import ConfigExpert
from remediation_expert import RemediationExpert

class SREAssistant(Agent):
    """主助理 - 協調各專家"""
    
    name = "SRE Assistant"
    description = "您的智能運維助理"
    
    def __init__(self):
        super().__init__()
        self.diagnostic = DiagnosticExpert()
        self.config = ConfigExpert()
        self.remediation = RemediationExpert()
    
    async def process(self, message: str) -> str:
        """
        處理用戶訊息的主邏輯
        """
        # 意圖識別
        intent = self.understand_intent(message)
        
        # 路由到合適的專家
        if intent.category == "diagnostic":
            result = await self.diagnostic.execute(intent)
        elif intent.category == "config":
            result = await self.config.execute(intent)
        elif intent.category == "fix":
            result = await self.remediation.execute(intent)
        else:
            result = await self.handle_general(intent)
        
        # 生成人性化回應
        return self.generate_response(result)
    
    def understand_intent(self, message: str):
        """意圖理解 - 可以很簡單"""
        keywords = {
            "diagnostic": ["檢查", "診斷", "狀態", "健康"],
            "config": ["配置", "設定", "修改", "更新"],
            "fix": ["修復", "清理", "重啟", "解決"]
        }
        
        for category, words in keywords.items():
            if any(word in message for word in words):
                return Intent(category=category, message=message)
        
        return Intent(category="general", message=message)