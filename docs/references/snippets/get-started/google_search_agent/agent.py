from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
   # 代理的唯一名稱。
   name="google_search_agent",
   # 代理將使用的大型語言模型（LLM）。
   model="gemini-2.0-flash",
   # 代理用途的簡短描述。
   description="使用 Google 搜尋來回答問題的代理。",
   # 設定代理行為的指令。
   instruction="您是一位專業的研究員。您總是堅持事實。",
   # 新增 google_search 工具以使用 Google 搜尋進行基礎資訊查詢。
   tools=[google_search]
)
