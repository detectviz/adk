# sre_assistant/sub_agents/diagnostic/citing_agent.py
"""
此模組定義了 CitingParallelDiagnosticsAgent。
該代理協調各種診斷子代理並行運行，
從它們的綜合輸出中推斷嚴重性級別，並將結果格式化以包含引用，
確保可追溯性。
"""
import logging
from typing import Optional, Dict, Any

from google.adk.agents import BaseAgent, InvocationContext, ParallelAgent

from .agent import DiagnosticAgent
from ...citation_manager import SRECitationFormatter

logger = logging.getLogger(__name__)


class CitingParallelDiagnosticsAgent(BaseAgent):
    """
    並行運行診斷代理，收集引用，並確保設置嚴重性級別。
    """
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
        """運行並行診斷，收集引用，並推斷嚴重性。"""

        # 運行底層的並行診斷代理
        await self.parallel_diagnostics.run_async(context)

        # 確保在上下文中設置了嚴重性級別
        if "severity" not in context.state:
            severity = self._infer_severity_from_results(context)
            context.state["severity"] = severity
            logger.warning(f"診斷代理未設置嚴重性，已推斷為: {severity}")

        # 從歷史記錄中的工具輸出收集並格式化引用
        citations = self._collect_citations(context)
        if citations:
            formatted_citations = self.citation_formatter.format_citations(citations)
            context.state["diagnostic_citations"] = formatted_citations

    def _collect_citations(self, context: InvocationContext) -> list:
        """從對話歷史的工具輸出中收集引用數據。"""
        citations = []
        for turn in context.history:
            if turn.role == "tool":
                tool_output = turn.content
                if isinstance(tool_output, tuple) and len(tool_output) == 2:
                    citations.append(tool_output[1])
        return citations

    def _infer_severity_from_results(self, context: InvocationContext) -> str:
        """從各種診斷代理的輸出中推斷出最高的嚴重性級別。"""
        metrics_analysis = context.state.get("metrics_analysis", {})
        logs_analysis = context.state.get("logs_analysis", {})
        traces_analysis = context.state.get("traces_analysis", {})

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

        # 返回找到的最高嚴重性，若無則返回 P3
        if "P0" in severities:
            return "P0"
        elif "P1" in severities:
            return "P1"
        elif "P2" in severities:
            return "P2"
        else:
            return "P3"
