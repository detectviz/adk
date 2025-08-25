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

"""FOMC 研究範例代理。"""

import logging
import warnings

from google.adk.agents import Agent

from . import MODEL, root_agent_prompt
from .shared_libraries.callbacks import rate_limit_callback
from .sub_agents.analysis_agent import AnalysisAgent
from .sub_agents.research_agent import ResearchAgent
from .sub_agents.retrieve_meeting_data_agent import RetrieveMeetingDataAgent
from .tools.store_state import store_state_tool

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

logger = logging.getLogger(__name__)
logger.debug("正在使用模型：%s", MODEL)


root_agent = Agent(
    model=MODEL,
    name="root_agent",
    description=(
        "使用提供的工具和其他代理來產生關於"
        "最近一次 FOMC 會議的分析報告。"
    ),
    instruction=root_agent_prompt.PROMPT,
    tools=[store_state_tool],
    sub_agents=[
        RetrieveMeetingDataAgent,
        ResearchAgent,
        AnalysisAgent,
    ],
    before_model_callback=rate_limit_callback,
)
