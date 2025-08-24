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
from google.adk.agents.sequential_agent import SequentialAgent

sub_agent_1 = Agent(
    name='sub_agent_1',
    description='第一號子代理 (sub agent)。',
    model='gemini-2.0-flash-001',
    instruction='只需要說 1。',
)

sub_agent_2 = Agent(
    name='sub_agent_2',
    description='第二號子代理 (sub agent)。',
    model='gemini-2.0-flash-001',
    instruction='只需要說 2。',
)
sequential_agent = SequentialAgent(
    name='sequential_agent',
    sub_agents=[sub_agent_1, sub_agent_2],
)

root_agent = sequential_agent
