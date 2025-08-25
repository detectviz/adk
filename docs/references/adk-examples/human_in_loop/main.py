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

import asyncio
import os
from typing import Any
from typing import Union

import agent
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.events.event import Event
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.tools.long_running_tool import LongRunningFunctionTool
from google.genai import types
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import export
from opentelemetry.sdk.trace import TracerProvider

load_dotenv(override=True)

APP_NAME = "human_in_the_loop"
USER_ID = "1234"
SESSION_ID = "session1234"

session_service = InMemorySessionService()


async def main():
  session = await session_service.create_session(
      app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
  )
  runner = Runner(
      agent=agent.root_agent,
      app_name=APP_NAME,
      session_service=session_service,
  )

  async def call_agent(query: str):
    content = types.Content(role="user", parts=[types.Part(text=query)])

    print(f'>>> 使用者查詢："{query}"')
    print("--- 正在執行代理 (agent) 的初始輪次 ---")

    events_async = runner.run_async(
        session_id=session.id, user_id=USER_ID, new_message=content
    )

    long_running_function_call: Union[types.FunctionCall, None] = None
    initial_tool_response: Union[types.FunctionResponse, None] = None
    ticket_id: Union[str, None] = None

    async for event in events_async:
      if event.content and event.content.parts:
        for i, part in enumerate(event.content.parts):
          if part.text:
            print(f"    部分 {i} [文字]: {part.text.strip()}")
          if part.function_call:
            print(
                f"    部分 {i} [函式呼叫]:"
                f" {part.function_call.name}({part.function_call.args}) ID:"
                f" {part.function_call.id}"
            )
            if not long_running_function_call and part.function_call.id in (
                event.long_running_tool_ids or []
            ):
              long_running_function_call = part.function_call
              print(
                  "      （擷取為 long_running_function_call，用於"
                  f" '{part.function_call.name}'）"
              )
          if part.function_response:
            print(
                f"    部分 {i} [函式回應]: 用於"
                f" '{part.function_response.name}', ID:"
                f" {part.function_response.id}, 回應:"
                f" {part.function_response.response}"
            )
            if (
                long_running_function_call
                and part.function_response.id == long_running_function_call.id
            ):
              initial_tool_response = part.function_response
              if initial_tool_response.response:
                ticket_id = initial_tool_response.response.get("ticketId")
              print(
                  "      （擷取為 initial_tool_response，用於"
                  f" '{part.function_response.name}', 工單 ID: {ticket_id}）"
              )

    print("--- 代理 (agent) 的初始輪次結束 ---\n")

    if (
        long_running_function_call
        and initial_tool_response
        and initial_tool_response.response.get("status") == "pending"
    ):
      print(f"--- 正在模擬工單的外部核准：{ticket_id} ---\n")

      updated_tool_output_data = {
          "status": "approved",
          "ticketId": ticket_id,
          "approver_feedback": "由經理於 " + str(
              asyncio.get_event_loop().time()
          ) + " 核准",
      }

      updated_function_response_part = types.Part(
          function_response=types.FunctionResponse(
              id=long_running_function_call.id,
              name=long_running_function_call.name,
              response=updated_tool_output_data,
          )
      )

      print(
          "--- 正在將更新的工具結果傳送給代理 (agent)，呼叫 ID"
          f" {long_running_function_call.id}: {updated_tool_output_data} ---"
      )
      print("--- 正在接收更新的工具結果後執行代理 (agent) 的輪次 ---")

      async for event in runner.run_async(
          session_id=session.id,
          user_id=USER_ID,
          new_message=types.Content(
              parts=[updated_function_response_part], role="user"
          ),
      ):
        if event.content and event.content.parts:
          for i, part in enumerate(event.content.parts):
            if part.text:
              print(f"    部分 {i} [文字]: {part.text.strip()}")
            if part.function_call:
              print(
                  f"    部分 {i} [函式呼叫]:"
                  f" {part.function_call.name}({part.function_call.args}) ID:"
                  f" {part.function_call.id}"
              )
            if part.function_response:
              print(
                  f"    部分 {i} [函式回應]: 用於"
                  f" '{part.function_response.name}', ID:"
                  f" {part.function_response.id}, 回應:"
                  f" {part.function_response.response}"
              )
      print("--- 在接收更新的工具結果後，代理 (agent) 的輪次結束 ---")

    elif long_running_function_call and not initial_tool_response:
      print(
          f"--- 長時間執行的函式 '{long_running_function_call.name}' 已被呼叫，"
          "但其初始回應未被擷取。 ---"
      )
    elif not long_running_function_call:
      print(
          "--- 在初始輪次中未偵測到長時間執行的函式呼叫。 ---"
      )

  await call_agent("請報銷 50 美元的餐費")
  print("=" * 70)
  await call_agent("請報銷 200 美元的會議差旅費")


if __name__ == "__main__":
  provider = TracerProvider()
  project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
  if not project_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set.")
  print("Tracing to project", project_id)
  processor = export.BatchSpanProcessor(
      CloudTraceSpanExporter(project_id=project_id)
  )
  provider.add_span_processor(processor)
  trace.set_tracer_provider(provider)

  asyncio.run(main())

  provider.force_flush()
  print("Done tracing to project", project_id)
