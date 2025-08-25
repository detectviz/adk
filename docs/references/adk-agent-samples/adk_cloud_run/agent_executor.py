from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    Part,
    TaskState,
    TextPart,
)
from a2a.utils import new_agent_text_message, new_task
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


class ADKAgentExecutor(AgentExecutor):
    def __init__(
        self,
        agent,
        status_message='正在處理請求...',
        artifact_name='response',
    ):
        """初始化一個通用的 ADK 代理 (Agent) 執行器。

        Args:
            agent: ADK 代理 (Agent) 實例
            status_message: 處理期間顯示的訊息
            artifact_name: 回應產物的名稱
        """
        self.agent = agent
        self.status_message = status_message
        self.artifact_name = artifact_name
        self.runner = Runner(
            app_name=agent.name,
            agent=agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """取消特定工作的執行。"""
        raise NotImplementedError(
            'ADKAgentExecutor 尚未實作取消功能。'
        )

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        if not context.message:
            raise ValueError('請求上下文中應包含訊息')

        query = context.get_user_input()
        task = context.current_task or new_task(context.message)
        await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)
        if context.call_context:
            user_id = context.call_context.user.user_name
        else:
            user_id = 'a2a_user'

        try:
            # 使用自訂訊息更新狀態
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(
                    self.status_message, task.context_id, task.id
                ),
            )

            # 使用 ADK 代理 (Agent) 進行處理
            session = await self.runner.session_service.create_session(
                app_name=self.agent.name,
                user_id=user_id,
                state={},
                session_id=task.context_id,
            )

            content = types.Content(
                role='user', parts=[types.Part.from_text(text=query)]
            )

            response_text = ''
            async for event in self.runner.run_async(
                user_id=user_id, session_id=session.id, new_message=content
            ):
                if (
                    event.is_final_response()
                    and event.content
                    and event.content.parts
                ):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text + '\n'
                        elif hasattr(part, 'function_call'):
                            # 如有需要，記錄或處理函式呼叫
                            pass  # 函式呼叫由 ADK 內部處理

            # 使用自訂名稱將回應新增為產物
            await updater.add_artifact(
                [Part(root=TextPart(text=response_text))],
                name=self.artifact_name,
            )

            await updater.complete()

        except Exception as e:
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(
                    f'錯誤：{e!s}', task.context_id, task.id
                ),
                final=True,
            )
