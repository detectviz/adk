# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.langchain_tool import LangchainTool
from google.genai import types
from langchain_community.tools import TavilySearchResults

# 確保您的環境中已設定 TAVILY_API_KEY
if not os.getenv("TAVILY_API_KEY"):
    print("警告：未設定 TAVILY_API_KEY 環境變數。")

APP_NAME = "news_app"
USER_ID = "1234"
SESSION_ID = "session1234"

# 實例化 LangChain 工具
tavily_search = TavilySearchResults(
    max_results=5,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True,
    include_images=True,
)

# 使用 LangchainTool 包裝
adk_tavily_tool = LangchainTool(tool=tavily_search)

# 使用包裝後的工具定義代理
my_agent = Agent(
    name="langchain_tool_agent",
    model="gemini-2.0-flash",
    description="使用 TavilySearch 來回答問題的代理。",
    instruction="我可以透過搜尋網際網路來回答您的問題。儘管問我任何事！",
    tools=[adk_tavily_tool] # 在此處新增包裝後的工具
)

async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=my_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner

# 代理互動
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("代理回應：", final_response)

# 注意：在 Colab 中，您可以直接在頂層使用 'await'。
# 如果將此程式碼作為獨立的 Python 腳本執行，您需要使用 asyncio.run() 或管理事件迴圈。
await call_agent_async("GOOG 的股價")
