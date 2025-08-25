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
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

APP_NAME="weather_sentiment_agent"
USER_ID="user1234"
SESSION_ID="1234"
MODEL_ID="gemini-2.0-flash"

# 工具 1
def get_weather_report(city: str) -> dict:
    """擷取指定城市的目前天氣報告。

    Returns:
        dict: 一個包含天氣資訊的字典，其中 'status' 鍵為 'success' 或 'error'，如果成功，則 'report' 鍵包含天氣詳細資訊，如果發生錯誤，則包含 'error_message'。
    """
    if city.lower() == "london":
        return {"status": "success", "report": "倫敦目前的天氣是多雲，溫度為攝氏 18 度，有降雨機率。"}
    elif city.lower() == "paris":
        return {"status": "success", "report": "巴黎天氣晴朗，溫度為攝氏 25 度。"}
    else:
        return {"status": "error", "error_message": f"'{city}' 的天氣資訊不可用。"}

weather_tool = FunctionTool(func=get_weather_report)


# 工具 2
def analyze_sentiment(text: str) -> dict:
    """分析給定文字的情緒。

    Returns:
        dict: 一個包含 'sentiment'（'positive'、'negative' 或 'neutral'）和 'confidence' 分數的字典。
    """
    if "good" in text.lower() or "sunny" in text.lower() or "好" in text or "晴" in text:
        return {"sentiment": "positive", "confidence": 0.8}
    elif "rain" in text.lower() or "bad" in text.lower() or "雨" in text or "不好" in text:
        return {"sentiment": "negative", "confidence": 0.7}
    else:
        return {"sentiment": "neutral", "confidence": 0.6}

sentiment_tool = FunctionTool(func=analyze_sentiment)


# 代理
weather_sentiment_agent = Agent(
    model=MODEL_ID,
    name='weather_sentiment_agent',
    instruction="""您是一個提供天氣資訊並分析使用者回饋情緒的樂於助人的助理。
**如果使用者詢問特定城市的天氣，請使用 'get_weather_report' 工具擷取天氣詳細資訊。**
**如果 'get_weather_report' 工具返回 'success' 狀態，請向使用者提供天氣報告。**
**如果 'get_weather_report' 工具返回 'error' 狀態，請告知使用者指定城市的天氣資訊不可用，並詢問他們是否有其他想查詢的城市。**
**提供天氣報告後，如果使用者對天氣給出回饋（例如，「那很好」或「我不喜歡下雨」），請使用 'analyze_sentiment' 工具來了解他們的情緒。** 然後，簡要地確認他們的情緒。
如果需要，您可以循序處理這些任務。""",
    tools=[weather_tool, sentiment_tool]
)

# 會話和執行器
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=weather_sentiment_agent, app_name=APP_NAME, session_service=session_service)
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
await call_agent_async("倫敦的天氣如何？")
