# sre_assistant/workflow_enhanced.py
"""增強版 SRE Workflow - 符合 ADK 最佳實踐"""

from typing import Dict, Any, List, Optional
from google.adk.agents import (
    SequentialAgent, 
    ParallelAgent, 
    LoopAgent,
    InvocationContext,
    BeforeAgentCallback,
    AfterAgentCallback
)
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

class EnhancedSREWorkflow(SequentialAgent):
    """符合 ADK 最佳實踐的 SRE 工作流程實現"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # 1. 診斷階段 - 正確配置並行執行
        diagnostic_phase = self._create_diagnostic_phase()
        
        # 2. 修復階段 - 使用動態分診
        remediation_phase = self._create_remediation_phase()
        
        # 3. 驗證階段 - ADK 推薦的 self-critic 模式
        verification_phase = self._create_verification_phase()
        
        # 4. 覆盤階段
        postmortem_phase = self._create_postmortem_phase()
        
        # 5. 優化階段 - 正確配置循環終止
        optimization_phase = self._create_optimization_phase()
        
        super().__init__(
            name="EnhancedSREWorkflow",
            sub_agents=[
                diagnostic_phase,
                remediation_phase,
                verification_phase,  # 新增驗證階段
                postmortem_phase,
                optimization_phase
            ],
            # ADK 最佳實踐：添加工作流程級別的回調
            before_agent_callback=self._workflow_pre_check,
            after_agent_callback=self._workflow_post_process
        )
    
    def _create_diagnostic_phase(self) -> ParallelAgent:
        """創建符合最佳實踐的並行診斷階段"""
        return ParallelAgent(
            name="DiagnosticPhase",
            sub_agents=[
                MetricsAnalyzer(),
                LogAnalyzer(), 
                TraceAnalyzer(),
                HistoricalMatcher()
            ],
            # ADK 最佳實踐：自定義聚合策略
            aggregation_strategy="custom",
            aggregation_function=self._aggregate_diagnostics,
            # 設置超時以防止無限等待
            timeout_seconds=30,
            # 允許部分失敗
            allow_partial_failure=True
        )
    
    def _aggregate_diagnostics(self, results: List[Dict]) -> Dict:
        """自定義診斷結果聚合邏輯"""
        aggregated = {
            "severity": self._calculate_severity(results),
            "root_causes": self._merge_root_causes(results),
            "confidence": self._calculate_confidence(results),
            "evidence": self._collect_evidence(results)
        }
        return aggregated
    
    def _create_remediation_phase(self) -> 'IntelligentDispatcher':
        """創建智能分診修復階段"""
        return IntelligentDispatcher(
            name="RemediationPhase",
            # 使用 ADK 推薦的動態代理選擇
            expert_registry={
                "k8s_issues": KubernetesRemediationAgent(),
                "database_issues": DatabaseRemediationAgent(),
                "network_issues": NetworkRemediationAgent(),
                "config_issues": ConfigurationFixAgent(),
            },
            # 條件執行回調
            before_agent_callback=self._check_remediation_safety
        )
    
    def _create_verification_phase(self) -> 'VerificationAgent':
        """創建修復後驗證階段 - ADK self-critic 模式"""
        return VerificationAgent(
            name="VerificationPhase",
            sub_agents=[
                HealthCheckAgent(),
                SLOValidationAgent(),
                RegressionCheckAgent()
            ],
            # 驗證失敗時的回滾機制
            on_failure_callback=self._trigger_rollback
        )
    
    def _create_optimization_phase(self) -> LoopAgent:
        """創建符合最佳實踐的循環優化階段"""
        return LoopAgent(
            name="OptimizationPhase",
            sub_agents=[
                ConfigTuner(),
                PerformanceOptimizer()
            ],
            # ADK 最佳實踐：明確的終止條件
            max_iterations=5,
            termination_condition=self._check_slo_targets,
            # 防止無限循環的超時
            timeout_seconds=300
        )
    
    # === 回調函數實現 ===
    
    def _workflow_pre_check(self, context: CallbackContext) -> Optional[types.Content]:
        """工作流程開始前的檢查"""
        # 驗證必要的權限和資源
        if not self._validate_permissions(context):
            return types.Content(
                parts=[types.Part(text="權限不足，終止工作流程")]
            )
        
        # 檢查速率限制
        if self._is_rate_limited(context):
            return types.Content(
                parts=[types.Part(text="觸發速率限制，請稍後重試")]
            )
        
        return None
    
    def _workflow_post_process(self, context: CallbackContext) -> Optional[types.Content]:
        """工作流程完成後的處理"""
        # 記錄審計日誌
        self._log_audit_trail(context)
        
        # 更新指標
        self._update_metrics(context)
        
        # 發送通知
        if context.state.get("severity") in ["P0", "P1"]:
            self._send_notifications(context)
        
        return None
    
    def _check_remediation_safety(self, context: CallbackContext) -> Optional[types.Content]:
        """修復前的安全檢查"""
        severity = context.state.get("severity")
        
        # P0 事件需要人工審批
        if severity == "P0":
            if not context.state.get("human_approval"):
                return types.Content(
                    parts=[types.Part(text="P0 事件需要人工審批，跳過自動修復")]
                )
        
        # 檢查變更窗口
        if not self._in_change_window():
            return types.Content(
                parts=[types.Part(text="不在變更窗口內，推遲修復")]
            )
        
        return None
    
    def _check_slo_targets(self, context: InvocationContext) -> bool:
        """檢查是否達到 SLO 目標"""
        current_metrics = context.state.get("performance_metrics", {})
        slo_targets = context.state.get("slo_targets", {})
        
        for metric, target in slo_targets.items():
            if current_metrics.get(metric, 0) < target:
                return False  # 繼續優化
        
        return True  # 達標，終止循環
    
    def _trigger_rollback(self, context: CallbackContext):
        """觸發回滾機制"""
        context.state["rollback_required"] = True
        context.state["rollback_reason"] = "Verification failed"
        # 實際回滾邏輯...


class IntelligentDispatcher(BaseAgent):
    """智能分診器 - 動態選擇專家代理"""
    
    def __init__(self, expert_registry: Dict[str, BaseAgent], **kwargs):
        super().__init__(**kwargs)
        self.expert_registry = expert_registry
        self.decision_llm = LlmAgent(
            name="DispatchDecisionEngine",
            instruction=self._build_dispatch_instruction(),
            output_schema=DispatchDecision  # 使用結構化輸出
        )
    
    async def run_async(self, context: InvocationContext):
        """動態選擇並執行適當的專家代理"""
        # 1. 分析診斷結果
        diagnostic_summary = context.state.get("diagnostic_summary")
        
        # 2. LLM 決策
        decision = await self.decision_llm.run_async(
            context,
            input_data={"diagnosis": diagnostic_summary}
        )
        
        # 3. 執行選定的專家
        selected_experts = decision.selected_experts
        if len(selected_experts) == 1:
            # 單個專家直接執行
            expert = self.expert_registry[selected_experts[0]]
            return await expert.run_async(context)
        else:
            # 多個專家並行執行
            parallel_experts = ParallelAgent(
                sub_agents=[self.expert_registry[e] for e in selected_experts]
            )
            return await parallel_experts.run_async(context)


class VerificationAgent(SequentialAgent):
    """修復後驗證代理 - 實現 ADK self-critic 模式"""
    
    def __init__(self, on_failure_callback=None, **kwargs):
        self.on_failure_callback = on_failure_callback
        super().__init__(**kwargs)
    
    async def run_async(self, context: InvocationContext):
        """執行驗證並處理失敗情況"""
        result = await super().run_async(context)
        
        # 檢查驗證結果
        if not context.state.get("verification_passed", False):
            if self.on_failure_callback:
                self.on_failure_callback(context)
            
            # 記錄驗證失敗
            context.state["remediation_status"] = "failed_verification"
        
        return result


# === 輔助類定義 ===

from pydantic import BaseModel

class DispatchDecision(BaseModel):
    """分診決策的結構化輸出"""
    selected_experts: List[str]
    reasoning: str
    confidence: float
    fallback_strategy: Optional[str] = None