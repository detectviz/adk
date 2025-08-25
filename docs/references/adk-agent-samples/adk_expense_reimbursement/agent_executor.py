import json

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    DataPart,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_parts_message,
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError
from agent import ReimbursementAgent


class ReimbursementAgentExecutor(AgentExecutor):
    """費用報銷 AgentExecutor 範例。"""

    def __init__(self):
        self.agent = ReimbursementAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        task = context.current_task

        # 此代理 (Agent) 總是會產生 Task 物件。如果此請求
        # 沒有目前的任務，請建立一個新任務並使用它。
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        # 叫用底層代理 (Agent)，使用串流結果。現在的串流
        # 是更新事件。
        async for item in self.agent.stream(query, task.context_id):
            is_task_complete = item['is_task_complete']
            artifacts = None
            if not is_task_complete:
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(
                        item['updates'], task.context_id, task.id
                    ),
                )
                continue
            # 如果回應是字典，則假設它是一個表單
            if isinstance(item['content'], dict):
                # 驗證它是否為有效的表單
                if (
                    'response' in item['content']
                    and 'result' in item['content']['response']
                ):
                    data = json.loads(item['content']['response']['result'])
                    await updater.update_status(
                        TaskState.input_required,
                        new_agent_parts_message(
                            [Part(root=DataPart(data=data))],
                            task.context_id,
                            task.id,
                        ),
                        final=True,
                    )
                    continue
                await updater.update_status(
                    TaskState.failed,
                    new_agent_text_message(
                        '達到非預期狀態',
                        task.context_id,
                        task.id,
                    ),
                    final=True,
                )
                break
            # 發出適當的事件
            await updater.add_artifact(
                [Part(root=TextPart(text=item['content']))], name='form'
            )
            await updater.complete()
            break

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())
