# type:ignore
import asyncio
import json
import os

from contextlib import asynccontextmanager

import click

from fastmcp.utilities.logging import get_logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult, ReadResourceResult


logger = get_logger(__name__)

env = {
    'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
}


@asynccontextmanager
async def init_session(host, port, transport):
    """根據指定的傳輸方式初始化和管理 MCP ClientSession。

    這個非同步內容管理器使用伺服器發送事件 (SSE) 或標準 I/O (STDIO) 傳輸來建立與 MCP 伺服器的連接。
    它處理連接的設定和拆卸，並產生一個準備好進行通訊的活動 `ClientSession` 物件。

    Args:
        host: MCP 伺服器的主機名稱或 IP 位址（用於 SSE）。
        port: MCP 伺服器的埠號（用於 SSE）。
        transport: 要使用的通訊傳輸方式（'sse' 或 'stdio'）。

    Yields:
        ClientSession: 一個已初始化且可供使用的 MCP 客戶端會話。

    Raises:
        ValueError: 如果提供了不支援的傳輸類型（隱含地，
                    因為它不符合 'sse' 或 'stdio'）。
        Exception: 在客戶端初始化或會話設定期間可能發生的其他例外情況。
    """
    if transport == 'sse':
        url = f'http://{host}:{port}/sse'
        async with sse_client(url) as (read_stream, write_stream):
            async with ClientSession(
                read_stream=read_stream, write_stream=write_stream
            ) as session:
                logger.debug('SSE ClientSession 已建立，正在初始化...')
                await session.initialize()
                logger.info('SSE ClientSession 初始化成功。')
                yield session
    elif transport == 'stdio':
        if not os.getenv('GOOGLE_API_KEY'):
            logger.error('未設定 GOOGLE_API_KEY')
            raise ValueError('未設定 GOOGLE_API_KEY')
        stdio_params = StdioServerParameters(
            command='uv',
            args=['run', 'a2a-mcp'],
            env=env,
        )
        async with stdio_client(stdio_params) as (read_stream, write_stream):
            async with ClientSession(
                read_stream=read_stream,
                write_stream=write_stream,
            ) as session:
                logger.debug('STDIO ClientSession 已建立，正在初始化...')
                await session.initialize()
                logger.info('STDIO ClientSession 初始化成功。')
                yield session
    else:
        logger.error(f'不支援的傳輸類型：{transport}')
        raise ValueError(
            f"不支援的傳輸類型：{transport}。必須是 'sse' 或 'stdio'。"
        )


async def find_agent(session: ClientSession, query) -> CallToolResult:
    """在連接的 MCP 伺服器上呼叫 'find_agent' 工具。

    Args:
        session: 活動的 ClientSession。
        query: 要發送到 'find_agent' 工具的自然語言查詢。

    Returns:
        工具呼叫的結果。
    """
    logger.info(f"正在使用查詢呼叫 'find_agent' 工具：'{query[:50]}...'")
    return await session.call_tool(
        name='find_agent',
        arguments={
            'query': query,
        },
    )


async def find_resource(session: ClientSession, resource) -> ReadResourceResult:
    """從連接的 MCP 伺服器讀取資源。

    Args:
        session: 活動的 ClientSession。
        resource: 要讀取的資源的 URI（例如，'resource://agent_cards/list'）。

    Returns:
        資源讀取操作的結果。
    """
    logger.info(f'正在讀取資源：{resource}')
    return await session.read_resource(resource)


async def search_flights(session: ClientSession) -> CallToolResult:
    """在連接的 MCP 伺服器上呼叫 'search_flights' 工具。

    Args:
        session: 活動的 ClientSession。
        query: 要發送到 'search_flights' 工具的自然語言查詢。

    Returns:
        工具呼叫的結果。
    """
    # TODO: 實作待定
    logger.info("正在呼叫 'search_flights' 工具'")
    return await session.call_tool(
        name='search_flights',
        arguments={
            'departure_airport': 'SFO',
            'arrival_airport': 'LHR',
            'start_date': '2025-06-03',
            'end_date': '2025-06-09',
        },
    )


async def search_hotels(session: ClientSession) -> CallToolResult:
    """在連接的 MCP 伺服器上呼叫 'search_hotels' 工具。

    Args:
        session: 活動的 ClientSession。
        query: 要發送到 'search_hotels' 工具的自然語言查詢。

    Returns:
        工具呼叫的結果。
    """
    # TODO: 實作待定
    logger.info("正在呼叫 'search_hotels' 工具'")
    return await session.call_tool(
        name='search_hotels',
        arguments={
            'location': 'A Suite room in St Pancras Square in London',
            'check_in_date': '2025-06-03',
            'check_out_date': '2025-06-09',
        },
    )


async def query_db(session: ClientSession) -> CallToolResult:
    """在連接的 MCP 伺服器上呼叫 'query' 工具。

    Args:
        session: 活動的 ClientSession。
        query: 要發送到 'query_db' 工具的自然語言查詢。

    Returns:
        工具呼叫的結果。
    """
    logger.info("正在呼叫 'query_db' 工具'")
    return await session.call_tool(
        name='query_travel_data',
        arguments={
            'query': "SELECT id, name, city, hotel_type, room_type, price_per_night FROM hotels WHERE city='London'",
        },
    )


# 測試工具
async def main(host, port, transport, query, resource, tool):
    """主非同步函式，用於連接到 MCP 伺服器並執行命令。

    用於本機測試。

    Args:
        host: 伺服器主機名稱。
        port: 伺服器埠號。
        transport: 連接傳輸方式（'sse' 或 'stdio'）。
        query: 'find_agent' 工具的選用查詢字串。
        resource: 要讀取的選用資源 URI。
        tool: 要執行的選用工具名稱。有效選項包括：
            'search_flights'、'search_hotels' 或 'query_db'。
    """
    logger.info('正在啟動客戶端以連接到 MCP')
    async with init_session(host, port, transport) as session:
        if query:
            result = await find_agent(session, query)
            data = json.loads(result.content[0].text)
            logger.info(json.dumps(data, indent=2))
        if resource:
            result = await find_resource(session, resource)
            logger.info(result)
            data = json.loads(result.contents[0].text)
            logger.info(json.dumps(data, indent=2))
        if tool:
            if tool == 'search_flights':
                results = await search_flights(session)
                logger.info(results.model_dump())
            if tool == 'search_hotels':
                result = await search_hotels(session)
                data = json.loads(result.content[0].text)
                logger.info(json.dumps(data, indent=2))
            if tool == 'query_db':
                result = await query_db(session)
                logger.info(result)
                data = json.loads(result.content[0].text)
                logger.info(json.dumps(data, indent=2))


# 命令列測試器
@click.command()
@click.option('--host', default='localhost', help='SSE 主機')
@click.option('--port', default='10100', help='SSE 埠號')
@click.option('--transport', default='stdio', help='MCP 傳輸方式')
@click.option('--find_agent', help='用以尋找代理的查詢')
@click.option('--resource', help='要定位的資源的 URI')
@click.option('--tool_name', type=click.Choice(['search_flights', 'search_hotels', 'query_db']),
              help='要執行的工具：search_flights、search_hotels 或 query_db')
def cli(host, port, transport, find_agent, resource, tool_name):
    """一個用於與代理卡 MCP 伺服器互動的命令列客戶端。"""
    asyncio.run(main(host, port, transport, find_agent, resource, tool_name))


if __name__ == '__main__':
    cli()
