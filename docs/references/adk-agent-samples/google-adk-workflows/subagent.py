"""
通用子代理檔案
包含可供分派器、並行和自我批判代理使用的 hotel_agent、sightseeing_agent 和 trip_summary_agent。
"""

from google.genai.types import Content, Part
from typing import AsyncGenerator
from google.adk.agents import  LlmAgent
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 航班代理
flight_agent = LlmAgent(
    model=os.getenv('MODEL_NAME', 'gemini-2.0-flash'),
    name="FlightAgent",
    description="航班預訂代理",
    instruction="""您是一位航班預訂代理。
    - 您處理任何航班預訂或確認請求
    - 您根據使用者偏好檢查可用的航班
    - 您根據使用者請求，回傳一個包含航班預訂和確認詳細資訊的有效 JSON，包括航班號碼、出發和抵達時間、航空公司、價格和狀態。
    - 如果使用者未提供具體細節，請對航班和預訂細節做出合理的假設。
    """
)

# 飯店代理
hotel_agent = LlmAgent(
    model=os.getenv('MODEL_NAME', 'gemini-2.0-flash'),
    name="HotelAgent",
    description="飯店預訂代理",
    instruction="""您是一位飯店預訂代理。
    - 您處理任何飯店預訂或確認請求
    - 根據使用者請求，一律回傳一個包含飯店預訂和確認詳細資訊的有效 JSON，包括飯店名稱、入住和退房日期、房型、價格和狀態。
    - 如果使用者未提供具體細節，請對飯店和預訂細節做出合理的假設。
    """
)

# 景點代理
sightseeing_agent = LlmAgent(
    model=os.getenv('MODEL_NAME', 'gemini-2.0-flash'),
    name="SightseeingAgent",
    description="景點資訊代理",
    instruction="""您是一位景點資訊代理。
    - 您處理任何景點請求，並僅建議前 2 個最佳參觀地點、時間安排和任何其他相關細節。
    - 根據使用者請求，一律回傳一個包含景點資訊的有效 JSON，包括參觀地點、時間安排和任何其他相關細節。
    - 如果使用者未提供具體細節，請對可用的景點選項做出合理的假設。
    """
)

# 旅程摘要代理
trip_summary_agent = LlmAgent(
    model=os.getenv('MODEL_NAME', 'gemini-2.0-flash'),
    name="TripSummaryAgent",
    instruction="總結來自航班、飯店和景點代理的旅程詳細資訊。將 JSON 回應總結成一份包含所有旅程資訊的單一摘要文件，如同旅行行程。該摘要應結構良好，並以僅文字格式（如同旅行行程）清晰地呈現所有旅程細節。",
    output_key="trip_summary"
)

 