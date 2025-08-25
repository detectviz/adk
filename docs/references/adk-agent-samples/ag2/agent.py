import json
import logging
import os
import traceback

from collections.abc import AsyncIterable
from typing import Any, Literal

from autogen import AssistantAgent, LLMConfig
from autogen.mcp import create_toolkit
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class ResponseModel(BaseModel):
    """YouTube MCP 代理 (Agent) 的回應模型。"""

    text_reply: str
    closed_captions: str | None
    status: Literal['TERMINATE', '']

    def format(self) -> str:
        """將回應格式化為字串。"""
        if self.closed_captions is None:
            return self.text_reply
        return f'{self.text_reply}\n\n隱藏式字幕：\n{self.closed_captions}'


def get_api_key() -> str:
    """處理 API 金鑰的輔助方法。"""
    load_dotenv()
    return os.getenv('OPENAI_API_KEY')


class YoutubeMCPAgent:
    """存取 YouTube MCP 伺服器以下載隱藏式字幕的代理 (Agent)。"""

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self):
        # 在此處匯入 AG2 相依性以隔離需求
        try:
            # 設定 LLM 組態與回應格式
            llm_config = LLMConfig(
                model='gpt-4o',
                api_key=get_api_key(),
                response_format=ResponseModel,
            )

            # 建立將使用 MCP 工具的助理代理 (assistant agent)
            self.agent = AssistantAgent(
                name='YoutubeMCPAgent',
                llm_config=llm_config,
                system_message=(
                    '你是一個專門處理 YouTube 影片的助理。'
                    '你可以使用 MCP 工具來擷取字幕和處理 YouTube 內容。'
                    '你可以提供字幕、總結影片或分析 YouTube 內容。'
                    "如果使用者詢問與 YouTube 影片無關的任何問題，或未提供 YouTube URL，"
                    '請禮貌地說明你只能協助處理與 YouTube 影片相關的任務。\n\n'
                    '重要提示：一律使用 ResponseModel 格式回應，並包含以下欄位：\n'
                    '- text_reply：你的主要回應文字\n'
                    '- closed_captions：YouTube 字幕（如果有的話），若不相關則為 null\n'
                    "- status：所有回應一律使用 'TERMINATE' \n\n"
                    '回應範例：\n'
                    '{\n'
                    '  "text_reply": "這是您要求的資訊...",\n'
                    '  "closed_captions": null,\n'
                    '  "status": "TERMINATE"\n'
                    '}'
                ),
            )

            self.initialized = True
            logger.info('MCP 代理 (Agent) 已成功初始化')
        except ImportError as e:
            logger.error(f'匯入 AG2 元件失敗：{e}')
            self.initialized = False

    def get_agent_response(self, response: str) -> dict[str, Any]:
        """以一致的結構格式化代理 (Agent) 回應。"""
        try:
            # 嘗試將回應解析為 ResponseModel JSON
            response_dict = json.loads(response)
            model = ResponseModel(**response_dict)

            # 所有最終回應都應被視為已完成
            return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': model.format(),
            }
        except Exception as e:
            # 記錄錯誤但繼續使用盡力而為的後備方案
            logger.error(f'解析回應時發生錯誤：{e}，回應：{response}')

            # 預設將其視為已完成的回應
            return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': response,
            }

    async def stream(
        self, query: str, session_id: str
    ) -> AsyncIterable[dict[str, Any]]:
        """從 MCP 代理 (Agent) 串流更新。"""
        if not self.initialized:
            yield {
                'is_task_complete': False,
                'require_user_input': True,
                'content': '代理 (Agent) 初始化失敗。請檢查相依性和日誌。',
            }
            return

        try:
            # 初始回應以確認查詢
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': '正在處理請求...',
            }

            logger.info(f'正在處理查詢：{query[:50]}...')

            try:
                # 為 mcp-youtube 建立 stdio 伺服器參數
                server_params = StdioServerParameters(
                    command='mcp-youtube',
                )

                # 使用 stdio 客戶端連接到 MCP 伺服器
                async with (
                    stdio_client(server_params) as (read, write),
                    ClientSession(read, write) as session,
                ):
                    # 初始化連線
                    await session.initialize()

                    # 建立工具套件並註冊工具
                    toolkit = await create_toolkit(session=session)
                    toolkit.register_for_llm(self.agent)

                    result = await self.agent.a_run(
                        message=query,
                        tools=toolkit.tools,
                        max_turns=2,  # 固定為 2 輪以允許使用工具
                        user_input=False,
                    )

                    # 從結果中擷取內容
                    try:
                        # 處理結果
                        await result.process()

                        # 取得包含輸出的摘要
                        response = await result.summary

                    except Exception as extraction_error:
                        logger.error(
                            f'擷取回應時發生錯誤：{extraction_error}'
                        )
                        traceback.print_exc()
                        response = (
                            f'處理請求時發生錯誤：{extraction_error!s}'
                        )

                    # 最終回應
                    yield self.get_agent_response(response)

            except Exception as e:
                logger.error(
                    f'處理期間發生錯誤：{traceback.format_exc()}'
                )
                yield {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': f'處理請求時發生錯誤：{e!s}',
                }
        except Exception as e:
            logger.error(f'串流代理 (Agent) 時發生錯誤：{traceback.format_exc()}')
            yield {
                'is_task_complete': False,
                'require_user_input': True,
                'content': f'處理請求時發生錯誤：{e!s}',
            }

    def invoke(self, query: str, session_id: str) -> dict[str, Any]:
        """MCP 代理 (Agent) 的同步叫用。"""
        raise NotImplementedError(
            '此代理 (Agent) 不支援同步叫用。請改用串流端點 (message/stream)。'
        )
