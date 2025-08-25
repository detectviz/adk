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

from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.llm_agent import LlmAgent
# 匯入 SequentialAgent 來協調並行和合併步驟
from google.adk.agents.sequential_agent import SequentialAgent
# 使用 InMemoryRunner 進行本地測試/原型設計
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

# --- 設定 (Configuration) ---
APP_NAME = "parallel_research_app"
USER_ID = "research_user_01"
SESSION_ID = "parallel_research_session_with_merge"
GEMINI_MODEL = "gemini-2.0-flash"


# --8<-- [start:init]
# agent.py 的一部分 --> 請參考 https://google.github.io/adk-docs/get-started/quickstart/ 了解設定方法
# --- 1. 定義研究員子代理 (Define Researcher Sub-Agents) (以並行方式執行) ---

# 研究員 1：再生能源
researcher_agent_1 = LlmAgent(
    name="RenewableEnergyResearcher",
    model=GEMINI_MODEL,
    instruction="""您是一位專精於能源的 AI 研究助理。
研究「再生能源」的最新進展。
使用提供的 Google 搜尋工具。
簡潔地總結您的主要發現（1-2 句話）。
*僅*輸出摘要。
""",
    description="研究再生能源。",
    tools=[google_search],
    # 將結果儲存在狀態中，供合併代理使用
    output_key="renewable_energy_result"
)

# 研究員 2：電動車
researcher_agent_2 = LlmAgent(
    name="EVResearcher",
    model=GEMINI_MODEL,
    instruction="""您是一位專精於交通運輸的 AI 研究助理。
研究「電動車技術」的最新發展。
使用提供的 Google 搜尋工具。
簡潔地總結您的主要發現（1-2 句話）。
*僅*輸出摘要。
""",
    description="研究電動車技術。",
    tools=[google_search],
    # 將結果儲存在狀態中，供合併代理使用
    output_key="ev_technology_result"
)

# 研究員 3：碳捕獲
researcher_agent_3 = LlmAgent(
    name="CarbonCaptureResearcher",
    model=GEMINI_MODEL,
    instruction="""您是一位專精於氣候解決方案的 AI 研究助理。
研究「碳捕獲方法」的現狀。
使用提供的 Google 搜尋工具。
簡潔地總結您的主要發現（1-2 句話）。
*僅*輸出摘要。
""",
    description="研究碳捕獲方法。",
    tools=[google_search],
    # 將結果儲存在狀態中，供合併代理使用
    output_key="carbon_capture_result"
)

# --- 2. 建立 ParallelAgent (Create the ParallelAgent) (同時執行研究員) ---
# 此代理協調研究員的並行執行。
# 一旦所有研究員完成並將其結果儲存在狀態中，它就會完成。
parallel_research_agent = ParallelAgent(
    name="ParallelWebResearchAgent",
    sub_agents=[researcher_agent_1, researcher_agent_2, researcher_agent_3],
    description="並行執行多個研究代理以收集資訊。"
)

# --- 3. 定義合併代理 (Define the Merger Agent) (在並行代理之後執行) ---
# 此代理會取用由並行代理儲存在會話狀態中的結果，
# 並將它們合成為一個單一、結構化且附有來源說明的回應。
merger_agent = LlmAgent(
    name="SynthesisAgent",
    model=GEMINI_MODEL,  # 如果需要，也可以使用更強大的模型進行合成
    instruction="""您是一位 AI 助理，負責將研究發現結合成一份結構化報告。

您的主要任務是綜合以下研究摘要，並清楚地將發現歸因於其來源領域。請使用標題為每個主題組織您的回應。確保報告連貫且流暢地整合了關鍵要點。

**至關重要：您的整個回應必須*完全*基於以下「輸入摘要」中提供的資訊。請勿添加任何未出現在這些特定摘要中的外部知識、事實或細節。**

**輸入摘要：**

*   **再生能源：**
    {renewable_energy_result}

*   **電動車：**
    {ev_technology_result}

*   **碳捕獲：**
    {carbon_capture_result}

**輸出格式：**

## 近期永續技術進展摘要

### 再生能源發現
（基於 RenewableEnergyResearcher 的發現）
[僅根據上面提供的再生能源輸入摘要進行綜合和闡述。]

### 電動車發現
（基於 EVResearcher 的發現）
[僅根據上面提供的電動車輸入摘要進行綜合和闡述。]

### 碳捕獲發現
（基於 CarbonCaptureResearcher 的發現）
[僅根據上面提供的碳捕獲輸入摘要進行綜合和闡述。]

### 整體結論
[提供一個簡短（1-2 句話）的結論性陳述，*僅*連結上面呈現的發現。]

*僅*按照此格式輸出結構化報告。請勿在此結構之外包含介紹性或結論性片語，並嚴格遵守僅使用所提供輸入摘要內容的原則。
""",
    description="將來自並行代理的研究發現結合成一份結構化、引證的報告，並嚴格基於所提供的輸入。",
    # 合併不需要工具
    # 此處不需要 output_key，因為其直接回應是序列的最終輸出
)


# --- 4. 建立 SequentialAgent (Create the SequentialAgent) (協調整體流程) ---
# 這是將要執行的主要代理。它首先執行 ParallelAgent
# 以填入狀態，然後執行 MergerAgent 以產生最終輸出。
sequential_pipeline_agent = SequentialAgent(
    name="ResearchAndSynthesisPipeline",
    # 首先執行並行研究，然後合併
    sub_agents=[parallel_research_agent, merger_agent],
    description="協調並行研究並綜合結果。"
)

root_agent = sequential_pipeline_agent
# --8<-- [end:init]

# # --- 5. 執行代理 (Running the Agent) (使用 InMemoryRunner 進行本地測試) 這適用於筆記本和腳本檔案 ---

# # 使用 InMemoryRunner：非常適合快速原型設計和本地測試
# runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
# print(f"已為代理 '{root_agent.name}' 建立 InMemoryRunner。")

# # 我們仍然需要存取會話服務（捆綁在 InMemoryRunner 中）
# # 以建立執行的會話實例。
# session_service = runner.session_service
# session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
# print(f"已為直接執行建立會話 '{SESSION_ID}'。")


# async def call_sequential_pipeline(query: str, user_id: str, session_id: str):
#     """
#     輔助的非同步函式，用於呼叫循序代理流程。
#     印出並行代理的中繼結果和最終合併後的回應。
#     """
#     print(f"\n--- 正在為查詢執行研究與綜合流程：'{query}' ---")
#     # 初始查詢主要觸發流程；此範例中的研究主題已在代理中固定。
#     content = types.Content(role='user', parts=[types.Part(text=query)])
#     final_response_text = None
#     # 追蹤哪些研究員已回報
#     researcher_outputs = {}
#     researcher_names = {"RenewableEnergyResearcher", "EVResearcher", "CarbonCaptureResearcher"}
#     merger_agent_name = "SynthesisAgent" # 序列中最後一個代理的名稱

#     print("正在開始流程...")
#     try:
#         async for event in runner.run_async(
#             user_id=user_id, session_id=session_id, new_message=content
#         ):
#             author_name = event.author or "系統"
#             is_final = event.is_final_response()
#             print(f"  [事件] 來自：{author_name}，最終：{is_final}") # 基本事件日誌

#             # 檢查是否為其中一個研究員代理的最終回應
#             if is_final and author_name in researcher_names and event.content and event.content.parts:
#                 researcher_output = event.content.parts[0].text.strip()
#                 if author_name not in researcher_outputs: # 每個研究員僅印出一次
#                     print(f"    -> 來自 {author_name} 的中繼結果：{researcher_output}")
#                     researcher_outputs[author_name] = researcher_output

#             # 檢查是否為合併代理（序列中的最後一個代理）的最終回應
#             elif is_final and author_name == merger_agent_name and event.content and event.content.parts:
#                  final_response_text = event.content.parts[0].text.strip()
#                  print(f"\n<<< 最終綜合回應（來自 {author_name}）：\n{final_response_text}")
#                  # 因為這是序列中的最後一個代理，我們可以在其最終回應後中斷
#                  break

#             elif event.is_error():
#                  print(f"  -> 來自 {author_name} 的錯誤：{event.error_message}")

#         if final_response_text is None:
#              print("<<< 流程已完成，但未從 SynthesisAgent 產生預期的最終文本回應。")

#     except Exception as e:
#         print(f"\n❌ 代理執行期間發生錯誤：{e}")



# initial_trigger_query = "總結近期永續技術的進展。"

# # 在 Colab/Jupyter 中：
# await call_sequential_pipeline(initial_trigger_query, user_id=USER_ID, session_id=SESSION_ID)

# # 在獨立的 Python 腳本中或如果 await 不受支援/失敗：
# # import asyncio
# # asyncio.run(call_sequential_pipeline(initial_trigger_query, user_id=USER_ID, session_id=SESSION_ID))
