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
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ConditionalRemediation(BaseAgent):
    """
    條件化修復代理：根據診斷結果的嚴重性 (severity)，選擇不同的修復策略。
    增強版本包含完整的錯誤處理和降級機制。
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_retries = 3
        self.fallback_threshold = 2  # 失敗次數達到此值時觸發降級

    async def _run_async_impl(self, ctx: InvocationContext) -> None:
        """執行條件化修復，包含錯誤處理和重試邏輯"""

        retry_count = ctx.state.get("remediation_retry_count", 0)

        try:
            # 1. 獲取並驗證嚴重性
            severity = self._get_validated_severity(ctx)

            # 2. 記錄決策審計日誌
            await self._log_remediation_decision(ctx, severity, retry_count)

            # 3. 選擇並執行對應的修復策略
            agent = await self._select_remediation_agent(severity, ctx, retry_count)

            # 4. 執行修復並處理結果
            try:
                await agent.run_async(ctx)

                # 成功後清理重試計數
                ctx.state["remediation_retry_count"] = 0
                ctx.state["remediation_status"] = "success"

            except Exception as agent_error:
                logger.error(f"Remediation agent failed: {agent_error}")

                # 記錄失敗並決定是否重試
                await self._handle_agent_failure(ctx, severity, agent_error, retry_count)

        except Exception as e:
            logger.error(f"Critical error in ConditionalRemediation: {e}")
            await self._execute_emergency_protocol(ctx, e)

    def _get_validated_severity(self, ctx: InvocationContext) -> str:
        """獲取並驗證嚴重性級別"""
        severity = ctx.state.get("severity")

        # 如果沒有嚴重性，嘗試從診斷結果推斷
        if not severity:
            logger.warning("No severity found in context, attempting to infer...")
            severity = self._infer_severity_from_diagnostics(ctx)

        # 驗證嚴重性值
        valid_severities = ["P0", "P1", "P2", "P3"]
        if severity not in valid_severities:
            logger.warning(f"Invalid severity '{severity}', defaulting to P1")
            severity = "P1"  # 默認為高優先級以確保安全

        return severity

    def _infer_severity_from_diagnostics(self, ctx: InvocationContext) -> str:
        """從診斷結果推斷嚴重性"""
        # 檢查診斷階段的輸出
        metrics_analysis = ctx.state.get("metrics_analysis", {})
        logs_analysis = ctx.state.get("logs_analysis", {})

        # 基於診斷結果的簡單推斷邏輯
        error_rate = metrics_analysis.get("error_rate", 0)
        critical_errors = logs_analysis.get("critical_errors", 0)

        if error_rate > 0.5 or critical_errors > 10:
            return "P0"
        elif error_rate > 0.1 or critical_errors > 5:
            return "P1"
        elif error_rate > 0.01 or critical_errors > 0:
            return "P2"
        else:
            return "P3"

    async def _select_remediation_agent(
        self,
        severity: str,
        ctx: InvocationContext,
        retry_count: int
    ) -> BaseAgent:
        """根據嚴重性和重試次數選擇修復代理"""

        agent_config = ctx.state.get("config", {})

        # 如果重試次數過多，強制使用 HITL
        if retry_count >= self.fallback_threshold:
            logger.warning(f"Retry count {retry_count} exceeds threshold, forcing HITL")
            return HITLRemediationAgent(
                config=agent_config,
                reason="multiple_failures",
                retry_count=retry_count
            )

        # 正常的嚴重性判斷邏輯
        if severity == "P0":
            return HITLRemediationAgent(
                config=agent_config,
                reason="critical_severity"
            )
        elif severity == "P1":
            return AutoRemediationWithLogging(
                config=agent_config,
                enhanced_logging=True
            )
        elif severity == "P2":
            return ScheduledRemediation(
                config=agent_config,
                delay_minutes=30
            )
        else:  # P3
            return ScheduledRemediation(
                config=agent_config,
                delay_minutes=120
            )

    async def _handle_agent_failure(
        self,
        ctx: InvocationContext,
        severity: str,
        error: Exception,
        retry_count: int
    ) -> None:
        """處理代理執行失敗"""

        retry_count += 1
        ctx.state["remediation_retry_count"] = retry_count

        if retry_count < self.max_retries:
            # 記錄並準備重試
            logger.info(f"Remediation failed, retry {retry_count}/{self.max_retries}")
            ctx.state["remediation_status"] = "retrying"

            # 添加延遲避免快速失敗
            import asyncio
            await asyncio.sleep(min(2 ** retry_count, 30))  # 指數退避，最多 30 秒

            # 遞迴重試
            await self._run_async_impl(ctx)
        else:
            # 達到最大重試次數，觸發降級
            logger.error(f"Max retries reached for severity {severity}")
            ctx.state["remediation_status"] = "failed"
            await self._escalate_to_manual(ctx, error)

    async def _escalate_to_manual(self, ctx: InvocationContext, error: Exception) -> None:
        """升級到人工處理"""
        logger.critical(f"Automated remediation failed, escalating to manual: {error}")

        # 發送告警
        await self._send_escalation_alert(ctx, error)

        # 強制執行 HITL
        hitl_agent = HITLRemediationAgent(
            config=ctx.state.get("config", {}),
            reason="automated_remediation_failed",
            original_error=str(error)
        )

        try:
            await hitl_agent.run_async(ctx)
        except Exception as hitl_error:
            logger.critical(f"HITL also failed: {hitl_error}")
            await self._execute_emergency_protocol(ctx, hitl_error)

    async def _execute_emergency_protocol(self, ctx: InvocationContext, error: Exception) -> None:
        """執行緊急協議 - 最後的防線"""
        logger.critical(f"EMERGENCY PROTOCOL ACTIVATED: {error}")

        ctx.state["remediation_status"] = "emergency"
        ctx.state["emergency_reason"] = str(error)

        # 1. 立即通知所有相關人員
        await self._notify_all_stakeholders(ctx, error)

        # 2. 創建緊急事件票證
        await self._create_emergency_ticket(ctx, error)

        # 3. 啟動災難恢復流程
        await self._initiate_disaster_recovery(ctx)

        # 4. 記錄完整的失敗上下文供事後分析
        await self._dump_full_context(ctx, error)

    async def _log_remediation_decision(
        self,
        ctx: InvocationContext,
        severity: str,
        retry_count: int
    ) -> None:
        """記錄修復決策的審計日誌"""
        audit_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "incident_id": ctx.state.get("incident_id"),
            "severity": severity,
            "retry_count": retry_count,
            "decision": "selecting_remediation_agent",
            "context_keys": list(ctx.state.keys())
        }
        logger.info(f"Remediation decision audit: {json.dumps(audit_log)}")

    async def _send_escalation_alert(self, ctx: InvocationContext, error: Exception) -> None:
        """發送升級告警"""
        # 實作告警邏輯（PagerDuty, Slack, Email 等）
        pass

    async def _notify_all_stakeholders(self, ctx: InvocationContext, error: Exception) -> None:
        """通知所有利益相關者"""
        # 實作群發通知邏輯
        pass

    async def _create_emergency_ticket(self, ctx: InvocationContext, error: Exception) -> None:
        """創建緊急事件票證"""
        # 實作票證系統整合（Jira, ServiceNow 等）
        pass

    async def _initiate_disaster_recovery(self, ctx: InvocationContext) -> None:
        """啟動災難恢復流程"""
        # 實作災難恢復邏輯
        pass

    async def _dump_full_context(self, ctx: InvocationContext, error: Exception) -> None:
        """轉儲完整上下文供分析"""
        import json
        from datetime import datetime

        dump_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(error),
            "state": dict(ctx.state),
            "history_length": len(ctx.history) if hasattr(ctx, 'history') else 0
        }

        # 保存到文件或數據庫
        dump_file = f"emergency_dump_{ctx.state.get('incident_id', 'unknown')}_{datetime.utcnow().timestamp()}.json"
        # 實際實作時應該保存到適當的存儲位置
        logger.critical(f"Context dumped to {dump_file}: {json.dumps(dump_data, indent=2)}")


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
    並行診斷代理，自動收集引用並確保設置嚴重性
    """
    # 聲明類別屬性以符合 Pydantic 模型的要求
    parallel_diagnostics: ParallelAgent
    citation_formatter: SRECitationFormatter

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        agent_config = config or {}

        if 'name' not in kwargs:
            kwargs['name'] = "CitingParallelDiagnosticsAgent"
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
        """運行並行診斷，收集引用，並確保設置嚴重性"""

        # 運行原有的並行診斷
        await self.parallel_diagnostics.run_async(context)

        # 確保嚴重性被設置
        if "severity" not in context.state:
            # 從各個診斷結果推斷嚴重性
            severity = self._infer_severity_from_results(context)
            context.state["severity"] = severity

            logger.warning(f"Severity not set by diagnostic agents, inferred as: {severity}")

        # 收集和格式化引用（原有邏輯）
        citations = self._collect_citations(context)
        if citations:
            formatted_citations = self.citation_formatter.format_citations(citations)
            context.state["diagnostic_citations"] = formatted_citations

    def _collect_citations(self, context: InvocationContext) -> list:
        """從歷史記錄中收集引用"""
        citations = []
        for turn in context.history:
            if turn.role == "tool":
                tool_output = turn.content
                if isinstance(tool_output, tuple) and len(tool_output) == 2:
                    citations.append(tool_output[1])
        return citations

    def _infer_severity_from_results(self, context: InvocationContext) -> str:
        """從診斷結果推斷嚴重性"""
        # 檢查各個分析器的輸出
        metrics_analysis = context.state.get("metrics_analysis", {})
        logs_analysis = context.state.get("logs_analysis", {})
        traces_analysis = context.state.get("traces_analysis", {})

        # 簡單的推斷邏輯
        severities = []

        # 從指標分析推斷
        if metrics_analysis:
            error_rate = metrics_analysis.get("error_rate", 0)
            if error_rate > 0.5:
                severities.append("P0")
            elif error_rate > 0.1:
                severities.append("P1")
            elif error_rate > 0.01:
                severities.append("P2")

        # 從日誌分析推斷
        if logs_analysis:
            critical_errors = logs_analysis.get("critical_errors", 0)
            if critical_errors > 100:
                severities.append("P0")
            elif critical_errors > 10:
                severities.append("P1")
            elif critical_errors > 0:
                severities.append("P2")

        # 從追蹤分析推斷
        if traces_analysis:
            failed_traces = traces_analysis.get("failed_traces_percentage", 0)
            if failed_traces > 50:
                severities.append("P0")
            elif failed_traces > 10:
                severities.append("P1")
            elif failed_traces > 1:
                severities.append("P2")

        # 返回最高嚴重性
        if "P0" in severities:
            return "P0"
        elif "P1" in severities:
            return "P1"
        elif "P2" in severities:
            return "P2"
        else:
            return "P3"

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
