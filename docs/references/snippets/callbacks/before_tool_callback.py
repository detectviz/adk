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

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from typing import Optional
from google.genai import types 
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from typing import Dict, Any


GEMINI_2_FLASH="gemini-2.0-flash"

def get_capital_city(country: str) -> str:
    """擷取給定國家的首都。"""
    print(f"--- 工具 'get_capital_city' 正在以國家：{country} 執行 ---")
    country_capitals = {
        "united states": "Washington, D.C.",
        "canada": "Ottawa",
        "france": "Paris",
        "germany": "Berlin",
    }
    return country_capitals.get(country.lower(), f"找不到 {country} 的首都")

capital_tool = FunctionTool(func=get_capital_city)

def simple_before_tool_modifier(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """檢查/修改工具參數或跳過工具呼叫。"""
    agent_name = tool_context.agent_name
    tool_name = tool.name
    print(f"[回呼] 代理 '{agent_name}' 中工具 '{tool_name}' 的工具呼叫前")
    print(f"[回呼] 原始參數：{args}")

    if tool_name == 'get_capital_city' and args.get('country', '').lower() == 'canada':
        print("[回呼] 偵測到 'Canada'。正在將參數修改為 'France'。")
        args['country'] = 'France'
        print(f"[回呼] 修改後的參數：{args}")
        return None

    # 如果工具是 'get_capital_city' 且國家是 'BLOCK'
    if tool_name == 'get_capital_city' and args.get('country', '').upper() == 'BLOCK':
        print("[回呼] 偵測到 'BLOCK'。正在跳過工具執行。")
        return {"result": "工具執行已被 before_tool_callback 封鎖。"}

    print("[回呼] 正在使用原始或先前修改的參數繼續。")
    return None

my_llm_agent = LlmAgent(
        name="ToolCallbackAgent",
        model=GEMINI_2_FLASH,
        instruction="您是一個可以尋找首都的代理。請使用 get_capital_city 工具。",
        description="一個展示 before_tool_callback 的 LLM 代理",
        tools=[capital_tool],
        before_tool_callback=simple_before_tool_modifier
)

APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

# 會話和執行器
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
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
await call_agent_async("Canada")
