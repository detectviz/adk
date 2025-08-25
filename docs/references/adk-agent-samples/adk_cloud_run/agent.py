import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


def create_calendar_event(event_details: dict) -> dict:
    """使用提供的詳細資訊建立日曆活動。"""
    # 此函式將包含建立日曆活動的邏輯。
    # 目前，我們只會傳回一個模擬的回應。
    return {
        'status': 'success',
        'message': f"活動 '{event_details['title']}' 已成功建立。",
    }


LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini/gemini-2.5-flash-lite')
root_agent = Agent(
    name='calendar_agent',
    model=LiteLlm(model=LITELLM_MODEL),
    description=('管理日曆活動的代理 (Agent)。'),
    instruction=('你是一個可以管理日曆活動的有用代理 (Agent)。'),
    tools=[create_calendar_event],
)
