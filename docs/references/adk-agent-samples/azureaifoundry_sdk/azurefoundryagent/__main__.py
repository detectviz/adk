import logging
import os

import click
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from dotenv import load_dotenv
from foundry_agent_executor import create_foundry_agent_executor
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10007)
def main(host: str, port: int):
    """執行 AI Foundry A2A 示範伺服器。"""
    # 驗證必要的環境變數
    required_env_vars = [
        'AZURE_AI_FOUNDRY_PROJECT_ENDPOINT',
        'AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME',
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(
            f'缺少必要的環境變數：{", ".join(missing_vars)}'
        )

    # 定義代理 (Agent) 技能
    skills = [
        AgentSkill(
            id='check_availability',
            name='檢查日曆可用性',
            description='使用使用者的日曆檢查其在特定時間是否有空',
            tags=['日曆', '排程'],
            examples=[
                '我明天上午 10 點到 11 點有空嗎？',
                '檢查我下週二下午的空閒時間',
                '我星期五早上有任何行程衝突嗎？',
            ],
        ),
        AgentSkill(
            id='get_upcoming_events',
            name='取得即將到來的活動',
            description='為使用者擷取即將到來的日曆活動',
            tags=['日曆', '活動'],
            examples=[
                '我今天有哪些會議？',
                '顯示我本週的排程',
                '接下來幾個小時有什麼活動？',
            ],
        ),
        AgentSkill(
            id='calendar_management',
            name='日曆管理',
            description='一般日曆管理和排程協助',
            tags=['日曆', '生產力'],
            examples=[
                '幫我管理我的日曆',
                '什麼時候是開會的最佳時間？',
                '優化我明天的排程',
            ],
        ),
    ]

    # 建立代理卡 (agent card)
    agent_card = AgentCard(
        name='AI Foundry 日曆代理 (Agent)',
        description='一個由 Azure AI Foundry 提供支援的智慧日曆管理代理 (Agent)。'
        '我可以協助您檢查可用性、管理活動並優化您的排程。',
        url=f'http://{host}:{port}/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=skills,
    )

    # 建立代理 (Agent) 執行器
    agent_executor = create_foundry_agent_executor(agent_card)

    # 建立請求處理常式
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    # 建立 A2A 應用程式
    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    # 取得路由
    routes = a2a_app.routes()

    # 新增健康檢查端點
    async def health_check(request: Request) -> PlainTextResponse:
        return PlainTextResponse('AI Foundry 日曆代理 (Agent) 正在執行！')

    routes.append(Route(path='/health', methods=['GET'], endpoint=health_check))

    # 建立 Starlette 應用程式
    app = Starlette(routes=routes)

    # 記錄啟動資訊
    logger.info(f'正在 {host}:{port} 上啟動 AI Foundry 日曆代理 (Agent)')
    logger.info(f'代理卡 (Agent card)：{agent_card.name}')
    logger.info(f'技能：{[skill.name for skill in skills]}')
    logger.info(f'健康檢查端點位於：http://{host}:{port}/health')

    # 執行伺服器
    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    main()
