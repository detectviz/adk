import datetime
import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.google_api_tool import (
    CalendarToolset,  # type: ignore[import-untyped]
)


def create_agent(client_id, client_secret) -> LlmAgent:
    """建構 ADK 代理 (Agent)。"""
    LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini/gemini-2.0-flash-001')
    toolset = CalendarToolset(client_id=client_id, client_secret=client_secret)
    return LlmAgent(
        model=LiteLlm(model=LITELLM_MODEL),
        name='calendar_agent',
        description="一個可以協助管理使用者日曆的代理 (Agent)",
        instruction=f"""
您是一個可以協助管理使用者日曆的代理 (Agent)。

使用者會要求查詢其日曆狀態的資訊或對其日曆進行變更。請使用提供的工具與日曆 API 互動。

如果未指定，請假設使用者想要的日曆是「主要」日曆。

使用日曆 API 工具時，請使用格式正確的 RFC3339 時間戳記。

今天是 {datetime.datetime.now()}。
""",
        tools=[toolset],
    )
