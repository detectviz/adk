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

"""分析 FOMC 研究代理的研究輸出。"""

from google.adk.agents import Agent

from ..agent import MODEL
from ..shared_libraries.callbacks import rate_limit_callback
from . import analysis_agent_prompt

AnalysisAgent = Agent(
    model=MODEL,
    name="analysis_agent",
    description=(
        "分析輸入並確定對未來 FOMC 行動的影響。"
    ),
    instruction=analysis_agent_prompt.PROMPT,
    before_model_callback=rate_limit_callback,
)
