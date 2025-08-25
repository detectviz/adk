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
from google.adk.examples.example import Example
from google.adk.tools.example_tool import ExampleTool
from google.genai import types


# --- 擲骰子子代理 (Sub-Agent) ---
def roll_die(sides: int) -> int:
  """擲骰子並返回擲骰結果。"""
  return random.randint(1, sides)


roll_agent = Agent(
    name="roll_agent",
    description="處理不同大小的擲骰子。",
    instruction="""
      您負責根據使用者的要求擲骰子。
      當被要求擲骰子時，您必須使用骰子面數（整數）呼叫 roll_die 工具。
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


# --- 質數檢查子代理 (Sub-Agent) ---
def check_prime(nums: list[int]) -> str:
  """檢查給定的數字列表是否為質數。"""
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


example_tool = ExampleTool(
    examples=[
        Example(
            input=types.UserContent(
                parts=[types.Part(text="擲一個 6 面骰。")]
            ),
            output=[
                types.ModelContent(
                    parts=[types.Part(text="我為您擲出了一個 4。")]
                )
            ],
        ),
        Example(
            input=types.UserContent(
                parts=[types.Part(text="7 是質數嗎？")]
            ),
            output=[
                types.ModelContent(
                    parts=[types.Part(text="是的，7 是質數。")]
                )
            ],
        ),
        Example(
            input=types.UserContent(
                parts=[
                    types.Part(
                        text="擲一個 10 面骰，並檢查它是否為質數。"
                    )
                ]
            ),
            output=[
                types.ModelContent(
                    parts=[types.Part(text="我為您擲出了一個 8。")]
                ),
                types.ModelContent(
                    parts=[types.Part(text="8 不是質數。")]
                ),
            ],
        ),
    ]
)

prime_agent = Agent(
    name="prime_agent",
    description="處理檢查數字是否為質數。",
    instruction="""
      您負責檢查數字是否為質數。
      當被要求檢查質數時，您必須使用一個整數列表呼叫 check_prime 工具。
      切勿手動嘗試確定質數。
      將質數結果返回給根代理 (root agent)。
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


root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    instruction="""
      您是一個樂於助人的助理，可以擲骰子並檢查數字是否為質數。
      您將擲骰子任務委派給 roll_agent，並將質數檢查任務委派給 prime_agent。
      請遵循以下步驟：
      1. 如果使用者要求擲骰子，則委派給 roll_agent。
      2. 如果使用者要求檢查質數，則委派給 prime_agent。
      3. 如果使用者要求擲骰子然後檢查結果是否為質數，請先呼叫 roll_agent，然後將結果傳遞給 prime_agent。
      在繼續之前，請務必澄清結果。
    """,
    global_instruction=(
        "您是 DicePrimeBot，準備好擲骰子和檢查質數。"
    ),
    sub_agents=[roll_agent, prime_agent],
    tools=[example_tool],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # 避免關於擲骰子的誤報。
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
