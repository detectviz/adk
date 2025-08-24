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

"""學術研究：研究建議、相關文獻查找、研究領域提案、網路知識存取。"""

# 匯入必要的模組
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .sub_agents.academic_newresearch import academic_newresearch_agent
from .sub_agents.academic_websearch import academic_websearch_agent

# 定義要使用的語言模型
MODEL = "gemini-2.5-pro"


# 定義學術協調員代理
# 這個代理是整個系統的主要協調者
academic_coordinator = LlmAgent(
    # 代理的名稱
    name="academic_coordinator",
    # 使用的語言模型
    model=MODEL,
    # 代理功能的簡要描述
    description=(
        "分析使用者提供的開創性論文，"
        "提供研究建議，尋找與開創性論文相關的當前論文，"
        "產生新研究方向的建議，以及存取網路資源以獲取知識"
    ),
    # 代理的詳細指令
    instruction=prompt.ACADEMIC_COORDINATOR_PROMPT,
    # 定義輸出的鍵
    output_key="seminal_paper",
    # 定義此代理可以使用的工具，這裡使用了兩個子代理作為工具
    tools=[
        AgentTool(agent=academic_websearch_agent),
        AgentTool(agent=academic_newresearch_agent),
    ],
)

# 將學術協調員代理設定為根代理
# 在這個應用中，academic_coordinator 是唯一且主要的代理
root_agent = academic_coordinator
