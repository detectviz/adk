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

from google.adk.agents.llm_agent import LlmAgent
from google.adk.auth.auth_credential import AuthCredentialTypes
from google.adk.tools.bigquery.bigquery_credentials import BigQueryCredentialsConfig
from google.adk.tools.bigquery.bigquery_toolset import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode
import google.auth

# 定義適當的憑證類型
CREDENTIALS_TYPE = AuthCredentialTypes.OAUTH2


# 將 BigQuery 工具設定的寫入模式設為允許。請注意，這僅是為了
# 展示 BigQuery 工具的全部功能。在生產環境中，您可能需要
# 將寫入模式更改為 BLOCKED（預設寫入模式，有效地使工具唯讀）
# 或 PROTECTED（僅允許在 BigQuery 會話的匿名資料集中寫入）。
tool_config = BigQueryToolConfig(write_mode=WriteMode.ALLOWED)

if CREDENTIALS_TYPE == AuthCredentialTypes.OAUTH2:
  # 初始化工具以進行互動式 OAuth
  # 必須設定環境變數 OAUTH_CLIENT_ID 和 OAUTH_CLIENT_SECRET
  credentials_config = BigQueryCredentialsConfig(
      client_id=os.getenv("OAUTH_CLIENT_ID"),
      client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
  )
elif CREDENTIALS_TYPE == AuthCredentialTypes.SERVICE_ACCOUNT:
  # 初始化工具以使用服務帳戶金鑰中的憑證。
  # 如果啟用此流程，請務必將檔案路徑替換為您自己的
  # 服務帳戶金鑰檔案
  # https://cloud.google.com/iam/docs/service-account-creds#user-managed-keys
  creds, _ = google.auth.load_credentials_from_file("service_account_key.json")
  credentials_config = BigQueryCredentialsConfig(credentials=creds)
else:
  # 初始化工具以使用應用程式預設憑證。
  # https://cloud.google.com/docs/authentication/provide-credentials-adc
  application_default_credentials, _ = google.auth.default()
  credentials_config = BigQueryCredentialsConfig(
      credentials=application_default_credentials
  )

bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config, bigquery_tool_config=tool_config
)

# `root_agent` 變數名稱決定了偵錯 CLI 的根代理 (Agent)
root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="bigquery_agent",
    description=(
        "此代理 (Agent) 可回答有關 BigQuery 資料和模型的問題，並執行 SQL 查詢。"
    ),
    instruction="""\
        您是一個可以存取多個 BigQuery 工具的資料科學代理 (Agent)。
        請利用這些工具來回答使用者的問題。
    """,
    tools=[bigquery_toolset],
)
