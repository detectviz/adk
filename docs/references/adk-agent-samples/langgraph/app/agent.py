import os

from collections.abc import AsyncIterable
from typing import Any, Literal

import httpx

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel


memory = MemorySaver()


@tool
def get_exchange_rate(
    currency_from: str = 'USD',
    currency_to: str = 'EUR',
    currency_date: str = 'latest',
):
    """使用此工具取得目前的匯率。

    參數：
        currency_from：要轉換的貨幣（例如 "USD"）。
        currency_to：要轉換成的貨幣（例如 "EUR"）。
        currency_date：匯率的日期或 "latest"。預設為
            "latest"。

    傳回：
        一個包含匯率資料的字典，如果請求失敗則傳回錯誤訊息。
    """
    try:
        response = httpx.get(
            f'https://api.frankfurter.app/{currency_date}',
            params={'from': currency_from, 'to': currency_to},
        )
        response.raise_for_status()

        data = response.json()
        if 'rates' not in data:
            return {'error': '無效的 API 回應格式。'}
        return data
    except httpx.HTTPError as e:
        return {'error': f'API 請求失敗：{e}'}
    except ValueError:
        return {'error': '來自 API 的 JSON 回應無效。'}


class ResponseFormat(BaseModel):
    """以此格式回應使用者。"""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str


class CurrencyAgent:
    """貨幣代理 (CurrencyAgent) - 一個專門用於貨幣轉換的助理。"""

    SYSTEM_INSTRUCTION = (
        '您是一個專門用於貨幣轉換的助理。'
        "您的唯一目的是使用 'get_exchange_rate' 工具來回答有關貨幣匯率的問題。"
        '如果使用者詢問任何與貨幣轉換或匯率無關的問題，'
        '請禮貌地說明您無法協助該主題，只能協助與貨幣相關的查詢。'
        '不要嘗試回答無關的問題或將工具用於其他目的。'
    )

    FORMAT_INSTRUCTION = (
        '如果使用者需要提供更多資訊才能完成請求，請將回應狀態設定為 input_required。'
        '如果在處理請求時發生錯誤，請將回應狀態設定為 error。'
        '如果請求已完成，請將回應狀態設定為 completed。'
    )

    def __init__(self):
        model_source = os.getenv('model_source', 'google')
        if model_source == 'google':
            self.model = ChatGoogleGenerativeAI(model='gemini-2.0-flash')
        else:
            self.model = ChatOpenAI(
                model=os.getenv('TOOL_LLM_NAME'),
                openai_api_key=os.getenv('API_KEY', 'EMPTY'),
                openai_api_base=os.getenv('TOOL_LLM_URL'),
                temperature=0,
            )
        self.tools = [get_exchange_rate]

        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=(self.FORMAT_INSTRUCTION, ResponseFormat),
        )

    async def stream(self, query, context_id) -> AsyncIterable[dict[str, Any]]:
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': context_id}}

        for item in self.graph.stream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if (
                isinstance(message, AIMessage)
                and message.tool_calls
                and len(message.tool_calls) > 0
            ):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': '正在查詢匯率...',
                }
            elif isinstance(message, ToolMessage):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': '正在處理匯率..',
                }

        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(
            structured_response, ResponseFormat
        ):
            if structured_response.status == 'input_required':
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'error':
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'completed':
                return {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.message,
                }

        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': (
                '我們目前無法處理您的請求。'
                '請再試一次。'
            ),
        }

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']
