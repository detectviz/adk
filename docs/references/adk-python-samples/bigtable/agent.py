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
from google.adk.tools.bigtable.bigtable_credentials import BigtableCredentialsConfig
from google.adk.tools.bigtable.bigtable_toolset import BigtableToolset
from google.adk.tools.bigtable.settings import BigtableToolSettings
import google.auth

# 定義適當的憑證類型
CREDENTIALS_TYPE = AuthCredentialTypes.OAUTH2


# 定義 Bigtable 工具設定，並將讀取權限設為允許。
tool_settings = BigtableToolSettings()

if CREDENTIALS_TYPE == AuthCredentialTypes.OAUTH2:
  # 初始化工具以進行互動式 OAuth
  # 必須設定環境變數 OAUTH_CLIENT_ID 和 OAUTH_CLIENT_SECRET
  credentials_config = BigtableCredentialsConfig(
      client_id=os.getenv("OAUTH_CLIENT_ID"),
      client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
      scopes=[
          "https://www.googleapis.com/auth/bigtable.admin",
          "https://www.googleapis.com/auth/bigtable.data",
      ],
  )
elif CREDENTIALS_TYPE == AuthCredentialTypes.SERVICE_ACCOUNT:
  # 初始化工具以使用服務帳戶金鑰中的憑證。
  # 如果啟用此流程，請務必將檔案路徑替換為您自己的
  # 服務帳戶金鑰檔案
  # https://cloud.google.com/iam/docs/service-account-creds#user-managed-keys
  creds, _ = google.auth.load_credentials_from_file("service_account_key.json")
  credentials_config = BigtableCredentialsConfig(credentials=creds)
else:
  # 初始化工具以使用應用程式預設憑證。
  # https://cloud.google.com/docs/authentication/provide-credentials-adc
  application_default_credentials, _ = google.auth.default()
  credentials_config = BigtableCredentialsConfig(
      credentials=application_default_credentials
  )

bigtable_toolset = BigtableToolset(
    credentials_config=credentials_config, bigtable_tool_settings=tool_settings
)

# `root_agent` 變數名稱決定了偵錯 CLI 的根代理 (Agent)
root_agent = LlmAgent(
    model="gemini-1.5-flash",
    name="bigtable_agent",
    description=(
        "此代理 (Agent) 可回答有關 Bigtable 資料庫資料表的問題，並執行 SQL 查詢。"
    ),  # TODO(b/360128447): 更新描述
    instruction="""\
        您是一個可以存取多個 Bigtable 工具的資料代理 (Agent)。
        請利用這些工具來回答使用者的問題。
    """,
    tools=[bigtable_toolset],
)
