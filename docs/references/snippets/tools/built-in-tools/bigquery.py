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

import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.bigquery import BigQueryCredentialsConfig
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode
from google.genai import types
import google.auth

# 為此範例代理定義常數
AGENT_NAME = "bigquery_agent"
APP_NAME = "bigquery_app"
USER_ID = "user1234"
SESSION_ID = "1234"
GEMINI_MODEL = "gemini-2.0-flash"

# 定義一個工具設定以阻止任何寫入操作
tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)

# 定義一個憑證設定 - 在此範例中，我們使用應用程式預設
# 憑證
# https://cloud.google.com/docs/authentication/provide-credentials-adc
application_default_credentials, _ = google.auth.default()
credentials_config = BigQueryCredentialsConfig(
    credentials=application_default_credentials
)

# 實例化一個 BigQuery 工具集
bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config, bigquery_tool_config=tool_config
)

# 代理定義
bigquery_agent = Agent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    description=(
        "回答有關 BigQuery 資料和模型的問題並執行"
        " SQL 查詢的代理。"
    ),
    instruction="""\
        您是一個可以存取多個 BigQuery 工具的資料科學代理。
        請利用這些工具來回答使用者的問題。
    """,
    tools=[bigquery_toolset],
)

# 會話和執行器
session_service = InMemorySessionService()
session = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID))
runner = Runner(agent=bigquery_agent, app_name=APP_NAME, session_service=session_service)

# 代理互動
def call_agent(query):
    """
    用查詢呼叫代理的輔助函式。
    """
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    print("使用者:", query)
    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("代理:", final_response)

call_agent("bigquery-public-data 專案中有沒有 ml 資料集？")
call_agent("告訴我更多關於 ml_datasets 的資訊。")
call_agent("它有哪些資料表？")
call_agent("告訴我更多關於 census_adult_income 資料表的資訊。")
call_agent("每個收入等級有多少列？")
