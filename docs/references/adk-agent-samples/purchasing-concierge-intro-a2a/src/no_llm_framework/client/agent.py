import asyncio
import json
import re

from collections.abc import Callable, Generator
from pathlib import Path
from typing import Literal
from uuid import uuid4

import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendStreamingMessageRequest,
    SendStreamingMessageSuccessResponse,
    TaskStatusUpdateEvent,
    TextPart,
)
from google import genai
from jinja2 import Template

from no_llm_framework.client.constant import GOOGLE_API_KEY


dir_path = Path(__file__).parent

with Path(dir_path / 'decide.jinja').open('r') as f:
    decide_template = Template(f.read())

with Path(dir_path / 'agents.jinja').open('r') as f:
    agents_template = Template(f.read())

with Path(dir_path / 'agent_answer.jinja').open('r') as f:
    agent_answer_template = Template(f.read())


def stream_llm(prompt: str) -> Generator[str]:
    """串流 LLM 回應。

    參數：
        prompt (str): 要傳送給 LLM 的提示。

    回傳：
        Generator[str, None, None]: LLM 回應的產生器。
    """
    client = genai.Client(vertexai=False, api_key=GOOGLE_API_KEY)
    for chunk in client.models.generate_content_stream(
        model='gemini-2.5-flash-lite',
        contents=prompt,
    ):
        yield chunk.text


class Agent:
    """用於以不同模式與 Google Gemini LLM 互動的代理。"""

    def __init__(
        self,
        mode: Literal['complete', 'stream'] = 'stream',
        token_stream_callback: Callable[[str], None] | None = None,
        agent_urls: list[str] | None = None,
        agent_prompt: str | None = None,
    ):
        self.mode = mode
        self.token_stream_callback = token_stream_callback
        self.agent_urls = agent_urls
        self.agents_registry: dict[str, AgentCard] = {}

    async def get_agents(self) -> tuple[dict[str, AgentCard], str]:
        """從所有代理 URL 擷取代理卡並呈現代理提示。

        回傳：
            tuple[dict[str, AgentCard], str]: 一個將代理名稱對應到 AgentCard 物件的字典，以及呈現的代理提示字串。
        """
        async with httpx.AsyncClient() as httpx_client:
            card_resolvers = [
                A2ACardResolver(httpx_client, url) for url in self.agent_urls
            ]
            agent_cards = await asyncio.gather(
                *[
                    card_resolver.get_agent_card()
                    for card_resolver in card_resolvers
                ]
            )
            agents_registry = {
                agent_card.name: agent_card for agent_card in agent_cards
            }
            agent_prompt = agents_template.render(agent_cards=agent_cards)
            return agents_registry, agent_prompt

    def call_llm(self, prompt: str) -> str:
        """使用給定的提示呼叫 LLM，並以字串或產生器的形式回傳回應。

        參數：
            prompt (str): 要傳送給 LLM 的提示。

        回傳：
            str or Generator[str]: 根據模式，LLM 的回應為字串或產生器。
        """
        if self.mode == 'complete':
            return stream_llm(prompt)

        result = ''
        for chunk in stream_llm(prompt):
            result += chunk
        return result

    async def decide(
        self,
        question: str,
        agents_prompt: str,
        called_agents: list[dict] | None = None,
    ) -> Generator[str, None]:
        """決定使用哪個代理來回答問題。

        參數：
            question (str): 要回答的問題。
            agents_prompt (str): 描述可用代理的提示。
            called_agents (list[dict] | None): 先前呼叫的代理及其答案。

        回傳：
            Generator[str, None]: LLM 回應的字串產生器。
        """
        if called_agents:
            call_agent_prompt = agent_answer_template.render(
                called_agents=called_agents
            )
        else:
            call_agent_prompt = ''
        prompt = decide_template.render(
            question=question,
            agent_prompt=agents_prompt,
            call_agent_prompt=call_agent_prompt,
        )
        return self.call_llm(prompt)

    def extract_agents(self, response: str) -> list[dict]:
        """從回應中擷取代理。

        參數：
            response (str): 來自 LLM 的回應。
        """
        pattern = r'```json\n(.*?)\n```'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return []

    async def send_message_to_an_agent(
        self, agent_card: AgentCard, message: str
    ):
        """向特定代理發送訊息並產生串流回應。

        參數：
            agent_card (AgentCard): 要發送訊息的目標代理。
            message (str): 要發送的訊息。

        產生：
            str: 來自代理的串流回應。
        """
        async with httpx.AsyncClient() as httpx_client:
            client = A2AClient(httpx_client, agent_card=agent_card)
            message = MessageSendParams(
                message=Message(
                    role=Role.user,
                    parts=[Part(TextPart(text=message))],
                    message_id=uuid4().hex,
                    task_id=uuid4().hex,
                )
            )

            streaming_request = SendStreamingMessageRequest(
                id=str(uuid4().hex), params=message
            )
            async for chunk in client.send_message_streaming(streaming_request):
                if isinstance(
                    chunk.root, SendStreamingMessageSuccessResponse
                ) and isinstance(chunk.root.result, TaskStatusUpdateEvent):
                    message = chunk.root.result.status.message
                    if message:
                        yield message.parts[0].root.text

    async def stream(self, question: str):
        """串流回答問題的過程，可能涉及多個代理。

        參數：
            question (str): 要回答的問題。

        產生：
            str: 串流輸出，包括代理回應和中間步驟。
        """
        agent_answers: list[dict] = []
        for _ in range(3):
            agents_registry, agent_prompt = await self.get_agents()
            response = ''
            for chunk in await self.decide(
                question, agent_prompt, agent_answers
            ):
                response += chunk
                if self.token_stream_callback:
                    self.token_stream_callback(chunk)
                yield chunk

            agents = self.extract_agents(response)
            if agents:
                for agent in agents:
                    agent_response = ''
                    agent_card = agents_registry[agent['name']]
                    yield f'<Agent name="{agent["name"]}">\n'
                    async for chunk in self.send_message_to_an_agent(
                        agent_card, agent['prompt']
                    ):
                        agent_response += chunk
                        if self.token_stream_callback:
                            self.token_stream_callback(chunk)
                        yield chunk
                    yield '</Agent>\n'
                    match = re.search(
                        r'<Answer>(.*?)</Answer>', agent_response, re.DOTALL
                    )
                    answer = match.group(1).strip() if match else agent_response
                    agent_answers.append(
                        {
                            'name': agent['name'],
                            'prompt': agent['prompt'],
                            'answer': answer,
                        }
                    )
            else:
                return


if __name__ == '__main__':
    import asyncio

    import colorama

    async def main():
        """執行 A2A Repo Agent 客戶端的主函式。"""
        agent = Agent(
            mode='stream',
            token_stream_callback=None,
            agent_urls=['http://localhost:9999/'],
        )

        async for chunk in agent.stream('What is A2A protocol?'):
            if chunk.startswith('<Agent name="'):
                print(colorama.Fore.CYAN + chunk, end='', flush=True)
            elif chunk.startswith('</Agent>'):
                print(colorama.Fore.RESET + chunk, end='', flush=True)
            else:
                print(chunk, end='', flush=True)

    asyncio.run(main())
