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

"""潛在客戶開發工作流程的 Pydantic 模型。"""

from pydantic import BaseModel, Field
from typing import List

class Lead(BaseModel):
    """單一潛在客戶的結構。"""
    company_name: str = Field(description="公司名稱。")
    country_of_origin: str = Field(description="公司總部所在的國家。")
    business_description: str = Field(description="關於公司業務的簡短一句描述。")

class LeadFinderOutput(BaseModel):
    """潛在客戶尋找代理的最終輸出結構。"""
    potential_leads: List[Lead] = Field(description="符合條件的潛在客戶列表。")

class LeadSignalAnalyzerOutput(BaseModel):
    """潛在客戶信號分析代理的輸出結構。"""
    summary: str = Field(description="為潛在客戶找到的投資前信號的摘要。")
    sources: List[str] = Field(description="支持調查結果的來源 URL 列表。")
