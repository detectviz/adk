# src/sre_assistant/workflow.py
"""
定義 SRE Assistant 的主工作流程協調器。

SREWorkflow 是一個 SequentialAgent，負責協調不同的專家子代理，
以完成 SRE 事件回應的各個階段。
"""
import logging
from typing import Optional, Dict, Any

from google.adk.agents import InvocationContext, SequentialAgent
from google.generativeai.types import (
    SafetySetting,
    HarmCategory,
    HarmBlockThreshold,
    GenerationConfig,
)

# --- 子代理匯入 ---
# 匯入構成工作流程各個階段的專家代理。
from .sub_agents.postmortem.agent import PostmortemAgent
from .sub_agents.remediation.dispatcher_agent import SREIntelligentDispatcher
from .sub_agents.diagnostic.citing_agent import CitingParallelDiagnosticsAgent
from .sub_agents.config.iterative_agent import IterativeOptimization

logger = logging.getLogger(__name__)


from .auth.tools import authenticate, check_authorization
from google.adk.agents import BaseAgent

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

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        透過組裝其組成的子代理來初始化 SRE 工作流程。

        Args:
            config (Optional[Dict[str, Any]]): 一個可選的配置字典，用於傳遞給子代理。
        """
        super().__init__(name="SREWorkflowCoordinator")
        agent_config = config or {}

        # --- 標準化設定 ---
        # 統一為所有 LLM-based 的子代理定義負責任 AI 的安全設定。
        # 這確保了所有生成內容都遵循相同的安全標準。
        safety_settings = [
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
        ]
        # 統一為所有 LLM-based 的子代理定義內容生成設定。
        # 較低的 temperature (0.4) 使其輸出更具確定性和事實性，適合 SRE 場景。
        generation_config = GenerationConfig(
            temperature=0.4, top_p=1.0, top_k=32, candidate_count=1, max_output_tokens=8192,
        )

        # --- 階段性子代理定義 ---
        # 根據 SRE 事件回應的生命週期，實例化各個階段的專家代理。
        # 將標準化設定向下傳遞給所有需要使用 LLM 的子代理。
        diagnostic_phase = CitingParallelDiagnosticsAgent(
            name="CitingParallelDiagnostics",
            config=agent_config,
            safety_settings=safety_settings,
            generation_config=generation_config,
        )
        remediation_phase = SREIntelligentDispatcher(
            name="SREIntelligentDispatcher",
            safety_settings=safety_settings,
            generation_config=generation_config,
        )
        postmortem_phase = PostmortemAgent(
            name="PostmortemAgent",
            safety_settings=safety_settings,
            generation_config=generation_config,
        )
        # 注意：IterativeOptimization 不是 LLM 代理，因此不需要傳遞這些設定。
        optimization_phase = IterativeOptimization()

        # --- 組裝核心工作流程序列 ---
        # 將各階段的專家代理組裝成一個循序執行的工作流程。
        # self.main_sequence 屬性持有了這個核心業務邏輯。
        self.main_sequence = SequentialAgent(
            name="MainSRESequence",
            sub_agents=[
                diagnostic_phase,
                remediation_phase,
                postmortem_phase,
                optimization_phase
            ]
        )

    async def _run_async_impl(self, ctx: InvocationContext) -> None:
        """
        執行包含認證和授權的完整工作流程。

        這是此代理的執行入口點。它首先執行安全檢查，然後才執行核心的業務邏輯。
        此方法假定 `ctx.state` 中已包含 'credentials', 'resource', 和 'action' 等
        從外部傳入的參數。

        Args:
            ctx (InvocationContext): ADK 的核心上下文對象，用於在代理執行過程中傳遞狀態。
        """
        # 步驟 1: 從上下文中提取執行工作流程所需的參數。
        # 這種設計使得工作流程本身是無狀態的，所有執行所需的狀態都由外部提供。
        credentials = ctx.state.get("credentials")
        resource = ctx.state.get("resource")
        action = ctx.state.get("action")

        if not all([credentials, resource, action]):
            missing = [k for k in ['credentials', 'resource', 'action'] if not ctx.state.get(k)]
            raise ValueError(f"Context is missing required keys for workflow execution: {missing}")

        # 步驟 2: 使用重構後的 `authenticate` 工具執行認證。
        # 這是取代舊 `AuthManager` 的無狀態方法。
        auth_success, user_info = await authenticate(ctx, credentials)
        if not auth_success:
            # 認證失敗時，在上下文中記錄失敗狀態並終止執行。
            # 這種方式比直接引發異常更為優雅，便於上層呼叫者處理。
            ctx.state["workflow_status"] = "failed_authentication"
            ctx.state["error_message"] = "Authentication failed."
            logger.error("Workflow terminated: Authentication failed.")
            return

        # 步驟 3: 使用重構後的 `check_authorization` 工具執行授權。
        authz_success = await check_authorization(ctx, resource, action)
        if not authz_success:
            # 授權失敗時，同樣記錄狀態並終止。
            ctx.state["workflow_status"] = "failed_authorization"
            ctx.state["error_message"] = f"User not authorized for action '{action}' on resource '{resource}'."
            logger.error(f"Workflow terminated: Authorization failed for user {user_info.get('email')}.")
            return

        # 步驟 4: 執行核心的 SRE 工作流程。
        # 只有在認證和授權都成功後，才會執行 `self.main_sequence`。
        logger.info(f"User {user_info.get('email')} authorized. Starting main SRE sequence.")
        await self.main_sequence.run_async(ctx)
        ctx.state["workflow_status"] = "completed_successfully"


def create_workflow(config: Optional[Dict[str, Any]] = None) -> SREWorkflow:
    """
    用於創建 SREWorkflow 實例的工廠函數。

    這是實例化工作流程的推薦方法，因為它將設定與使用分離。
    """
    return SREWorkflow(config)
