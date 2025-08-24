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
  if not 'rolls' in tool_context.state:
    tool_context.state['rolls'] = []

  tool_context.state['rolls'] = tool_context.state['rolls'] + [result]
  return result


async def check_prime(nums: list[int]) -> str:
  """檢查給定的數字清單是否為質數。

  Args:
    nums: 要檢查的數字清單。

  Returns:
    一個字串，指出哪個數字是質數。
  """
  primes = set()
  for number in nums:
    number = int(number)
    if number <= 1:
      continue
    is_prime = True
    for i in range(2, int(number**0.5) + 1):
      if number % i == 0:
        is_prime = False
        break
    if is_prime:
      primes.add(number)
  return (
      '找不到質數。'
      if not primes
      else f"{', '.join(str(num) for num in primes)} 是質數。"
  )


root_agent = Agent(
    model='gemini-2.0-flash',
    name='data_processing_agent',
    description=(
        '可以擲一個 8 面骰子並檢查質數的 hello world 代理。'
    ),
    instruction="""
      您擲骰子並回答有關擲骰結果的問題。
      您可以擲不同大小的骰子。
      您可以透過平行呼叫函式（在一個請求和一個回合中）來平行使用多個工具。
      可以討論先前的擲骰角色，並對擲骰發表評論。
      當被要求擲骰子時，您必須使用面數呼叫 roll_die 工具。請務必傳入一個整數。請勿傳入字串。
      您絕不應該自己擲骰子。
      檢查質數時，請使用整數清單呼叫 check_prime 工具。請務必傳入一個整數清單。您絕不應該傳入字串。
      在呼叫工具之前，您不應該檢查質數。
      當被要求擲骰子並檢查質數時，您應該始終進行以下兩個函式呼叫：
      1. 您應該先呼叫 roll_die 工具來擲骰子。在呼叫 check_prime 工具之前，請等待函式回應。
      2. 從 roll_die 工具取得函式回應後，您應該使用 roll_die 結果呼叫 check_prime 工具。
        2.1 如果使用者要求您根據先前的擲骰結果檢查質數，請務必將先前的擲骰結果包含在清單中。
      3. 當您回應時，您必須包含步驟 1 中的 roll_die 結果。
      當要求擲骰子和檢查質數時，您應該始終執行前面的 3 個步驟。
      您不應該依賴先前的質數結果歷史記錄。
    """,
    tools=[
        roll_die,
        check_prime,
    ],
    # planner=BuiltInPlanner(
    #     thinking_config=types.ThinkingConfig(
    #         include_thoughts=True,
    #     ),
    # ),
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # 避免關於擲骰子的誤報。
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
