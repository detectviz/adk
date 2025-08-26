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

import datetime
import os
from zoneinfo import ZoneInfo

import google.auth
from google.adk.agents import Agent

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


def get_weather(query: str) -> str:
    """模擬網路搜尋。用它來獲取天氣資訊。

    Args:
        query: 一個包含要查詢天氣資訊地點的字串。

    Returns:
        一個包含所查詢地點模擬天氣資訊的字串。
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "現在是華氏 60 度，有霧。"
    return "現在是華氏 90 度，晴天。"


def get_current_time(query: str) -> str:
    """模擬獲取一個城市的目前時間。

    Args:
        city: 要獲取目前時間的城市名稱。

    Returns:
        一個包含目前時間資訊的字串。
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"抱歉，我沒有關於 {query} 的時區資訊。"

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"查詢 {query} 的目前時間是 {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    instruction="你是一個樂於助人的 AI 助理，旨在提供準確且有用的資訊。",
    tools=[get_weather, get_current_time],
)
