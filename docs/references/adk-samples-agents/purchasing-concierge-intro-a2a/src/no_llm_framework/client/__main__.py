import asyncio
from typing import Literal


import asyncclick as click
import colorama
from no_llm_framework.client.agent import Agent


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=9999)
@click.option('--mode', 'mode', default='streaming')
@click.option('--question', 'question', required=True)
async def a_main(
    host: str,
    port: int,
    mode: Literal['completion', 'streaming'],
    question: str,
):
    """執行 A2A Repo Agent 客戶端的主函式。

    參數：
        host (str): 執行伺服器的主機位址。
        port (int): 執行伺服器的埠號。
        mode (Literal['completion', 'streaming']): 執行伺服器的模式。
        question (str): 要詢問代理的問題。
    """  # noqa: E501
    agent = Agent(
        mode='stream',
        token_stream_callback=None,
        agent_urls=[f'http://{host}:{port}/'],
    )
    async for chunk in agent.stream(question):
        if chunk.startswith('<Agent name="'):
            print(colorama.Fore.CYAN + chunk, end='', flush=True)
        elif chunk.startswith('</Agent>'):
            print(colorama.Fore.RESET + chunk, end='', flush=True)
        else:
            print(chunk, end='', flush=True)


def main() -> None:
    """執行 A2A Repo Agent 客戶端的主函式。"""
    asyncio.run(a_main())


if __name__ == '__main__':
    main()
