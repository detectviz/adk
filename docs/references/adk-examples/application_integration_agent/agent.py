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

"""使用應用程式整合工具集 (Application Integration toolset) 的範例代理 (Agent)"""

import os

from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.application_integration_tool import ApplicationIntegrationToolset

# 從 .env 檔案載入環境變數
load_dotenv()

connection_name = os.getenv("CONNECTION_NAME")
connection_project = os.getenv("CONNECTION_PROJECT")
connection_location = os.getenv("CONNECTION_LOCATION")


jira_toolset = ApplicationIntegrationToolset(
    project=connection_project,
    location=connection_location,
    connection=connection_name,
    entity_operations={"Issues": [], "Projects": []},
    tool_name_prefix="jira_issue_manager",
)

root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="Issue_Management_Agent",
    instruction="""
    您是一個協助管理 JIRA 實例中問題的代理 (Agent)。
    請根據工具的回應，提供準確的答覆。您可以根據使用者要求或情況，對回應進行適當的格式化。
    如果工具回應中出現錯誤，請理解錯誤並嘗試修復，然後再次執行工具。例如，如果缺少變數或參數，請嘗試在請求或使用者查詢中尋找，或設定預設值，然後再次執行工具，或檢查是否有其他工具可以提供詳細資訊。
    如果使用者請求中包含計數、最大值、最小值等數學運算，請呼叫工具以取得資料，執行數學運算，然後在回應中傳回結果。例如，若要取得最大值，請先擷取清單，然後再進行數學運算。
    """,
    tools=[jira_toolset],
)
