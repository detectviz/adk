# src/sre_assistant/sub_agents/diagnostic/agent.py
# 說明：此檔案定義了診斷專家 (DiagnosticExpert) 代理。
# 這個代理使用大型語言模型 (LLM) 和一系列專用工具 (如 PromQLQueryTool)
# 來分析系統問題的根本原因。它整合了 prompts.py 中定義的提示模板
# 和 tools.py 中定義的工具，以執行結構化的診斷工作流程。

from google.adk.agents import LlmAgent
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from .tools import (
    promql_query,
    log_search,
    trace_analysis,
    anomaly_detection
)
from .prompts import DIAGNOSTIC_PROMPT
from ...citation_manager import SRECitationFormatter
from typing import List, Dict, Any, AsyncGenerator
import json
from google.adk.tools.agent_tool import agent_tool

class DiagnosticAgent(LlmAgent):
    """
    診斷專家：整合多源數據進行根因分析
    增強版本包含自動嚴重性評估
    """

    def __init__(self, config=None, instruction=None, tools=None, safety_settings=None, generation_config=None):
        """
        初始化診斷代理。

        Args:
            config (dict, optional): 代理的通用配置。
            instruction (str, optional): 指向 LLM 的特定指令。
            tools (list, optional): 此代理可使用的工具列表。
            safety_settings (list, optional): 傳遞給 LLM 的安全設定。
            generation_config (GenerationConfig, optional): 傳遞給 LLM 的生成設定。
        """
        # 增強的指令，包含嚴重性評估
        enhanced_instruction = (instruction or DIAGNOSTIC_PROMPT.base) + """

        **重要**: 在診斷結束時，你必須評估問題的嚴重性並設置 severity 級別：
        - P0: 生產環境完全不可用，影響所有用戶
        - P1: 生產環境部分不可用，影響大量用戶
        - P2: 功能降級但可用，影響部分用戶
        - P3: 非關鍵問題，影響少數用戶或無用戶影響

        使用 set_severity 工具來設置評估的嚴重性級別。
        """

        # 添加嚴重性設置工具
        severity_tool = self._create_severity_tool()
        all_tools = (tools or self._load_all_tools()) + [severity_tool]

        super().__init__(
            name="DiagnosticExpert",
            model="gemini-1.5-flash-001",
            tools=all_tools,
            instruction=enhanced_instruction,
            safety_settings=safety_settings,
            generation_config=generation_config,
        )

    def _create_severity_tool(self):
        """創建用於設置嚴重性的工具"""

        @agent_tool
        def set_severity(
            severity: str,
            reason: str,
            impact_assessment: Dict[str, Any]
        ) -> Dict[str, Any]:
            """
            設置事件的嚴重性級別。

            Args:
                severity: P0, P1, P2 或 P3
                reason: 設置此嚴重性的原因
                impact_assessment: 影響評估，包含：
                    - affected_users: 受影響用戶數量或百分比
                    - affected_services: 受影響服務列表
                    - business_impact: 業務影響描述
                    - error_rate: 錯誤率
                    - response_time_degradation: 響應時間降級百分比

            Returns:
                確認嚴重性設置的結果
            """
            # 這個工具會自動更新 context.state
            return {
                "status": "success",
                "severity_set": severity,
                "reason": reason,
                "impact": impact_assessment
            }

        return set_severity

    def _load_all_tools(self):
        """載入所有可用的診斷工具函數。"""
        return [
            promql_query,
            log_search,
            trace_analysis,
            anomaly_detection
        ]

    @classmethod
    def create_metrics_analyzer(cls, config=None, safety_settings=None, generation_config=None):
        """工廠方法：建立專注於指標分析的診斷代理"""
        metrics_tools = [
            promql_query,
            anomaly_detection,
            cls._create_metrics_severity_evaluator()  # 專門的指標嚴重性評估
        ]

        instruction = DIAGNOSTICS_PROMPT.metrics_focus + """

        基於指標分析評估嚴重性時，重點關注：
        - 錯誤率 > 50% → P0
        - 錯誤率 > 10% → P1
        - 響應時間增加 > 5x → P1
        - 響應時間增加 > 2x → P2
        """

        return cls(
            config=config,
            instruction=instruction,
            tools=metrics_tools,
            safety_settings=safety_settings,
            generation_config=generation_config
        )

    @classmethod
    def create_log_analyzer(cls, config=None, safety_settings=None, generation_config=None):
        """
        工廠方法：建立一個專注於**日誌分析**的診斷代理實例。
        """
        log_tools = [log_search]
        return cls(
            config=config,
            instruction=DIAGNOSTICS_PROMPT.logs_focus,
            tools=log_tools,
            safety_settings=safety_settings,
            generation_config=generation_config
        )

    @classmethod
    def create_trace_analyzer(cls, config=None, safety_settings=None, generation_config=None):
        """
        工廠方法：建立一個專注於**分散式追蹤分析**的診斷代理實例。
        """
        trace_tools = [trace_analysis]
        return cls(
            config=config,
            instruction=DIAGNOSTICS_PROMPT.base,
            tools=trace_tools,
            safety_settings=safety_settings,
            generation_config=generation_config
        )

    @staticmethod
    def _create_metrics_severity_evaluator():
        """創建基於指標的嚴重性自動評估工具"""

        @agent_tool
        def evaluate_metrics_severity(
            error_rate: float,
            response_time_ms: float,
            baseline_response_time_ms: float,
            affected_endpoints: list
        ) -> Dict[str, Any]:
            """
            基於指標自動評估嚴重性。

            Args:
                error_rate: 當前錯誤率 (0-1)
                response_time_ms: 當前響應時間（毫秒）
                baseline_response_time_ms: 基線響應時間（毫秒）
                affected_endpoints: 受影響的端點列表

            Returns:
                嚴重性評估結果
            """
            severity = "P3"  # 默認最低級別
            reasons = []

            # 錯誤率評估
            if error_rate > 0.5:
                severity = "P0"
                reasons.append(f"Critical error rate: {error_rate*100:.1f}%")
            elif error_rate > 0.1:
                severity = "P1" if severity != "P0" else severity
                reasons.append(f"High error rate: {error_rate*100:.1f}%")
            elif error_rate > 0.01:
                severity = "P2" if severity not in ["P0", "P1"] else severity
                reasons.append(f"Elevated error rate: {error_rate*100:.1f}%")

            # 響應時間評估
            if baseline_response_time_ms > 0:
                degradation = response_time_ms / baseline_response_time_ms
                if degradation > 5:
                    severity = "P1" if severity != "P0" else severity
                    reasons.append(f"Severe response time degradation: {degradation:.1f}x")
                elif degradation > 2:
                    severity = "P2" if severity not in ["P0", "P1"] else severity
                    reasons.append(f"Response time degradation: {degradation:.1f}x")

            # 影響範圍評估
            critical_endpoints = ["/api/payment", "/api/auth", "/api/checkout"]
            if any(endpoint in critical_endpoints for endpoint in affected_endpoints):
                severity = "P1" if severity not in ["P0"] else severity
                reasons.append("Critical endpoints affected")

            return {
                "suggested_severity": severity,
                "reasons": reasons,
                "metrics": {
                    "error_rate": error_rate,
                    "response_time_ms": response_time_ms,
                    "degradation_factor": response_time_ms / baseline_response_time_ms if baseline_response_time_ms > 0 else 0
                }
            }

        return evaluate_metrics_severity
