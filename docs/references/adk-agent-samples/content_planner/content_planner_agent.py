from google.adk.agents import Agent
from google.adk.tools import google_search


root_agent = Agent(
    name="content_planner_agent",
    model="gemini-2.5-flash",
    description="規劃代理 (Agent)，根據高階描述為一段內容建立詳細且合乎邏輯的大綱。",
    instruction="您是一位專業的內容規劃師。您的任務是根據高階描述為一段內容建立詳細且合乎邏輯的大綱。",
    tools=[google_search],
)
