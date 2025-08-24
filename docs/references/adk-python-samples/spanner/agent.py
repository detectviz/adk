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
from google.adk.tools.spanner.settings import Capabilities
from google.adk.tools.spanner.settings import SpannerToolSettings
from google.adk.tools.spanner.spanner_credentials import SpannerCredentialsConfig
from google.adk.tools.spanner.spanner_toolset import SpannerToolset
import google.auth

# 定義適當的憑證類型
CREDENTIALS_TYPE = AuthCredentialTypes.OAUTH2


# 定義 Spanner 工具設定，並將讀取功能設定為允許。
tool_settings = SpannerToolSettings(capabilities=[Capabilities.DATA_READ])

if CREDENTIALS_TYPE == AuthCredentialTypes.OAUTH2:
  # 初始化工具以進行互動式 OAuth
  # 必須設定環境變數 OAUTH_CLIENT_ID 和 OAUTH_CLIENT_SECRET
  credentials_config = SpannerCredentialsConfig(
      client_id=os.getenv("OAUTH_CLIENT_ID"),
      client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
      scopes=[
          "https://www.googleapis.com/auth/spanner.admin",
          "https://www.googleapis.com/auth/spanner.data",
      ],
  )
elif CREDENTIALS_TYPE == AuthCredentialTypes.SERVICE_ACCOUNT:
  # 初始化工具以使用服務帳戶金鑰中的憑證。
  # 如果啟用此流程，請務必將檔案路徑替換為您自己的
  # 服務帳戶金鑰檔案
  # https://cloud.google.com/iam/docs/service-account-creds#user-managed-keys
  creds, _ = google.auth.load_credentials_from_file("service_account_key.json")
  credentials_config = SpannerCredentialsConfig(credentials=creds)
else:
  # 初始化工具以使用應用程式預設憑證。
  # https://cloud.google.com/docs/authentication/provide-credentials-adc
  application_default_credentials, _ = google.auth.default()
  credentials_config = SpannerCredentialsConfig(
      credentials=application_default_credentials
  )

spanner_toolset = SpannerToolset(
    credentials_config=credentials_config, spanner_tool_settings=tool_settings
)

# 變數名稱 `root_agent` 決定了您的根代理程式是什麼，用於
# 偵錯 CLI
root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="spanner_agent",
    description=(
        "用於回答有關 Spanner 資料庫資料表的問題並執行 SQL 查詢的代理。"
    ),
    instruction="""\
        您是一個可以存取多個 Spanner 工具的資料代理。
        請利用這些工具來回答使用者的問題。
    """,
    tools=[spanner_toolset],
)
