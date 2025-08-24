import click
import uvicorn

from a2a.server.agent_execution import AgentExecutor
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers.default_request_handler import (
    DefaultRequestHandler,
)
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    GetTaskRequest,
    GetTaskResponse,
    SendMessageRequest,
    SendMessageResponse,
)

from no_llm_framework.server.agent_executor import HelloWorldAgentExecutor


class A2ARequestHandler(DefaultRequestHandler):
    """A2A Repo Agent 的 A2A 請求處理常式。"""

    def __init__(
        self, agent_executor: AgentExecutor, task_store: InMemoryTaskStore
    ):
        super().__init__(agent_executor, task_store)

    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        return await super().on_get_task(request)

    async def on_message_send(
        self, request: SendMessageRequest
    ) -> SendMessageResponse:
        return await super().on_message_send(request)


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=9999)
def main(host: str, port: int):
    """啟動 A2A Repo Agent 伺服器。

    此函式使用指定的主機和埠號初始化 A2A Repo Agent 伺服器。
    它會建立一個包含代理名稱、描述、版本和能力的代理卡。

    參數：
        host (str): 執行伺服器的主機位址。
        port (int): 執行伺服器的埠號。
    """
    skill = AgentSkill(
        id='answer_detail_about_A2A_repo',
        name='回答關於 A2A repo 的任何資訊',
        description='代理將查詢有關 A2A repo 的資訊並回答問題。',
        tags=['A2A repo'],
        examples=['什麼是 A2A repo？', '什麼是 Google A2A repo？'],
    )

    agent_card = AgentCard(
        name='A2A 協定代理',
        description='擁有 A2A 協定資訊並能回答相關問題的 A2A 協定知識代理。',
        url=f'http://{host}:{port}/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(
            input_modes=['text'],
            output_modes=['text'],
            streaming=True,
        ),
        skills=[skill],
        # authentication=AgentAuthentication(schemes=['public']),
        examples=['什麼是 A2A 協定？', '什麼是 Google A2A？'],
    )

    task_store = InMemoryTaskStore()
    request_handler = A2ARequestHandler(
        agent_executor=HelloWorldAgentExecutor(),
        task_store=task_store,
    )

    server = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )
    uvicorn.run(server.build(), host=host, port=port)


if __name__ == '__main__':
    main()
