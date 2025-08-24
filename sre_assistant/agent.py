# sre_assistant/agent.py
# 說明：此檔案定義了 SRE Assistant 的主協調器 (SRECoordinator)。
# SRECoordinator 是一個 SequentialAgent，負責按順序調度各個專家子代理 (Diagnostic, Remediation, Postmortem, Config)，
# 以完成一個完整的 SRE 事件處理工作流。
from typing import Optional, Dict, Any
import asyncio
from google.adk.tools import agent_tool
from google.adk.agents import SequentialAgent, LlmAgent, ParallelAgent

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
    主協調器：實現一個基於工作流程的 SRE 自動化過程。
    此版本採用了更先進的架構，包括並行診斷和條件化修復調度。
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # 說明：初始化主協調器。
        # 這個新架構旨在提高效率和靈活性。
        agent_config = config or {}

        # --- 階段 1: 並行診斷 ---
        # 說明：此階段並行運行多個診斷代理，以快速收集全面的故障資訊。
        # 這種方法大大縮短了問題分析所需的時間。
        diagnostic_phase = ParallelAgent(
            name="ParallelDiagnostics",
            sub_agents=[
                DiagnosticAgent.create_metrics_analyzer(config=agent_config),
                DiagnosticAgent.create_log_analyzer(config=agent_config),
                DiagnosticAgent.create_trace_analyzer(config=agent_config)
            ]
        )

        # --- 階段 2: 條件化修復 (調度器) ---
        # 說明：這是一個基於 LLM 的調度器，它會分析診斷階段的輸出，
        # 並根據問題的性質和嚴重性，決定下一步要採取的修復措施。
        # 這種設計使得修復流程更具彈性，為未來引入 HITL (人工介入) 或多種修復策略奠定了基礎。
        remediation_dispatcher = LlmAgent(
            name="RemediationDispatcher",
            model="gemini-1.5-flash",  # 假設使用 Flash 模型進行快速決策
            instruction="""
            Analyze the diagnostic results provided. Your task is to determine the best course of action.
            For now, your only option is to call the 'RemediationAgent'.
            In the future, you will have more options, such as escalating to a human or triggering a rollback.
            Based on the diagnostic data, call the appropriate tool.
            """,
            tools=[agent_tool.AgentTool(agent=RemediationAgent(config=agent_config))]
        )

        # --- 階段 3 & 4: 覆盤和配置 ---
        # 說明：這些是標準的 SRE 流程，在事件解決後進行。
        # 它們目前仍然是預留位置，將在後續開發中完善。
        postmortem_phase = PostmortemAgent(config=agent_config)
        config_phase = ConfigAgent(config=agent_config)

        # --- 組裝工作流程 ---
        # 說明：將所有階段組合成一個順序執行的工作流程。
        # 這個結構清晰地定義了 SRE 事件處理的完整生命週期。
        super().__init__(
            name="SREWorkflowCoordinator",
            sub_agents=[
                diagnostic_phase,
                remediation_dispatcher,
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
