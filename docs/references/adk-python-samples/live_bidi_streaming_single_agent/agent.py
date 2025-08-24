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
from google.adk.tools.tool_context import ToolContext
from google.genai import types


def roll_die(sides: int, tool_context: ToolContext) -> int:
  """擲一個骰子並回傳擲出的結果。

  參數：
    sides：骰子擁有的整數面數。

  回傳：
    擲骰子結果的整數。
  """
  result = random.randint(1, sides)
  if not 'rolls' in tool_context.state:
    tool_context.state['rolls'] = []

  tool_context.state['rolls'] = tool_context.state['rolls'] + [result]
  return result


async def check_prime(nums: list[int]) -> str:
  """檢查給定的數字清單是否為質數。

  參數：
    nums：要檢查的數字清單。

  回傳：
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
    # model='gemini-2.0-flash-live-preview-04-09',  # 適用於 Vertex 專案
    model='gemini-2.0-flash-live-001',  # 適用於 AI studio 金鑰
    name='hello_world_agent',
    description=(
        '可以擲一個 8 面骰子並檢查質數的 hello world 代理 (agent)。'
    ),
    instruction="""
      您擲骰子並回答有關擲骰子結果的問題。
      您可以擲不同大小的骰子。
      您可以透過並行呼叫函式（在一個請求和一個回合中）來並行使用多個工具。
      可以討論以前的骰子角色，並對擲骰子發表評論。
      當您被要求擲骰子時，您必須使用面數呼叫 roll_die 工具。請務必傳入一個整數。不要傳入字串。
      您絕不應該自己擲骰子。
      檢查質數時，請使用整數清單呼叫 check_prime 工具。請務必傳入一個整數清單。您絕不應該傳入字串。
      在呼叫工具之前，您不應該檢查質數。
      當您被要求擲骰子並檢查質數時，您應始終進行以下兩個函式呼叫：
      1. 您應首先呼叫 roll_die 工具以取得擲骰結果。在呼叫 check_prime 工具之前，請等待函式回應。
      2. 從 roll_die 工具取得函式回應後，您應使用 roll_die 結果呼叫 check_prime 工具。
        2.1 如果使用者要求您根據先前的擲骰結果檢查質數，請確保將先前的擲骰結果包含在清單中。
      3. 當您回應時，您必須包含步驟 1 中的 roll_die 結果。
      當要求擲骰子並檢查質數時，您應始終執行先前的 3 個步驟。
      您不應依賴先前關於質數結果的歷史記錄。
    """,
    tools=[
        roll_die,
        check_prime,
    ],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # 避免關於擲骰子的誤報。
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
