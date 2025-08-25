# pylint: disable=logging-fstring-interpolation

import asyncio
import os
import sys

from contextlib import asynccontextmanager
from typing import Any

import click
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent_executor import (
    AirbnbAgentExecutor,
)
from airbnb_agent import (
    AirbnbAgent,
)
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv(override=True)

SERVER_CONFIGS = {
    'bnb': {
        'command': 'npx',
        'args': ['-y', '@openbnb/mcp-server-airbnb', '--ignore-robots-txt'],
        'transport': 'stdio',
    },
}

app_context: dict[str, Any] = {}


DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 10002
DEFAULT_LOG_LEVEL = 'info'


@asynccontextmanager
async def app_lifespan(context: dict[str, Any]):
    """管理共享資源（如 MCP 客戶端和工具）的生命週期。"""
    print('生命週期：正在初始化 MCP 客戶端和工具...')

    # 此變數將持有 MultiServerMCPClient 實例
    mcp_client_instance: MultiServerMCPClient | None = None

    try:
        # 遵循 MultiServerMCPClient 初始化錯誤訊息中的選項 1：
        # 1. client = MultiServerMCPClient(...)
        mcp_client_instance = MultiServerMCPClient(SERVER_CONFIGS)
        mcp_tools = await mcp_client_instance.get_tools()
        context['mcp_tools'] = mcp_tools

        tool_count = len(mcp_tools) if mcp_tools else 0
        print(
            f'生命週期：MCP 工具預載成功（找到 {tool_count} 個工具）。'
        )
        yield  # 應用程式在此處執行
    except Exception as e:
        print(f'生命週期：初始化期間發生錯誤：{e}', file=sys.stderr)
        # 如果發生例外，mcp_client_instance 可能存在且需要清理。
        # 下方的 finally 區塊將處理此問題。
        raise
    finally:
        print('生命週期：正在關閉 MCP 客戶端...')
        if (
            mcp_client_instance
        ):  # 檢查是否已建立 MultiServerMCPClient 實例
            # 原始程式碼在 MultiServerMCPClient 實例上呼叫 __aexit__
            # (即 mcp_client_manager)。我們假設這仍然是正確的清理方法。
            if hasattr(mcp_client_instance, '__aexit__'):
                try:
                    print(
                        f'生命週期：正在 {type(mcp_client_instance).__name__} 實例上呼叫 __aexit__...'
                    )
                    await mcp_client_instance.__aexit__(None, None, None)
                    print(
                        '生命週期：已透過 __aexit__ 釋放 MCP 客戶端資源。'
                    )
                except Exception as e:
                    print(
                        f'生命週期：MCP 客戶端 __aexit__ 期間發生錯誤：{e}',
                        file=sys.stderr,
                    )
            else:
                # 如果只有上下文管理器用法變更，這將是意料之外的。
                # 記錄錯誤，因為這可能導致資源洩漏。
                print(
                    f'生命週期：嚴重錯誤 - {type(mcp_client_instance).__name__} 實例沒有用於清理的 __aexit__ 方法。可能發生資源洩漏。',
                    file=sys.stderr,
                )
        else:
            # 這種情況表示 MultiServerMCPClient() 建構函式可能失敗或未被執行。
            print(
                '生命週期：未建立 MCP 客戶端實例，不嘗試透過 __aexit__ 關閉。'
            )

        # 如同原始程式碼中一樣，清除應用程式上下文。
        print('生命週期：正在清除應用程式上下文。')
        context.clear()


def main(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    log_level: str = DEFAULT_LOG_LEVEL,
):
    """啟動 Airbnb 代理 (Agent) 伺服器的命令列介面。"""
    # 驗證是否已設定 API 金鑰。
    # 如果使用 Vertex AI API，則非必要。
    if os.getenv('GOOGLE_GENAI_USE_VERTEXAI') != 'TRUE' and not os.getenv(
        'GOOGLE_API_KEY'
    ):
        raise ValueError(
            'GOOGLE_API_KEY 環境變數未設定且 '
            'GOOGLE_GENAI_USE_VERTEXAI 不為 TRUE。'
        )

    async def run_server_async():
        async with app_lifespan(app_context):
            if not app_context.get('mcp_tools'):
                print(
                    '警告：未載入 MCP 工具。代理 (Agent) 可能無法正常運作。',
                    file=sys.stderr,
                )
                # 根據需求，您可以在此處 sys.exit(1)

            # 使用預載的工具初始化 AirbnbAgentExecutor
            airbnb_agent_executor = AirbnbAgentExecutor(
                mcp_tools=app_context.get('mcp_tools', [])
            )

            request_handler = DefaultRequestHandler(
                agent_executor=airbnb_agent_executor,
                task_store=InMemoryTaskStore(),
            )

            # 建立 A2AServer 實例
            a2a_server = A2AStarletteApplication(
                agent_card=get_agent_card(host, port),
                http_handler=request_handler,
            )

            # 從 A2AServer 實例取得 ASGI 應用程式
            asgi_app = a2a_server.build()

            config = uvicorn.Config(
                app=asgi_app,
                host=host,
                port=port,
                log_level=log_level.lower(),
                lifespan='auto',
            )

            uvicorn_server = uvicorn.Server(config)

            print(
                f'正在 http://{host}:{port} 啟動 Uvicorn 伺服器，日誌級別為 {log_level}...'
            )
            try:
                await uvicorn_server.serve()
            except KeyboardInterrupt:
                print('已請求伺服器關閉 (鍵盤中斷)。')
            finally:
                print('Uvicorn 伺服器已停止。')
                # app_lifespan 的 finally 區塊會處理 mcp_client 的關閉

    try:
        asyncio.run(run_server_async())
    except RuntimeError as e:
        if '無法從執行中的事件迴圈呼叫' in str(e):
            print(
                '嚴重錯誤：嘗試巢狀化 asyncio.run()。這應該已被阻止。',
                file=sys.stderr,
            )
        else:
            print(f'main 中發生執行時錯誤：{e}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'main 中發生未預期的錯誤：{e}', file=sys.stderr)
        sys.exit(1)


def get_agent_card(host: str, port: int):
    """傳回貨幣代理 (Currency Agent) 的代理卡 (Agent Card)。"""
    capabilities = AgentCapabilities(streaming=True, push_notifications=True)
    skill = AgentSkill(
        id='airbnb_search',
        name='搜尋 airbnb 住宿',
        description='協助使用 airbnb 搜尋住宿',
        tags=['airbnb accommodation'],
        examples=[
            '請在加州洛杉磯尋找一間房間，入住日期為 2025 年 4 月 15 日，退房日期為 4 月 18 日，2 位成人'
        ],
    )
    app_url = os.environ.get('APP_URL', f'http://{host}:{port}')

    return AgentCard(
        name='Airbnb 代理 (Agent)',
        description='協助搜尋住宿',
        url=app_url,
        version='1.0.0',
        default_input_modes=AirbnbAgent.SUPPORTED_CONTENT_TYPES,
        default_output_modes=AirbnbAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill],
    )


@click.command()
@click.option(
    '--host',
    'host',
    default=DEFAULT_HOST,
    help='要繫結伺服器的主機名稱。',
)
@click.option(
    '--port',
    'port',
    default=DEFAULT_PORT,
    type=int,
    help='要繫結伺服器的通訊埠。',
)
@click.option(
    '--log-level',
    'log_level',
    default=DEFAULT_LOG_LEVEL,
    help='Uvicorn 日誌級別。',
)
def cli(host: str, port: int, log_level: str):
    main(host, port, log_level)


if __name__ == '__main__':
    main()
