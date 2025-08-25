import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParameters,
)


def create_weather_agent() -> LlmAgent:
    """建構 ADK 代理 (Agent)。"""
    LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini-2.5-flash')
    return LlmAgent(
        model=LiteLlm(model=LITELLM_MODEL),
        name='weather_agent',
        description='一個可以協助回答天氣問題的代理 (Agent)',
        instruction="""你是一位專業的天氣預報助理。你的主要職責是利用提供的工具來擷取和轉達天氣資訊以回應使用者查詢。你必須完全依賴這些工具來取得資料，並避免捏造資訊。請確保所有回應都包含所用工具的詳細輸出，並以 Markdown 格式化""",
        tools=[
            MCPToolset(
                connection_params=StdioServerParameters(
                    command='python',
                    args=['./weather_mcp.py'],
                ),
            )
        ],
    )
