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

from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.plugins.base_plugin import BasePlugin


class CountInvocationPlugin(BasePlugin):
  """一個自訂外掛程式，用於計算代理和工具的呼叫次數。"""

  def __init__(self) -> None:
    """使用計數器初始化外掛程式。"""
    super().__init__(name="count_invocation")
    self.agent_count: int = 0
    self.tool_count: int = 0
    self.llm_request_count: int = 0

  async def before_agent_callback(
      self, *, agent: BaseAgent, callback_context: CallbackContext
  ) -> None:
    """計算代理執行次數。"""
    self.agent_count += 1
    print(f"[Plugin] Agent run count: {self.agent_count}")

  async def before_model_callback(
      self, *, callback_context: CallbackContext, llm_request: LlmRequest
  ) -> None:
    """計算 LLM 請求次數。"""
    self.llm_request_count += 1
    print(f"[Plugin] LLM request count: {self.llm_request_count}")
