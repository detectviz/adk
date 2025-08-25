from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    Part,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError
from agent import DiceAgent


class DiceAgentExecutor(AgentExecutor):
    """骰子代理執行器範例 (Dice AgentExecutor Example)。"""

    def __init__(self):
        self.agent = DiceAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        task = context.current_task

        # 此代理 (Agent) 總是產生 Task 物件。如果此請求沒有
        # 目前的任務，請建立一個新任務並使用它。
        if not task:
            task = new_task(context.message) # type: ignore
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        # 使用串流結果叫用底層代理 (Agent)。串流
        # 現在是更新事件。
        async for finished, text in self.agent.stream(query, task.context_id):
            if not finished:
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(text, task.context_id, task.id),
                )
                continue
            # 發出適當的事件
            await updater.add_artifact(
                [Part(root=TextPart(text=text))],
                name='response',
            )
            await updater.complete()
            break

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> None:
        raise ServerError(error=UnsupportedOperationError())
