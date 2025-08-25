from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils import new_agent_text_message, new_task, new_text_artifact
from agent import HRAgent


class HRAgentExecutor(AgentExecutor):
    """HR 代理執行器範例 (HR AgentExecutor Example)。"""

    def __init__(self):
        self.agent = HRAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        task = context.current_task

        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        # 使用串流結果叫用底層代理 (Agent)
        async for event in self.agent.stream(query, task.context_id):
            task_state = TaskState(event['task_state'])
            if event['is_task_complete']:
                await event_queue.enqueue_event(
                    TaskArtifactUpdateEvent(
                        append=False,
                        context_id=task.context_id,
                        task_id=task.id,
                        last_chunk=True,
                        artifact=new_text_artifact(
                            name='current_result',
                            description='對代理 (Agent) 的請求結果。',
                            text=event['content'],
                        ),
                    )
                )
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(state=task_state),
                        final=True,
                        context_id=task.context_id,
                        task_id=task.id,
                    )
                )
            else:
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(
                            state=task_state,
                            message=new_agent_text_message(
                                event['content'],
                                task.context_id,
                                task.id,
                            ),
                        ),
                        final=task_state
                        in {
                            TaskState.input_required,
                            TaskState.failed,
                            TaskState.unknown,
                        },
                        context_id=task.context_id,
                        task_id=task.id,
                    )
                )

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise Exception('不支援取消')
