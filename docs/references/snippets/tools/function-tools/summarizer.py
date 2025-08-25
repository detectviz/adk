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

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

APP_NAME="summary_agent"
USER_ID="user1234"
SESSION_ID="1234"

summary_agent = Agent(
    model="gemini-2.0-flash",
    name="summary_agent",
    instruction="""您是一位專業的摘要員。請閱讀以下文字並提供簡潔的摘要。""",
    description="用於摘要文字的代理",
)

root_agent = Agent(
    model='gemini-2.0-flash',
    name='root_agent',
    instruction="""您是一位樂於助人的助理。當使用者提供一段文字時，請使用 'summarize' 工具產生摘要。請務必將使用者的訊息完全照原樣轉發給 'summarize' 工具，不要自行修改或摘要。將工具的回應呈現給使用者。""",
    tools=[AgentTool(agent=summary_agent)]
)

# 會話和執行器
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


# 代理互動
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("代理回應：", final_response)


long_text = """量子運算代表了一種根本不同的計算方法，
利用量子力學的奇特原理來處理資訊。與依賴於代表 0 或 1 的位元的傳統電腦不同，
量子電腦使用量子位元，它可以存在於疊加態中——實際上
同時是 0、1 或兩者的組合。此外，量子位元可以變得糾纏，
這意味著無論距離多遠，它們的命運都是交織在一起的，從而實現了複雜的關聯。這種平行性和
互聯性賦予了量子電腦解決特定類型的極其複雜問題的潛力——例如
藥物發現、材料科學、複雜系統優化和破解某些類型的密碼學——遠
比最強大的傳統超級電腦所能達到的速度快得多，儘管該技術仍主要處於開發階段。"""


# 注意：在 Colab 中，您可以直接在頂層使用 'await'。
# 如果將此程式碼作為獨立的 Python 腳本執行，您需要使用 asyncio.run() 或管理事件迴圈。
await call_agent_async(long_text)
