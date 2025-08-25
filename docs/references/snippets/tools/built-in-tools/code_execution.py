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
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.code_executors import BuiltInCodeExecutor
from google.genai import types

AGENT_NAME = "calculator_agent"
APP_NAME = "calculator"
USER_ID = "user1234"
SESSION_ID = "session_code_exec_async"
GEMINI_MODEL = "gemini-2.0-flash"

# 代理定義
code_agent = LlmAgent(
    name=AGENT_NAME,
    model=GEMINI_MODEL,
    code_executor=BuiltInCodeExecutor(),
    instruction="""您是一個計算器代理。
    當給定一個數學表達式時，編寫並執行 Python 程式碼來計算結果。
    僅以純文字形式返回最終的數值結果，不含 markdown 或程式碼區塊。
    """,
    description="執行 Python 程式碼以執行計算。",
)

# 會話和執行器
session_service = InMemorySessionService()
session = asyncio.run(session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
))
runner = Runner(agent=code_agent, app_name=APP_NAME, session_service=session_service)


# 代理互動 (非同步)
async def call_agent_async(query):
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(f"\n--- 正在執行查詢：{query} ---")
    final_response_text = "未擷取到最終文字回應。"
    try:
        # 使用 run_async
        async for event in runner.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=content
        ):
            print(f"事件 ID：{event.id}，作者：{event.author}")

            # --- 首先檢查特定部分 ---
            has_specific_part = False
            if event.content and event.content.parts:
                for part in event.content.parts:  # 迭代所有部分
                    if part.executable_code:
                        # 透過 .code 存取實際的程式碼字串
                        print(
                            f"  偵錯：代理產生的程式碼：\n```python\n{part.executable_code.code}\n```"
                        )
                        has_specific_part = True
                    elif part.code_execution_result:
                        # 正確存取 outcome 和 output
                        print(
                            f"  偵錯：程式碼執行結果：{part.code_execution_result.outcome} - 輸出：\n{part.code_execution_result.output}"
                        )
                        has_specific_part = True
                    # 也印出在任何事件中找到的任何文字部分以進行偵錯
                    elif part.text and not part.text.isspace():
                        print(f"  文字：'{part.text.strip()}'")
                        # 此處不要設定 has_specific_part=True，因為我們需要下面的最終回應邏輯

            # --- 在特定部分之後檢查最終回應 ---
            # 僅當它沒有我們剛處理的特定程式碼部分時才將其視為最終回應
            if not has_specific_part and event.is_final_response():
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                ):
                    final_response_text = event.content.parts[0].text.strip()
                    print(f"==> 最終代理回應：{final_response_text}")
                else:
                    print("==> 最終代理回應：[最終事件中沒有文字內容]")

    except Exception as e:
        print(f"代理執行期間發生錯誤：{e}")
    print("-" * 30)


# 執行範例的主非同步函式
async def main():
    await call_agent_async("計算 (5 + 7) * 3 的值")
    await call_agent_async("10 的階乘是多少？")


# 執行主非同步函式
try:
    asyncio.run(main())
except RuntimeError as e:
    # 處理在已執行的事件迴圈中執行 asyncio.run 時的特定錯誤（如 Jupyter/Colab）
    if "cannot be called from a running event loop" in str(e):
        print("\n正在現有事件迴圈中執行（如 Colab/Jupyter）。")
        print("請改在筆記本儲存格中執行 `await main()`。")
        # 如果在像筆記本這樣的互動式環境中，您可能需要執行：
        # await main()
    else:
        raise e  # 重新引發其他執行時錯誤
