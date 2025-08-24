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

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.genai import types


# --- 擲骰子子代理 ---
def roll_die(sides: int) -> int:
  """擲一個骰子並傳回擲出的結果。"""
  return random.randint(1, sides)


roll_agent = LlmAgent(
    name="roll_agent",
    description="處理不同大小的骰子擲骰。",
    model="gemini-2.0-flash",
    instruction="""
      您負責根據使用者的要求擲骰子。
      當被要求擲骰子時，您必須使用骰子面數作為整數呼叫 roll_die 工具。
    """,
    tools=[roll_die],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # 避免關於擲骰子的誤報。
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)


def check_prime(nums: list[int]) -> str:
  """檢查給定的數字清單是否為質數。"""
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


prime_agent = LlmAgent(
    name="prime_agent",
    description="處理檢查數字是否為質數。",
    model="gemini-2.0-flash",
    instruction="""
      您負責檢查數字是否為質數。
      當被要求檢查質數時，您必須使用整數清單呼叫 check_prime 工具。
      切勿嘗試手動確定質數。
      將質數結果傳回給根代理。
    """,
    tools=[check_prime],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # 避免關於擲骰子的誤報。
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)

root_agent = SequentialAgent(
    name="simple_sequential_agent",
    sub_agents=[roll_agent, prime_agent],
    # 代理將按照提供的順序執行：roll_agent -> prime_agent
)
