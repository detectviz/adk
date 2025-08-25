"""適用於 A2A 框架的 AI Foundry Agent Executor。
從 ADK 代理 (Agent) 執行器模式改編，以與 Azure AI Foundry 代理 (Agent) 搭配使用。
"""

import logging

from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    AgentCard,
    FilePart,
    FileWithBytes,
    FileWithUri,
    Part,
    TaskState,
    TextPart,
)
from a2a.utils.message import new_agent_text_message
from foundry_agent import FoundryCalendarAgent


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FoundryAgentExecutor(AgentExecutor):
    """一個執行基於 Azure AI Foundry 的代理 (Agent) 的 AgentExecutor。
    從 ADK 代理 (Agent) 執行器模式改編。
    """

    def __init__(self, card: AgentCard):
        self._card = card
        self._foundry_agent: FoundryCalendarAgent | None = None
        self._active_threads: dict[
            str, str
        ] = {}  # context_id -> thread_id mapping

    async def _get_or_create_agent(self) -> FoundryCalendarAgent:
        """取得或建立 Foundry 日曆代理 (Agent)。"""
        if not self._foundry_agent:
            from foundry_agent import create_foundry_calendar_agent

            self._foundry_agent = await create_foundry_calendar_agent()
        return self._foundry_agent

    async def _get_or_create_thread(self, context_id: str) -> str:
        """為給定的上下文取得或建立一個執行緒。"""
        if context_id not in self._active_threads:
            agent = await self._get_or_create_agent()
            thread = await agent.create_thread()
            self._active_threads[context_id] = thread.id
            logger.info(
                f'已為上下文 {context_id} 建立新執行緒 {thread.id}'
            )

        return self._active_threads[context_id]

    async def _process_request(
        self,
        message_parts: list[Part],
        context_id: str,
        task_updater: TaskUpdater,
    ) -> None:
        """透過 Foundry 代理 (Agent) 處理使用者請求。"""
        try:
            # 將 A2A 部分轉換為文字訊息
            user_message = self._convert_parts_to_text(message_parts)

            # 取得代理 (Agent) 和執行緒
            agent = await self._get_or_create_agent()
            thread_id = await self._get_or_create_thread(context_id)

            # 更新狀態
            await task_updater.update_status(
                TaskState.working,
                message=new_agent_text_message(
                    '正在處理您的請求...', context_id=context_id
                ),
            )

            # 執行對話
            responses = await agent.run_conversation(thread_id, user_message)

            # 傳回回應
            for response in responses:
                await task_updater.update_status(
                    TaskState.working,
                    message=new_agent_text_message(
                        response, context_id=context_id
                    ),
                )

            # 標示為完成
            final_message = responses[-1] if responses else '任務已完成。'
            await task_updater.complete(
                message=new_agent_text_message(
                    final_message, context_id=context_id
                )
            )

        except Exception as e:
            logger.error(f'處理請求時發生錯誤：{e}', exc_info=True)
            await task_updater.failed(
                message=new_agent_text_message(
                    f'錯誤：{e!s}', context_id=context_id
                )
            )

    def _convert_parts_to_text(self, parts: list[Part]) -> str:
        """將 A2A 訊息部分轉換為文字字串。"""
        text_parts = []

        for part in parts:
            part = part.root
            if isinstance(part, TextPart):
                text_parts.append(part.text)
            elif isinstance(part, FilePart):
                # 為示範目的，僅指出檔案存在
                if isinstance(part.file, FileWithUri):
                    text_parts.append(f'[檔案：{part.file.uri}]')
                elif isinstance(part.file, FileWithBytes):
                    text_parts.append(f'[檔案：{len(part.file.bytes)} 位元組]')
            else:
                logger.warning(f'不支援的部分類型：{type(part)}')

        return ' '.join(text_parts)

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        """執行代理 (Agent) 請求。"""
        logger.info(f'正在為上下文執行請求：{context.context_id}')

        # 建立任務更新器
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)

        # 通知任務提交
        if not context.current_task:
            await updater.submit()

        # 開始工作
        await updater.start_work()

        # 處理請求
        await self._process_request(
            context.message.parts,
            context.context_id,
            updater,
        )

        logger.debug(
            f'Foundry 代理 (Agent) 執行完成，針對 {context.context_id}'
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """取消正在進行的執行。"""
        logger.info(f'正在取消上下文的執行：{context.context_id}')

        # 目前僅記錄取消
        # 在完整的實作中，您可能需要：
        # 1. 取消任何正在進行的 API 呼叫
        # 2. 清理資源
        # 3. 通知任務儲存庫

        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.failed(
            message=new_agent_text_message(
                '任務已由使用者取消', context_id=context.context_id
            )
        )

    async def cleanup(self):
        """清理資源。"""
        if self._foundry_agent:
            await self._foundry_agent.cleanup_agent()
            self._foundry_agent = None
        self._active_threads.clear()
        logger.info('Foundry 代理 (Agent) 執行器已清理')


def create_foundry_agent_executor(card: AgentCard) -> FoundryAgentExecutor:
    """用於建立 Foundry 代理 (Agent) 執行器的工廠函式。"""
    return FoundryAgentExecutor(card)
