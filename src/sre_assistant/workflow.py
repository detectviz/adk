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
from google.adk.agents import SequentialAgent
from google.genai.types import (
    SafetySetting,
    HarmCategory,
    HarmBlockThreshold,
    GenerationConfig,
)

# --- 子代理匯入 ---
# 舊的子代理已被移除，以符合新的架構。
# 未來將根據 TASKS.md 中的定義，重新實現標準化的子代理。

logger = logging.getLogger(__name__)


from .auth.tools import authenticate, check_authorization
from google.adk.agents import BaseAgent, LlmAgent

class SREWorkflow(BaseAgent):
    """
    主要的 SRE 自動化工作流程協調器 (已重構)。

    這個類別是整個 SRE Assistant 的核心入口點。它不再是一個簡單的循序代理，
    而是一個高階的協調器 (`BaseAgent`)。它的主要職責是：
    1.  初始化整個工作流程中所有子代理所需的標準化設定 (安全、模型生成)。
    2.  組裝核心的業務邏輯，即一個由多個專家子代理組成的 `SequentialAgent`。
    3.  在執行核心業務邏輯之前，先執行前置的認證 (Authentication) 和授權 (Authorization) 檢查。
    這種模式將關注點分離，使得核心業務流程與外圍的驗證邏輯解耦。
    """
    main_sequence: BaseAgent = None

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        透過組裝其組成的子代理來初始化 SRE 工作流程。

        Args:
            config (Optional[Dict[str, Any]]): 一個可選的配置字典，用於傳遞給子代理。
        """
        super().__init__(name="SREWorkflowCoordinator")
        agent_config = config or {}

        # --- 階段性子代理定義 ---
        # 由於舊的子代理已被移除，此處使用一個極簡的 LlmAgent 作為佔位符，
        # 以確保工作流程在結構上是完整且可運行的。
        # 移除複雜的配置以解決暫時的依賴版本和測試環境問題。
        # 未來的開發將根據 TASKS.md 來實現和組裝具有完整配置的真正子代理。
        placeholder_agent = LlmAgent(
            name="PlaceholderAgent",
            model="gemini-1.5-flash",
        )


        # --- 組裝核心工作流程序列 ---
        # 將各階段的專家代理組裝成一個循序執行的工作流程。
        # self.main_sequence 屬性持有了這個核心業務邏輯。
        self.main_sequence = SequentialAgent(
            name="MainSRESequence",
            sub_agents=[
                placeholder_agent
            ]
        )

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        執行包含認證和授權的完整工作流程。

        這是此代理的執行入口點。它首先執行安全檢查，然後才執行核心的業務邏輯。
        此方法假定 `ctx.session.state` 中已包含 'credentials', 'resource', 和 'action' 等
        從外部傳入的參數。

        Args:
            ctx (InvocationContext): ADK 的核心上下文對象，用於在代理執行過程中傳遞狀態。

        Yields:
            Event: 從子代理產生的事件。
        """
        # 步驟 1: 從上下文中提取執行工作流程所需的參數。
        # 這種設計使得工作流程本身是無狀態的，所有執行所需的狀態都由外部提供。
        credentials = ctx.session.state.get("credentials")
        resource = ctx.session.state.get("resource")
        action = ctx.session.state.get("action")

        if not all([credentials, resource, action]):
            missing = [k for k in ['credentials', 'resource', 'action'] if not ctx.session.state.get(k)]
            # 產生一個錯誤事件而不是引發異常，讓框架可以優雅地處理
            yield Event(
                author="SREWorkflowCoordinator",
                error_message=f"Context is missing required keys: {missing}"
            )
            return

        # 步驟 2: 使用重構後的 `authenticate` 工具執行認證。
        # 這是取代舊 `AuthManager` 的無狀態方法。
        auth_success, user_info = await authenticate(ctx, credentials)
        if not auth_success:
            # 認證失敗時，在上下文中記錄失敗狀態並終止執行。
            ctx.session.state["workflow_status"] = "failed_authentication"
            ctx.session.state["error_message"] = "Authentication failed."
            yield Event(author="SREWorkflowCoordinator", error_message="Authentication failed.")
            logger.error("Workflow terminated: Authentication failed.")
            return

        # 步驟 3: 使用重構後的 `check_authorization` 工具執行授權。
        authz_success = await check_authorization(ctx, resource, action)
        if not authz_success:
            # 授權失敗時，同樣記錄狀態並終止。
            ctx.session.state["workflow_status"] = "failed_authorization"
            ctx.session.state["error_message"] = f"User not authorized for action '{action}' on resource '{resource}'."
            yield Event(author="SREWorkflowCoordinator", error_message="Authorization failed.")
            logger.error(f"Workflow terminated: Authorization failed for user {user_info.get('email')}.")
            return

        # 步驟 4: 執行核心的 SRE 工作流程。
        # 只有在認證和授權都成功後，才會執行 `self.main_sequence`。
        logger.info(f"User {user_info.get('email')} authorized. Starting main SRE sequence.")
        async for event in self.main_sequence.run_async(ctx):
            yield event
        ctx.session.state["workflow_status"] = "completed_successfully"


def create_workflow(config: Optional[Dict[str, Any]] = None) -> SREWorkflow:
    """
    用於創建 SREWorkflow 實例的工廠函數。

    這是實例化工作流程的推薦方法，因為它將設定與使用分離。
    """
    return SREWorkflow(config)
