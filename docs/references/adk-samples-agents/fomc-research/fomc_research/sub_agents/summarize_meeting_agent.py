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

"""總結 FOMC 會議記錄的內容。"""

from google.adk.agents import Agent

from ..agent import MODEL
from ..shared_libraries.callbacks import rate_limit_callback
from ..tools.store_state import store_state_tool
from . import summarize_meeting_agent_prompt

SummarizeMeetingAgent = Agent(
    name="summarize_meeting_agent",
    model=MODEL,
    description=(
        "總結最新 FOMC 會議的內容和情緒。"
    ),
    instruction=summarize_meeting_agent_prompt.PROMPT,
    tools=[
        store_state_tool,
    ],
    before_model_callback=rate_limit_callback,
)
