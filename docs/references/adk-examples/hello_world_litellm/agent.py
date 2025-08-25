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

from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm


def roll_die(sides: int) -> int:
  """擲骰子並返回擲骰結果。

  Args:
    sides: 骰子的面數（整數）。

  Returns:
    擲骰結果的整數。
  """
  return random.randint(1, sides)


async def check_prime(nums: list[int]) -> str:
  """檢查給定的數字列表是否為質數。

  Args:
    nums: 要檢查的數字列表。

  Returns:
    一個字串，指出哪些數字是質數。
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
      "找不到質數。"
      if not primes
      else f"{', '.join(str(num) for num in primes)} 是質數。"
  )


root_agent = Agent(
    # model=LiteLlm(model="gemini/gemini-2.5-pro-exp-03-25"),
    # model=LiteLlm(model="vertex_ai/gemini-2.5-pro-exp-03-25"),
    # model=LiteLlm(model="vertex_ai/claude-3-5-haiku"),
    model=LiteLlm(model="openai/gpt-4o"),
    # model=LiteLlm(model="anthropic/claude-3-sonnet-20240229"),
    name="data_processing_agent",
    description=(
        "一個可以擲八面骰並檢查質數的 hello world 代理 (agent)。"
    ),
    instruction="""
      您會擲骰子并回答有關擲骰結果的問題。
      您可以擲不同大小的骰子。
      您可以透過並行呼叫函式（在一個請求和一個回合中）來並行使用多個工具。
      可以討論以前的擲骰角色，並對擲骰結果發表評論。
      當您被要求擲骰子時，您必須使用面數呼叫 roll_die 工具。請務必傳入一個整數。不要傳入字串。
      您不應該自己擲骰子。
      檢查質數時，請使用整數列表呼叫 check_prime 工具。請務必傳入一個整數列表。您不應該傳入字串。
      在呼叫工具之前，您不應該檢查質數。
      當您被要求擲骰子並檢查質數時，您應該始終進行以下兩個函式呼叫：
      1. 您應該先呼叫 roll_die 工具來取得擲骰結果。在呼叫 check_prime 工具之前，請等待函式回應。
      2. 從 roll_die 工具取得函式回應後，您應該使用 roll_die 結果呼叫 check_prime 工具。
        2.1 如果使用者要求您根據先前的擲骰結果檢查質數，請確保將先前的擲骰結果包含在列表中。
      3. 當您回應時，您必須包含步驟 1 中的 roll_die 結果。
      在要求擲骰和檢查質數時，您應該始終執行前面的 3 個步驟。
      您不應依賴質數結果的先前歷史記錄。
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
