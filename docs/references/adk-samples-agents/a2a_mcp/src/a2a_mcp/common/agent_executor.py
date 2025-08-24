import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    DataPart,
    InvalidParamsError,
    SendStreamingMessageSuccessResponse,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatusUpdateEvent,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError
from a2a_mcp.common.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class GenericAgentExecutor(AgentExecutor):
    """旅行代理使用的 AgentExecutor。"""

    def __init__(self, agent: BaseAgent):
        self.agent = agent

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        logger.info(f'正在執行代理 {self.agent.agent_name}')
        error = self._validate_request(context)
        if error:
            raise ServerError(error=InvalidParamsError())

        query = context.get_user_input()

        task = context.current_task

        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)

        async for item in self.agent.stream(query, task.context_id, task.id):
            # 代理對代理的呼叫將返回事件，
            # 更新相關 ID 以便代理回來。
            if hasattr(item, 'root') and isinstance(
                item.root, SendStreamingMessageSuccessResponse
            ):
                event = item.root.result
                if isinstance(
                    event,
                    (TaskStatusUpdateEvent | TaskArtifactUpdateEvent),
                ):
                    await event_queue.enqueue_event(event)
                continue

            is_task_complete = item['is_task_complete']
            require_user_input = item['require_user_input']

            if is_task_complete:
                if item['response_type'] == 'data':
                    part = DataPart(data=item['content'])
                else:
                    part = TextPart(text=item['content'])

                await updater.add_artifact(
                    [part],
                    name=f'{self.agent.agent_name}-result',
                )
                await updater.complete()
                break
            if require_user_input:
                await updater.update_status(
                    TaskState.input_required,
                    new_agent_text_message(
                        item['content'],
                        task.context_id,
                        task.id,
                    ),
                    final=True,
                )
                break
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(
                    item['content'],
                    task.context_id,
                    task.id,
                ),
            )

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())
