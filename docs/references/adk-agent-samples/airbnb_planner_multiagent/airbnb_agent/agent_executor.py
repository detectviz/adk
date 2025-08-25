# pylint: disable=logging-fstring-interpolation
import logging

from typing import Any, override

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import (
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils import new_agent_text_message, new_task, new_text_artifact
from airbnb_agent import (
    AirbnbAgent,
)


logger = logging.getLogger(__name__)


class AirbnbAgentExecutor(AgentExecutor):
    """使用具有預載工具的代理 (Agent) 的 AirbnbAgentExecutor。"""

    def __init__(self, mcp_tools: list[Any]):
        """初始化 AirbnbAgentExecutor。

        Args:
            mcp_tools: 用於 AirbnbAgent 的預載 MCP 工具列表。
        """
        super().__init__()
        logger.info(
            f'正在使用 {len(mcp_tools) if mcp_tools else "無"} 個 MCP 工具初始化 AirbnbAgentExecutor。'
        )
        self.agent = AirbnbAgent(mcp_tools=mcp_tools)

    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        task = context.current_task

        if not context.message:
            raise Exception('未提供訊息')

        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        # 叫用底層代理 (Agent)，使用串流結果
        async for event in self.agent.stream(query, task.context_id):
            if event['is_task_complete']:
                await event_queue.enqueue_event(
                    TaskArtifactUpdateEvent(
                        append=False,
                        context_id=task.context_id,
                        task_id=task.id,
                        last_chunk=True,
                        artifact=new_text_artifact(
                            name='current_result',
                            description='向代理 (Agent) 發出請求的結果。',
                            text=event['content'],
                        ),
                    )
                )
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(state=TaskState.completed),
                        final=True,
                        context_id=task.context_id,
                        task_id=task.id,
                    )
                )
            elif event['require_user_input']:
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(
                            state=TaskState.input_required,
                            message=new_agent_text_message(
                                event['content'],
                                task.context_id,
                                task.id,
                            ),
                        ),
                        final=True,
                        context_id=task.context_id,
                        task_id=task.id,
                    )
                )
            else:
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(
                            state=TaskState.working,
                            message=new_agent_text_message(
                                event['content'],
                                task.context_id,
                                task.id,
                            ),
                        ),
                        final=False,
                        context_id=task.context_id,
                        task_id=task.id,
                    )
                )

    @override
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('不支援取消')
