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


async def check_prime(nums: list[int]) -> str:
  """檢查給定的數字列表是否為質數。

  Args:
    nums: 要檢查的數字列表。

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
    name='check_prime_agent',
    description='可以檢查數字是否為質數的代理。',
    instruction="""
      您負責檢查數字是否為質數。
      檢查質數時，請使用整數列表呼叫 check_prime 工具。請務必傳入整數列表，絕不應傳入字串。
      您不應依賴先前的質數結果歷史紀錄。
    """,
    tools=[
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
