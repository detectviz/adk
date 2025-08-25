import asyncio
import logging
import os

from collections.abc import AsyncIterable
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Any, Literal

import httpx

from dotenv import load_dotenv
from pydantic import BaseModel
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.contents import (
    FunctionCallContent,
    FunctionResultContent,
    StreamingChatMessageContent,
    StreamingTextContent,
)
from semantic_kernel.functions import KernelArguments, kernel_function


if TYPE_CHECKING:
    from semantic_kernel.connectors.ai.chat_completion_client_base import (
        ChatCompletionClientBase,
    )
    from semantic_kernel.contents import ChatMessageContent

logger = logging.getLogger(__name__)

load_dotenv()

# region 聊天服務設定


class ChatServices(str, Enum):
    """支援的聊天完成服務列舉。"""

    AZURE_OPENAI = 'azure_openai'
    OPENAI = 'openai'


service_id = 'default'


def get_chat_completion_service(
    service_name: ChatServices,
) -> 'ChatCompletionClientBase':
    """根據服務名稱傳回適當的聊天完成服務。

    Args:
        service_name (ChatServices): 服務名稱。

    Returns:
        ChatCompletionClientBase: 已設定的聊天完成服務。

    Raises:
        ValueError: 如果不支援該服務名稱或缺少必要的環境變數。
    """
    if service_name == ChatServices.AZURE_OPENAI:
        return _get_azure_openai_chat_completion_service()
    if service_name == ChatServices.OPENAI:
        return _get_openai_chat_completion_service()
    raise ValueError(f'不支援的服務名稱：{service_name}')


def _get_azure_openai_chat_completion_service() -> AzureChatCompletion:
    """傳回 Azure OpenAI 聊天完成服務。

    Returns:
        AzureChatCompletion: 已設定的 Azure OpenAI 服務。
    """
    return AzureChatCompletion(service_id=service_id)


def _get_openai_chat_completion_service() -> OpenAIChatCompletion:
    """傳回 OpenAI 聊天完成服務。

    Returns:
        OpenAIChatCompletion: 已設定的 OpenAI 服務。
    """
    return OpenAIChatCompletion(
        service_id=service_id,
        ai_model_id=os.getenv('OPENAI_MODEL_ID'),
        api_key=os.getenv('OPENAI_API_KEY'),
    )


# endregion

# region 外掛程式


class CurrencyPlugin:
    """一個利用 Frankfurter 取得匯率的簡單貨幣外掛程式。

    此外掛程式由 `currency_exchange_agent` 使用。
    """

    @kernel_function(
        description='使用 Frankfurter API 擷取 currency_from 和 currency_to 之間的匯率'
    )
    def get_exchange_rate(
        self,
        currency_from: Annotated[
            str, '要換出的貨幣代碼，例如 USD'
        ],
        currency_to: Annotated[
            str, '要換入的貨幣代碼，例如 EUR 或 INR'
        ],
        date: Annotated[str, "日期或 'latest'"] = 'latest',
    ) -> str:
        try:
            response = httpx.get(
                f'https://api.frankfurter.app/{date}',
                params={'from': currency_from, 'to': currency_to},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            if 'rates' not in data or currency_to not in data['rates']:
                return f'無法擷取 {currency_from} 到 {currency_to} 的匯率'
            rate = data['rates'][currency_to]
            return f'1 {currency_from} = {rate} {currency_to}'
        except Exception as e:
            return f'貨幣 API 呼叫失敗：{e!s}'


# endregion

# region 回應格式


class ResponseFormat(BaseModel):
    """一個回應格式模型，用於指示模型應如何回應。"""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str


# endregion

# region 語意核心代理


class SemanticKernelTravelAgent:
    """包裝基於語意核心的代理以處理旅遊相關任務。"""

    agent: ChatCompletionAgent
    thread: ChatHistoryAgentThread = None
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self):
        # 明確設定聊天完成服務
        # 預設使用 Azure OpenAI。若要使用 OpenAI 服務，請變更為 ChatServices.OPENAI。
        chat_service = get_chat_completion_service(ChatServices.AZURE_OPENAI)

        currency_exchange_agent = ChatCompletionAgent(
            service=chat_service,
            name='CurrencyExchangeAgent',
            instructions=(
                '您專門處理來自旅客的貨幣相關請求。'
                '這包括提供目前匯率、在不同貨幣之間轉換金額、'
                '解釋與貨幣兌換相關的費用或收費，以及提供兌換貨幣的最佳實踐建議。'
                '您的目標是迅速且準確地協助旅客解決所有與貨幣相關的問題。'
            ),
            plugins=[CurrencyPlugin()],
        )

        # 定義一個 ActivityPlannerAgent 來處理活動相關的任務
        activity_planner_agent = ChatCompletionAgent(
            service=chat_service,
            name='ActivityPlannerAgent',
            instructions=(
                '您專門為旅客規劃和推薦活動。'
                '這包括建議觀光選項、當地活動、餐飲推薦、'
                '預訂景點門票、提供旅遊行程建議，並確保活動'
                '符合旅客的偏好和行程安排。'
                '您的目標是為旅客創造愉快且個人化的體驗。'
            ),
        )

        # 定義主要的 TravelManagerAgent 以將任務委派給適當的代理
        self.agent = ChatCompletionAgent(
            service=chat_service,
            name='TravelManagerAgent',
            instructions=(
                "您的角色是仔細分析旅客的請求，並根據查詢的"
                '具體細節將其轉發給適當的代理。'
                '將任何涉及金額、貨幣匯率、貨幣換算、與貨幣兌換相關的費用、'
                '金融交易或付款方式的請求轉發給 CurrencyExchangeAgent。'
                '將與規劃活動、觀光推薦、餐飲建議、活動'
                '預訂、行程建立或任何不明確涉及金錢'
                '交易的旅遊體驗方面相關的請求轉發給 ActivityPlannerAgent。'
                '您的主要目標是精確高效地進行委派，以確保旅客能迅速獲得'
                '準確且專業的協助。'
            ),
            plugins=[currency_exchange_agent, activity_planner_agent],
            arguments=KernelArguments(
                settings=OpenAIChatPromptExecutionSettings(
                    response_format=ResponseFormat,
                )
            ),
        )

    async def invoke(self, user_input: str, session_id: str) -> dict[str, Any]:
        """處理同步任務（如 message/send）。

        Args:
            user_input (str): 使用者輸入訊息。
            session_id (str): 會話的唯一識別碼。

        Returns:
            dict: 一個包含內容、任務完成狀態和
            使用者輸入需求的字典。
        """
        await self._ensure_thread_exists(session_id)

        # 使用 SK 的 get_response 進行單次呼叫
        response = await self.agent.get_response(
            messages=user_input,
            thread=self.thread,
        )
        return self._get_agent_response(response.content)

    async def stream(
        self,
        user_input: str,
        session_id: str,
    ) -> AsyncIterable[dict[str, Any]]:
        """對於串流任務，我們產生 SK 代理的 invoke_stream 進度。

        Args:
            user_input (str): 使用者輸入訊息。
            session_id (str): 會話的唯一識別碼。

        Yields:
            dict: 一個包含內容、任務完成狀態和
            使用者輸入需求的字典。
        """
        await self._ensure_thread_exists(session_id)

        plugin_notice_seen = False
        plugin_event = asyncio.Event()

        text_notice_seen = False
        chunks: list[StreamingChatMessageContent] = []

        async def _handle_intermediate_message(
            message: 'ChatMessageContent',
        ) -> None:
            """處理來自代理的中介訊息。"""
            nonlocal plugin_notice_seen
            if not plugin_notice_seen:
                plugin_notice_seen = True
                plugin_event.set()
            # 處理函式呼叫期間中介訊息的範例
            for item in message.items or []:
                if isinstance(item, FunctionResultContent):
                    print(
                        f'SK 函式結果：> {item.result} 對於函式：{item.name}'
                    )
                elif isinstance(item, FunctionCallContent):
                    print(
                        f'SK 函式呼叫：> {item.name} 帶有參數：{item.arguments}'
                    )
                else:
                    print(f'SK 訊息：> {item}')

        async for chunk in self.agent.invoke_stream(
            messages=user_input,
            thread=self.thread,
            on_intermediate_message=_handle_intermediate_message,
        ):
            if plugin_event.is_set():
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': '正在處理函式呼叫...',
                }
                plugin_event.clear()

            if any(isinstance(i, StreamingTextContent) for i in chunk.items):
                if not text_notice_seen:
                    yield {
                        'is_task_complete': False,
                        'require_user_input': False,
                        'content': '正在建立輸出...',
                    }
                    text_notice_seen = True
                chunks.append(chunk.message)

        if chunks:
            yield self._get_agent_response(sum(chunks[1:], chunks[0]))

    def _get_agent_response(
        self, message: 'ChatMessageContent'
    ) -> dict[str, Any]:
        """從代理的訊息內容中提取結構化回應。

        Args:
            message (ChatMessageContent): 來自代理的訊息內容。

        Returns:
            dict: 一個包含內容、任務完成狀態和使用者輸入需求的字典。
        """
        structured_response = ResponseFormat.model_validate_json(
            message.content
        )

        default_response = {
            'is_task_complete': False,
            'require_user_input': True,
            'content': '我們目前無法處理您的請求。請再試一次。',
        }

        if isinstance(structured_response, ResponseFormat):
            response_map = {
                'input_required': {
                    'is_task_complete': False,
                    'require_user_input': True,
                },
                'error': {
                    'is_task_complete': False,
                    'require_user_input': True,
                },
                'completed': {
                    'is_task_complete': True,
                    'require_user_input': False,
                },
            }

            response = response_map.get(structured_response.status)
            if response:
                return {**response, 'content': structured_response.message}

        return default_response

    async def _ensure_thread_exists(self, session_id: str) -> None:
        """確保給定會話 ID 的執行緒存在。

        Args:
            session_id (str): 會話的唯一識別碼。
        """
        if self.thread is None or self.thread.id != session_id:
            await self.thread.delete() if self.thread else None
            self.thread = ChatHistoryAgentThread(thread_id=session_id)


# endregion
