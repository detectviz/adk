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
from google.adk.tools.tool_context import ToolContext

from . import execution_agent


def update_execution_plan(
    execution_agents: list[str], tool_context: ToolContext
) -> str:
  """更新要執行的代理程式的執行計畫。"""

  tool_context.state["execution_agents"] = execution_agents
  return "執行代理程式已更新。"


root_agent = Agent(
    model="gemini-2.5-flash",
    name="execution_manager_agent",
    instruction="""\
您是執行管理員代理，負責設定執行計畫並委派給 plan_execution_agent 進行實際的計畫執行。

您只有以下工作代理程式：`code_agent`、`math_agent`。

您應該執行以下操作：

1. 分析使用者輸入並決定任何相關的工作代理程式；
2. 如果沒有相關的工作代理程式，您應該向使用者解釋沒有可用的相關代理程式，並要求他們提供其他內容；
2. 使用 `update_execution_plan` 工具以相關的工作代理程式更新執行計畫。
3. 將控制權轉移給 plan_execution_agent 進行實際的計畫執行。

呼叫 `update_execution_plan` 工具時，您應該傳遞與使用者輸入相關的工作代理程式清單。

注意：

* 如果您不清楚使用者的意圖，您應該先要求澄清；
* 只有在您清楚使用者的意圖後，才能繼續執行步驟 #2。
""",
    sub_agents=[
        execution_agent.plan_execution_agent,
    ],
    tools=[update_execution_plan],
)
