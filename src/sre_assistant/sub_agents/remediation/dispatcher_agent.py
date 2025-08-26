# src/sre_assistant/sub_agents/remediation/dispatcher_agent.py
"""
This module defines the SREIntelligentDispatcher agent, which uses an LLM
to dynamically select an expert remediation agent based on diagnostic data.
"""
from typing import Dict, Any, List

from google.adk.agents import BaseAgent, InvocationContext, LlmAgent, ParallelAgent

# ==============================================================================
#  專家修復代理 (佔位符)
# ==============================================================================
# 說明：
# 這些是代表不同修復能力的專家代理。在一個完整的系統中，
# 每一個都將會是一個功能齊全的代理，能夠執行具體的修復操作。
# 目前，我們使用簡單的 LlmAgent 作為佔位符。

class RollbackRemediationAgent(LlmAgent):
    """專家代理：執行應用程式或基礎設施的回滾操作。"""
    def __init__(self, **kwargs):
        super().__init__(name="RollbackExpert", instruction="執行回滾...", **kwargs)

class AutoScalingAgent(LlmAgent):
    """專家代理：調整服務的計算資源（例如，增加 Pod 數量）。"""
    def __init__(self, **kwargs):
        super().__init__(name="ScalingExpert", instruction="調整資源規模...", **kwargs)

class ServiceRestartAgent(LlmAgent):
    """專家代理：安全地重啟一個或多個服務。"""
    def __init__(self, **kwargs):
        super().__init__(name="RestartExpert", instruction="正在重啟服務...", **kwargs)

class ConfigurationFixAgent(LlmAgent):
    """專家代理：修復錯誤的服務配置。"""
    def __init__(self, **kwargs):
        super().__init__(name="ConfigExpert", instruction="正在修復配置...", **kwargs)


# ==============================================================================
#  智慧分診器
# ==============================================================================

class SREIntelligentDispatcher(BaseAgent):
    """
    智慧分診器 (SREIntelligentDispatcher)

    功能：
    1. 接收並分析來自診斷階段的綜合數據。
    2. 使用一個大型語言模型 (LLM) 來理解問題的本質。
    3. 從一個專家代理註冊表中，選擇一個或多個最適合處理當前問題的專家。
    4. 動態地執行選定的專家代理（如果選擇了多個，則並行執行）。
    """

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

        # 專家註冊表：將專家名稱映射到其實例。
        self.expert_registry: Dict[str, BaseAgent] = {
            "rollback_fix": RollbackRemediationAgent(),
            "scaling_fix": AutoScalingAgent(),
            "restart_fix": ServiceRestartAgent(),
            "config_fix": ConfigurationFixAgent(),
        }

        # LLM 決策引擎：用於從診斷數據中選擇專家。
        self.dispatcher_llm = LlmAgent(
            name="DecisionEngine",
            instruction=self._build_dispatcher_instruction()
        )

    def _build_dispatcher_instruction(self) -> str:
        """建立並返回給 LLM 的指示 (Instruction)。"""
        expert_list = "\n".join([f"- {name}" for name in self.expert_registry.keys()])
        return (
            "You are an expert SRE operations manager. "
            "Your task is to analyze the provided diagnostic summary and select the best expert(s) to fix the issue. "
            "Choose one or more from the following list. "
            "Respond with a comma-separated list of expert names (e.g., 'rollback_fix,restart_fix').\n\n"
            f"Available experts:\n{expert_list}"
        )

    def _summarize_diagnostics(self, ctx: InvocationContext) -> str:
        """從上下文中提取並格式化診斷資訊，以供 LLM 分析。"""
        summary_parts = []
        if metrics := ctx.state.get("metrics_analysis"):
            summary_parts.append(f"Metrics Analysis: {metrics}")
        if logs := ctx.state.get("logs_analysis"):
            summary_parts.append(f"Logs Analysis: {logs}")
        if traces := ctx.state.get("traces_analysis"):
            summary_parts.append(f"Traces Analysis: {traces}")
        if citations := ctx.state.get("diagnostic_citations"):
            summary_parts.append(f"Citations: {citations}")

        return "\n".join(summary_parts) if summary_parts else "No diagnostic data available."

    def _parse_expert_selection(self, decision: str) -> List[BaseAgent]:
        """從 LLM 的回應中解析出選擇的專家代理。"""
        selected_names = [name.strip() for name in decision.split(',')]
        selected_experts = []
        for name in selected_names:
            if expert := self.expert_registry.get(name):
                selected_experts.append(expert)
            else:
                print(f"Warning: LLM selected an unknown expert: {name}")
        return selected_experts

    async def _run_async_impl(self, ctx: InvocationContext) -> None:
        """執行智慧分診的核心邏輯。"""

        # 1. 產生診斷摘要
        diagnostic_summary = self._summarize_diagnostics(ctx)
        ctx.state["dispatcher_prompt"] = diagnostic_summary # 儲存 prompt 以便除錯

        # 2. 呼叫 LLM 進行決策
        decision = await self.dispatcher_llm.run_async(prompt=diagnostic_summary)
        ctx.state["dispatcher_decision"] = decision # 儲存 LLM 回應

        # 3. 解析 LLM 回應並選擇專家
        selected_experts = self._parse_expert_selection(decision)

        if not selected_experts:
            ctx.state["remediation_status"] = "failed_no_expert_selected"
            print("Dispatcher failed: No valid expert was selected by the LLM.")
            return

        # 4. 建立並執行工作流程
        if len(selected_experts) == 1:
            # 如果只有一位專家，直接執行
            workflow = selected_experts[0]
        else:
            # 如果有多位專家，並行執行
            workflow = ParallelAgent(sub_agents=selected_experts, name="ParallelRemediationExperts")

        # 執行選定的修復工作流程
        await workflow.run_async(ctx)

        ctx.state["remediation_status"] = "dispatcher_executed"
        print(f"Dispatcher executed experts: {[agent.name for agent in selected_experts]}")
