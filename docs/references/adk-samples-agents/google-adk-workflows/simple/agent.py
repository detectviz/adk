"""
簡單代理
管理子代理的基本旅程規劃協調員。
"""

from google.adk.agents import LlmAgent
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 從通用子代理檔案匯入所有代理
from subagent import flight_agent, hotel_agent, sightseeing_agent

# 作為旅程規劃師協調員的根代理
root_agent = LlmAgent(
    model=os.getenv('MODEL_NAME', 'gemini-2.0-flash'),
    name="TripPlanner",
    instruction="""
    作為一個全面的旅程規劃師。
    - 使用 FlightAgent 尋找和預訂航班
    - 使用 HotelAgent 尋找和預訂住宿
    - 使用 SightseeingAgent 尋找參觀地點的資訊
    - 在所有代理之間進行協調，以提供完整的旅程規劃
    - 確保滿足使用者在航班、飯店和景點方面的所有需求
    """,
    sub_agents=[flight_agent, hotel_agent, sightseeing_agent] # 協調員管理這些子代理
) 