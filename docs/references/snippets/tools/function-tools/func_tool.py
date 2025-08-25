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
from google.genai import types

import yfinance as yf


APP_NAME = "stock_app"
USER_ID = "1234"
SESSION_ID = "session1234"

def get_stock_price(symbol: str):
    """
    擷取給定股票代號的目前股價。

    Args:
        symbol (str): 股票代號（例如 "AAPL", "GOOG"）。

    Returns:
        float: 目前股價，如果發生錯誤則為 None。
    """
    try:
        stock = yf.Ticker(symbol)
        historical_data = stock.history(period="1d")
        if not historical_data.empty:
            current_price = historical_data['Close'].iloc[-1]
            return current_price
        else:
            return None
    except Exception as e:
        print(f"擷取 {symbol} 的股價時發生錯誤：{e}")
        return None


stock_price_agent = Agent(
    model='gemini-2.0-flash',
    name='stock_agent',
    instruction= '您是一個擷取股價的代理。如果提供了股票代號，請擷取目前價格。如果只給了公司名稱，請先執行 Google 搜尋以找到正確的股票代號，然後再擷取股價。如果提供的股票代號無效或無法擷取資料，請告知使用者找不到股價。',
    description='此代理專門擷取即時股價。給定股票代號（例如 AAPL、GOOG、MSFT）或股票名稱，使用工具和可靠的資料來源提供最新的價格。',
    tools=[get_stock_price], # 您可以直接將 Python 函式新增到工具清單中；它們將被自動包裝為 FunctionTools。
)


# 會話和執行器
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=stock_price_agent, app_name=APP_NAME, session_service=session_service)
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


# 注意：在 Colab 中，您可以直接在頂層使用 'await'。
# 如果將此程式碼作為獨立的 Python 腳本執行，您需要使用 asyncio.run() 或管理事件迴圈。
await call_agent_async("GOOG 的股價")
