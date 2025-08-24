import random

from google.adk.examples.example import Example
from google.adk.tools.example_tool import ExampleTool
from google.genai import types


def roll_die(sides: int) -> int:
  """擲一個骰子並傳回擲出的結果。"""
  return random.randint(1, sides)


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


example_tool = ExampleTool(
    examples=[
        Example(
            input=types.UserContent(
                parts=[types.Part(text="擲一個 6 面的骰子。")]
            ),
            output=[
                types.ModelContent(
                    parts=[types.Part(text="我為您擲出一個 4。")]
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
                        text="擲一個 10 面的骰子並檢查它是否為質數。"
                    )
                ]
            ),
            output=[
                types.ModelContent(
                    parts=[types.Part(text="我為您擲出一個 8。")]
                ),
                types.ModelContent(
                    parts=[types.Part(text="8 不是質數。")]
                ),
            ],
        ),
    ]
)
