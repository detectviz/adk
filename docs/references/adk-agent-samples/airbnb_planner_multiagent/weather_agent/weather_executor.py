import logging

from typing import TYPE_CHECKING

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
    UnsupportedOperationError,
)
from a2a.utils.errors import ServerError
from google.adk import Runner
from google.genai import types


if TYPE_CHECKING:
    from google.adk.sessions.session import Session


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Constants
DEFAULT_USER_ID = 'self'


class WeatherExecutor(AgentExecutor):
    """一個為天氣執行基於 ADK 的代理 (Agent) 的 AgentExecutor。"""

    def __init__(self, runner: Runner, card: AgentCard):
        self.runner = runner
        self._card = card
        # 追蹤活動中的工作階段以備可能取消
        self._active_sessions: set[str] = set()

    async def _process_request(
        self,
        new_message: types.Content,
        session_id: str,
        task_updater: TaskUpdater,
    ) -> None:
        session_obj = await self._upsert_session(session_id)
        # 使用已解析的工作階段物件中的 ID 更新 session_id。
        # (如果它已存在，可能與傳入的 ID 相同)
        session_id = session_obj.id

        # 將此工作階段追蹤為活動中
        self._active_sessions.add(session_id)

        try:
            async for event in self.runner.run_async(
                session_id=session_id,
                user_id=DEFAULT_USER_ID,
                new_message=new_message,
            ):
                if event.is_final_response():
                    parts = [
                        convert_genai_part_to_a2a(part)
                        for part in event.content.parts
                        if (part.text or part.file_data or part.inline_data)
                    ]
                    logger.debug('正在產生最終回應：%s', parts)
                    await task_updater.add_artifact(parts)
                    await task_updater.update_status(
                        TaskState.completed, final=True
                    )
                    break
                if not event.get_function_calls():
                    logger.debug('正在產生更新回應')
                    await task_updater.update_status(
                        TaskState.working,
                        message=task_updater.new_agent_message(
                            [
                                convert_genai_part_to_a2a(part)
                                for part in event.content.parts
                                if (
                                    part.text
                                    or part.file_data
                                    or part.inline_data
                                )
                            ],
                        ),
                    )
                else:
                    logger.debug('正在略過事件')
        finally:
            # 完成後從活動中的工作階段中移除
            self._active_sessions.discard(session_id)

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        # 執行代理 (Agent)，直到完成或任務暫停。
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        # 立即通知任務已提交。
        if not context.current_task:
            await updater.update_status(TaskState.submitted)
        await updater.update_status(TaskState.working)
        await self._process_request(
            types.UserContent(
                parts=[
                    convert_a2a_part_to_genai(part)
                    for part in context.message.parts
                ],
            ),
            context.context_id,
            updater,
        )
        logger.debug('[天氣] 執行結束')

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """取消給定上下文的執行。

        目前會記錄取消嘗試，因為底層的 ADK 執行器
        不支援直接取消正在進行的任務。
        """
        session_id = context.context_id
        if session_id in self._active_sessions:
            logger.info(
                f'已要求取消活動中的天氣工作階段：{session_id}'
            )
            # TODO: 在 ADK 支援時實作適當的取消功能
            self._active_sessions.discard(session_id)
        else:
            logger.debug(
                f'已要求取消非活動中的天氣工作階段：{session_id}'
            )

        raise ServerError(error=UnsupportedOperationError())

    async def _upsert_session(self, session_id: str) -> 'Session':
        """如果工作階段存在，則擷取該工作階段，否則建立一個新工作階段。

        確保非同步工作階段服務方法已正確等待。
        """
        session = await self.runner.session_service.get_session(
            app_name=self.runner.app_name,
            user_id=DEFAULT_USER_ID,
            session_id=session_id,
        )
        if session is None:
            session = await self.runner.session_service.create_session(
                app_name=self.runner.app_name,
                user_id=DEFAULT_USER_ID,
                session_id=session_id,
            )
        return session


def convert_a2a_part_to_genai(part: Part) -> types.Part:
    """將單一 A2A Part 類型轉換為 Google Gen AI Part 類型。

    Args:
        part: 要轉換的 A2A Part

    Returns:
        等效的 Google Gen AI Part

    Raises:
        ValueError: 如果不支援該部分類型
    """
    part = part.root
    if isinstance(part, TextPart):
        return types.Part(text=part.text)
    if isinstance(part, FilePart):
        if isinstance(part.file, FileWithUri):
            return types.Part(
                file_data=types.FileData(
                    file_uri=part.file.uri, mime_type=part.file.mime_type
                )
            )
        if isinstance(part.file, FileWithBytes):
            return types.Part(
                inline_data=types.Blob(
                    data=part.file.bytes, mime_type=part.file.mime_type
                )
            )
        raise ValueError(f'不支援的檔案類型：{type(part.file)}')
    raise ValueError(f'不支援的部分類型：{type(part)}')


def convert_genai_part_to_a2a(part: types.Part) -> Part:
    """將單一 Google Gen AI Part 類型轉換為 A2A Part 類型。

    Args:
        part: 要轉換的 Google Gen AI Part

    Returns:
        等效的 A2A Part

    Raises:
        ValueError: 如果不支援該部分類型
    """
    if part.text:
        return TextPart(text=part.text)
    if part.file_data:
        return FilePart(
            file=FileWithUri(
                uri=part.file_data.file_uri,
                mime_type=part.file_data.mime_type,
            )
        )
    if part.inline_data:
        return Part(
            root=FilePart(
                file=FileWithBytes(
                    bytes=part.inline_data.data,
                    mime_type=part.inline_data.mime_type,
                )
            )
        )
    raise ValueError(f'不支援的部分類型：{part}')
