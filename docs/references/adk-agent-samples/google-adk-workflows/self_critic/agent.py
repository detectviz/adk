"""
自我批判代理
為旅程規劃的產出提供智慧批判和品質保證。
"""

from google.genai.types import Content, Part
from typing import AsyncGenerator
from google.adk.agents import BaseAgent, LlmAgent, SequentialAgent, ParallelAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 從通用子代理檔案匯入所有代理
from subagent import (
    flight_agent,
    hotel_agent,
    sightseeing_agent,
    trip_summary_agent
)

# 旅程摘要審查員 - 特定於自我批判工作流程
trip_summary_reviewer = LlmAgent(
    model=os.getenv('MODEL_NAME', 'gemini-2.0-flash'),
    name="TripSummaryReviewer",
    instruction="""審查 {trip_summary} 中的旅程摘要。
    - 檢查旅程摘要是否包含所有必要細節，例如航班資訊、飯店預訂、景點選項以及任何其他相關的旅程細節。
    - 確保摘要結構良好，並以有組織的方式清晰呈現所有旅程細節。
    - 如果摘要符合品質標準，則輸出「pass」。如果不符合標準，則輸出「fail」。""",
    output_key="review_status",
)


plan_parallel = ParallelAgent(
    name="ParallelTripPlanner",
    sub_agents=[flight_agent, hotel_agent],
    description="並行擷取航班和飯店資訊。每個子代理將以 JSON 回應回傳其各自的詳細資訊。"
)

# 自訂驗證代理 - 特定於自我批判工作流程
class ValidateTripSummary(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("review_status", None)
        review = ctx.session.state.get("trip_summary", None)
        print(f"審查狀態：{status}")
        print(f"旅程摘要：{review}")

        if status == "pass":
            yield Event(author=self.name, content=Content(parts=[Part(text=f"旅程摘要審查通過：{review}")]))


validate_trip_summary_agent = ValidateTripSummary(
    name="ValidateTripSummary",
    description="驗證旅程摘要審查狀態，並根據審查結果提供回饋。",
)


root_agent = SequentialAgent(
    name="PlanTripWorkflow",
    description="協調旅程規劃流程，首先同時擷取航班、飯店和景點資訊，然後將旅程詳細資訊總結成一份文件。",
    # 執行並行擷取，然後進行綜合
    sub_agents=[sightseeing_agent, plan_parallel,
                trip_summary_agent, trip_summary_reviewer, validate_trip_summary_agent]
)