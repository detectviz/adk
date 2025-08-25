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

# --8<-- [start:init]
# agent.py 的一部分 --> 請參考 https://google.github.io/adk-docs/get-started/quickstart/ 了解設定方法

import asyncio
import os
from google.adk.agents import LoopAgent, LlmAgent, BaseAgent, SequentialAgent
from google.genai import types
from google.adk.runners import InMemoryRunner
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.tool_context import ToolContext
from typing import AsyncGenerator, Optional
from google.adk.events import Event, EventActions

# --- 常數 (Constants) ---
APP_NAME = "doc_writing_app_v3" # 新的應用程式名稱
USER_ID = "dev_user_01"
SESSION_ID_BASE = "loop_exit_tool_session" # 新的基礎會話 ID
GEMINI_MODEL = "gemini-2.0-flash"
STATE_INITIAL_TOPIC = "initial_topic"

# --- 狀態鍵 (State Keys) ---
STATE_CURRENT_DOC = "current_document"
STATE_CRITICISM = "criticism"
# 定義評論家（Critic）用來表示完成的確切片語
COMPLETION_PHRASE = "未發現主要問題。"

# --- 工具定義 (Tool Definition) ---
def exit_loop(tool_context: ToolContext):
  """僅當評論指出不需要進一步更改時才呼叫此函式，表示迭代過程應該結束。"""
  print(f"  [工具呼叫] exit_loop 由 {tool_context.agent_name} 觸發")
  tool_context.actions.escalate = True
  # 返回空字典，因為工具通常應返回可序列化為 JSON 的輸出
  return {}

# --- 代理定義 (Agent Definitions) ---

# 步驟 1：初始寫作代理（在開始時執行一次）
initial_writer_agent = LlmAgent(
    name="InitialWriterAgent",
    model=GEMINI_MODEL,
    include_contents='none',
    # 修改後的指令：要求一個稍微更發展的開頭
    instruction=f"""您是一位創意寫作助理，負責開始一個故事。
    撰寫一個短篇故事的*初稿*（目標 2-4 句話）。
    內容*僅*基於下面提供的主題。嘗試引入一個特定元素（如角色、場景細節或起始動作）使其引人入勝。
    主題：{{initial_topic}}

    *僅*輸出故事/文件文本。不要添加介紹或解釋。
""",
    description="根據主題撰寫初始文件草稿，旨在提供一些初步實質內容。",
    output_key=STATE_CURRENT_DOC
)

# 步驟 2a：評論代理（在優化迴圈內）
critic_agent_in_loop = LlmAgent(
    name="CriticAgent",
    model=GEMINI_MODEL,
    include_contents='none',
    # 修改後的指令：更細微的完成標準，尋找清晰的改進路徑。
    instruction=f"""您是一位建設性的評論 AI，正在審查一份簡短的文件草稿（通常 2-6 句話）。您的目標是提供平衡的回饋。

    **待審查文件：**
    ```
    {{current_document}}
    ```

    **任務：**
    根據初始主題（如果已知），審查文件的清晰度、吸引力和基本連貫性。

    如果您發現 1-2 個*清晰且可操作*的改進方法，可以更好地捕捉主題或增強讀者參與度（例如，「需要一個更強的開頭句」、「闡明角色的目標」）：
    簡潔地提供這些具體建議。*僅*輸出評論文本。

    否則，如果文件連貫，在其長度內充分闡述了主題，並且沒有明顯的錯誤或遺漏：
    *完全*回應片語「{COMPLETION_PHRASE}」，不要有其他內容。它不需要完美，只需在此階段功能上完整即可。如果核心內容健全，避免提出純粹主觀的風格偏好。

    不要添加解釋。僅輸出評論或確切的完成片語。
""",
    description="審查目前的草稿，如果需要明確的改進則提供評論，否則表示完成。",
    output_key=STATE_CRITICISM
)


# 步驟 2b：優化/退出代理（在優化迴圈內）
refiner_agent_in_loop = LlmAgent(
    name="RefinerAgent",
    model=GEMINI_MODEL,
    # 完全依賴於透過佔位符的狀態
    include_contents='none',
    instruction=f"""您是一位創意寫作助理，根據回饋優化文件或退出流程。
    **目前文件：**
    ```
    {{current_document}}
    ```
    **評論/建議：**
    {{criticism}}

    **任務：**
    分析「評論/建議」。
    如果評論*完全*是「{COMPLETION_PHRASE}」：
    您必須呼叫 'exit_loop' 函式。不要輸出任何文本。
    否則（評論包含可操作的回饋）：
    仔細應用建議以改進「目前文件」。*僅*輸出優化後的文件文本。

    不要添加解釋。要麼輸出優化後的文件，要麼呼叫 exit_loop 函式。
""",
    description="根據評論優化文件，如果評論表示完成，則呼叫 exit_loop。",
    tools=[exit_loop], # 提供 exit_loop 工具
    output_key=STATE_CURRENT_DOC # 用優化後的版本覆蓋 state['current_document']
)


# 步驟 2：優化迴圈代理
refinement_loop = LoopAgent(
    name="RefinementLoop",
    # 代理順序至關重要：先評論，然後優化/退出
    sub_agents=[
        critic_agent_in_loop,
        refiner_agent_in_loop,
    ],
    max_iterations=5 # 限制迴圈次數
)

# 步驟 3：整體循序流程
# 為了與 ADK 工具相容，根代理必須命名為 `root_agent`
root_agent = SequentialAgent(
    name="IterativeWritingPipeline",
    sub_agents=[
        initial_writer_agent, # 首先執行以建立初始文件
        refinement_loop       # 然後執行評論/優化迴圈
    ],
    description="撰寫一份初始文件，然後使用退出工具透過評論迭代地進行優化。"
)
# --8<-- [end:init]


# --- 在筆記本/腳本上執行代理 ---
# runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
# print(f"已為代理 '{root_agent.name}' 建立 InMemoryRunner。")


# # 互動函式（經過修改以顯示代理名稱和流程）
# async def call_pipeline_async(initial_topic: str, user_id: str, session_id: str):
#     print(f"\n--- 開始迭代寫作流程（退出工具），主題：'{initial_topic}' ---")
#     session_service = runner.session_service
#     initial_state = {STATE_INITIAL_TOPIC: initial_topic}
#     # 在 run_async 之前明確建立/檢查會話
#     session = session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
#     if not session:
#         print(f"  找不到會話 '{session_id}'，正在使用初始狀態建立...")
#         session = session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id, state=initial_state)
#         print(f"  已建立會話 '{session_id}'。")
#     else:
#         print(f"  會話 '{session_id}' 已存在。為新執行重設狀態。")
#         try:
#             # 如果重複使用會話 ID，則清除迭代狀態
#             stored_session = session_service.sessions[APP_NAME][user_id][session_id]
#             stored_session.state = {STATE_INITIAL_TOPIC: initial_topic} # 重設狀態
#         except KeyError: pass # 如果 get_session 成功，則不應發生

#     initial_message = types.Content(role='user', parts=[types.Part(text="開始寫作流程。")])
#     loop_iteration = 0
#     pipeline_finished_via_exit = False
#     last_known_doc = "未生成文件。" # 儲存最後的文件輸出

#     try:
#         async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=initial_message):
#             author_name = event.author or "系統"
#             is_final = event.is_final_response()
#             print(f"  [事件] 來自：{author_name}，最終：{is_final}")

#             # 每個主代理完成時顯示其輸出
#             if is_final and event.content and event.content.parts:
#                 output_text = event.content.parts[0].text.strip()

#                 if author_name == initial_writer_agent.name:
#                     print(f"\n[初稿] 由 {author_name} ({STATE_CURRENT_DOC}):")
#                     print(output_text)
#                     last_known_doc = output_text
#                 elif author_name == critic_agent_in_loop.name:
#                     loop_iteration += 1
#                     print(f"\n[迴圈迭代 {loop_iteration}] 由 {author_name} ({STATE_CRITICISM}) 的評論:")
#                     print(output_text)
#                     print(f"  (儲存到狀態鍵 '{STATE_CRITICISM}')")
#                 elif author_name == refiner_agent_in_loop.name:
#                     # 僅在實際優化時才印出（未呼叫 exit_loop）
#                     if not event.actions.escalate: # 檢查*此*事件的動作中是否未觸發退出
#                         print(f"[迴圈迭代 {loop_iteration}] 由 {author_name} ({STATE_CURRENT_DOC}) 的優化:")
#                         print(output_text)
#                         last_known_doc = output_text
#                         print(f"  (覆蓋狀態鍵 '{STATE_CURRENT_DOC}')")

#             # 檢查迴圈是否由 exit_loop 工具的提升（escalation）終止
#             # 注意：提升動作可能附加到*工具回應*事件，
#             # 或*後續模型回應*（如果發生摘要）。
#             # 我們透過查看 RefinerAgent 是否呼叫工具來檢測迴圈終止
#             # （由工具的 print 語句指示）或是否達到最大迭代次數。
#             if event.actions and event.actions.escalate:
#                  # 如果是內部提升傳播，我們不確定作者是誰
#                  print(f"\n--- 優化迴圈終止（檢測到提升） ---")
#                  pipeline_finished_via_exit = True
#                  # 一旦檢測到提升，就退出事件處理迴圈
#                  # 因為 LoopAgent 應該停止產生更多內部事件。
#                  break

#             elif event.error_message:
#                  print(f"  -> 來自 {author_name} 的錯誤：{event.error_message}")
#                  break # 發生錯誤時停止

#     except Exception as e: print(f"\n❌ 代理執行期間發生錯誤：{e}")

#     # 根據是否（大概）呼叫了 exit_loop 來確定最終狀態
#     if pipeline_finished_via_exit:
#         print(f"\n--- 流程完成（由 exit_loop 終止） ---")
#     else:
#         print(f"\n--- 流程完成（達到最大迭代次數 {refinement_loop.max_iterations} 或發生錯誤） ---")

#     print(f"最終文件輸出：\n{last_known_doc}")

#     # 最終狀態擷取
#     final_session_object = runner.session_service.get_session(app_name=APP_NAME,user_id=user_id, session_id=session_id)
#     print("\n--- 最終會話狀態 ---")
#     if final_session_object: print(final_session_object.state)
#     else: print("找不到狀態（無法擷取最終會話物件）。")
#     print("-" * 30)


# topic = "一個機器人產生了意想不到的情感"
# # topic = "與植物型外星物種溝通的挑戰"


# session_id = f"{SESSION_ID_BASE}_{hash(topic) % 1000}" # 唯一的會話 ID

# # 在 Colab/Jupyter 中：
# await call_pipeline_async(topic, user_id=USER_ID, session_id=session_id)

# # 在獨立的 Python 腳本中或如果 await 不受支援/失敗：
# # asyncio.run(call_pipeline_async(topic, user_id=USER_ID, session_id=session_id))
