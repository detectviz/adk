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

# --- 完整的範例程式碼，展示 LlmAgent 使用工具 (Tools) 與輸出結構 (Output Schema) 的比較 ---
import json # 用於美化輸出字典

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field

# --- 1. 定義常數 (Define Constants) ---
APP_NAME = "agent_comparison_app"
USER_ID = "test_user_456"
SESSION_ID_TOOL_AGENT = "session_tool_agent_xyz"
SESSION_ID_SCHEMA_AGENT = "session_schema_agent_xyz"
MODEL_NAME = "gemini-2.0-flash"

# --- 2. 定義結構 (Define Schemas) ---

# 兩個代理都使用的輸入結構
class CountryInput(BaseModel):
    country: str = Field(description="要取得資訊的國家。")

# 僅供第二個代理使用的輸出結構
class CapitalInfoOutput(BaseModel):
    capital: str = Field(description="該國家的首都。")
    # 注意：人口數僅為示意；LLM 將推斷或估計此值
    # 因為設定 output_schema 時無法使用工具。
    population_estimate: str = Field(description="首都的估計人口數。")

# --- 3. 定義工具 (Define the Tool) (僅供第一個代理使用) ---
def get_capital_city(country: str) -> str:
    """擷取給定國家的首都。"""
    print(f"\n-- 工具呼叫 (Tool Call): get_capital_city(country='{country}') --")
    country_capitals = {
        "united states": "Washington, D.C.",
        "canada": "Ottawa",
        "france": "Paris",
        "japan": "Tokyo",
    }
    result = country_capitals.get(country.lower(), f"抱歉，我找不到 {country} 的首都。")
    print(f"-- 工具結果 (Tool Result): '{result}' --")
    return result

# --- 4. 設定代理 (Configure Agents) ---

# 代理 1：使用工具和 output_key
capital_agent_with_tool = LlmAgent(
    model=MODEL_NAME,
    name="capital_agent_tool",
    description="使用特定工具擷取首都。",
    instruction="""您是一個有幫助的代理，使用工具提供國家的首都。
使用者將以 JSON 格式提供國家名稱，例如 {"country": "國家名稱"}。
1. 提取國家名稱。
2. 使用 `get_capital_city` 工具尋找首都。
3. 清晰地回覆使用者，說明工具找到的首都。
""",
    tools=[get_capital_city],
    input_schema=CountryInput,
    output_key="capital_tool_result", # 儲存最終的文字回應
)

# 代理 2：使用 output_schema (無法使用工具)
structured_info_agent_schema = LlmAgent(
    model=MODEL_NAME,
    name="structured_info_agent_schema",
    description="以特定的 JSON 格式提供首都和估計的人口。",
    instruction=f"""您是一個提供國家資訊的代理。
使用者將以 JSON 格式提供國家名稱，例如 {{"country": "國家名稱"}}。
僅以符合此確切結構的 JSON 物件回應：
{json.dumps(CapitalInfoOutput.model_json_schema(), indent=2)}
運用您的知識來判斷首都並估計人口。請勿使用任何工具。
""",
    # *** 此處沒有 tools 參數 - 使用 output_schema 會阻止工具的使用 ***
    input_schema=CountryInput,
    output_schema=CapitalInfoOutput, # 強制使用 JSON 輸出結構
    output_key="structured_info_result", # 儲存最終的 JSON 回應
)

# --- 5. 設定會話管理和執行器 (Set up Session Management and Runners) ---
session_service = InMemorySessionService()

# 為了清晰起見，建立獨立的會話，雖然如果上下文管理得當，這並非絕對必要
await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_TOOL_AGENT)
await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_SCHEMA_AGENT)

# 為每個代理建立一個執行器
capital_runner = Runner(
    agent=capital_agent_with_tool,
    app_name=APP_NAME,
    session_service=session_service
)
structured_runner = Runner(
    agent=structured_info_agent_schema,
    app_name=APP_NAME,
    session_service=session_service
)

# --- 6. 定義代理互動邏輯 (Define Agent Interaction Logic) ---
async def call_agent_and_print(
    runner_instance: Runner,
    agent_instance: LlmAgent,
    session_id: str,
    query_json: str
):
    """將查詢傳送至指定的代理/執行器並印出結果。"""
    print(f"\n>>> 正在呼叫代理：'{agent_instance.name}' | 查詢：{query_json}")

    user_content = types.Content(role='user', parts=[types.Part(text=query_json)])

    final_response_content = "未收到最終回應。"
    async for event in runner_instance.run_async(user_id=USER_ID, session_id=session_id, new_message=user_content):
        # print(f"事件：{event.type}，作者：{event.author}") # 取消註解以進行詳細日誌記錄
        if event.is_final_response() and event.content and event.content.parts:
            # 對於 output_schema，內容是 JSON 字串本身
            final_response_content = event.content.parts[0].text

    print(f"<<< 代理 '{agent_instance.name}' 的回應：{final_response_content}")

    current_session = await session_service.get_session(app_name=APP_NAME,
                                                  user_id=USER_ID,
                                                  session_id=session_id)
    stored_output = current_session.state.get(agent_instance.output_key)

    # 如果儲存的輸出看起來像 JSON（可能來自 output_schema），則美化輸出
    print(f"--- 會話狀態 ['{agent_instance.output_key}']: ", end="")
    try:
        # 嘗試解析並美化輸出（如果是 JSON）
        parsed_output = json.loads(stored_output)
        print(json.dumps(parsed_output, indent=2))
    except (json.JSONDecodeError, TypeError):
         # 否則，以字串形式印出
        print(stored_output)
    print("-" * 30)


# --- 7. 執行互動 (Run Interactions) ---
async def main():
    print("--- 測試使用工具的代理 ---")
    await call_agent_and_print(capital_runner, capital_agent_with_tool, SESSION_ID_TOOL_AGENT, '{"country": "France"}')
    await call_agent_and_print(capital_runner, capital_agent_with_tool, SESSION_ID_TOOL_AGENT, '{"country": "Canada"}')

    print("\n\n--- 測試使用輸出結構的代理 (不使用工具) ---")
    await call_agent_and_print(structured_runner, structured_info_agent_schema, SESSION_ID_SCHEMA_AGENT, '{"country": "France"}')
    await call_agent_and_print(structured_runner, structured_info_agent_schema, SESSION_ID_SCHEMA_AGENT, '{"country": "Japan"}')

# --- 執行代理 ---
# 注意：在 Colab 中，您可以直接在頂層使用 'await'。
# 如果將此程式碼作為獨立的 Python 腳本執行，您需要使用 asyncio.run() 或管理事件迴圈。
if __name__ == "__main__":
    await main()
