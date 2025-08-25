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

"""意圖提取代理 - 從使用者查詢中提取國家、產業、階段和意圖。"""

import os
from google.adk.agents import LlmAgent
from .schemas import IntentExtractionResult

# 載入環境變數
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .prompt import INTENT_EXTRACTOR_PROMPT


# 建立意圖提取代理
intent_extractor_agent = LlmAgent(
    name="intent_extractor_agent",
    model=os.getenv("LEAD_GEN_TRIAGE_MODEL", "gemini-1.5-flash"),
    instruction=INTENT_EXTRACTOR_PROMPT,
    output_schema=IntentExtractionResult,
    output_key="intent_extraction_result",
    description="從查詢中提取使用者意圖、國家、產業和對話階段",
)
