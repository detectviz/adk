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

"""用於尋找新研究方向的 Academic_newresearch_agent"""

# 匯入必要的模組
from google.adk import Agent

from . import prompt

# 定義要使用的語言模型
MODEL = "gemini-2.5-pro"

# 定義學術新研究代理
# 這個代理的職責是根據開創性論文和相關近期論文，提出新的研究方向
academic_newresearch_agent = Agent(
    # 使用的語言模型
    model=MODEL,
    # 代理的名稱
    name="academic_newresearch_agent",
    # 代理的詳細指令
    instruction=prompt.ACADEMIC_NEWRESEARCH_PROMPT,
)
