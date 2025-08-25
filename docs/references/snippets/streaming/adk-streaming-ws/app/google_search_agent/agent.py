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

from google.adk.agents import Agent
from google.adk.tools import google_search  # 匯入工具

root_agent = Agent(
   # 代理的唯一名稱。
   name="google_search_agent",
   # 代理將使用的大型語言模型（LLM）。
   model="gemini-2.0-flash-exp", # 如果此模型無效，請嘗試以下模型
   #model="gemini-2.0-flash-live-001",
   # 代理用途的簡短描述。
   description="使用 Google 搜尋來回答問題的代理。",
   # 設定代理行為的指令。
   instruction="使用 Google 搜尋工具回答問題。",
   # 新增 google_search 工具以使用 Google 搜尋進行基礎資訊查詢。
   tools=[google_search],
)
