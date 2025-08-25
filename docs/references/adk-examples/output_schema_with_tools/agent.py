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

"""示範 output_schema 與工具功能的範例代理。

此代理程式示範如何將結構化輸出 (output_schema) 與其他工具一併使用。
先前不允許此組合，但現在透過使用特殊 set_model_response 工具的因應措施來支援。
"""

from google.adk.agents import LlmAgent
from pydantic import BaseModel
from pydantic import Field
import requests


class PersonInfo(BaseModel):
  """關於個人的結構化資訊。"""

  name: str = Field(description="個人的全名")
  age: int = Field(description="個人的年齡")
  occupation: str = Field(description="個人的工作或職業")
  location: str = Field(description="他們居住的城市和國家")
  biography: str = Field(description="個人的簡短傳記")


def search_wikipedia(query: str) -> str:
  """在維基百科上搜尋有關主題的資訊。

  Args:
    query: 要在維基百科上查詢的搜尋查詢

  Returns:
    如果找到，則為維基百科文章的摘要，如果找不到，則為錯誤訊息
  """
  try:
    # 使用維基百科 API 搜尋文章
    search_url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        + query.replace(" ", "_")
    )
    response = requests.get(search_url, timeout=10)

    if response.status_code == 200:
      data = response.json()
      return (
          f"標題：{data.get('title', '不適用')}\n\n摘要："
          f" {data.get('extract', '沒有可用的摘要')}"
      )
    else:
      return (
          f"找不到 '{query}' 的維基百科文章。狀態碼："
          f" {response.status_code}"
      )

  except Exception as e:
    return f"搜尋維基百科時發生錯誤：{str(e)}"


def get_current_year() -> str:
  """取得目前年份。

  Returns:
    目前年份 (字串格式)
  """
  from datetime import datetime

  return str(datetime.now().year)


# 建立同時具有 output_schema 和工具的代理
root_agent = LlmAgent(
    name="person_info_agent",
    model="gemini-2.5-pro",
    instruction="""
您是一位收集名人資訊的得力助手。

當被問及某人時，您應該：
1. 使用 search_wikipedia 工具尋找有關他們的資訊
2. 如果需要計算年齡，請使用 get_current_year 工具
3. 使用 PersonInfo 格式將資訊編譯為結構化回應

務必使用 set_model_response 工具以必要的結構化格式提供您的最終答案。
    """.strip(),
    output_schema=PersonInfo,
    tools=[
        search_wikipedia,
        get_current_year,
    ],
)
