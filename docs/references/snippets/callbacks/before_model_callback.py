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
from google.adk.models import LlmResponse, LlmRequest
from google.adk.runners import Runner
from typing import Optional
from google.genai import types 
from google.adk.sessions import InMemorySessionService

GEMINI_2_FLASH="gemini-2.0-flash"

# --- 定義回呼函式 ---
def simple_before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """檢查/修改 LLM 請求或跳過呼叫。"""
    agent_name = callback_context.agent_name
    print(f"[回呼] 代理 {agent_name} 的模型呼叫前")

    # 檢查請求內容中的最後一則使用者訊息
    last_user_message = ""
    if llm_request.contents and llm_request.contents[-1].role == 'user':
         if llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text
    print(f"[回呼] 正在檢查最後一則使用者訊息：'{last_user_message}'")

    # --- 修改範例 ---
    # 在系統指令前加上前綴
    original_instruction = llm_request.config.system_instruction or types.Content(role="system", parts=[])
    prefix = "[由回呼修改] "
    # 確保 system_instruction 是 Content 且 parts 列表存在
    if not isinstance(original_instruction, types.Content):
         # 處理它可能是字串的情況（雖然設定預期是 Content）
         original_instruction = types.Content(role="system", parts=[types.Part(text=str(original_instruction))])
    if not original_instruction.parts:
        original_instruction.parts.append(types.Part(text="")) # 如果不存在，則新增一個空部分

    # 修改第一部分的文字
    modified_text = prefix + (original_instruction.parts[0].text or "")
    original_instruction.parts[0].text = modified_text
    llm_request.config.system_instruction = original_instruction
    print(f"[回呼] 已將系統指令修改為：'{modified_text}'")

    # --- 跳過範例 ---
    # 檢查最後一則使用者訊息是否包含 "BLOCK"
    if "BLOCK" in last_user_message.upper():
        print("[回呼] 找到 'BLOCK' 關鍵字。正在跳過 LLM 呼叫。")
        # 返回一個 LlmResponse 以跳過實際的 LLM 呼叫
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="LLM 呼叫已被 before_model_callback 封鎖。")],
            )
        )
    else:
        print("[回呼] 正在繼續進行 LLM 呼叫。")
        # 返回 None 以允許（已修改的）請求傳送至 LLM
        return None


# 建立 LlmAgent 並指派回呼
my_llm_agent = LlmAgent(
        name="ModelCallbackAgent",
        model=GEMINI_2_FLASH,
        instruction="您是一位有幫助的助理。", # 基本指令
        description="一個展示 before_model_callback 的 LLM 代理",
        before_model_callback=simple_before_model_modifier # 在此處指派函式
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
await call_agent_async("寫一個關於 BLOCK 的笑話")
