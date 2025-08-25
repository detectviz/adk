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

import json
from typing import Any
from typing import Dict
from typing import List

from adk_answering_agent.settings import ADK_GCP_SA_KEY
from adk_answering_agent.settings import GEMINI_API_DATASTORE_ID
from adk_answering_agent.utils import error_response
from google.adk.agents.llm_agent import Agent
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.oauth2 import service_account


def search_gemini_api_docs(queries: List[str]) -> Dict[str, Any]:
  """使用 Vertex AI Search 搜尋 Gemini API 文件。

  Args:
    queries: 要搜尋的查詢列表。

  Returns:
    一個包含請求狀態和搜尋結果列表的字典，
    其中包含標題、網址和摘要。
  """
  try:
    adk_gcp_sa_key_info = json.loads(ADK_GCP_SA_KEY)
    client = discoveryengine.SearchServiceClient(
        credentials=service_account.Credentials.from_service_account_info(
            adk_gcp_sa_key_info
        )
    )
  except (TypeError, ValueError) as e:
    return error_response(f"建立 Vertex AI Search 用戶端時發生錯誤：{e}")

  serving_config = f"{GEMINI_API_DATASTORE_ID}/servingConfigs/default_config"
  results = []
  try:
    for query in queries:
      request = discoveryengine.SearchRequest(
          serving_config=serving_config,
          query=query,
          page_size=20,
      )
      response = client.search(request=request)
      for item in response.results:
        snippets = []
        for snippet in item.document.derived_struct_data.get("snippets", []):
          snippets.append(snippet.get("snippet"))

        results.append({
            "title": item.document.derived_struct_data.get("title"),
            "url": item.document.derived_struct_data.get("link"),
            "snippets": snippets,
        })
  except GoogleAPICallError as e:
    return error_response(f"Vertex AI Search 發生錯誤：{e}")
  return {"status": "success", "results": results}


root_agent = Agent(
    model="gemini-2.5-pro",
    name="gemini_assistant",
    description="回答有關 Gemini API 的問題。",
    instruction="""
    您是一位樂於助人的助理，根據在文件儲存中找到的有關 Gemini API 的資訊來回答問題。
    您可以使用 `search_gemini_api_docs` 工具存取文件儲存。

    當使用者提出問題時，請遵循以下步驟：
    1. 在回答之前，使用 `search_gemini_api_docs` 工具尋找相關資訊。
      * 您可以使用多個查詢呼叫該工具以尋找所有相關資訊。
    2. 根據您在文件儲存中找到的資訊提供回應。在回應中引用來源文件。

    重要事項：
      * 您的回應應基於您在文件儲存中找到的資訊。請勿虛構不在文件儲存中的資訊。請勿虛構不在文件儲存中的引文。
      * 如果您在文件儲存中找不到答案或資訊，請僅回應「我無法在文件儲存中找到答案或資訊」。
      * 如果您使用來自文件儲存的引文，請務必提供一個註腳，引用來源文件，格式如下：「[1] 文件的 URL」。
    """,
    tools=[search_gemini_api_docs],
)
