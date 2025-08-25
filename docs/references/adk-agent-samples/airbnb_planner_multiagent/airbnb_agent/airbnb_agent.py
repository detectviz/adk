# ruff: noqa: E501
# pylint: disable=logging-fstring-interpolation
import logging
import os

from collections.abc import AsyncIterable
from typing import Any, Literal

import httpx

from langchain_core.messages import AIMessage, AIMessageChunk
from langchain_core.runnables.config import (
    RunnableConfig,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel


logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

memory = MemorySaver()


class ResponseFormat(BaseModel):
    """以此格式回應使用者。"""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str


class AirbnbAgent:
    """Airbnb 代理 (Agent) 範例。"""

    SYSTEM_INSTRUCTION = """你是一位專門協助處理 Airbnb 住宿的助理。你的主要職責是利用提供的工具來搜尋 Airbnb 房源並回答相關問題。你必須完全依賴這些工具來獲取資訊；請勿捏造房源或價格。請確保你以 Markdown 格式化的回應包含所有相關的工具輸出，並特別強調提供房源的直接連結"""

    RESPONSE_FORMAT_INSTRUCTION: str = (
        '如果請求已完全處理且不需要進一步輸入，請選擇狀態為 "completed"。'
        '如果你需要使用者提供更多資訊或提出澄清問題，請選擇狀態為 "input_required"。'
        '如果發生錯誤或無法滿足請求，請選擇狀態為 "error"。'
    )

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self, mcp_tools: list[Any]):  # 已修改以接受 mcp_tools
        """初始化 Airbnb 代理 (Agent)。

        Args:
            mcp_tools: 預載的 MCP (模型上下文協定) 工具列表。
        """
        logger.info('正在使用預載的 MCP 工具初始化 AirbnbAgent...')
        try:
            model = os.getenv('GOOGLE_GENAI_MODEL')
            if not model:
                raise ValueError(
                    '未設定 GOOGLE_GENAI_MODEL 環境變數'
                )

            if os.getenv('GOOGLE_GENAI_USE_VERTEXAI') == 'TRUE':
                # 如果不使用 Vertex AI，則使用 Google Generative AI 進行初始化
                logger.info('ChatVertexAI 模型已成功初始化。')
                self.model = ChatVertexAI(model=model)

            else:
                # 使用您提供的檔案中的模型名稱
                self.model = ChatGoogleGenerativeAI(model=model)
                logger.info(
                    'ChatGoogleGenerativeAI 模型已成功初始化。'
                )

        except Exception as e:
            logger.error(
                f'初始化 ChatGoogleGenerativeAI 模型失敗：{e}',
                exc_info=True,
            )
            raise

        self.mcp_tools = mcp_tools
        if not self.mcp_tools:
            raise ValueError('未向 AirbnbAgent 提供 MCP 工具')

    async def ainvoke(self, query: str, session_id: str) -> dict[str, Any]:
        logger.info(
            f"Airbnb.ainvoke 以查詢 '{query}' 和 session_id '{session_id}' 被呼叫"
        )
        try:
            airbnb_agent_runnable = create_react_agent(
                self.model,
                tools=self.mcp_tools,  # 使用預載的工具
                checkpointer=memory,
                prompt=self.SYSTEM_INSTRUCTION,
                response_format=(
                    self.RESPONSE_FORMAT_INSTRUCTION,
                    ResponseFormat,
                ),
            )
            logger.debug(
                '為 Airbnb 任務建立/設定的 LangGraph React 代理 (Agent) 已預載工具。'
            )

            config: RunnableConfig = {'configurable': {'thread_id': session_id}}
            langgraph_input = {'messages': [('user', query)]}

            logger.debug(
                f'正在以輸入 {langgraph_input} 和設定 {config} 叫用 Airbnb 代理 (Agent)'
            )

            await airbnb_agent_runnable.ainvoke(langgraph_input, config)
            logger.debug(
                'Airbnb 代理 (Agent) ainvoke 呼叫完成。正在從狀態中擷取回應...'
            )

            response = self._get_agent_response_from_state(
                config, airbnb_agent_runnable
            )
            logger.info(
                f'來自 Airbnb 代理 (Agent) 狀態的回應（工作階段 {session_id}）：{response}'
            )
            return response

        except httpx.HTTPStatusError as http_err:
            logger.error(
                f'Airbnb.ainvoke (Airbnb 任務) 中發生 HTTPStatusError：{http_err.response.status_code} - {http_err}',
                exc_info=True,
            )
            return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'Airbnb 任務的外部服務發生錯誤：{http_err.response.status_code}',
            }
        except Exception as e:
            logger.error(
                f'AirbnbAgent.ainvoke (Airbnb 任務) 中發生未處理的例外狀況：{type(e).__name__} - {e}',
                exc_info=True,
            )
            # 考慮是否要重新引發或傳回結構化錯誤
            return {
                'is_task_complete': True,  # 或 False，將任務標示為錯誤
                'require_user_input': False,
                'content': f'處理您的 airbnb 任務時發生未預期的錯誤：{type(e).__name__}。',
            }
            # 或者如果執行器應該處理它，則重新引發：
            # raise

    def _get_agent_response_from_state(
        self, config: RunnableConfig, agent_runnable
    ) -> dict[str, Any]:
        """從給定的 agent_runnable 狀態中擷取並格式化代理 (Agent) 的回應。"""
        logger.debug(
            f'正在為設定 {config} 進入 _get_agent_response_from_state，使用代理 (Agent)：{type(agent_runnable).__name__}'
        )
        try:
            if not hasattr(agent_runnable, 'get_state'):
                logger.error(
                    f'類型為 {type(agent_runnable).__name__} 的可執行代理 (Agent) 沒有 get_state 方法。'
                )
                return {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': '內部錯誤：代理 (Agent) 狀態擷取設定錯誤。',
                }

            current_state_snapshot = agent_runnable.get_state(config)
            # 下面這行在您的原始程式碼中導致錯誤，因為 .values 可能不是字典，
            # 而是一個您可以從中存取 .values.messages 等屬性的物件。
            # 讓我們更小心地存取它。
            state_values = getattr(current_state_snapshot, 'values', None)
            logger.debug(
                f'擷取到的狀態快照值：{"可用" if state_values else "不可用或無"}'
            )

        except Exception as e:
            logger.error(
                f'從 agent_runnable ({type(agent_runnable).__name__}) 取得狀態時發生錯誤：{e}',
                exc_info=True,
            )
            return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': '錯誤：無法擷取代理 (Agent) 狀態。',
            }

        if not state_values:
            logger.error(
                f'找不到設定 {config} 的狀態值（來自代理 (Agent) {type(agent_runnable).__name__}）'
            )
            return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': '錯誤：代理 (Agent) 狀態不可用。',
            }

        structured_response = (
            state_values.get('structured_response')
            if isinstance(state_values, dict)
            else getattr(state_values, 'structured_response', None)
        )

        if structured_response and isinstance(
            structured_response, ResponseFormat
        ):
            logger.info(
                f'來自 structured_response 的格式化回應：{structured_response}'
            )
            if structured_response.status == 'completed':
                return {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.message,
                }
            # 對於 'input_required' 或 'error'，從使用者的角度來看，任務尚未完成
            # 但從代理 (Agent) 的目前輪次來看可能已完成。A2A 會處理任務完成狀態。
            return {
                'is_task_complete': False,  # 讓 A2A 邏輯根據 require_user_input 決定
                'require_user_input': structured_response.status
                == 'input_required',
                'content': structured_response.message,  # 如果狀態為 'error'，這將是錯誤訊息
            }

        # 如果 structured_response 不如預期，則執行後備方案
        final_messages = (
            state_values.get('messages', [])
            if isinstance(state_values, dict)
            else getattr(state_values, 'messages', [])
        )

        if final_messages and isinstance(final_messages[-1], AIMessage):
            ai_content = final_messages[-1].content
            if (
                isinstance(ai_content, str) and ai_content
            ):  # 確保它是一個非空字串
                logger.warning(
                    f'找不到結構化回應或格式不符。正在為設定 {config} 後備至最後一則 AI 訊息內容。'
                )
                return {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': ai_content,
                }
            if isinstance(
                ai_content, list
            ):  # 處理 AIMessage 內容可能是部分列表的情況（例如文字和工具呼叫）
                # 如果是部分列表，請嘗試擷取文字內容
                text_parts = [
                    part['text']
                    for part in ai_content
                    if isinstance(part, dict) and part.get('type') == 'text'
                ]
                if text_parts:
                    logger.warning(
                        f'找不到結構化回應。正在為設定 {config} 後備至最後一則 AI 訊息部分的串連文字。'
                    )
                    return {
                        'is_task_complete': True,
                        'require_user_input': False,
                        'content': '\n'.join(text_parts),
                    }

        logger.warning(
            f'找不到結構化回應或格式不符，且沒有合適的後備 AI 訊息。設定 {config} 的狀態：{state_values}'
        )
        return {
            'is_task_complete': False,
            'require_user_input': True,  # 預設需要輸入或發出問題信號
            'content': '由於未預期的回應格式，我們目前無法處理您的請求。請再試一次。',
        }

    # stream 方法也會使用 self.mcp_tools，如果它同樣建立了一個代理 (Agent) 實例
    async def stream(self, query: str, session_id: str) -> AsyncIterable[Any]:
        logger.info(
            f"AirbnbAgent.stream 以查詢 '{query}' 和 sessionId '{session_id}' 被呼叫"
        )
        agent_runnable = create_react_agent(
            self.model,
            tools=self.mcp_tools,  # 使用預載的工具
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=(
                self.RESPONSE_FORMAT_INSTRUCTION,
                ResponseFormat,
            ),  # 確保最終回應可以是結構化的
        )
        config: RunnableConfig = {'configurable': {'thread_id': session_id}}
        langgraph_input = {'messages': [('user', query)]}

        logger.debug(
            f'正在從 Airbnb 代理 (Agent) 串流，輸入為：{langgraph_input}，設定為：{config}'
        )
        try:
            async for chunk in agent_runnable.astream_events(
                langgraph_input, config, version='v1'
            ):
                logger.debug(f'工作階段 {session_id} 的串流區塊：{chunk}')
                event_name = chunk.get('event')
                data = chunk.get('data', {})
                content_to_yield = None

                if event_name == 'on_tool_start':
                    tool_name = data.get('name', '一個工具')
                    # tool_input = data.get("input", {}) # 可能會很冗長
                    content_to_yield = f'正在使用工具：{tool_name}...'
                elif event_name == 'on_chat_model_stream':
                    message_chunk = data.get('chunk')
                    if (
                        isinstance(message_chunk, AIMessageChunk)
                        and message_chunk.content
                    ):
                        content_to_yield = message_chunk.content

                if content_to_yield:
                    yield {
                        'is_task_complete': False,
                        'require_user_input': False,
                        'content': content_to_yield,
                    }

            # 所有事件結束後，從代理 (Agent) 的狀態中取得最終的結構化回應
            final_response = self._get_agent_response_from_state(
                config, agent_runnable
            )
            logger.info(
                f'串流結束後從狀態取得的最終回應（工作階段 {session_id}）：{final_response}'
            )
            yield final_response

        except Exception as e:
            logger.error(
                f'工作階段 {session_id} 的 AirbnbAgent.stream 期間發生錯誤：{e}',
                exc_info=True,
            )
            yield {
                'is_task_complete': True,  # 串流因錯誤而結束
                'require_user_input': False,
                'content': f'串流期間發生錯誤：{getattr(e, "message", str(e))}',
            }
