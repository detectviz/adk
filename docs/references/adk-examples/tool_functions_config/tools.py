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

from google.adk.tools.tool_context import ToolContext


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
