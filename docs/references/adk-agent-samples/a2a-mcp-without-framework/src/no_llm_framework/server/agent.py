import asyncio
import json
import re

from collections.abc import AsyncGenerator, Callable, Generator
from pathlib import Path
from typing import Literal

from google import genai
from jinja2 import Template
from mcp.types import CallToolResult

from no_llm_framework.server.constant import GOOGLE_API_KEY
from no_llm_framework.server.mcp import call_mcp_tool, get_mcp_tool_prompt


dir_path = Path(__file__).parent

with Path(dir_path / 'decide.jinja').open('r') as f:
    decide_template = Template(f.read())

with Path(dir_path / 'tool.jinja').open('r') as f:
    tool_template = Template(f.read())

with Path(dir_path / 'called_tools_history.jinja').open('r') as f:
    called_tools_history_template = Template(f.read())


def stream_llm(prompt: str) -> Generator[str, None]:
    """串流 LLM 回應。

    Args:
        prompt (str): 要傳送至 LLM 的提示。

    Returns:
        Generator[str, None, None]: LLM 回應的生成器。
    """
    client = genai.Client(vertexai=False, api_key=GOOGLE_API_KEY)
    for chunk in client.models.generate_content_stream(
        model='gemini-2.5-flash-lite',
        contents=prompt,
    ):
        yield chunk.text


class Agent:
    """用於以不同模式與 Google Gemini LLM 互動的代理 (Agent)。"""

    def __init__(
        self,
        mode: Literal['complete', 'stream'] = 'stream',
        token_stream_callback: Callable[[str], None] | None = None,
        mcp_url: str | None = None,
    ):
        self.mode = mode
        self.token_stream_callback = token_stream_callback
        self.mcp_url = mcp_url

    def call_llm(self, prompt: str) -> Generator[str, None]:
        """使用給定的提示呼叫 LLM，並傳回一個回應生成器。

        Args:
            prompt (str): 要傳送至 LLM 的提示。

        Returns:
            Generator[str, None]: 一個產生 LLM 回應的生成器。
        """
        return stream_llm(prompt)

    async def decide(
        self, question: str, called_tools: list[dict] | None = None
    ) -> Generator[str, None]:
        """決定使用哪種工具來回答問題。

        Args:
            question (str): 要回答的問題。
            called_tools (list[dict]): 已被呼叫的工具。
        """
        if self.mcp_url is None:
            return self.call_llm(question)
        tool_prompt = await get_mcp_tool_prompt(self.mcp_url)
        if called_tools:
            called_tools_prompt = called_tools_history_template.render(
                called_tools=called_tools
            )
        else:
            called_tools_prompt = ''

        prompt = decide_template.render(
            question=question,
            tool_prompt=tool_prompt,
            called_tools=called_tools_prompt,
        )
        return self.call_llm(prompt)

    def extract_tools(self, response: str) -> list[dict]:
        """從回應中提取工具。

        Args:
            response (str): 來自 LLM 的回應。
        """
        pattern = r'```json\n(.*?)\n```'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return []

    async def call_tool(self, tools: list[dict]) -> list[CallToolResult]:
        """呼叫工具。

        Args:
            tools (list[dict]): 要呼叫的工具。
        """
        return await asyncio.gather(
            *[
                call_mcp_tool(self.mcp_url, tool['name'], tool['arguments'])
                for tool in tools
            ]
        )

    async def stream(self, question: str) -> AsyncGenerator[str]:
        """串流回答問題的過程，可能涉及工具呼叫。

        Args:
            question (str): 要回答的問題。

        Yields:
            dict: 串流輸出，包括中間步驟和最終結果。
        """
        called_tools = []
        for i in range(10):
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': f'Step {i}',
            }

            response = ''
            for chunk in await self.decide(question, called_tools):
                response += chunk
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': chunk,
                }
            tools = self.extract_tools(response)
            if not tools:
                break
            results = await self.call_tool(tools)

            called_tools += [
                {
                    'tool': tool['name'],
                    'arguments': tool['arguments'],
                    'isError': result.isError,
                    'result': result.content[0].text,
                }
                for tool, result in zip(tools, results, strict=True)
            ]
            called_tools_history = called_tools_history_template.render(
                called_tools=called_tools, question=question
            )
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': called_tools_history,
            }

        yield {
            'is_task_complete': True,
            'require_user_input': False,
            'content': 'Task completed',
        }


if __name__ == '__main__':
    agent = Agent(
        token_stream_callback=lambda token: print(token, end='', flush=True),
        mcp_url='https://gitmcp.io/google/A2A',
    )

    async def main():
        """主函式。"""
        async for chunk in agent.stream('What is A2A Protocol?'):
            print(chunk)

    asyncio.run(main())
