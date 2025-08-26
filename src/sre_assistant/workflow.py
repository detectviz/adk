# src/sre_assistant/workflow.py
"""
定義 SRE Assistant 的主工作流程協調器。

SREWorkflow 是一個 SequentialAgent，負責協調不同的專家子代理，
以完成 SRE 事件回應的各個階段。
"""
import logging
from typing import Optional, Dict, Any

from google.adk.agents import InvocationContext, SequentialAgent

# --- 核心服務匯入 ---
# 匯入 AuthManager 單例，用於處理認證和授權。
try:
    from .auth.auth_manager import AuthManager, auth_manager
except ImportError:
    # 針對設定檔尚未更新的環境提供佔位符。
    print("警告：無法匯入 AuthManager。將使用佔位符。")
    auth_manager = None
    AuthManager = type("AuthManager", (), {})

# --- 子代理匯入 ---
# 匯入構成工作流程各個階段的專家代理。
from .sub_agents.postmortem.agent import PostmortemAgent
from .sub_agents.remediation.dispatcher_agent import SREIntelligentDispatcher
from .sub_agents.diagnostic.citing_agent import CitingParallelDiagnosticsAgent
from .sub_agents.config.iterative_agent import IterativeOptimization

logger = logging.getLogger(__name__)


class SREWorkflow(SequentialAgent):
    """
    主要的 SRE 自動化工作流程。

    此代理透過四個不同的階段來協調事件回應流程：
    1. 並行診斷：同時從多個來源收集數據。
    2. 智慧分診：根據嚴重性選擇修復策略。(此處已更新為智慧分診器)
    3. 事後檢討：產生事件後報告。
    4. 迭代優化：微調設定以滿足 SLO 目標。
    """
    auth_manager: Optional[AuthManager] = None

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """透過組裝其組成的子代理來初始化 SRE 工作流程。"""
        agent_config = config or {}

        # --- 階段 1：帶引用的並行診斷 ---
        diagnostic_phase = CitingParallelDiagnosticsAgent(
            name="CitingParallelDiagnostics", config=agent_config
        )

        # --- 階段 2：智慧分診器 ---
        remediation_phase = SREIntelligentDispatcher(name="SREIntelligentDispatcher")

        # --- 階段 3：事後檢討 ---
        postmortem_phase = PostmortemAgent(name="PostmortemAgent")

        # --- 階段 4：迭代優化 ---
        optimization_phase = IterativeOptimization()

        # --- 組裝工作流程 ---
        super().__init__(
            name="SREWorkflowCoordinator",
            sub_agents=[
                diagnostic_phase,
                remediation_phase,
                postmortem_phase,
                optimization_phase
            ]
        )
        self.auth_manager = auth_manager

    async def run_with_auth(
        self,
        credentials: Dict[str, Any],
        resource: str,
        action: str,
        initial_context: Optional[InvocationContext] = None
    ) -> InvocationContext:
        """
        帶有認證和授權的工作流程執行入口點。

        此包裝器在執行核心工作流程之前驗證使用者權限。

        參數:
            credentials: 使用者提供的憑證 (例如 API 金鑰、權杖)。
            resource: 操作的目標資源。
            action: 要在資源上執行的操作。
            initial_context: 可選的初始代理上下文。

        返回:
            工作流程執行完畢後的代理上下文。

        引發:
            PermissionError: 如果認證或授權失敗。
            ImportError: 如果 AuthManager 不可用。
        """
        if not self.auth_manager:
            raise ImportError("AuthManager 不可用。")

        ctx = initial_context or InvocationContext()

        # 1. 認證 (將上下文傳遞給無狀態的 AuthManager)
        success, user_info = await self.auth_manager.authenticate(ctx, credentials)
        if not success:
            raise PermissionError("認證失敗。")

        logger.info(f"使用者 {user_info.get('email', user_info.get('user_id'))} 認證成功。")
        ctx.state["user_info"] = user_info  # 將使用者資訊注入上下文

        # 2. 授權 (將上下文傳遞給無狀態的 AuthManager)
        authorized = await self.auth_manager.authorize(ctx, user_info, resource, action)
        if not authorized:
            raise PermissionError(f"使用者未被授權在 '{resource}' 上執行 '{action}' 操作。")

        logger.info(f"在資源 '{resource}' 上執行 '{action}' 操作的授權成功。")

        # 3. 執行核心工作流程
        return await self.run_async(ctx)


def create_workflow(config: Optional[Dict[str, Any]] = None) -> SREWorkflow:
    """
    用於創建 SREWorkflow 實例的工廠函數。

    這是實例化工作流程的推薦方法，因為它將設定與使用分離。
    """
    return SREWorkflow(config)
