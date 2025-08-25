import logging

import click
import httpx

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import SemanticKernelMCPAgentExecutor
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


@click.command()
@click.option('--host', default='localhost')
@click.option('--port', default=10002)
def main(host, port):
    """使用 A2A 啟動 Semantic Kernel MCP Agent 伺服器。"""
    httpx_client = httpx.AsyncClient()
    request_handler = DefaultRequestHandler(
        agent_executor=SemanticKernelMCPAgentExecutor(),
        task_store=InMemoryTaskStore(),
        push_notifier=InMemoryPushNotifier(httpx_client),
    )

    server = A2AStarletteApplication(
        agent_card=get_agent_card(host, port), http_handler=request_handler
    )
    import uvicorn

    uvicorn.run(server.build(), host=host, port=port)


def get_agent_card(host: str, port: int):
    """傳回 Semantic Kernel MCP Agent 的代理卡 (Agent Card)。"""
    # 建置代理卡 (agent card)
    capabilities = AgentCapabilities(streaming=True)
    skill_mcp_tools = AgentSkill(
        id='dev_tools_agent',
        name='開發工具',
        description=(
            '透過模型上下文協定 (MCP) 工具提供全面的開發和任務協助，'
            '包括 git clone，並使用 VSCode 或 VSCode Insiders 開啟'
        ),
        tags=['開發', '工具', 'git', 'vscode', 'vscode-insiders'],
        examples=[
            '複製 https://github.com/kinfey/mcpdemo1',
            '在 VSCode 中開啟 /path',
            '複製 https://github.com/kinfey/mcpdemo1，並使用 VSCode Insiders 開啟',
        ],
    )

    agent_card = AgentCard(
        name='DevToolsAgent',
        description=(
            '此代理 (Agent) 透過 git 和 VSCode 工具提供全面的開發和任務協助'
        ),
        url='http://localhost:10002/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=capabilities,
        skills=[skill_mcp_tools],
    )

    return agent_card


if __name__ == '__main__':
    main()
