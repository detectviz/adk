# sre_assistant/sub_agents/remediation/conditional_agent.py
"""
此模組定義了 ConditionalRemediation 代理及其佔位符依賴項。
該代理根據事件的嚴重性選擇修復策略。
"""
import logging
import json
from datetime import datetime

from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents import LlmAgent

logger = logging.getLogger(__name__)


# --- 佔位符代理 (Placeholder Agents) ---
# 這些是 ConditionalRemediation 所需的佔位符代理。
# 在後續的開發階段，它們將被完整的功能所取代。

class HITLRemediationAgent(LlmAgent):
    """佔位符：需要人工介入 (HITL) 審批的修復代理。"""
    def __init__(self, **kwargs):
        super().__init__(name="HITLRemediationAgent", instruction="等待人工介入...", **kwargs)

class AutoRemediationWithLogging(LlmAgent):
    """佔位符：執行自動修復並帶有詳細日誌記錄的代理。"""
    def __init__(self, **kwargs):
        super().__init__(name="AutoRemediationWithLogging", instruction="正在執行自動化修復並記錄日誌...", **kwargs)

class ScheduledRemediation(LlmAgent):
    """佔位符：用於安排低優先級問題修復的代理。"""
    def __init__(self, **kwargs):
        super().__init__(name="ScheduledRemediation", instruction="排程修復至稍後執行...", **kwargs)


# --- 條件修復代理 (Conditional Remediation Agent) ---

class ConditionalRemediation(BaseAgent):
    """
    根據事件嚴重性選擇修復策略，並帶有增強的錯誤處理和降級機制。
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_retries = 3
        self.fallback_threshold = 2  # 失敗次數達到此值後觸發降級

    async def _run_async_impl(self, ctx: InvocationContext) -> None:
        """執行帶有錯誤處理和重試機制的條件修復邏輯。"""

        retry_count = ctx.state.get("remediation_retry_count", 0)

        try:
            # 1. 獲取並驗證嚴重性
            severity = self._get_validated_severity(ctx)

            # 2. 記錄決策以供審計
            await self._log_remediation_decision(ctx, severity, retry_count)

            # 3. 選擇並執行對應的修復策略
            agent = await self._select_remediation_agent(severity, ctx, retry_count)

            # 4. 執行選定的代理並處理結果
            try:
                await agent.run_async(ctx)

                # 成功後清除重試計數器
                ctx.state["remediation_retry_count"] = 0
                ctx.state["remediation_status"] = "success"

            except Exception as agent_error:
                logger.error(f"修復代理執行失敗: {agent_error}")

                # 處理失敗並決定是否重試
                await self._handle_agent_failure(ctx, severity, agent_error, retry_count)

        except Exception as e:
            logger.error(f"ConditionalRemediation 發生嚴重錯誤: {e}")
            await self._execute_emergency_protocol(ctx, e)

    def _get_validated_severity(self, ctx: InvocationContext) -> str:
        """從上下文中獲取並驗證嚴重性級別。"""
        severity = ctx.state.get("severity")

        # 如果嚴重性不存在，則嘗試從診斷結果中推斷
        if not severity:
            logger.warning("在上下文中找不到嚴重性，嘗試推斷...")
            severity = self._infer_severity_from_diagnostics(ctx)

        # 驗證嚴重性值的有效性
        valid_severities = ["P0", "P1", "P2", "P3"]
        if severity not in valid_severities:
            logger.warning(f"無效的嚴重性 '{severity}'，預設為 P1")
            severity = "P1"  # 為安全起見，預設為高優先級

        return severity

    def _infer_severity_from_diagnostics(self, ctx: InvocationContext) -> str:
        """從上下文中的診斷結果推斷嚴重性。"""
        metrics_analysis = ctx.state.get("metrics_analysis", {})
        logs_analysis = ctx.state.get("logs_analysis", {})

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
        """根據嚴重性和重試次數選擇修復代理。"""

        agent_config = ctx.state.get("config", {})

        # 如果重試次數超過降級閾值，則強制使用 HITL
        if retry_count >= self.fallback_threshold:
            logger.warning(f"重試次數 {retry_count} 超過閾值，強制使用 HITL")
            return HITLRemediationAgent(
                config=agent_config,
                reason="multiple_failures",
                retry_count=retry_count
            )

        # 標準的基於嚴重性的選擇邏輯
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
        """處理代理執行失敗。"""

        retry_count += 1
        ctx.state["remediation_retry_count"] = retry_count

        if retry_count < self.max_retries:
            logger.info(f"修復失敗，第 {retry_count}/{self.max_retries} 次重試")
            ctx.state["remediation_status"] = "retrying"

            # 增加指數退避延遲以避免快速連續失敗
            import asyncio
            await asyncio.sleep(min(2 ** retry_count, 30))

            # 遞迴重試
            await self._run_async_impl(ctx)
        else:
            logger.error(f"嚴重性 {severity} 的問題已達到最大重試次數")
            ctx.state["remediation_status"] = "failed"
            await self._escalate_to_manual(ctx, error)

    async def _escalate_to_manual(self, ctx: InvocationContext, error: Exception) -> None:
        """將失敗的修復升級至人工處理。"""
        logger.critical(f"自動化修復失敗，升級至人工處理: {error}")

        await self._send_escalation_alert(ctx, error)

        hitl_agent = HITLRemediationAgent(
            config=ctx.state.get("config", {}),
            reason="automated_remediation_failed",
            original_error=str(error)
        )

        try:
            await hitl_agent.run_async(ctx)
        except Exception as hitl_error:
            logger.critical(f"HITL 流程也失敗了: {hitl_error}")
            await self._execute_emergency_protocol(ctx, hitl_error)

    async def _execute_emergency_protocol(self, ctx: InvocationContext, error: Exception) -> None:
        """作為最後手段執行緊急協議。"""
        logger.critical(f"緊急協議已啟動: {error}")

        ctx.state["remediation_status"] = "emergency"
        ctx.state["emergency_reason"] = str(error)

        await self._notify_all_stakeholders(ctx, error)
        await self._create_emergency_ticket(ctx, error)
        await self._initiate_disaster_recovery(ctx)
        await self._dump_full_context(ctx, error)

    async def _log_remediation_decision(
        self,
        ctx: InvocationContext,
        severity: str,
        retry_count: int
    ) -> None:
        """為審計目的記錄修復決策。"""
        audit_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "incident_id": ctx.state.get("incident_id"),
            "severity": severity,
            "retry_count": retry_count,
            "decision": "selecting_remediation_agent",
            "context_keys": list(ctx.state.keys())
        }
        logger.info(f"修復決策審計: {json.dumps(audit_log)}")

    async def _send_escalation_alert(self, ctx: InvocationContext, error: Exception) -> None:
        """佔位符：用於發送升級警報。"""
        pass

    async def _notify_all_stakeholders(self, ctx: InvocationContext, error: Exception) -> None:
        """佔位符：用於通知所有利益相關者。"""
        pass

    async def _create_emergency_ticket(self, ctx: InvocationContext, error: Exception) -> None:
        """佔位符：用於在 Jira 等系統中創建緊急事件工單。"""
        pass

    async def _initiate_disaster_recovery(self, ctx: InvocationContext) -> None:
        """佔位符：用於啟動災難恢復流程。"""
        pass

    async def _dump_full_context(self, ctx: InvocationContext, error: Exception) -> None:
        """將完整的上下文轉儲到檔案或資料庫以供事後分析。"""
        dump_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(error),
            "state": dict(ctx.state),
            "history_length": len(ctx.history) if hasattr(ctx, 'history') else 0
        }
        dump_file = f"emergency_dump_{ctx.state.get('incident_id', 'unknown')}_{datetime.utcnow().timestamp()}.json"
        logger.critical(f"上下文已轉儲至 {dump_file}: {json.dumps(dump_data, indent=2)}")
