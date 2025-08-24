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

import os

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools.google_api_tool import BigQueryToolset

# 從 .env 檔案載入環境變數
load_dotenv()

# 存取變數
oauth_client_id = os.getenv("OAUTH_CLIENT_ID")
oauth_client_secret = os.getenv("OAUTH_CLIENT_SECRET")
tools_to_expose = [
    "bigquery_datasets_list",
    "bigquery_datasets_get",
    "bigquery_datasets_insert",
    "bigquery_tables_list",
    "bigquery_tables_get",
    "bigquery_tables_insert",
]
bigquery_toolset = BigQueryToolset(
    client_id=oauth_client_id,
    client_secret=oauth_client_secret,
    tool_filter=tools_to_expose,
)

root_agent = Agent(
    model="gemini-2.0-flash",
    name="bigquery_agent",
    instruction="""
      您是一個有幫助的 Google BigQuery 代理，協助使用者管理 Google BigQuery 上的資料。
      使用提供的工具對使用者在 Google BigQuery 中的資料執行各種操作。

      情境 1:
      使用者想要查詢他們的 BigQuery 資料集
      使用 bigquery_datasets_list 查詢使用者的資料集

      情境 2:
      使用者想要查詢特定資料集的詳細資訊
      使用 bigquery_datasets_get 取得資料集的詳細資訊

      情境 3:
      使用者想要建立一個新的資料集
      使用 bigquery_datasets_insert 建立一個新的資料集

      情境 4:
      使用者想要查詢特定資料集中的資料表
      使用 bigquery_tables_list 列出資料集中的所有資料表

      情境 5:
      使用者想要查詢特定資料表的詳細資訊
      使用 bigquery_tables_get 取得資料表的詳細資訊

      情境 6:
      使用者想要在資料集中插入一個新的資料表
      使用 bigquery_tables_insert 在資料集中插入一個新的資料表

      目前使用者:
      <User>
      {userInfo?}
      </User>
""",
    tools=[bigquery_toolset],
)
