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

from google.adk.agents.llm_agent import Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset

root_agent = Agent(
    model="gemini-2.0-flash",
    name="root_agent",
    instruction="您是一位樂於助人的助理",
    # 將工具箱工具新增至 ADK 代理
    tools=[
        ToolboxToolset(
            server_url="http://127.0.0.1:5000", toolset_name="my-toolset"
        )
    ],
)
