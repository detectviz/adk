"""此檔案作為應用程式的主要進入點。

它會初始化 A2A 伺服器、定義代理 (Agent) 的功能，
並啟動伺服器以處理傳入的請求。請注意，代理 (Agent) 在通訊埠 10011 上執行。
"""

import logging

import click

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent import ChartGenerationAgent
from agent_executor import ChartGenerationAgentExecutor
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10011)
def main(host, port):
    """A2A 圖表產生代理 (Agent) 的進入點。"""
    try:
        capabilities = AgentCapabilities(streaming=False)
        skill = AgentSkill(
            id='chart_generator',
            name='圖表產生器',
            description='根據傳入的類 CSV 資料產生圖表',
            tags=['產生圖片', '編輯圖片'],
            examples=[
                '產生營收圖表：一月,$1000 二月,$2000 三月,$1500'
            ],
        )

        agent_card = AgentCard(
            name='圖表產生器代理 (Agent)',
            description='從結構化的類 CSV 資料輸入產生圖表。',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            default_input_modes=ChartGenerationAgent.SUPPORTED_CONTENT_TYPES,
            default_output_modes=ChartGenerationAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=ChartGenerationAgentExecutor(),
            task_store=InMemoryTaskStore(),
        )

        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )

        import uvicorn

        uvicorn.run(server.build(), host=host, port=port)

    except Exception as e:
        logger.error(f'伺服器啟動期間發生錯誤：{e}')
        exit(1)


if __name__ == '__main__':
    main()
