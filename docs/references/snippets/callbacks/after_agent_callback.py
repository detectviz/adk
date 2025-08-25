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

# # --- 設定說明 ---
# # 1. 安裝 ADK 套件：
# !pip install google-adk
# # 如果使用 colab/jupyter 筆記本，請務必重新啟動核心

# # 2. 設定您的 Gemini API 金鑰：
# #    - 從 Google AI Studio 取得金鑰：https://aistudio.google.com/app/apikey
# #    - 將其設定為環境變數：
# import os
# os.environ["GOOGLE_API_KEY"] = "請在此處替換為您的實際金鑰" # <--- 請替換為您的實際金鑰
# # 或了解其他驗證方法（如 Vertex AI）：
# # https://google.github.io/adk-docs/agents/models/


# ADK 匯入
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import InMemoryRunner # 使用 InMemoryRunner
from google.genai import types # 用於 types.Content
from typing import Optional

# 定義模型 - 使用要求的特定模型名稱
GEMINI_2_FLASH="gemini-2.0-flash"

# --- 1. 定義回呼函式 ---
def modify_output_after_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    記錄代理的退出，並檢查會話狀態中的 'add_concluding_note'。
    如果為 True，則返回新的 Content 以*取代*代理的原始輸出。
    如果為 False 或不存在，則返回 None，允許使用代理的原始輸出。
    """
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    print(f"\n[回呼] 正在退出代理：{agent_name} (呼叫 ID: {invocation_id})")
    print(f"[回呼] 目前狀態：{current_state}")

    # 範例：檢查狀態以決定是否修改最終輸出
    if current_state.get("add_concluding_note", False):
        print(f"[回呼] 狀態條件 'add_concluding_note=True' 已滿足：正在取代代理 {agent_name} 的輸出。")
        # 返回 Content 以*取代*代理自己的輸出
        return types.Content(
            parts=[types.Part(text=f"由 after_agent_callback 新增的結論性說明，取代原始輸出。")],
            role="model" # 將模型角色指派給覆寫的回應
        )
    else:
        print(f"[回呼] 未滿足狀態條件：正在使用代理 {agent_name} 的原始輸出。")
        # 返回 None - 將使用在此回呼之前產生的代理輸出。
        return None

# --- 2. 設定帶有回呼的代理 ---
llm_agent_with_after_cb = LlmAgent(
    name="MySimpleAgentWithAfter",
    model=GEMINI_2_FLASH,
    instruction="您是一個簡單的代理。只需說「處理完成！」",
    description="一個展示 after_agent_callback 用於輸出修改的 LLM 代理",
    after_agent_callback=modify_output_after_agent # 在此處指派回呼
)

# --- 3. 使用 InMemoryRunner 設定執行器和會話 ---
async def main():
    app_name = "after_agent_demo"
    user_id = "test_user_after"
    session_id_normal = "session_run_normally"
    session_id_modify = "session_modify_output"

    # 使用 InMemoryRunner - 它包含 InMemorySessionService
    runner = InMemoryRunner(agent=llm_agent_with_after_cb, app_name=app_name)
    # 取得捆綁的會話服務以建立會話
    session_service = runner.session_service

    # 建立會話 1：代理輸出將按原樣使用（預設為空狀態）
    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id_normal
        # 無初始狀態表示在回呼檢查中 'add_concluding_note' 將為 False
    )
    # print(f"已使用預設狀態建立會話 '{session_id_normal}'。")

    # 建立會話 2：代理輸出將被回呼取代
    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id_modify,
        state={"add_concluding_note": True} # 在此處設定狀態旗標
    )
    # print(f"已使用狀態 {{'add_concluding_note': True}} 建立會話 '{session_id_modify}'。")


    # --- 情境 1：執行時回呼允許代理的原始輸出 ---
    print("\n" + "="*20 + f" 情境 1：在會話 '{session_id_normal}' 上執行代理（應使用原始輸出） " + "="*20)
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id_normal,
        new_message=types.Content(role="user", parts=[types.Part(text="請處理這個。")])
    ):
        # 印出最終輸出（來自 LLM 或回呼覆寫）
        if event.is_final_response() and event.content:
            print(f"最終輸出：[{event.author}] {event.content.parts[0].text.strip()}")
        elif event.is_error():
             print(f"錯誤事件：{event.error_details}")

    # --- 情境 2：執行時回呼取代代理的輸出 ---
    print("\n" + "="*20 + f" 情境 2：在會話 '{session_id_modify}' 上執行代理（應取代輸出） " + "="*20)
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id_modify,
        new_message=types.Content(role="user", parts=[types.Part(text="請處理這個並新增說明。")])
    ):
         # 印出最終輸出（來自 LLM 或回呼覆寫）
         if event.is_final_response() and event.content:
            print(f"最終輸出：[{event.author}] {event.content.parts[0].text.strip()}")
         elif event.is_error():
             print(f"錯誤事件：{event.error_details}")

# --- 4. 執行 ---
# 在 Python 腳本中：
# import asyncio
# if __name__ == "__main__":
#     # 如果不使用 Vertex AI 驗證，請確保設定 GOOGLE_API_KEY 環境變數
#     # 或確保為 Vertex AI 設定應用程式預設憑證 (ADC)
#     asyncio.run(main())

# 在 Jupyter 筆記本或類似環境中：
await main()
