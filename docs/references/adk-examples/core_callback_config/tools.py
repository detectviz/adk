import random

from google.adk.tools.tool_context import ToolContext


def roll_die(sides: int, tool_context: ToolContext) -> int:
  """擲一個骰子並回傳擲骰結果。

  Args:
    sides: 骰子擁有的整數面數。

  Returns:
    擲骰結果的整數。
  """
  result = random.randint(1, sides)
  if not 'rolls' in tool_context.state:
    tool_context.state['rolls'] = []

  tool_context.state['rolls'] = tool_context.state['rolls'] + [result]
  return result


def check_prime(nums: list[int]) -> str:
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
