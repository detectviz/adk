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

"""意圖提取代理的 Pydantic 模型。"""

from pydantic import BaseModel, Field
from typing import Optional, Literal

class IntentExtractionResult(BaseModel):
    country: Optional[str] = Field(
        default=None,
        description="潛在客戶開發的目標國家。範例：'Thailand', 'Singapore', 'Malaysia'"
    )
    industry: Optional[str] = Field(
        default=None,
        description="目標產業領域。範例：'fintech', 'healthcare', 'SaaS', 'e-commerce'"
    )
    stage: Literal["pattern_discovery", "lead_generation", "follow_up", "chitchat"] = Field(
        description="目前的對話階段，用於決定下一步行動"
    )
    intent: Literal["find_leads", "find_patterns", "company_research", "general_chat"] = Field(
        description="使用者的主要意圖或目標"
    )
    confidence: float = Field(
        description="提取的信心分數 (0.0 到 1.0)"
    )
    reasoning: str = Field(
        description="提取決策的簡要說明"
    )
