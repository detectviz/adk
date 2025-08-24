"""
並行代理
為實現最高效率，協調旅遊代理的並行執行。
"""

from google.adk.agents import  ParallelAgent, SequentialAgent
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 從通用子代理檔案匯入所有代理
from subagent import flight_agent, hotel_agent, sightseeing_agent, trip_summary_agent

plan_parallel = ParallelAgent(
    name="ParallelTripPlanner",
    sub_agents=[flight_agent, hotel_agent],
    description="並行擷取航班和飯店資訊。每個子代理將以 JSON 回應回傳其各自的詳細資訊。"
)


# 主要並行工作流程
root_agent = SequentialAgent(
    name="ParallelWorkflow",
    description="協調旅遊規劃任務的並行執行",
    sub_agents=[
        sightseeing_agent,  
        plan_parallel,
        trip_summary_agent     
    ]
) 