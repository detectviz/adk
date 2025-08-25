import asyncio
from pathlib import Path

from jinja2 import Template
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.types import CallToolResult, TextContent

dir_path = Path(__file__).parent

with Path(dir_path / 'tool.jinja').open('r') as f:
    template = Template(f.read())


async def get_mcp_tool_prompt(url: str) -> str:
    """為給定的 URL 取得 MCP 工具提示。

    參數：
        url (str): MCP 工具的 URL。

    回傳：
        str: MCP 工具提示。
    """
    async with (
        sse_client(url) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()

        resources = await session.list_tools()
        return template.render(tools=resources.tools)


async def call_mcp_tool(
    url: str, tool_name: str, arguments: dict | None = None
) -> CallToolResult:
    """使用給定的 URL 和工具名稱呼叫 MCP 工具。

    參數：
        url (str): MCP 工具的 URL。
        tool_name (str): 要呼叫的工具名稱。
        arguments (dict | None, optional): 要傳遞給工具的參數。預設為 None。

    回傳：
        CallToolResult: 工具呼叫的結果。
    """  # noqa: E501
    async with (
        sse_client(
            url=url,
        ) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()

        return await session.call_tool(tool_name, arguments=arguments)


if __name__ == '__main__':
    print(asyncio.run(get_mcp_tool_prompt('https://gitmcp.io/google/A2A')))
    result = asyncio.run(
        call_mcp_tool('https://gitmcp.io/google/A2A', 'fetch_A2A_documentation')
    )
    for content in result.content:
        if isinstance(content, TextContent):
            print(content.text)
