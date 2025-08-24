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

import random

from google.adk import Agent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.models.anthropic_llm import Claude
from google.adk.models.lite_llm import LiteLlm
from google.adk.planners.built_in_planner import BuiltInPlanner
from google.adk.planners.plan_re_act_planner import PlanReActPlanner
from google.adk.tools.tool_context import ToolContext
from google.genai import types


def roll_die(sides: int, tool_context: ToolContext) -> int:
  """擲一個骰子並傳回擲出的結果。

  Args:
    sides: 骰子擁有的整數面數。

  Returns:
    擲骰子結果的整數。
  """
  result = random.randint(1, sides)
  if 'rolls' not in tool_context.state:
    tool_context.state['rolls'] = []

  tool_context.state['rolls'] = tool_context.state['rolls'] + [result]
  return result


roll_agent_with_openai = LlmAgent(
    model=LiteLlm(model='openai/gpt-4o'),
    description='處理不同大小的擲骰。',
    name='roll_agent_with_openai',
    instruction="""
      您負責根據使用者的要求擲骰子。
      當被要求擲骰子時，您必須使用骰子面數作為整數呼叫 roll_die 工具。
    """,
    tools=[roll_die],
)

roll_agent_with_claude = LlmAgent(
    model=Claude(model='claude-3-7-sonnet@20250219'),
    description='處理不同大小的擲骰。',
    name='roll_agent_with_claude',
    instruction="""
      您負責根據使用者的要求擲骰子。
      當被要求擲骰子時，您必須使用骰子面數作為整數呼叫 roll_die 工具。
    """,
    tools=[roll_die],
)

roll_agent_with_litellm_claude = LlmAgent(
    model=LiteLlm(model='vertex_ai/claude-3-7-sonnet'),
    description='處理不同大小的擲骰。',
    name='roll_agent_with_litellm_claude',
    instruction="""
      您負責根據使用者的要求擲骰子。
      當被要求擲骰子時，您必須使用骰子面數作為整數呼叫 roll_die 工具。
    """,
    tools=[roll_die],
)

roll_agent_with_gemini = LlmAgent(
    model='gemini-2.0-flash',
    description='處理不同大小的擲骰。',
    name='roll_agent_with_gemini',
    instruction="""
      您負責根據使用者的要求擲骰子。
      當被要求擲骰子時，您必須使用骰子面數作為整數呼叫 roll_die 工具。
    """,
    tools=[roll_die],
)

root_agent = SequentialAgent(
    name='code_pipeline_agent',
    sub_agents=[
        roll_agent_with_openai,
        roll_agent_with_claude,
        roll_agent_with_litellm_claude,
        roll_agent_with_gemini,
    ],
)
