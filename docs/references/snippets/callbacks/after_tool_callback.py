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
from copy import deepcopy

GEMINI_2_FLASH="gemini-2.0-flash"

# --- 定義一個簡單的工具函式（與之前相同）---
def get_capital_city(country: str) -> str:
    """擷取給定國家的首都。"""
    print(f"--- 工具 'get_capital_city' 正在執行，國家：{country} ---")
    country_capitals = {
        "united states": "Washington, D.C.",
        "canada": "Ottawa",
        "france": "Paris",
        "germany": "Berlin",
    }
    return {"result": country_capitals.get(country.lower(), f"找不到 {country} 的首都")}

# --- 將函式包裝成一個工具 ---
capital_tool = FunctionTool(func=get_capital_city)

# --- 定義回呼函式 ---
def simple_after_tool_modifier(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:
    """在工具執行後檢查/修改工具結果。"""
    agent_name = tool_context.agent_name
    tool_name = tool.name
    print(f"[回呼] 代理 '{agent_name}' 中工具 '{tool_name}' 的工具呼叫後")
    print(f"[回呼] 使用的參數：{args}")
    print(f"[回呼] 原始工具回應：{tool_response}")

    # 函式工具結果的預設結構是 {"result": <return_value>}
    original_result_value = tool_response.get("result", "")
    # original_result_value = tool_response

    # --- 修改範例 ---
    # 如果工具是 'get_capital_city' 且結果是 'Washington, D.C.'
    if tool_name == 'get_capital_city' and original_result_value == "Washington, D.C.":
        print("[回呼] 偵測到 'Washington, D.C.'。正在修改工具回應。")

        # 重要：建立一個新字典或修改一個副本
        modified_response = deepcopy(tool_response)
        modified_response["result"] = f"{original_result_value} (注意：這是美國的首都)。"
        modified_response["note_added_by_callback"] = True # 如果需要，可以新增額外資訊

        print(f"[回呼] 修改後的工具回應：{modified_response}")
        return modified_response # 返回修改後的字典

    print("[回呼] 傳遞原始工具回應。")
    # 返回 None 以使用原始的 tool_response
    return None


# 建立 LlmAgent 並指派回呼
my_llm_agent = LlmAgent(
        name="AfterToolCallbackAgent",
        model=GEMINI_2_FLASH,
        instruction="您是一個使用 get_capital_city 工具尋找首都的代理。請清楚地報告結果。",
        description="一個展示 after_tool_callback 的 LLM 代理",
        tools=[capital_tool], # 新增工具
        after_tool_callback=simple_after_tool_modifier # 指派回呼
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
await call_agent_async("united states")
