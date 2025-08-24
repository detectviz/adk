# sre_assistant/tests/test_e2e_workflow.py

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json
import uuid

from sre_assistant.workflow import SREWorkflow
from google.adk.agents.invocation_context import InvocationContext
from google.adk.session_service import BaseSessionService
from google.adk.agents.base_agent import BaseAgent
from google.adk.session import Session

# Mock classes to satisfy Pydantic validation
class MockSessionService(BaseSessionService):
    async def create_session(self, **kwargs): pass
    async def get_session(self, **kwargs): pass
    async def update_session(self, **kwargs): pass
    async def delete_session(self, **kwargs): pass
    async def list_sessions(self, **kwargs): return []

class MockAgent(BaseAgent):
    async def run_async(self, **kwargs): pass

class MockSession(Session):
    def __init__(self):
        super().__init__(session_id="mock_session", session_service=MockSessionService())


# 測試場景定義
TEST_SCENARIOS = {
    "p0_production_down": {
        "description": "生產環境完全不可用",
        "metrics": {
            "error_rate": 0.95,
            "response_time_ms": 10000,
            "baseline_response_time_ms": 200,
            "affected_users_percentage": 100
        },
        "logs": {
            "critical_errors": 500,
            "error_messages": ["Connection refused", "Database unreachable"],
            "affected_services": ["api-gateway", "payment-service", "auth-service"]
        },
        "expected_severity": "P0",
        "expected_remediation": "HITLRemediationAgent",
        "expected_citations": True
    },
    "p1_partial_outage": {
        "description": "部分服務降級",
        "metrics": {
            "error_rate": 0.25,
            "response_time_ms": 1500,
            "baseline_response_time_ms": 300,
            "affected_users_percentage": 40
        },
        "logs": {
            "critical_errors": 50,
            "error_messages": ["Timeout", "Circuit breaker open"],
            "affected_services": ["recommendation-service"]
        },
        "expected_severity": "P1",
        "expected_remediation": "AutoRemediationWithLogging",
        "expected_citations": True
    },
    "p2_performance_degradation": {
        "description": "性能降級但服務可用",
        "metrics": {
            "error_rate": 0.02,
            "response_time_ms": 800,
            "baseline_response_time_ms": 300,
            "affected_users_percentage": 10
        },
        "logs": {
            "critical_errors": 5,
            "error_messages": ["Slow query warning"],
            "affected_services": ["analytics-service"]
        },
        "expected_severity": "P2",
        "expected_remediation": "ScheduledRemediation",
        "expected_citations": True
    }
}

class TestE2EWorkflow:
    """端到端工作流程測試套件"""

    @pytest.fixture
    def mock_workflow(self):
        """創建模擬的 SREWorkflow"""
        from sre_assistant.workflow import SREWorkflow

        # Mock 所有外部依賴
        with patch('sre_assistant.workflow.auth_manager') as mock_auth:
            mock_auth.authenticate = AsyncMock(return_value=(True, {"user": "test"}))
            mock_auth.authorize = AsyncMock(return_value=True)

            workflow = SREWorkflow(config={
                "test_mode": True,
                "timeout": 30
            })

            # Mock 工具調用
            self._mock_diagnostic_tools(workflow)
            self._mock_remediation_tools(workflow)

            return workflow

    def _mock_diagnostic_tools(self, workflow):
        """模擬診斷工具"""
        # Mock Prometheus 查詢
        with patch('sre_assistant.sub_agents.diagnostic.tools.promql_query') as mock_prom:
            mock_prom.side_effect = self._prometheus_mock_response

        # Mock 日誌搜索
        with patch('sre_assistant.sub_agents.diagnostic.tools.log_search') as mock_logs:
            mock_logs.side_effect = self._log_search_mock_response

    def _mock_remediation_tools(self, workflow):
        """模擬修復工具"""
        # Mock Kubernetes 操作
        with patch('sre_assistant.sub_agents.remediation.tools.restart_pod') as mock_k8s:
            mock_k8s.return_value = {"status": "success", "message": "Pod restarted"}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("scenario_name,scenario", TEST_SCENARIOS.items())
    async def test_complete_workflow(self, mock_workflow, scenario_name, scenario):
        """測試完整的工作流程"""

        # 準備測試上下文
        context = self._create_test_context(scenario, mock_workflow)

        # 執行工作流程
        start_time = datetime.utcnow()

        try:
            # 運行工作流程
            result_context = await asyncio.wait_for(
                mock_workflow.run_async(context),
                timeout=60
            )

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            # 驗證結果
            self._verify_workflow_result(result_context, scenario, execution_time)

        except asyncio.TimeoutError:
            pytest.fail(f"Workflow timeout for scenario: {scenario_name}")
        except Exception as e:
            pytest.fail(f"Workflow failed for scenario {scenario_name}: {e}")

    def _create_test_context(self, scenario, agent):
        """創建測試上下文"""
        context = InvocationContext(
            session_service=MockSessionService(),
            invocation_id=f"inv-{uuid.uuid4()}",
            agent=agent,
            session=MockSession()
        )
        context.state = {
            "incident_id": f"test-{datetime.utcnow().timestamp()}",
            "test_scenario": scenario,
            "metrics_data": scenario["metrics"],
            "logs_data": scenario["logs"]
        }

        return context

    def _verify_workflow_result(self, result_context, scenario, execution_time):
        """驗證工作流程結果"""

        # 1. 驗證嚴重性評估
        assert result_context.state.get("severity") == scenario["expected_severity"], \
            f"Expected severity {scenario['expected_severity']}, got {result_context.state.get('severity')}"

        # 2. 驗證修復策略選擇
        remediation_agent_name = result_context.state.get("remediation_agent_name")
        assert remediation_agent_name == scenario["expected_remediation"], \
            f"Expected remediation {scenario['expected_remediation']}, got {remediation_agent_name}"

        # 3. 驗證引用存在
        if scenario["expected_citations"]:
            assert "diagnostic_citations" in result_context.state, \
                "Expected citations in diagnostic results"

            citations = result_context.state["diagnostic_citations"]
            assert len(citations) > 0, "Citations should not be empty"

        # 4. 驗證性能
        if scenario["expected_severity"] == "P0":
            # P0 應該在 30 秒內完成
            assert execution_time < 30, \
                f"P0 incident took {execution_time}s, expected < 30s"

        # 5. 驗證審計日誌
        # This would require inspecting logs, which is outside this test's scope.
        # We can check if the audit log function was called if we patch it.

        # 6. 驗證狀態完整性
        required_states = [
            "severity",
            "remediation_status",
        ]
        for state_key in required_states:
            assert state_key in result_context.state, \
                f"Required state '{state_key}' not found"

    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, mock_workflow):
        """測試工作流程錯誤處理"""
        # This test is complex and requires more specific mocks.
        # For example, mocking a remediation tool to consistently fail.
        # We will add a placeholder for now.
        pass

    # Mock responses for tools
    async def _prometheus_mock_response(self, query):
        return {"status": "success", "data": {"result": []}}, {"source": "prometheus", "query": query}

    async def _log_search_mock_response(self, query):
        return {"hits": 0, "logs": []}, {"source": "log_db", "query": query}

# We need to adjust the placeholder agents to record their execution
from sre_assistant.workflow import HITLRemediationAgent, AutoRemediationWithLogging, ScheduledRemediation

async def run_async_recorder(self, ctx):
    ctx.state["remediation_agent_name"] = self.name
    # A real agent would return a new context, but for this mock, we'll just modify in place
    return ctx

# Patch the placeholder agents to record their name upon execution
@pytest.fixture(autouse=True)
def patch_remediation_agents():
    with patch.object(HITLRemediationAgent, "run_async", new=run_async_recorder), \
         patch.object(AutoRemediationWithLogging, "run_async", new=run_async_recorder), \
         patch.object(ScheduledRemediation, "run_async", new=run_async_recorder):
        yield
