import logging
import os

import click

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent import ReimbursementAgent
from agent_executor import ReimbursementAgentExecutor
from dotenv import load_dotenv
from timestamp_ext import TimestampExtension


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """缺少 API 金鑰的例外情況。"""


@click.command()
@click.option('--host', default='localhost')
@click.option('--port', default=10002)
def main(host, port):
    try:
        # Check for API key only if Vertex AI is not configured
        if not os.getenv('GOOGLE_GENAI_USE_VERTEXAI') == 'TRUE':
            if not os.getenv('GEMINI_API_KEY'):
                raise MissingAPIKeyError(
                    'GEMINI_API_KEY 環境變數未設定且 GOOGLE_GENAI_USE_VERTEXAI 不為 TRUE。'
                )

        hello_ext = TimestampExtension()
        capabilities = AgentCapabilities(
            streaming=True,
            extensions=[
                hello_ext.agent_extension(),
            ],
        )
        skill = AgentSkill(
            id='process_reimbursement',
            name='處理報銷工具',
            description='根據使用者提供的報銷金額和目的，協助處理報銷流程。',
            tags=['reimbursement'],
            examples=[
                '你能幫我報銷與客戶共進午餐的 20 美元嗎？'
            ],
        )
        agent_card = AgentCard(
            name='報銷代理 (Reimbursement Agent)',
            description='此代理 (Agent) 根據員工提供的報銷金額和目的，處理報銷流程。',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            default_input_modes=ReimbursementAgent.SUPPORTED_CONTENT_TYPES,
            default_output_modes=ReimbursementAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )
        agent_executor = ReimbursementAgentExecutor()
        # 使用裝飾器版本的擴充功能以獲得最佳易用性。
        agent_executor = hello_ext.wrap_executor(agent_executor)
        request_handler = DefaultRequestHandler(
            agent_executor=agent_executor,
            task_store=InMemoryTaskStore(),
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )
        import uvicorn

        uvicorn.run(server.build(), host=host, port=port)
    except MissingAPIKeyError as e:
        logger.error(f'Error: {e}')
        exit(1)
    except Exception as e:
        logger.error(f'伺服器啟動期間發生錯誤：{e}')
        exit(1)


if __name__ == '__main__':
    main()
