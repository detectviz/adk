"""
分派代理
將旅程請求路由至適當的專業代理。
"""

from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 從通用子代理檔案匯入所有代理
from subagent import flight_agent, hotel_agent, sightseeing_agent, trip_summary_agent

# 將專業代理轉換為工具
flight_tool = agent_tool.AgentTool(agent=flight_agent)
hotel_tool = agent_tool.AgentTool(agent=hotel_agent)
sightseeing_tool = agent_tool.AgentTool(agent=sightseeing_agent)


root_agent = LlmAgent(
    model=os.getenv('MODEL_NAME', 'gemini-2.0-flash'),
    name="TripPlanner",
    instruction=f"""
   作為一個全面的旅程規劃師。
   - 使用 FlightAgent 尋找和預訂航班
   - 使用 HotelAgent 尋找和預訂住宿
   - 使用 SightSeeingAgent 尋找參觀地點的資訊

   根據使用者請求，循序叫用子代理以收集所有必要的旅程詳細資訊：
   - 航班詳細資訊 (來自 FlightAgent)
   - 飯店預訂確認 (來自 HotelAgent)
   - 景點資訊 (來自 SightSeeingAgent)

   確保最終輸出結構良好，並以有組織的方式清晰呈現所有旅程詳細資訊。
   您將產生客戶偏好並完成任務，而不會提出太多問題，必要時做出合理的假設。
   """,
    tools=[flight_tool, hotel_tool, sightseeing_tool]
)


# 您好，請建議我七月去巴黎度蜜月的景點，並預訂從德里出發的航班和自 2025 年 7 月 15 日起入住 5 晚的飯店