import asyncio
import functools
import logging
import os

import click
import sqlalchemy
import sqlalchemy.ext.asyncio
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import DatabaseTaskStore, InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent import root_agent as calendar_agent
from agent_executor import ADKAgentExecutor
from dotenv import load_dotenv
from google.cloud.alloydbconnector import AsyncConnector
from starlette.applications import Starlette


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """缺少 API 金鑰的例外情況。"""


async def create_sqlalchemy_engine(
    inst_uri: str,
    user: str,
    password: str,
    db: str,
    refresh_strategy: str = 'background',
) -> tuple[sqlalchemy.ext.asyncio.engine.AsyncEngine, AsyncConnector]:
    """為 AlloyDB 執行個體建立一個連線池，並傳回該池和連接器。
    呼叫者負責關閉連線池和連接器。

    Args:
        instance_uri (str):
            執行個體 URI 指定相對於專案、
            區域和叢集的執行個體。例如：
            "projects/my-project/locations/us-central1/clusters/my-cluster/instances/my-instance"
        user (str):
            資料庫使用者名稱，例如 postgres
        password (str):
            資料庫使用者的密碼，例如 secret-password
        db (str):
            資料庫的名稱，例如 mydb
        refresh_strategy (Optional[str]):
            AlloyDB 連接器的重新整理策略。可以是 "lazy"
            或 "background" 其中之一。對於無伺服器環境，請使用 "lazy" 以避免
            因 CPU 節流而導致的錯誤。
    """
    connector = AsyncConnector(refresh_strategy=refresh_strategy)

    # create SQLAlchemy connection pool
    engine = sqlalchemy.ext.asyncio.create_async_engine(
        'postgresql+asyncpg://',
        async_creator=lambda: connector.connect(
            inst_uri,
            'asyncpg',
            user=user,
            password=password,
            db=db,
            ip_type='PUBLIC',
        ),
        execution_options={'isolation_level': 'AUTOCOMMIT'},
    )
    return engine, connector


def make_sync(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@click.command()
@click.option('--host', default='localhost')
@click.option('--port', default=10002)
@make_sync
async def main(host, port):
    agent_card = AgentCard(
        name=calendar_agent.name,
        description=calendar_agent.description,
        version='1.0.0',
        url=os.environ['APP_URL'],
        default_input_modes=['text', 'text/plain'],
        default_output_modes=['text', 'text/plain'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[
            AgentSkill(
                id='add_calendar_event',
                name='新增日曆活動',
                description='建立一個新的日曆活動。',
                tags=['calendar', 'event', 'create'],
                examples=[
                    '為我明天上午 10 點的會議新增一個日曆活動。',
                ],
            )
        ],
    )

    use_alloy_db_str = os.getenv('USE_ALLOY_DB', 'False')
    if use_alloy_db_str.lower() == 'true':
        DB_INSTANCE = os.environ['DB_INSTANCE']
        DB_NAME = os.environ['DB_NAME']
        DB_USER = os.environ['DB_USER']
        DB_PASS = os.environ['DB_PASS']

        engine, connector = await create_sqlalchemy_engine(
            DB_INSTANCE,
            DB_USER,
            DB_PASS,
            DB_NAME,
        )
        task_store = DatabaseTaskStore(engine)
    else:
        task_store = InMemoryTaskStore()

    request_handler = DefaultRequestHandler(
        agent_executor=ADKAgentExecutor(
            agent=calendar_agent,
        ),
        task_store=task_store,
    )

    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )
    routes = a2a_app.routes()
    app = Starlette(
        routes=routes,
        middleware=[],
    )

    config = uvicorn.Config(app, host=host, port=port, log_level='info')
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == '__main__':
    main()
