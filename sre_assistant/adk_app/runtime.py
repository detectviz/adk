# ADK 標準執行階段 (Runtime) 建構器
from __future__ import annotations
import os
import time
from typing import TYPE_CHECKING, Optional, Dict, Any

# 官方 ADK 核心元件
from google.adk.agents import LlmAgent, LoopAgent, AgentConfig
from google.adk.planners import BuiltInPlanner
from google.adk.runner import Runner
from google.adk.tools import ToolRegistry
from google.adk.callbacks import CallbackContext

# 專案內部已標準化的元件
from sre_assistant.core.config import load_adk_config
from sre_assistant.core.session import get_session_service
from sre_assistant.core.safety import pre_screen_input_callback
from sre_assistant.core.structured_logger import get_logger, log_event
from sre_assistant.experts.experts import list_expert_tools
from sre_assistant.tools.toolset import SREAssistantToolset

if TYPE_CHECKING:
    from google.adk.agents import Agent

# 獲取專用的 logger 實例
logger = get_logger(__name__)

# --- 結構化日誌回呼函式 ---
async def before_agent_callback_with_logging(ctx: CallbackContext) -> Optional[Dict[str, Any]]:
    """在代理執行前，結合安全檢查與日誌記錄。"""
    log_event(logger, "agent_execution_started", {
        "agent_name": ctx.agent.name,
        "session_id": ctx.session.id,
        "user_input": ctx.get_last_user_input()
    })
    ctx.session.state["temp:start_time"] = time.monotonic()
    # 執行安全檢查
    return await pre_screen_input_callback(ctx)

async def after_agent_callback_with_logging(ctx: CallbackContext):
    """在代理執行後，記錄執行結果與延遲。"""
    start_time = ctx.session.state.get("temp:start_time", time.monotonic())
    latency_ms = (time.monotonic() - start_time) * 1000
    log_event(logger, "agent_execution_finished", {
        "agent_name": ctx.agent.name,
        "session_id": ctx.session.id,
        "final_output": ctx.get_last_turn().output,
        "latency_ms": round(latency_ms, 2)
    })

def build_runner_from_config(config: dict) -> Runner:
    """根據解析後的 adk.yaml 設定檔，建構一個完全符合 ADK 標準的 Runner。"""
    registry = ToolRegistry()
    registry.register(SREAssistantToolset())

    agent_config = AgentConfig(config.get("agent", {}))
    expert_tools = list_expert_tools(agent_config, registry)
    main_agent_tools = [registry] + expert_tools

    main_llm = LlmAgent(
        name="SRECoordinatorAgent",
        model=agent_config.model,
        instruction=agent_config.instruction,
        tools=main_agent_tools,
        tools_allowlist=agent_config.tools,
        before_agent_callback=before_agent_callback_with_logging,
        after_agent_callback=after_agent_callback_with_logging
    )

    planner = BuiltInPlanner()
    loop_agent = LoopAgent(
        agents=[main_llm],
        planner=planner,
        max_iterations=config.get("runner", {}).get("max_iterations", 10)
    )

    return Runner(agent=loop_agent, session_service=get_session_service())

def get_runner() -> Runner:
    """讀取設定檔並建立一個全域 Runner 實例。"""
    config = load_adk_config()
    return build_runner_from_config(config)

RUNNER = get_runner()
