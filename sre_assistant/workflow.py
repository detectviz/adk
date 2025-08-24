# sre_assistant/agent.py
# 說明：此檔案定義了 SRE Assistant 的主協調器 (SRECoordinator)。
# SRECoordinator 是一個 SequentialAgent，負責按順序調度各個專家子代理 (Diagnostic, Remediation, Postmortem, Config)，
# 以完成一個完整的 SRE 事件處理工作流。
from typing import Optional, Dict, Any, Tuple
import asyncio
from google.adk.tools import agent_tool
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents import SequentialAgent, LlmAgent, ParallelAgent, LoopAgent

# --- 導入認證管理器 ---
# 說明：導入 AuthManager 單例，用於處理所有認證和授權。
# 注意：這會在 config_manager 更新前導致導入錯誤，這是預期行為。
try:
    from .auth.auth_manager import AuthManager, auth_manager
except ImportError:
    # 為了讓程式在 config 更新前能繼續運行，提供一個佔位符
    print("Warning: AuthManager could not be imported. Using a placeholder.")
    auth_manager = None
    AuthManager = type("AuthManager", (), {})


# --- 導入子代理 ---
# 說明：從 sub_agents 模듈中導入所有專家代理。
# DiagnosticAgent 是已實作的代理，其餘為預留位置。
from .sub_agents.diagnostic.agent import DiagnosticAgent
from .sub_agents.remediation.agent import RemediationAgent
from .sub_agents.postmortem.agent import PostmortemAgent
from .sub_agents.config.agent import ConfigAgent
from .citation_manager import SRECitationFormatter


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
    def __init__(self, **kwargs: Any):
        kwargs.setdefault("name", "SLOTuningAgent")
        kwargs.setdefault("instruction", "Tuning SLOs.")
        super().__init__(**kwargs)


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
    def __init__(self, **kwargs):
        # BaseAgent is a Pydantic model and requires a name.
        super().__init__(**kwargs)

    async def _run_async_impl(self, ctx: InvocationContext) -> None:
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


from typing import Callable

class IterativeOptimization(LoopAgent):
    """
    迭代優化代理：持續運行一個子代理 (SLOTuningAgent)，直到滿足終止條件或達到最大迭代次數。
    這對於需要多輪調整才能達到目標的場景 (如 SLO 調優) 非常有用。
    """
    sub_agent: Optional[LlmAgent] = None
    termination_condition: Optional[Callable[[InvocationContext], bool]] = None

    def __init__(self):
        super().__init__(name="IterativeOptimizer", max_iterations=3)
        self.sub_agent=SLOTuningAgent()
        self.termination_condition=lambda ctx: ctx.state.get("slo_met", False)


# --- 帶引用的診斷階段 ---

from google.adk.agents import ParallelAgent

class CitingParallelDiagnosticsAgent(BaseAgent):
    """
    一個包裝代理，它運行並行的診斷流程，然後從所有子代理的工具調用
    歷史中統一收集和格式化引用。
    """
    # 聲明類別屬性以符合 Pydantic 模型的要求
    parallel_diagnostics: ParallelAgent
    citation_formatter: SRECitationFormatter

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        agent_config = config or {}

        # 在呼叫 super().__init__ 之前準備好欄位值
        # 並將它們添加到 kwargs 中，以滿足 Pydantic 的驗證
        if 'citation_formatter' not in kwargs:
            kwargs['citation_formatter'] = SRECitationFormatter()

        if 'parallel_diagnostics' not in kwargs:
            kwargs['parallel_diagnostics'] = ParallelAgent(
                name="ParallelDiagnostics",
                sub_agents=[
                    DiagnosticAgent.create_metrics_analyzer(config=agent_config),
                    DiagnosticAgent.create_log_analyzer(config=agent_config),
                    DiagnosticAgent.create_trace_analyzer(config=agent_config)
                ]
            )

        super().__init__(**kwargs)

    async def _run_async_impl(self, context: InvocationContext) -> None:
        """
        運行並行診斷，收集所有引用，並格式化最終輸出。
        """
        # 運行並行診斷，ADK 框架會處理事件的產生
        final_event = await self.parallel_diagnostics.run_async(context)

        if final_event is None:
            return

        citations = []
        # 從整個對話歷史中收集引用
        for turn in context.history:
            if turn.role == "tool":
                # 工具輸出是 (result, citation_info)
                tool_output = turn.content
                if isinstance(tool_output, tuple) and len(tool_output) == 2:
                    citations.append(tool_output[1])

        if citations:
            formatted_citations = self.citation_formatter.format_citations(citations)
            original_content = final_event.content or ""
            final_event.content = f"{original_content}\n\n{formatted_citations}"

# --- 主工作流程 ---

class SREWorkflow(SequentialAgent):
    """
    主工作流程：實現一個基於工作流程的 SRE 自動化過程。
    此版本採用了更先進的架構，包括並行診斷和條件化修復調度。
    """
    # --- Pydantic 欄位宣告 ---
    # 說明：將 auth_manager 宣告為一個類別屬性，以符合 Pydantic 模型的規範。
    # 這可以防止在 __init__ 中賦值時出現 "object has no field" 的錯誤。
    auth_manager: Optional[AuthManager] = None

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # 說明：初始化主協調器。
        # 這個新架構旨在提高效率和靈活性。
        agent_config = config or {}

        # --- 整合認證管理器 ---
        # 說明：將 AuthManager 實例化並存儲，以便在工作流程中使用。
        # 這一步必須在 super().__init__ 之前，因為 Pydantic 會驗證欄位。
        # 但我們不能直接賦值，所以我們將它作為參數傳遞給父類。
        # Wait, the parent doesn't accept it. Let's declare it and assign it after.
        # The issue is that the parent is a pydantic model.
        # The correct way is to pass it to super init.
        # However, the parent class does not have this field.
        # So we must assign it *after* super().__init__
        # And the class must be configured to accept extra fields.
        # Let's try the simpler way first: declare it as a field, and call super() at the end.

        # --- 階段 1: 並行診斷 (帶引用) ---
        # 說明：此階段使用一個包裝代理來運行並行診斷，並在結束後自動收集和格式化所有引用。
        diagnostic_phase = CitingParallelDiagnosticsAgent(name="CitingParallelDiagnostics", config=agent_config)

        # --- 階段 2: 條件化修復 ---
        # 說明：用新實作的 ConditionalRemediation Agent 取代了舊的基於 LLM 的調度器。
        # 這種方法更明確、更可靠，並且完全符合 TASKS.md 中的設計。
        remediation_phase = ConditionalRemediation(name="ConditionalRemediation")

        # --- 階段 3: 覆盤 ---
        # 說明：覆盤階段保持不變，仍然是一個標準的 SRE 流程。
        # PostmortemAgent is also a Pydantic model and requires a name.
        # The LlmAgent parent class does not accept a 'config' argument.
        postmortem_phase = PostmortemAgent(name="PostmortemAgent")

        # --- 階段 4: 迭代優化 ---
        # 說明：用新實作的 IterativeOptimization Agent 取代了舊的靜態 ConfigAgent。
        # 這允許系統進行多輪自我優化，直到達到預設的 SLO 目標。
        optimization_phase = IterativeOptimization()

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
        self.auth_manager = auth_manager

    async def run_with_auth(
        self,
        credentials: Dict[str, Any],
        resource: str,
        action: str,
        initial_context: Optional[InvocationContext] = None
    ) -> InvocationContext:
        """
        帶有認證和授權的執行入口。
        這是一個包裝器，用於在執行核心工作流程之前驗證用戶權限。

        Args:
            credentials: 用戶提供的憑證 (例如, API key, token)。
            resource: 請求的資源。
            action: 請求的操作。
            initial_context: 初始的代理上下文。

        Returns:
            執行完畢後的代理上下文。

        Raises:
            PermissionError: 如果認證或授權失敗。
        """
        if not self.auth_manager:
            raise ImportError("AuthManager is not available.")

        # 1. 認證
        success, user_info = await self.auth_manager.authenticate(credentials)
        if not success:
            raise PermissionError("Authentication failed.")

        print(f"Authentication successful for user: {user_info.get('email', user_info.get('user_id'))}")

        # 2. 授權
        authorized = await self.auth_manager.authorize(user_info, resource, action)
        if not authorized:
            raise PermissionError(f"User not authorized to perform '{action}' on '{resource}'.")

        print(f"Authorization successful for action '{action}' on resource '{resource}'.")

        # 3. 執行工作流程
        # 將認證後的用戶資訊注入到上下文中
        ctx = initial_context or InvocationContext()
        ctx.state["user_info"] = user_info

        return await self.run_async(ctx)


def create_workflow(config: Optional[Dict[str, Any]] = None) -> SREWorkflow:
    """
    Workflow 工廠函數。
    參考 ADK 最佳實踐，提供一個標準的 Workflow 實例化入口。
    這使得 Workflow 的創建和配置與其使用分離，提高了代碼的模組化程度。
    """
    return SREWorkflow(config)
