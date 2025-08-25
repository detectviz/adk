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

from google.adk.agents.llm_agent import Agent


def get_weather(city: str) -> dict:
  """擷取指定城市的目前天氣報告。

  Args:
      city (str): 要擷取天氣報告的城市名稱。

  Returns:
      dict: 狀態和結果或錯誤訊息。
  """
  if city.lower() == "new york":
    return {
        "status": "success",
        "report": (
            "紐約的天氣是晴天，溫度為攝氏 25 度"
            " (華氏 77 度)。"
        ),
    }
  else:
    return {
        "status": "error",
        "error_message": f"'{city}' 的天氣資訊不可用。",
    }


def get_current_time(city: str) -> dict:
  """傳回指定城市的目前時間。

  Args:
      city (str): 要擷取目前時間的城市名稱。

  Returns:
      dict: 狀態和結果或錯誤訊息。
  """
  import datetime
  from zoneinfo import ZoneInfo

  if city.lower() == "new york":
    tz_identifier = "America/New_York"
  else:
    return {
        "status": "error",
        "error_message": (
            f"抱歉，我沒有 {city} 的時區資訊。"
        ),
    }

  tz = ZoneInfo(tz_identifier)
  now = datetime.datetime.now(tz)
  report = (
      f'{city} 的目前時間是 {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
  )
  return {"status": "success", "report": report}


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "用於回答有關城市時間和天氣問題的代理。"
    ),
    instruction=(
        "我可以回答您有關城市時間和天氣的問題。"
    ),
    tools=[get_weather, get_current_time],
)
