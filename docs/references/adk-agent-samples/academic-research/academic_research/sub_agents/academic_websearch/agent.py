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

"""使用搜尋工具尋找研究論文的 Academic_websearch_agent。"""

# 匯入必要的模組
from google.adk import Agent
from google.adk.tools import google_search

from . import prompt

# 定義要使用的語言模型
MODEL = "gemini-2.5-pro"


# 定義學術網路搜尋代理
# 這個代理的職責是使用 Google 搜尋工具來尋找引用開創性論文的近期學術論文
academic_websearch_agent = Agent(
    # 使用的語言模型
    model=MODEL,
    # 代理的名稱
    name="academic_websearch_agent",
    # 代理的詳細指令
    instruction=prompt.ACADEMIC_WEBSEARCH_PROMPT,
    # 定義輸出的鍵
    output_key="recent_citing_papers",
    # 定義此代理可以使用的工具，這裡使用了 Google 搜尋工具
    tools=[google_search],
)
