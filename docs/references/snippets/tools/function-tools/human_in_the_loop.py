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
from typing import Any
from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.tools import LongRunningFunctionTool
from google.adk.sessions import InMemorySessionService
from google.genai import types

# --8<-- [start:define_long_running_function]

# 1. 定義長時間執行的函式
def ask_for_approval(
    purpose: str, amount: float
) -> dict[str, Any]:
    """請求核准報銷。"""
    # 為核准建立一個工單
    # 向核准人發送帶有工單連結的通知
    return {'status': 'pending', 'approver': 'Sean Zhou', 'purpose' : purpose, 'amount': amount, 'ticket-id': 'approval-ticket-1'}

def reimburse(purpose: str, amount: float) -> str:
    """向員工報銷款項。"""
    # 將報銷請求傳送給支付供應商
    return {'status': 'ok'}

# 2. 使用 LongRunningFunctionTool 包裝函式
long_running_tool = LongRunningFunctionTool(func=ask_for_approval)

# --8<-- [end:define_long_running_function]

# 3. 在代理中使用該工具
file_processor_agent = Agent(
    # 使用與函式呼叫相容的模型
    model="gemini-2.0-flash",
    name='reimbursement_agent',
    instruction="""
      您是一個負責處理員工報銷流程的代理。如果金額低於 100 美元，您將自動核准報銷。

      如果金額大於 100 美元，您將向經理請求核准。如果經理核准，您將呼叫 reimburse() 向員工報銷款項。如果經理拒絕，您將通知員工該請求被拒絕。
    """,
    tools=[reimburse, long_running_tool]
)


APP_NAME = "human_in_the_loop"
USER_ID = "1234"
SESSION_ID = "session1234"

# 會話和執行器
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=file_processor_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner

# --8<-- [start: call_reimbursement_tool]

# 代理互動
async def call_agent_async(query):

    def get_long_running_function_call(event: Event) -> types.FunctionCall:
        # 從事件中取得長時間執行的函式呼叫
        if not event.long_running_tool_ids or not event.content or not event.content.parts:
            return
        for part in event.content.parts:
            if (
                part
                and part.function_call
                and event.long_running_tool_ids
                and part.function_call.id in event.long_running_tool_ids
            ):
                return part.function_call

    def get_function_response(event: Event, function_call_id: str) -> types.FunctionResponse:
        # 取得具有指定 ID 的函式呼叫的函式回應。
        if not event.content or not event.content.parts:
            return
        for part in event.content.parts:
            if (
                part
                and part.function_response
                and part.function_response.id == function_call_id
            ):
                return part.function_response

    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    print("\n正在執行代理...")
    events_async = runner.run_async(
        session_id=session.id, user_id=USER_ID, new_message=content
    )


    long_running_function_call, long_running_function_response, ticket_id = None, None, None
    async for event in events_async:
        # 使用輔助函式檢查特定的驗證請求事件
        if not long_running_function_call:
            long_running_function_call = get_long_running_function_call(event)
        else:
            long_running_function_response = get_function_response(event, long_running_function_call.id)
            if long_running_function_response:
                ticket_id = long_running_function_response.response['ticket-id']
        if event.content and event.content.parts:
            if text := ''.join(part.text or '' for part in event.content.parts):
                print(f'[{event.author}]: {text}')


    if long_running_function_response:
        # 透過 ticket_id 查詢對應工單的狀態
        # 傳回一個中繼/最終回應
        updated_response = long_running_function_response.model_copy(deep=True)
        updated_response.response = {'status': 'approved'}
        async for event in runner.run_async(
          session_id=session.id, user_id=USER_ID, new_message=types.Content(parts=[types.Part(function_response = updated_response)], role='user')
        ):
            if event.content and event.content.parts:
                if text := ''.join(part.text or '' for part in event.content.parts):
                    print(f'[{event.author}]: {text}')
          
# --8<-- [end:call_reimbursement_tool]          

# 注意：在 Colab 中，您可以直接在頂層使用 'await'。
# 如果將此程式碼作為獨立的 Python 腳本執行，您需要使用 asyncio.run() 或管理事件迴圈。
                   
# 不需要核准的報銷
# asyncio.run(call_agent_async("請報銷 50 美元的餐費"))
await call_agent_async("請報銷 50 美元的餐費") # 對於筆記本，請取消註解此行並註解上一行
# 需要核准的報銷
# asyncio.run(call_agent_async("請報銷 200 美元的餐費"))
await call_agent_async("請報銷 200 美元的餐費") # 對於筆記本，請取消註解此行並註解上一行
