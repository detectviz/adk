# mypy: ignore-errors
import asyncio
import logging
import os

from collections.abc import AsyncGenerator, AsyncIterable
from typing import Any
from uuid import uuid4

import httpx

from a2a.client import A2AClient
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    Artifact,
    FilePart,
    FileWithBytes,
    FileWithUri,
    GetTaskRequest,
    GetTaskSuccessResponse,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    SendMessageSuccessResponse,
    Task,
    TaskQueryParams,
    TaskState,
    TaskStatus,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import get_text_parts
from a2a.utils.errors import ServerError
from google.adk import Runner
from google.adk.agents import LlmAgent, RunConfig
from google.adk.artifacts import InMemoryArtifactService
from google.adk.events import Event
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.tools import BaseTool, ToolContext
from google.genai import types
from pydantic import ConfigDict


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

AUTH_TASK_POLLING_DELAY_SECONDS = 0.2


class A2ARunConfig(RunConfig):
    """自訂 ADK RunConfig 的覆寫，以透過事件循環傳遞額外資料。"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    current_task_updater: TaskUpdater


class ADKAgentExecutor(AgentExecutor):
    """執行基於 ADK 的代理 (Agent) 的 AgentExecutor。"""

    def __init__(self, calendar_agent_url):
        LITELLM_MODEL = os.getenv(
            'LITELLM_MODEL', 'gemini/gemini-2.0-flash-001'
        )
        self._agent = LlmAgent(
            model=LiteLlm(model=LITELLM_MODEL),
            name='birthday_planner_agent',
            description='一個協助管理生日派對的代理 (Agent)。',
            after_tool_callback=self._handle_auth_required_task,
            instruction="""
    您是一個協助規劃生日派對的代理 (Agent)。

    作為派對策劃者，您的工作是為正在規劃生日派對的使用者提供意見和創意。

    您應該就以下方面提供建議，或鼓勵使用者提供詳細資訊：
    - 場地
    - 舉辦派對的時間、星期幾
    - 適合年齡的活動
    - 派對主題

    您可以將任務委派給一個獨立的日曆代理 (Calendar Agent)，以協助管理使用者的日曆。
    """,
            tools=[self.message_calendar_agent],
        )
        self.calendar_agent_endpoint = calendar_agent_url
        self.runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def _run_agent(
        self,
        session_id,
        new_message: types.Content,
        task_updater: TaskUpdater,
    ) -> AsyncGenerator[Event]:
        return self.runner.run_async(
            session_id=session_id,
            user_id='self',
            new_message=new_message,
            run_config=A2ARunConfig(current_task_updater=task_updater),
        )

    async def _handle_auth_required_task(
        self,
        tool: BaseTool,
        args: dict[str, Any],
        tool_context: ToolContext,
        tool_response: dict,
    ) -> dict | None:
        """處理需要驗證的請求。"""
        if tool.name != 'message_calendar_agent':
            return None
        if not tool_context.state.get('task_suspended'):
            return None
        dependent_task = Task.model_validate(
            tool_context.state['dependent_task']
        )
        if dependent_task.status.state != TaskState.auth_required:
            return None
        task_updater = self._get_task_updater(tool_context)
        task_updater.update_status(
            dependent_task.status.state, message=dependent_task.status.message
        )
        # 這不是一個穩健的解決方案。我們預期日曆代理 (Calendar Agent) 只會
        # 從 auth-required -> completed。一個更穩健的解決方案應具備
        # 更完整的狀態轉換處理。
        task = await self._wait_for_dependent_task(dependent_task)
        task_updater.update_status(
            TaskState.working,
            message=task_updater.new_agent_message(
                [Part(TextPart(text='正在檢查日曆代理 (Calendar Agent) 的輸出'))]
            ),
        )
        tool_context.state['task_suspended'] = False
        tool_context.state['dependent_task'] = None
        content = []
        if task.artifacts:
            for artifact in task.artifacts:
                content.extend(get_text_parts(artifact.parts))
        return {'response': '\n'.join(content)}

    def _get_task_updater(self, tool_context: ToolContext):
        return tool_context._invocation_context.run_config.current_task_updater

    async def _process_request(
        self,
        new_message: types.Content,
        session_id: str,
        task_updater: TaskUpdater,
    ) -> AsyncIterable[TaskStatus | Artifact]:
        session = await self._upsert_session(
            session_id,
        )
        session_id = session.id
        async for event in self._run_agent(
            session_id, new_message, task_updater
        ):
            logger.debug('Received ADK event: %s', event)
            if event.is_final_response():
                response = convert_genai_parts_to_a2a(event.content.parts)
                logger.debug('Yielding final response: %s', response)
                await task_updater.add_artifact(response)
                await task_updater.complete()
                break
            if calls := event.get_function_calls():
                for call in calls:
                    # 提供我們正在做什麼的更新。
                    if call.name == 'message_calendar_agent':
                        await task_updater.update_status(
                            TaskState.working,
                            message=task_updater.new_agent_message(
                                [
                                    Part(
                                        root=TextPart(
                                            text='正在傳送訊息給日曆代理 (Calendar Agent)'
                                        )
                                    )
                                ]
                            ),
                        )
            elif not event.get_function_calls():
                logger.debug('Yielding update response')
                await task_updater.update_status(
                    TaskState.working,
                    message=task_updater.new_agent_message(
                        convert_genai_parts_to_a2a(event.content.parts)
                    ),
                )
            else:
                logger.debug('Skipping event')

    async def _wait_for_dependent_task(self, dependent_task: Task):
        async with httpx.AsyncClient() as client:
            # 訂閱會是個好方法。但我們將改用輪詢。
            a2a_client = A2AClient(
                httpx_client=client, url=self.calendar_agent_endpoint
            )
            # 我們希望等到任務進入終止狀態。
            while not self._is_task_complete(dependent_task):
                await asyncio.sleep(AUTH_TASK_POLLING_DELAY_SECONDS)
                response = await a2a_client.get_task(
                    GetTaskRequest(
                        id=str(uuid4()),
                        params=TaskQueryParams(id=dependent_task.id),
                    )
                )
                if not isinstance(response.root, GetTaskSuccessResponse):
                    logger.debug('Getting dependent task failed: %s', response)
                    # 在實際情境中，可能需要將此回應回饋給
                    # 代理 (Agent) 循環來決定如何處理。我們這裡只會讓
                    # 任務失敗。
                    raise Exception('取得相依任務失敗')
                dependent_task = response.root.result
            return dependent_task

    def _is_task_complete(self, task: Task) -> bool:
        return task.status.state == TaskState.completed

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        # 執行代理 (Agent)，直到完成或任務被暫停。
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        # 立即通知任務已提交。
        if not context.current_task:
            await updater.submit()
        await updater.start_work()
        await self._process_request(
            types.UserContent(
                parts=convert_a2a_parts_to_genai(context.message.parts),
            ),
            context.context_id,
            updater,
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        # 理想情況下：終止任何進行中的任務。
        raise ServerError(error=UnsupportedOperationError())

    async def _upsert_session(self, session_id: str):
        return await self.runner.session_service.get_session(
            app_name=self.runner.app_name, user_id='self', session_id=session_id
        ) or await self.runner.session_service.create_session(
            app_name=self.runner.app_name, user_id='self', session_id=session_id
        )

    async def message_calendar_agent(
        self, message: str, tool_context: ToolContext
    ):
        """傳送訊息給日曆代理 (Calendar Agent)。"""
        # 我們對 A2A 狀態機採用過於簡化的方法：
        # - 所有對日曆代理 (Calendar Agent) 的請求都使用當前的會話 ID 作為上下文 ID (Context ID)。
        # - 如果日曆代理 (Calendar Agent) 在此會話中的最後一個回應產生了非終端
        #   任務狀態，則請求會引用該任務。
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(
                message=Message(
                    context_id=tool_context._invocation_context.session.id,
                    task_id=tool_context.state.get('task_id'),
                    message_id=str(uuid4()),
                    role=Role.user,
                    parts=[Part(TextPart(text=message))],
                )
            ),
        )
        response = await self._send_agent_message(request)
        logger.debug('[A2A Client] Received response: %s', response)
        task_id = None
        content = []
        if isinstance(response.root, SendMessageSuccessResponse):
            if isinstance(response.root.result, Task):
                task = response.root.result
                if task.artifacts:
                    for artifact in task.artifacts:
                        content.extend(get_text_parts(artifact.parts))
                if not content:
                    content.extend(get_text_parts(task.status.message.parts))
                # 理想情況下應為「是終端狀態」
                if task.status.state != TaskState.completed:
                    task_id = task.id
                if task.status.state == TaskState.auth_required:
                    tool_context.state['task_suspended'] = True
                    tool_context.state['dependent_task'] = task.model_dump()
            else:
                content.extend(get_text_parts(response.root.result.parts))
        tool_context.state['task_id'] = task_id
        # 全部轉換成一個字串。
        return {'response': '\n'.join(content)}

    async def _send_agent_message(self, request: SendMessageRequest):
        async with httpx.AsyncClient() as client:
            calendar_agent_client = A2AClient(
                httpx_client=client, url=self.calendar_agent_endpoint
            )
            return await calendar_agent_client.send_message(request)

    async def _get_agent_task(self, task_id) -> Task:
        async with httpx.AsyncClient() as client:
            a2a_client = A2AClient(
                httpx_client=client, url=self.calendar_agent_endpoint
            )
            await a2a_client.get_task({'id': task_id})


def convert_a2a_parts_to_genai(parts: list[Part]) -> list[types.Part]:
    """將 A2A Part 類型列表轉換為 Google Gen AI Part 類型列表。"""
    return [convert_a2a_part_to_genai(part) for part in parts]


def convert_a2a_part_to_genai(part: Part) -> types.Part:
    """將單一 A2A Part 類型轉換為 Google Gen AI Part 類型。"""
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
        raise ValueError(f'Unsupported file type: {type(part.file)}')
    raise ValueError(f'Unsupported part type: {type(part)}')


def convert_genai_parts_to_a2a(parts: list[types.Part]) -> list[Part]:
    """將 Google Gen AI Part 類型列表轉換為 A2A Part 類型列表。"""
    return [
        convert_genai_part_to_a2a(part)
        for part in parts
        if (part.text or part.file_data or part.inline_data)
    ]


def convert_genai_part_to_a2a(part: types.Part) -> Part:
    """將單一 Google Gen AI Part 類型轉換為 A2A Part 類型。"""
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
    raise ValueError(f'Unsupported part type: {part}')
