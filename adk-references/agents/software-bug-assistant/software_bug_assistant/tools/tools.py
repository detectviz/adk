# Copyright 2025 Google LLC
#
# 根據 Apache 授權條款 2.0 版 (「授權」) 授權；
# 除非遵守授權，否則您不得使用此檔案。
# 您可以在以下網址取得授權副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據授權散佈的軟體
# 是以「現狀」為基礎散佈的，
# 不附帶任何明示或暗示的保證或條件。
# 請參閱授權以了解特定語言下的權限和
# 限制。
# 為此模組新增 docstring

from datetime import datetime
import os

from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.langchain_tool import LangchainTool
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from langchain_community.tools import StackExchangeTool
from langchain_community.utilities import StackExchangeAPIWrapper
from toolbox_core import ToolboxSyncClient

from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


# ----- 函式工具範例 -----
def get_current_date() -> dict:
    """
    以 YYYY-MM-DD 格式取得目前日期
    """
    return {"current_date": datetime.now().strftime("%Y-%m-%d")}


# ----- 內建工具範例 -----
search_agent = Agent(
    model="gemini-2.5-flash",
    name="search_agent",
    instruction="""
    您是 Google 搜尋的專家。
    """,
    tools=[google_search],
)

search_tool = AgentTool(search_agent)

# ----- 第三方工具 (LangChainTool) 範例 -----
stack_exchange_tool = StackExchangeTool(api_wrapper=StackExchangeAPIWrapper())
# 使用 LangchainTool 將 LangChain 工具轉換為 ADK 工具
langchain_tool = LangchainTool(stack_exchange_tool)

# ----- Google Cloud 工具 (MCP Toolbox for Databases) 範例 -----
TOOLBOX_URL = os.getenv("MCP_TOOLBOX_URL", "http://127.0.0.1:5000")

# 初始化 Toolbox 用戶端
toolbox = ToolboxSyncClient(TOOLBOX_URL)
# 從工具集載入所有工具
toolbox_tools = toolbox.load_toolset("tickets_toolset")


# ----- MCP 工具 (streamable-http) 範例 -----
mcp_tools = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://api.githubcopilot.com/mcp/",
        headers={
            "Authorization": "Bearer " + os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
        },
    ),
    # 唯讀工具
    tool_filter=[
        "search_repositories",
        "search_issues",
        "list_issues",
        "get_issue",
        "list_pull_requests",
        "get_pull_request",
    ],
)
