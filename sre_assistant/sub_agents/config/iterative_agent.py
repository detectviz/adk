# sre_assistant/sub_agents/config/iterative_agent.py
"""
此模組定義了 IterativeOptimization 代理，該代理使用循環
重複應用一個子代理，直到滿足終止條件。
它專為服務等級目標 (SLO) 調優等任務而設計。
"""
from typing import Optional, Callable, Any

from google.adk.agents import LlmAgent, LoopAgent, InvocationContext


class SLOTuningAgent(LlmAgent):
    """佔位符：用於在循環中調整 SLO 配置的代理。"""
    def __init__(self, **kwargs: Any):
        kwargs.setdefault("name", "SLOTuningAgent")
        kwargs.setdefault("instruction", "正在調整 SLO。")
        super().__init__(**kwargs)


class IterativeOptimization(LoopAgent):
    """
    持續運行一個子代理 (SLOTuningAgent)，直到滿足終止條件
    或達到最大迭代次數。
    """
    sub_agent: Optional[LlmAgent] = None
    termination_condition: Optional[Callable[[InvocationContext], bool]] = None

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "IterativeOptimizer"
        if 'max_iterations' not in kwargs:
            kwargs['max_iterations'] = 3

        super().__init__(**kwargs)

        # 如果未提供 sub_agent 和 termination_condition，則設置預設值
        if self.sub_agent is None:
            self.sub_agent = SLOTuningAgent()
        if self.termination_condition is None:
            self.termination_condition = lambda ctx: ctx.state.get("slo_met", False)
