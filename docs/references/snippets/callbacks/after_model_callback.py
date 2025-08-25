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
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import Runner
from typing import Optional
from google.genai import types 
from google.adk.sessions import InMemorySessionService
from google.adk.models import LlmResponse
import copy

GEMINI_2_FLASH="gemini-2.0-flash"

# --- 定義回呼函式 ---
def simple_after_model_modifier(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """在收到大型語言模型（LLM）回應後，檢查/修改它。"""
    agent_name = callback_context.agent_name
    print(f"[回呼] 代理 {agent_name} 的模型呼叫後")

    # --- 檢查 ---
    original_text = ""
    if llm_response.content and llm_response.content.parts:
        # 此範例假設為簡單的文字回應
        if llm_response.content.parts[0].text:
            original_text = llm_response.content.parts[0].text
            print(f"[回呼] 檢查到的原始回應文字：'{original_text[:100]}...'") # 記錄片段
        elif llm_response.content.parts[0].function_call:
             print(f"[回呼] 檢查到的回應：包含函式呼叫 '{llm_response.content.parts[0].function_call.name}'。不進行文字修改。")
             return None # 在此範例中不修改工具呼叫
        else:
             print("[回呼] 檢查到的回應：未找到文字內容。")
             return None
    elif llm_response.error_message:
        print(f"[回呼] 檢查到的回應：包含錯誤 '{llm_response.error_message}'。不進行修改。")
        return None
    else:
        print("[回呼] 檢查到的回應：空的 LlmResponse。")
        return None # 無法修改

    # --- 修改範例 ---
    # 將 "joke" 替換為 "funny story"（不區分大小寫）
    search_term = "joke"
    replace_term = "funny story"
    if search_term in original_text.lower():
        print(f"[回呼] 找到 '{search_term}'。正在修改回應。")
        modified_text = original_text.replace(search_term, replace_term)
        modified_text = modified_text.replace(search_term.capitalize(), replace_term.capitalize()) # 處理大寫

        # 使用修改後的內容建立一個新的 LlmResponse
        # 深層複製 parts 以避免在有其他回呼存在時修改原始物件
        modified_parts = [copy.deepcopy(part) for part in llm_response.content.parts]
        modified_parts[0].text = modified_text # 更新複製部分中的文字

        new_response = LlmResponse(
             content=types.Content(role="model", parts=modified_parts),
             # 如有需要，複製其他相關欄位，例如 grounding_metadata
             grounding_metadata=llm_response.grounding_metadata
             )
        print(f"[回呼] 返回修改後的回應。")
        return new_response # 返回修改後的回應
    else:
        print(f"[回呼] 未找到 '{search_term}'。傳遞原始回應。")
        # 返回 None 以使用原始的 llm_response
        return None


# 建立 LlmAgent 並指派回呼
my_llm_agent = LlmAgent(
        name="AfterModelCallbackAgent",
        model=GEMINI_2_FLASH,
        instruction="您是一位有幫助的助理。",
        description="一個展示 after_model_callback 的 LLM 代理",
        after_model_callback=simple_after_model_modifier # 在此處指派函式
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
  session, runner = await setup_session_and_runner()

  content = types.Content(role='user', parts=[types.Part(text=query)])
  events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

  async for event in events:
      if event.is_final_response():
          final_response = event.content.parts[0].text
          print("代理回應：", final_response)

# 注意：在 Colab 中，您可以直接在頂層使用 'await'。
# 如果將此程式碼作為獨立的 Python 腳本執行，您需要使用 asyncio.run() 或管理事件迴圈。
await call_agent_async("""多次寫下「joke」這個詞""")
