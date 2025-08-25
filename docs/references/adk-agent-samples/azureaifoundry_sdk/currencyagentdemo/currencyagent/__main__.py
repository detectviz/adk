import logging

import click
import httpx

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import CurrencyAgentExecutor
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


@click.command()
@click.option('--host', default='localhost')
@click.option('--port', default=47128)  # Updated to a less commonly used port
def main(host, port):
    """使用 A2A 啟動 Semantic Kernel Agent 伺服器。"""
    logger.info(f'正在 {host}:{port} 上啟動貨幣代理 (Currency Agent) 伺服器')

    httpx_client = httpx.AsyncClient()
    agent_card = get_agent_card(host, port)

    # 使用適當的設定建立任務儲存庫
    task_store = InMemoryTaskStore()
    logger.info('已建立任務儲存庫')

    # 使用適當的設定建立執行器和請求處理常式
    executor = CurrencyAgentExecutor()
    logger.info('已建立代理 (Agent) 執行器')

    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=task_store,
        push_notifier=InMemoryPushNotifier(httpx_client),
    )
    logger.info('已建立請求處理常式')

    # 使用適當的 JSON-RPC 方法設定伺服器
    server = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )
    logger.info('已建立 A2A 伺服器應用程式')

    # 新增用於偵錯請求的中介軟體
    app = server.build()

    @app.middleware('http')
    async def log_requests(request, call_next):
        body = await request.body()
        logger.info(f'傳入請求：{request.method} {request.url}')
        logger.info(
            f'請求主體：{body.decode("utf-8") if body else "空"}'
        )
        response = await call_next(request)
        return response

    import uvicorn

    logger.info(f'正在 http://{host}:{port} 啟動 uvicorn 伺服器')
    uvicorn.run(app, host=host, port=port)


def get_agent_card(host: str, port: int):
    """傳回 Azure Foundry Agent Service 的代理卡 (Agent Card)。"""
    # 建置代理卡 (agent card)
    capabilities = AgentCapabilities(streaming=True)
    skill_trip_planning = AgentSkill(
        id='currency_exchange_agent',
        name='貨幣兌換代理 (Agent)',
        description=(
            '使用 Frankfurter API 的即時匯率處理貨幣兌換查詢和換算。'
            '提供準確的貨幣換算率和與旅遊相關的財務建議。'
        ),
        tags=['貨幣', '兌換', '換算', '旅遊', '金融'],
        examples=[
            '1 美元等於多少歐元？',
            '目前美元兌日圓的匯率是多少？',
            '將 100 英鎊換算成美元',
        ],
    )

    agent_card = AgentCard(
        name='貨幣兌換代理 (Agent)',
        description=(
            '一個專門的貨幣兌換代理 (Agent)，為旅行者和國際交易提供即時貨幣換算率和財務資訊。'
        ),
        url=f'http://{host}:{port}/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=capabilities,
        skills=[skill_trip_planning],
    )

    return agent_card


if __name__ == '__main__':
    main()
