# sre_assistant/agent.py
# 說明：此檔案定義了 SRE Assistant 的主協調器 (SRECoordinator)。
# SRECoordinator 是一個 SequentialAgent，負責按順序調度各個專家子代理 (Diagnostic, Remediation, Postmortem, Config)，
# 以完成一個完整的 SRE 事件處理工作流。
from typing import Optional, Dict, Any
import asyncio
from google.adk.tools import agent_tool
from google.adk.agents import (
    SequentialAgent,
    LlmAgent,
    ParallelAgent,
    BaseAgent,
    AgentContext,
    LoopAgent,
)


# --- 導入子代理 ---
# 說明：從 sub_agents 模組中導入所有專家代理。
# DiagnosticAgent 是已實作的代理，其餘為預留位置。
from .sub_agents.diagnostic.agent import DiagnosticAgent
from .sub_agents.remediation.agent import RemediationAgent
from .sub_agents.postmortem.agent import PostmortemAgent
from .sub_agents.config.agent import ConfigAgent


# --- 新增的佔位代理 (New Placeholder Agents) ---
# 說明：這些是為了建構新的工作流程 (Workflow) 所需的佔位代理。
# 它們將在後續的開發中被完整實作。

class HITLRemediationAgent(LlmAgent):
    """預留位置：需要人工介入 (HITL) 的修復代理。"""
    def __init__(self, **kwargs):
        super().__init__(name="HITLRemediationAgent", instruction="Awaiting human intervention.", **kwargs)

class AutoRemediationWithLogging(LlmAgent):
    """預留位置：自動修復並記錄日誌的代理。"""
    def __init__(self, **kwargs):
        super().__init__(name="AutoRemediationWithLogging", instruction="Performing automated remediation with logging.", **kwargs)

class ScheduledRemediation(LlmAgent):
    """預留位置：計劃性修復代理，通常用於低優先級問題。"""
    def __init__(self, **kwargs):
        super().__init__(name="ScheduledRemediation", instruction="Scheduling remediation for a later time.", **kwargs)

class SLOTuningAgent(LlmAgent):
    """預留位置：用於在循環中調整 SLO 配置的代理。"""
    def __init__(self, **kwargs):
        super().__init__(name="SLOTuningAgent", instruction="Tuning SLOs.", **kwargs)


# --- 預留位置 (Placeholder) ---
# 說明：當所有模組都實作完成後，這些預留位置將被移除。
class SREErrorBudgetManager:
    """預留位置：SRE 錯誤預算管理器"""
    pass

class ResponseQualityTracker:
    """預留位置：回應品質追蹤器"""
    pass

# --- Workflow Agents ---
# 說明：這些是組成新工作流程核心邏輯的代理。

class ConditionalRemediation(BaseAgent):
    """
    條件化修復代理：根據診斷結果的嚴重性 (severity)，選擇不同的修復策略。
    這是實現彈性 SRE 工作流程的關鍵。
    """
    async def _run_async_impl(self, ctx: AgentContext) -> None:
        # 從上下文中獲取嚴重性，如果不存在則默認為 'P2'
        severity = ctx.state.get("severity", "P2")
        agent_config = ctx.state.get("config", {})

        print(f"Detected severity: {severity}. Dispatching appropriate agent.")

        if severity == "P0":
            # 最高優先級問題，需要人工介入
            agent = HITLRemediationAgent(config=agent_config)
        elif severity == "P1":
            # 高優先級問題，可以自動化但需要記錄
            agent = AutoRemediationWithLogging(config=agent_config)
        else:
            # 其他低優先級問題，安排後續處理
            agent = ScheduledRemediation(config=agent_config)

        await agent.run_async(ctx)


class IterativeOptimization(LoopAgent):
    """
    迭代優化代理：持續運行一個子代理 (SLOTuningAgent)，直到滿足終止條件或達到最大迭代次數。
    這對於需要多輪調整才能達到目標的場景 (如 SLO 調優) 非常有用。
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="IterativeOptimizer",
            sub_agent=SLOTuningAgent(config=config),
            max_iterations=3,
            termination_condition=lambda ctx: ctx.state.get("slo_met", False)
        )


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

        # --- 階段 2: 條件化修復 ---
        # 說明：用新實作的 ConditionalRemediation Agent 取代了舊的基於 LLM 的調度器。
        # 這種方法更明確、更可靠，並且完全符合 TASKS.md 中的設計。
        remediation_phase = ConditionalRemediation()

        # --- 階段 3: 覆盤 ---
        # 說明：覆盤階段保持不變，仍然是一個標準的 SRE 流程。
        postmortem_phase = PostmortemAgent(config=agent_config)

        # --- 階段 4: 迭代優化 ---
        # 說明：用新實作的 IterativeOptimization Agent 取代了舊的靜態 ConfigAgent。
        # 這允許系統進行多輪自我優化，直到達到預設的 SLO 目標。
        optimization_phase = IterativeOptimization(config=agent_config)

        # --- 組裝工作流程 ---
        # 說明：將所有新的和更新後的階段組合成最終的工作流程。
        # 這個新結構完全體現了 TASKS.md 中定義的先進工作流模式。
        super().__init__(
            name="SREWorkflowCoordinator",
            sub_agents=[
                diagnostic_phase,
                remediation_phase,
                postmortem_phase,
                optimization_phase
            ]
        )

def create_agent(config: Optional[Dict[str, Any]] = None) -> SRECoordinator:
    """
    Agent 工廠函數。
    參考 ADK 最佳實踐，提供一個標準的 Agent 實例化入口。
    這使得 Agent 的創建和配置與其使用分離，提高了代碼的模組化程度。
    """
    return SRECoordinator(config)
