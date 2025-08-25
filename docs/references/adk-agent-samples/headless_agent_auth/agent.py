import os

from collections.abc import AsyncIterable
from typing import Any, Literal

import httpx

from auth0.authentication.get_token import GetToken
from auth0.management import Auth0
from auth0_ai_langchain.auth0_ai import Auth0AI
from auth0_ai_langchain.ciba import get_ciba_credentials
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel


auth0_ai = Auth0AI(
    auth0={
        'domain': os.getenv('HR_AUTH0_DOMAIN'),
        'client_id': os.getenv('HR_AGENT_AUTH0_CLIENT_ID'),
        'client_secret': os.getenv('HR_AGENT_AUTH0_CLIENT_SECRET'),
    }
)


with_async_user_confirmation = auth0_ai.with_async_user_confirmation(
    binding_message='核准與外部方分享您的就業詳細資訊。',
    scopes=['read:employee'],
    user_id=lambda employee_id, **__: employee_id,
    audience=os.getenv('HR_API_AUTH0_AUDIENCE'),
    on_authorization_request='block',  # TODO：這僅用於示範目的
)


get_token = GetToken(
    domain=os.getenv('HR_AUTH0_DOMAIN'),
    client_id=os.getenv('HR_AGENT_AUTH0_CLIENT_ID'),
    client_secret=os.getenv('HR_AGENT_AUTH0_CLIENT_SECRET'),
)


@tool
async def is_active_employee(employee_id: str) -> dict[str, Any]:
    """確認某人是否為公司的在職員工。

    參數：
        employee_id (str)：員工的身分證明。

    傳回：
        dict：一個包含就業狀態的字典，如果請求失敗，則包含錯誤訊息。
    """
    try:
        credentials = get_ciba_credentials()
        response = await httpx.AsyncClient().get(
            f'{os.getenv("HR_API_BASE_URL", "http://localhost:10051")}/employees/{employee_id}',
            headers={
                'Authorization': f'{credentials["token_type"]} {credentials["access_token"]}',
                'Content-Type': 'application/json',
            },
        )

        if response.status_code == 404:
            return {'active': False}
        if response.status_code == 200:
            return {'active': True}
        response.raise_for_status()
    except httpx.HTTPError as e:
        return {'error': f'HR API 請求失敗：{e}'}
    except Exception:
        return {'error': '來自 HR API 的非預期回應。'}


@tool
def get_employee_id_by_email(work_email: str) -> dict[str, Any] | None:
    """透過電子郵件傳回員工 ID。

    參數：
        work_email (str)：員工的工作電子郵件。

    傳回：
        dict：一個包含員工 ID 的字典（如果存在），否則為 None。
    """
    try:
        user = Auth0(
            domain=get_token.domain,
            token=get_token.client_credentials(
                f'https://{os.getenv("HR_AUTH0_DOMAIN")}/api/v2/'
            )['access_token'],
        ).users_by_email.search_users_by_email(
            email=work_email, fields=['user_id']
        )[0]

        return {'employee_id': user['user_id']} if user else None
    except Exception:
        return {'error': '來自 Auth0 管理 API 的非預期回應。'}


class ResponseFormat(BaseModel):
    """以此格式回應使用者。"""

    status: Literal['completed', 'input-required', 'rejected', 'failed'] = (
        'failed'
    )
    message: str


class HRAgent:
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    SYSTEM_INSTRUCTION: str = (
        '您是一個處理第三方提出的有關 Staff0 員工的外部驗證請求的代理 (Agent)。'
        '請勿嘗試回答不相關的問題或將工具用於其他目的。'
        "如果使用員工 ID 詢問某人的員工狀態，請使用 `is_active_employee` 工具。"
        '如果他們改為提供工作電子郵件，請先呼叫 `get_employee_id_by_email` 工具以取得員工 ID，然後再使用 `is_active_employee`。'
    )

    RESPONSE_FORMAT_INSTRUCTION: str = (
        '如果請求已完全處理，請將狀態設定為「已完成」。'
        '如果工具回應表示需要使用者輸入才能繼續，請將狀態設定為「需要輸入」。'
        '如果工具回應包含 AccessDeniedInterrupt 錯誤，請將訊息設定為「使用者拒絕授權請求」，並將狀態設定為「已拒絕」。'
        '對於任何其他工具錯誤，請將狀態設定為「失敗」。'
    )

    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model='gemini-1.5-flash')
        self.tools = [
            get_employee_id_by_email,
            with_async_user_confirmation(is_active_employee),
        ]

        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=MemorySaver(),
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=(self.RESPONSE_FORMAT_INSTRUCTION, ResponseFormat),
        )

    async def invoke(self, query: str, context_id: str) -> dict[str, Any]:
        config: RunnableConfig = {'configurable': {'thread_id': context_id}}
        await self.graph.ainvoke({'messages': [('user', query)]}, config)
        return self.get_agent_response(config)

    async def stream(
        self, query: str, context_id: str
    ) -> AsyncIterable[dict[str, Any]]:
        inputs: dict[str, Any] = {'messages': [('user', query)]}
        config: RunnableConfig = {'configurable': {'thread_id': context_id}}

        async for item in self.graph.astream(
            inputs, config, stream_mode='values'
        ):
            message = item['messages'][-1] if 'messages' in item else None
            if message:
                if (
                    isinstance(message, AIMessage)
                    and message.tool_calls
                    and len(message.tool_calls) > 0
                ):
                    yield {
                        'is_task_complete': False,
                        'task_state': 'working',
                        'content': '正在查詢就業狀態...',
                    }
                elif isinstance(message, ToolMessage):
                    yield {
                        'is_task_complete': False,
                        'task_state': 'working',
                        'content': '正在處理就業狀態...',
                    }

        yield self.get_agent_response(config)

    def get_agent_response(self, config: RunnableConfig) -> dict[str, Any]:
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')

        if structured_response and isinstance(
            structured_response, ResponseFormat
        ):
            return {
                'is_task_complete': structured_response.status == 'completed',
                'task_state': structured_response.status,
                'content': structured_response.message,
            }

        return {
            'is_task_complete': False,
            'task_state': 'unknown',
            'content': '我們目前無法處理您的請求。請再試一次。',
        }
