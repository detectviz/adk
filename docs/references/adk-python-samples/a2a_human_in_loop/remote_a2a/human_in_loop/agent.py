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

from typing import Any

from google.adk import Agent
from google.adk.tools.long_running_tool import LongRunningFunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types


def reimburse(purpose: str, amount: float) -> str:
  """將款項報銷給員工。"""
  return {
      'status': 'ok',
  }


def ask_for_approval(
    purpose: str, amount: float, tool_context: ToolContext
) -> dict[str, Any]:
  """請求報銷批准。"""
  return {
      'status': 'pending',
      'amount': amount,
      'ticketId': 'reimbursement-ticket-001',
  }


root_agent = Agent(
    model='gemini-2.0-flash',
    name='reimbursement_agent',
    instruction="""
      您是一個負責處理員工報銷流程的代理。
      如果金額小於 100 美元，您將自動批准報銷。

      如果金額大於 100 美元，您將向經理請求批准。
      如果經理批准，您將呼叫 reimburse() 將款項報銷給員工。
      如果經理拒絕，您將通知員工該拒絕。
""",
    tools=[reimburse, LongRunningFunctionTool(func=ask_for_approval)],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)
