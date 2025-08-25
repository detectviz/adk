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

#!/bin/bash

# 執行以下腳本將代理發布到您的 agentspace。

# 獲取腳本所在的目錄
SCRIPT_DIR=$(dirname "$0")

# 從位於腳本父目錄的 .env 檔案中載入環境變數
if [ -f "${SCRIPT_DIR}/../.env" ]; then
  export $(grep -v '^#' "${SCRIPT_DIR}/../.env" | xargs)
fi

export APP_ID="${AGENT_SPACE_ID}"
export LOCATION="${GOOGLE_CLOUD_LOCATION}"
export REASONING_ENGINE_ID="${REASONING_ENGINE_ID}"

export PROJECT_ID=$(gcloud config get-value project)
echo "使用專案 ID: ${PROJECT_ID}"

curl -X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "X-Goog-User-Project: ${PROJECT_ID}" \
-d "{
  \"displayName\": \"潛在客戶開發代理\",
  \"description\": \"此代理會發現投資模式並尋找新的潛在客戶。\",
  \"adk_agent_definition\": {
    \"tool_settings\": {
      \"tool_description\": \"此代理會發現投資模式並尋找新的潛在客戶。\"
    },
    \"provisioned_reasoning_engine\": {
      \"reasoning_engine\": \"projects/${PROJECT_ID}/locations/${LOCATION}/reasoningEngines/${REASONING_ENGINE_ID}\"
    }
  }
}" \
"https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents"
