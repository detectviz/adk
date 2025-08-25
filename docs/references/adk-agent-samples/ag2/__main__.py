import logging
import os

import click

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent import YoutubeMCPAgent  # type: ignore[import-untyped]
from agent_executor import AG2AgentExecutor  # type: ignore[import-untyped]
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10010)
def main(host, port):
    """啟動 AG2 MCP 代理 (Agent) 伺服器。"""
    if not os.getenv('OPENAI_API_KEY'):
        print('OPENAI_API_KEY 環境變數未設定。')

    request_handler = DefaultRequestHandler(
        agent_executor=AG2AgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    server = A2AStarletteApplication(
        agent_card=get_agent_card(host, port), http_handler=request_handler
    )
    import uvicorn

    uvicorn.run(server.build(), host=host, port=port)


def get_agent_card(host: str, port: int):
    """傳回 AG2 代理 (Agent) 的代理卡 (Agent Card)。"""
    capabilities = AgentCapabilities(streaming=True)
    skill = AgentSkill(
        id='download_closed_captions',
        name='下載 YouTube 隱藏式字幕',
        description='從 YouTube 影片中擷取隱藏式字幕/逐字稿',
        tags=['youtube', 'captions', 'transcription', 'video'],
        examples=[
            '從此 YouTube 影片中擷取逐字稿：https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            '下載此 YouTube 教學課程的字幕',
        ],
    )
    return AgentCard(
        name='YouTube 字幕代理 (Agent)',
        description='可從 YouTube 影片中擷取隱藏式字幕和逐字稿的 AI 代理 (Agent)。此代理 (Agent) 提供可用於進一步處理的原始轉錄資料。',
        url=f'http://{host}:{port}/',
        version='1.0.0',
        default_input_modes=YoutubeMCPAgent.SUPPORTED_CONTENT_TYPES,
        default_output_modes=YoutubeMCPAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill],
    )


if __name__ == '__main__':
    main()
