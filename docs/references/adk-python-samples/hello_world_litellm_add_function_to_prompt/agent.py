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
from google.adk.models.lite_llm import LiteLlm
from langchain_core.utils.function_calling import convert_to_openai_function


def roll_die(sides: int) -> int:
  """擲骰子並返回擲骰結果。

  Args:
    sides: 骰子的面數（整數）。

  Returns:
    擲骰結果的整數。
  """
  return random.randint(1, sides)


def check_prime(number: int) -> str:
  """檢查給定的數字是否為質數。

  Args:
    number: 要檢查的輸入數字。

  Returns:
    一個字串，指出該數字是否為質數。
  """
  if number <= 1:
    return f"{number} 不是質數。"
  is_prime = True
  for i in range(2, int(number**0.5) + 1):
    if number % i == 0:
      is_prime = False
      break
  if is_prime:
    return f"{number} 是質數。"
  else:
    return f"{number} 不是質數。"


root_agent = Agent(
    model=LiteLlm(
        model="vertex_ai/meta/llama-4-maverick-17b-128e-instruct-maas",
        # 如果模型未經函式訓練，而您希望啟用函式呼叫，
        # 您可以將函式新增至模型中，這些函式將在推論期間新增至提示中。
        functions=[
            convert_to_openai_function(roll_die),
            convert_to_openai_function(check_prime),
        ],
    ),
    name="data_processing_agent",
    description="""您是一位樂於助人的助理。""",
    instruction="""
      您是一位樂於助人的助理，可以選擇性地呼叫工具。
      如果呼叫工具，工具格式應為 json，且工具引數應從使用者輸入中解析。
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
