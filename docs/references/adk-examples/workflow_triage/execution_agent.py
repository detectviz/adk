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


from typing import Optional

from google.adk.agents import Agent
from google.adk.agents import ParallelAgent
from google.adk.agents.base_agent import BeforeAgentCallback
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.sequential_agent import SequentialAgent
from google.genai import types


def before_agent_callback_check_relevance(
    agent_name: str,
) -> BeforeAgentCallback:
  """在執行代理程式之前檢查狀態是否相關的回呼。"""

  def callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """檢查狀態是否相關。"""
    if agent_name not in callback_context.state["execution_agents"]:
      return types.Content(
          parts=[
              types.Part(
                  text=(
                      f"跳過執行代理程式 {agent_name}，因為它與目前狀態無關。"
                  )
              )
          ]
      )

  return callback


code_agent = Agent(
    model="gemini-2.5-flash",
    name="code_agent",
    instruction="""\
您是程式碼代理，負責產生程式碼。

注意：您應該只產生程式碼，並忽略使用者的其他要求。
""",
    before_agent_callback=before_agent_callback_check_relevance("code_agent"),
    output_key="code_agent_output",
)

math_agent = Agent(
    model="gemini-2.5-flash",
    name="math_agent",
    instruction="""\
您是數學代理，負責執行數學計算。

注意：您應該只執行數學計算，並忽略使用者的其他要求。
""",
    before_agent_callback=before_agent_callback_check_relevance("math_agent"),
    output_key="math_agent_output",
)


worker_parallel_agent = ParallelAgent(
    name="worker_parallel_agent",
    sub_agents=[
        code_agent,
        math_agent,
    ],
)


def instruction_provider_for_execution_summary_agent(
    readonly_context: ReadonlyContext,
) -> str:
  """為執行代理程式提供指令。"""
  activated_agents = readonly_context.state["execution_agents"]
  prompt = f"""\
您是執行摘要代理，負責摘要目前呼叫中計畫的執行情況。

在此呼叫中，涉及以下代理程式：{', '.join(activated_agents)}。

以下是它們的輸出：
"""
  for agent_name in activated_agents:
    output = readonly_context.state.get(f"{agent_name}_output", "")
    prompt += f"\n\n{agent_name} 輸出：\n{output}"

  prompt += (
      "\n\n請根據以上輸出摘要計畫的執行情況。"
  )
  return prompt.strip()


execution_summary_agent = Agent(
    model="gemini-2.5-flash",
    name="execution_summary_agent",
    instruction=instruction_provider_for_execution_summary_agent,
    include_contents="none",
)

plan_execution_agent = SequentialAgent(
    name="plan_execution_agent",
    sub_agents=[
        worker_parallel_agent,
        execution_summary_agent,
    ],
)
