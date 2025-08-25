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

"""模式發現工作流程的 Pydantic 模型。"""

from pydantic import BaseModel, Field
from typing import List, Optional

class Company(BaseModel):
    """由代理找到的單一公司的結構。"""
    company_name: str = Field(description="公司名稱。")
    country_of_origin: str = Field(description="公司總部所在的國家。")
    investment_type: str = Field(description="投資的性質（例如，新辦公室、收購）。")
    investment_date: str = Field(description="投資日期（例如，2023-Q4）。")
    source_url: str = Field(description="來源文章或新聞稿的 URL。")
    business_description: str = Field(description="關於公司業務的簡短一句描述。")

class CompanyFinderOutput(BaseModel):
    """公司尋找代理的最終輸出結構。"""
    companies_found: List[Company] = Field(description="符合條件的公司列表。")

class ValidationResult(BaseModel):
    """單一公司的驗證結果結構。"""
    company_name: str = Field(description="公司名稱。")
    is_valid: bool = Field(description="如果公司符合所有驗證標準，則為 True。")
    reasoning: str = Field(description="驗證決策的簡要說明。")
    corrected_country_of_origin: Optional[str] = Field(
        default=None,
        description="更正後的來源國，如果原始資料有誤。"
    )

class SignalSearcherOutput(BaseModel):
    """信號搜尋代理的輸出結構。"""
    summary: str = Field(description="找到的投資前信號的摘要。")
    sources: List[str] = Field(description="支持調查結果的來源 URL 列表。")
