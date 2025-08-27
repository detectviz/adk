# src/sre_assistant/workflow.py
"""
定義 SRE Assistant 的主工作流程協調器。

SREWorkflow 是一個 SequentialAgent，負責協調不同的專家子代理，
以完成 SRE 事件回應的各個階段。
"""
import logging
from typing import Optional, Dict, Any, AsyncGenerator

from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents import SequentialAgent, LlmAgent, BaseAgent
from google.adk.tools import FunctionTool, LongRunningFunctionTool
from google.genai.types import (
    SafetySetting,
    HarmCategory,
    HarmBlockThreshold,
    GenerationConfig,
)

logger = logging.getLogger(__name__)


from .auth.tools import authenticate, check_authorization
from .tool_registry import tool_registry


# 步驟 1: 定義代表高風險操作和人工審批的 Python 函數。
# 這遵循 `human_in_the_loop.py` 程式碼片段的模式。

@FunctionTool
def execute_high_risk_remediation(reason: str) -> Dict[str, Any]:
    """一個模擬的工具，代表一個高風險的修復操作。"""
    logger.warning(f"正在執行高風險操作: {reason}")
    return {"status": "completed", "action": reason}

def ask_for_approval(reason: str, amount: float) -> dict[str, Any]:
    """請求核准報銷。此函數將由 LongRunningFunctionTool 包裝。"""
    logger.info(f"發出人工審批請求，原因: {reason}, 金額: {amount}")
    return {'status': 'pending', 'approver': 'sre-lead@example.com', 'reason' : reason, 'amount': amount}

# 使用 LongRunningFunctionTool 包裝審批函數
human_approval_tool = LongRunningFunctionTool(func=ask_for_approval)


class SREWorkflow(BaseAgent):
    """
    主要的 SRE 自動化工作流程協調器 (已重構)。

    這個類別現在主要作為一個工廠，用於構建一個包含正確 HITL 流程的
    `SequentialAgent`。外部的運行器 (Runner) 將負責處理事件循環和
    回饋響應，以符合 ADK 的長時運行工具模式。
    """
    main_sequence: BaseAgent

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        透過組裝其組成的子代理來初始化 SRE 工作流程。
        """
        # 步驟 1: 提前構建子代理。
        approval_requester_agent = LlmAgent(
            name="ApprovalRequester",
            model="gemini-1.5-flash",
            tools=[human_approval_tool],
            instruction="""
            你是一個安全流程協調員。
            你需要為一個高風險操作請求人工批准。
            請調用 ask_for_approval 工具，原因為 '重啟生產資料庫'，金額為 500。
            """
        )
        remediation_executor_agent = LlmAgent(
            name="RemediationExecutor",
            model="gemini-1.5-flash",
            tools=[execute_high_risk_remediation],
            instruction="""
            你是一個自動化操作執行器。
            請檢查上一步 (ask_for_approval) 的輸出。
            如果 'status' 字段為 'approved'，請調用 execute_high_risk_remediation 工具，
            並將原因設置為 '由Manager批准後執行'。
            如果 'status' 字段為 'rejected'，請輸出 '操作已被取消' 並停止。
            """
        )
        main_sequence_agent = SequentialAgent(
            name="MainSRESequence",
            sub_agents=[
                approval_requester_agent,
                remediation_executor_agent
            ]
        )

        # 步驟 2: 在調用 super().__init__ 時，將 main_sequence 作為參數傳入。
        # 這符合 Pydantic V2 的初始化和驗證模型。
        super().__init__(name="SREWorkflowCoordinator", main_sequence=main_sequence_agent)

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        執行核心的 SRE 工作流程。

        注意：此方法現在只代理到 `main_sequence`。所有複雜的事件循環、
        認證和回饋邏輯都已移至外部的運行器 (Runner) 或測試循環中，
        以符合 `human_in_the_loop.py` 範例揭示的模式。
        """
        logger.info("SREWorkflowCoordinator: 正在啟動主序列...")
        async for event in self.main_sequence.run_async(ctx):
            yield event
        logger.info("SREWorkflowCoordinator: 主序列已完成。")


def create_workflow(config: Optional[Dict[str, Any]] = None) -> SREWorkflow:
    """
    用於創建 SREWorkflow 實例的工廠函數。

    這是實例化工作流程的推薦方法，因為它將設定與使用分離。
    """
    return SREWorkflow(config)
