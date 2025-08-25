# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import os
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.genai import types
# 變更 1：匯入 InMemoryRunner 而非 Runner/InMemorySessionService
from google.adk.runners import InMemoryRunner
from typing import Optional # 用於類型提示

# --- 常數 (Constants) ---
APP_NAME = "code_pipeline_app"
USER_ID = "dev_user_01"
SESSION_ID = "pipeline_session_02" # 如果需要，為每次執行使用唯一的會話 ID
GEMINI_MODEL = "gemini-2.0-flash"


# --8<-- [start:init]
# agent.py 的一部分 --> 請參考 https://google.github.io/adk-docs/get-started/quickstart/ 了解設定方法

# --- 1. 為每個流程階段定義子代理 (Define Sub-Agents for Each Pipeline Stage) ---

# 程式碼撰寫代理 (Code Writer Agent)
# 接收初始規格（來自使用者查詢）並撰寫程式碼。
code_writer_agent = LlmAgent(
    name="CodeWriterAgent",
    model=GEMINI_MODEL,
    # 變更 3：改進的指令
    instruction="""您是一位 Python 程式碼產生器。
*僅*根據使用者的要求，撰寫滿足需求的 Python 程式碼。
*僅*輸出完整的 Python 程式碼區塊，並用三個反引號 (```python ... ```) 括起來。
請勿在程式碼區塊前後添加任何其他文字。
""",
    description="根據規格撰寫初始 Python 程式碼。",
    output_key="generated_code" # 將輸出儲存在 state['generated_code'] 中
)

# 程式碼審查代理 (Code Reviewer Agent)
# 接收前一個代理產生的程式碼（從狀態中讀取）並提供回饋。
code_reviewer_agent = LlmAgent(
    name="CodeReviewerAgent",
    model=GEMINI_MODEL,
    # 變更 3：改進的指令，正確使用狀態鍵注入
    instruction="""您是一位專業的 Python 程式碼審查員。
    您的任務是就所提供的程式碼提供建設性的回饋。

    **待審查的程式碼：**
    ```python
    {generated_code}
    ```

**審查標準：**
1.  **正確性：** 程式碼是否如預期般運作？是否有邏輯錯誤？
2.  **可讀性：** 程式碼是否清晰易懂？是否遵循 PEP 8 風格指南？
3.  **效率：** 程式碼是否合理高效？是否有明顯的效能瓶頸？
4.  **邊界情況：** 程式碼是否能妥善處理潛在的邊界情況或無效輸入？
5.  **最佳實踐：** 程式碼是否遵循常見的 Python 最佳實踐？

**輸出：**
以簡潔的項目符號列表形式提供您的回饋。專注於最重要的改進點。
如果程式碼非常出色且無需更改，只需說明：「未發現主要問題。」
*僅*輸出審查意見或「未發現主要問題」的聲明。
""",
    description="審查程式碼並提供回饋。",
    output_key="review_comments", # 將輸出儲存在 state['review_comments'] 中
)


# 程式碼重構代理 (Code Refactorer Agent)
# 接收原始程式碼和審查意見（從狀態中讀取）並重構程式碼。
code_refactorer_agent = LlmAgent(
    name="CodeRefactorerAgent",
    model=GEMINI_MODEL,
    # 變更 3：改進的指令，正確使用狀態鍵注入
    instruction="""您是一位 Python 程式碼重構 AI。
您的目標是根據提供的審查意見改進給定的 Python 程式碼。

  **原始程式碼：**
  ```python
  {generated_code}
  ```

  **審查意見：**
  {review_comments}

**任務：**
仔細應用審查意見中的建議來重構原始程式碼。
如果審查意見指出「未發現主要問題」，則返回未經修改的原始程式碼。
確保最終的程式碼是完整、可運作的，並包含必要的匯入和文件字串。

**輸出：**
*僅*輸出最終重構後的 Python 程式碼區塊，並用三個反引號 (```python ... ```) 括起來。
請勿在程式碼區塊前後添加任何其他文字。
""",
    description="根據審查意見重構程式碼。",
    output_key="refactored_code", # 將輸出儲存在 state['refactored_code'] 中
)


# --- 2. 建立 SequentialAgent (Create the SequentialAgent) ---
# 此代理透過按順序執行子代理來協調流程。
code_pipeline_agent = SequentialAgent(
    name="CodePipelineAgent",
    sub_agents=[code_writer_agent, code_reviewer_agent, code_refactorer_agent],
    description="執行程式碼撰寫、審查和重構的序列。",
    # 代理將按照提供的順序執行：撰寫 -> 審查 -> 重構
)

# 為了與 ADK 工具相容，根代理必須命名為 `root_agent`
root_agent = code_pipeline_agent
# --8<-- [end:init]

# --- 3. 執行代理 (Running the Agent) (使用 InMemoryRunner 進行本地測試) ---

# # 使用 InMemoryRunner
# runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
# print(f"已為代理 '{root_agent.name}' 建立 InMemoryRunner。")


# # --- 互動函式 ---
# async def call_code_pipeline(query: str, user_id: str, session_id: str) -> Optional[str]:
#     """為給定的查詢執行程式碼流程，並印出中繼/最終步驟。"""
#     print(f"\n{'='*15} 正在為查詢執行程式碼流程：'{query}' {'='*15}")
#     print(f"嘗試使用會話 ID：{session_id}")
#     content = types.Content(role='user', parts=[types.Part(text=query)])
#     final_code = None
#     pipeline_step_outputs = {}

#     # --- 在 run_async 之前明確建立/檢查會話 ---
#     session_service = runner.session_service
#     session = session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
  
#     # --- 執行代理 ---
#     async for event in runner.run_async(
#         user_id=user_id, session_id=session_id, new_message=content
#     ):
#         author_name = event.author or "系統"
#         is_final = event.is_final_response()

#         if is_final and event.content and event.content.parts:
#             output_text = event.content.parts[0].text.strip()
#             pipeline_step_outputs[author_name] = output_text

#             print(f"\n--- 來自 {author_name} 的輸出 ---")
#             print(output_text)
#             print("-" * (len(author_name) + 18))

#             if author_name == code_refactorer_agent.name:
#                 final_code = output_text

#         elif event.error_message:
#               # 記錄錯誤，但如果可能，允許迴圈繼續
#               print(f"  -> 來自 {author_name} 的錯誤：{event.error_message}")

#     if final_code is None:
#         print("\n流程未產生最終的重構程式碼。")

#     # --- 最終狀態擷取 ---
#     print("\n--- 正在嘗試擷取最終會話狀態 ---")
#     final_session_object = None
#     try:
#         # 透過內部 session_service 使用正確的方法
#         final_session_object = runner.session_service.get_session(
#             app_name=APP_NAME, user_id=user_id, session_id=session_id
#         )
#     except Exception as e:
#          print(f"   -> 擷取最終會話物件時發生錯誤：{e}")

#     if final_session_object:
#         print(final_session_object.state) # 存取 .state 屬性
#     else:
#         print("找不到狀態（無法擷取最終會話物件）。")
#     print("=" * 50)

#     return final_code


# query = "撰寫一個使用遞迴計算數字階乘的 Python 函式。"
# # query = "建立一個簡單的 Python 類別 'Book'，具有屬性 title 和 author。"
# # query = "產生一個 Python 函式，接收一個數字列表並返回平方和。"
# # query = "撰寫一個 Python 腳本，讀取名為 'input.txt' 的文字檔案的第一行。"

# # 在 Colab/Jupyter 中：
# await call_code_pipeline(query, user_id=USER_ID, session_id=SESSION_ID)

# # 在獨立的 Python 腳本中或如果 await 不受支援/失敗：
# # asyncio.run(call_code_pipeline(query, user_id=USER_ID, session_id=SESSION_ID))
