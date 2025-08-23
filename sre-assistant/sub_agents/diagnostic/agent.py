# sre-assistant/sub_agents/diagnostic/agent.py
# 說明：此檔案定義了診斷專家 (DiagnosticExpert) 代理。
# 這個代理使用大型語言模型 (LLM) 和一系列專用工具 (如 PromQLQueryTool)
# 來分析系統問題的根本原因。它整合了 prompts.py 中定義的提示模板
# 和 tools.py 中定義的工具，以執行結構化的診斷工作流程。

from google.adk.agents import LlmAgent
from .tools import (
    promql_query,
    log_search,
    trace_analysis,
    anomaly_detection
)
from .prompts import DIAGNOSTIC_PROMPT

class DiagnosticAgent(LlmAgent):
    """
    診斷專家：整合多源數據進行根因分析
    參考 ADK Sample: RAG agent, software-bug-assistant

    此代理的核心職責是利用其工具集收集數據，並根據其指示 (instruction)
    來分析數據，最終生成一份結構化的診斷報告。
    """

    def __init__(self, config=None, instruction=DIAGNOSTIC_PROMPT.base, tools=None):
        """
        初始化診斷代理。

        Args:
            config (dict, optional): 代理的配置。 Defaults to None.
            instruction (str, optional): 指導模型行為的系統指令。預設為基礎診斷提示。
            tools (list, optional): 此代理可用的工具列表。如果未提供，則載入所有診斷工具。
        """
        super().__init__(
            # 註：ADK 的 LlmAgent 需要一個 name 和 model 參數。
            name="DiagnosticExpert",
            model="gemini-1.5-flash-001",
            tools=tools or self._load_all_tools(),
            instruction=instruction
        )
        # 註：config 參數暫時保留，以備將來擴展，但目前不在代理中使用。
        # self.config = config or {} # 移除此行以避免 Pydantic 驗證錯誤

    def _load_all_tools(self):
        """載入所有可用的診斷工具函數。"""
        return [
            promql_query,
            log_search,
            trace_analysis,
            anomaly_detection
        ]

    @classmethod
    def create_metrics_analyzer(cls, config=None):
        """
        工廠方法：建立一個專注於**指標分析**的診斷代理實例。

        此實例被配置為僅使用與指標相關的工具，並遵循專為指標分析設計的提示。
        這種模式使得我們可以建立多個專注於特定任務的「微代理」。
        """
        metrics_tools = [promql_query, anomaly_detection]
        return cls(
            config=config,
            instruction=DIAGNOSTIC_PROMPT.metrics_focus,
            tools=metrics_tools
        )

    @classmethod
    def create_log_analyzer(cls, config=None):
        """
        工廠方法：建立一個專注於**日誌分析**的診斷代理實例。

        此實例被配置為僅使用日誌搜尋工具，並遵循專為日誌分析設計的提示。
        """
        log_tools = [log_search]
        return cls(
            config=config,
            instruction=DIAGNOSTIC_PROMPT.logs_focus,
            tools=log_tools
        )

    @classmethod
    def create_trace_analyzer(cls, config=None):
        """
        工廠方法：建立一個專注於**分散式追蹤分析**的診斷代理實例。

        此方法是對 ARCHITECTURE.md 的一個擴展，以滿足 SRECoordinator 中
        並行診斷 (ParallelAgent) 的需求。
        """
        trace_tools = [trace_analysis]
        # 未來可以為追蹤分析建立一個專門的提示模板。
        return cls(
            config=config,
            instruction=DIAGNOSTIC_PROMPT.base, # 暫時使用基礎提示
            tools=trace_tools
        )
