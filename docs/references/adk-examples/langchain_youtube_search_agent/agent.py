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

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools.youtube.search import YouTubeSearchTool

# 實例化工具
langchain_yt_tool = YouTubeSearchTool()

# 將工具包裝在 ADK 的 LangchainTool 類別中
adk_yt_tool = LangchainTool(
    tool=langchain_yt_tool,
)

root_agent = LlmAgent(
    name="youtube_search_agent",
    model="gemini-2.0-flash",  # 請替換為實際的模型名稱
    instruction="""
    請使用者提供歌手姓名以及要搜尋的影片數量。
    """,
    description="幫助使用者在 YouTube 上搜尋影片。",
    tools=[adk_yt_tool],
    output_key="youtube_search_output",
)
