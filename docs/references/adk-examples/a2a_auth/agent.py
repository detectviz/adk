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


from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools.youtube.search import YouTubeSearchTool

# 實例化工具
langchain_yt_tool = YouTubeSearchTool()

# 將工具包裝在 ADK 的 LangchainTool 類別中
adk_yt_tool = LangchainTool(
    tool=langchain_yt_tool,
)

youtube_search_agent = Agent(
    name="youtube_search_agent",
    model="gemini-2.0-flash",  # 請替換為實際的模型名稱
    instruction="""
    請要求客戶提供歌手姓名以及要搜尋的影片數量。
    """,
    description="協助客戶在 YouTube 上搜尋影片。",
    tools=[adk_yt_tool],
    output_key="youtube_search_output",
)

bigquery_agent = RemoteA2aAgent(
    name="bigquery_agent",
    description="協助客戶管理 Notion 工作區。",
    agent_card=(
        f"http://localhost:8001/a2a/bigquery_agent{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)

root_agent = Agent(
    model="gemini-2.0-flash",
    name="root_agent",
    instruction="""
      您是一位樂於助人的助理，可以協助搜尋 YouTube 影片、查詢 BigQuery 資料集與資料表。
      您會將 YouTube 搜尋任務委派給 youtube_search_agent。
      您會將 BigQuery 任務委派給 bigquery_agent。
      在繼續之前，請務必釐清結果。
    """,
    global_instruction=(
        "您是一位樂於助人的助理，可以協助搜尋 YouTube 影片、查詢 BigQuery 資料集與資料表。"
    ),
    sub_agents=[youtube_search_agent, bigquery_agent],
)
