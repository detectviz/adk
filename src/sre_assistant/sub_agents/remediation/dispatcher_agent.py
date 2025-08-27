# src/sre_assistant/sub_agents/remediation/dispatcher_agent.py
"""
This module defines the SREIntelligentDispatcher agent, which uses an LLM
to dynamically select an expert remediation agent based on diagnostic data.
"""
from typing import Dict, Any, List

from google.adk.agents import BaseAgent, LlmAgent, ParallelAgent
from google.adk.agents.invocation_context import InvocationContext

# ==============================================================================
#  專家修復代理 (佔位符)
# ==============================================================================
# 說明：
# 這些是代表不同修復能力的專家代理。在一個完整的系統中，
# 每一個都將會是一個功能齊全的代理，能夠執行具體的修復操作。
# 目前，我們使用簡單的 LlmAgent 作為佔位符。

from google.genai.types import GenerateContentConfig

def _prepare_llm_agent_kwargs(kwargs):
    """Helper to wrap safety/generation configs for LlmAgent."""
    safety_settings = kwargs.pop("safety_settings", None)
    generation_config = kwargs.pop("generation_config", None)

    if safety_settings or generation_config:
        kwargs["generate_content_config"] = GenerateContentConfig(
            safety_settings=safety_settings,
            temperature=generation_config.temperature if generation_config else 0.4,
            top_p=generation_config.top_p if generation_config else 1.0,
            top_k=generation_config.top_k if generation_config else 32,
            candidate_count=generation_config.candidate_count if generation_config else 1,
            max_output_tokens=generation_config.max_output_tokens if generation_config else 8192,
        )
    return kwargs

class RollbackRemediationAgent(LlmAgent):
    """專家代理：執行應用程式或基礎設施的回滾操作。"""
    def __init__(self, **kwargs):
        # 使用 setdefault 確保即使外部未提供，也有預設的 name 和 instruction。
        # 同時允許從外部傳入的 kwargs (如 safety_settings) 覆蓋或添加參數。
        kwargs.setdefault("name", "RollbackExpert")
        kwargs.setdefault("instruction", "執行回滾...")
        super().__init__(**_prepare_llm_agent_kwargs(kwargs))

class AutoScalingAgent(LlmAgent):
    """專家代理：調整服務的計算資源（例如，增加 Pod 數量）。"""
    def __init__(self, **kwargs):
        kwargs.setdefault("name", "ScalingExpert")
        kwargs.setdefault("instruction", "調整資源規模...")
        super().__init__(**_prepare_llm_agent_kwargs(kwargs))

class ServiceRestartAgent(LlmAgent):
    """專家代理：安全地重啟一個或多個服務。"""
    def __init__(self, **kwargs):
        kwargs.setdefault("name", "RestartExpert")
        kwargs.setdefault("instruction", "正在重啟服務...")
        super().__init__(**_prepare_llm_agent_kwargs(kwargs))

class ConfigurationFixAgent(LlmAgent):
    """專家代理：修復錯誤的服務配置。"""
    def __init__(self, **kwargs):
        kwargs.setdefault("name", "ConfigExpert")
        kwargs.setdefault("instruction", "正在修復配置...")
        super().__init__(**_prepare_llm_agent_kwargs(kwargs))


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
    expert_registry: Dict[str, BaseAgent] = None
    dispatcher_llm: LlmAgent = None

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

        # 從傳入的 kwargs 中提取上層工作流程傳遞過來的標準化設定。
        safety_settings = kwargs.get("safety_settings")
        generation_config = kwargs.get("generation_config")

        # 將這些設定打包，以便統一傳遞給所有需要 LLM 的內部代理。
        llm_agent_kwargs = {
            "safety_settings": safety_settings,
            "generation_config": generation_config,
        }

        # 專家註冊表：將專家名稱映射到其代理實例。
        # 在實例化時，將繼承來的標準化設定傳遞下去。
        self.expert_registry = {
            "rollback_fix": RollbackRemediationAgent(**llm_agent_kwargs.copy()),
            "scaling_fix": AutoScalingAgent(**llm_agent_kwargs.copy()),
            "restart_fix": ServiceRestartAgent(**llm_agent_kwargs.copy()),
            "config_fix": ConfigurationFixAgent(**llm_agent_kwargs.copy()),
        }

        # LLM 決策引擎：此分診器內部使用一個專用的 LLM 代理來做決策。
        # 同樣，我們將標準化設定應用於此決策引擎。
        self.dispatcher_llm = LlmAgent(
            name="DecisionEngine",
            instruction=self._build_dispatcher_instruction(),
            **_prepare_llm_agent_kwargs(llm_agent_kwargs.copy())
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
        if metrics := ctx.session.state.get("metrics_analysis"):
            summary_parts.append(f"Metrics Analysis: {metrics}")
        if logs := ctx.session.state.get("logs_analysis"):
            summary_parts.append(f"Logs Analysis: {logs}")
        if traces := ctx.session.state.get("traces_analysis"):
            summary_parts.append(f"Traces Analysis: {traces}")
        if citations := ctx.session.state.get("diagnostic_citations"):
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
        ctx.session.state["dispatcher_prompt"] = diagnostic_summary # 儲存 prompt 以便除錯

        # 2. 呼叫 LLM 進行決策
        decision = await self.dispatcher_llm.run_async(prompt=diagnostic_summary)
        ctx.session.state["dispatcher_decision"] = decision # 儲存 LLM 回應

        # 3. 解析 LLM 回應並選擇專家
        selected_experts = self._parse_expert_selection(decision)

        if not selected_experts:
            ctx.session.state["remediation_status"] = "failed_no_expert_selected"
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

        ctx.session.state["remediation_status"] = "dispatcher_executed"
        print(f"Dispatcher executed experts: {[agent.name for agent in selected_experts]}")
