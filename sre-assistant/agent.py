# sre-assistant/agent.py
# 說明：此檔案定義了 SRE Assistant 的主協調器 (SRECoordinator)。
# SRECoordinator 是一個 SequentialAgent，負責按順序調度各個專家子代理 (Diagnostic, Remediation, Postmortem, Config)，
# 以完成一個完整的 SRE 事件處理工作流。
from google.adk.agents import SequentialAgent, LlmAgent, ParallelAgent
from google.adk.tools.agent_tool import AgentTool
from typing import Optional, Dict, Any

# --- 導入子代理 ---
# 說明：從 sub_agents 模組中導入所有專家代理。
# DiagnosticAgent 是已實作的代理，其餘為預留位置。
from .sub_agents.diagnostic.agent import DiagnosticAgent
from .sub_agents.remediation.agent import RemediationAgent
from .sub_agents.postmortem.agent import PostmortemAgent
from .sub_agents.config.agent import ConfigAgent


# --- 預留位置 (Placeholder) ---
# 說明：當所有模組都實作完成後，這些預留位置將被移除。
class SREErrorBudgetManager:
    """預留位置：SRE 錯誤預算管理器"""
    pass

class ResponseQualityTracker:
    """預留位置：回應品質追蹤器"""
    pass

# --- 主協調器 ---

class SRECoordinator(SequentialAgent):
    """
    主協調器：實現標準 SRE 工作流。
    此版本整合了已完成的 DiagnosticExpert，並為其他專家使用預留位置。
    詳細的回呼、SRE 指標整合和錯誤處理將在後續步驟中添加。
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # 說明：初始化主協調器。
        # 這裡定義了由各個子代理組成的 SRE 工作流。
        # DiagnosticExpert 已被整合，其餘專家仍為預留位置。

        # 將 config 作為局部變數，用於初始化子代理，而不是將其設為 SRECoordinator 的屬性，
        # 以避免 Pydantic 的欄位驗證錯誤。
        agent_config = config or {}

        # 實例化預留位置管理器 (也是局部變數)
        slo_manager = SREErrorBudgetManager()
        response_quality_tracker = ResponseQualityTracker()

        # --- 建立子代理 ---

        # 診斷階段 - 並行檢查
        # 說明：使用 ParallelAgent 讓三個不同專長的診斷代理並行執行，
        # 這能更快地從指標、日誌和追蹤中收集資訊。
        diagnostic_phase = ParallelAgent(
            name="DiagnosticPhase",
            sub_agents=[
                DiagnosticAgent.create_metrics_analyzer(),
                DiagnosticAgent.create_log_analyzer(),
                DiagnosticAgent.create_trace_analyzer()
            ]
        )

        # 修復、覆盤和配置階段 (仍使用預留位置)
        remediation_phase = RemediationAgent(config=agent_config)
        postmortem_phase = PostmortemAgent(config=agent_config)
        config_phase = ConfigAgent(config=agent_config)

        # 根據 ADK 的 API，SequentialAgent 的建構子需要 'name' 和 'sub_agents' 參數。
        # 'instruction' 參數不適用於非 LLM 的 WorkflowAgent。
        # WorkflowAgent 的 sub_agents 應該是 Agent 實例，而不是 AgentTool。
        super().__init__(
            name="SRECoordinator",
            sub_agents=[
                diagnostic_phase,
                remediation_phase,
                postmortem_phase,
                config_phase
            ]
        )

def create_agent(config: Optional[Dict[str, Any]] = None) -> SRECoordinator:
    """
    Agent 工廠函數。
    參考 ADK 最佳實踐，提供一個標準的 Agent 實例化入口。
    這使得 Agent 的創建和配置與其使用分離，提高了代碼的模組化程度。
    """
    return SRECoordinator(config)
