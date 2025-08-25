import asyncio
import json
import os

from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

import asyncclick as click
import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    GetTaskRequest,
    Message,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
    Task,
    TaskArtifactUpdateEvent,
    TaskQueryParams,
    TaskState,
    TaskStatusUpdateEvent,
    TextPart,
)
from auth0.authentication.get_token import GetToken
from dotenv import load_dotenv


load_dotenv()
access_token = None


class AgentAuth(httpx.Auth):
    """自訂 httpx 的驗證類別，以注入代理 (Agent) 所需的存取權杖。"""

    def __init__(self, agent_card: AgentCard):
        self.agent_card = agent_card

    def auth_flow(self, request):
        global access_token
        auth = self.agent_card.authentication

        # 如果不使用 oauth2 或缺少憑證詳細資訊，則跳過
        if not (
            any(scheme.lower() == 'oauth2' for scheme in auth.schemes)
            and auth.credentials
        ):
            yield request
            return

        if not access_token:
            token_url = json.loads(auth.credentials)['tokenUrl']
            print(f'\n正在從 {token_url} 擷取代理 (Agent) 存取權杖...')
            get_token = GetToken(
                domain=urlparse(token_url).hostname,
                client_id=os.getenv('A2A_CLIENT_AUTH0_CLIENT_ID'),
                client_secret=os.getenv('A2A_CLIENT_AUTH0_CLIENT_SECRET'),
            )
            access_token = get_token.client_credentials(
                os.getenv('HR_AGENT_AUTH0_AUDIENCE')
            )['access_token']
            print('完成。\n')

        request.headers['Authorization'] = f'Bearer {access_token}'
        yield request


@click.command()
@click.option('--agent', default='http://localhost:10050')
@click.option('--context_id')
@click.option('--history', default=False, is_flag=True)
@click.option('--debug', default=False, is_flag=True)
async def cli(agent: str, context_id: str | None, history: bool, debug: bool):
    async with httpx.AsyncClient() as httpx_client:
        agent_card = await (
            A2ACardResolver(
                httpx_client=httpx_client,
                base_url=agent,
            )
        ).get_agent_card()

        print('======= 代理 (Agent) 名片 ========')
        print(agent_card.model_dump_json(exclude_none=True, indent=2))

        httpx_client.auth = AgentAuth(agent_card)

        client = A2AClient(
            httpx_client=httpx_client,
            agent_card=agent_card,
        )

        if not context_id:
            context_id = uuid4().hex

        continue_loop = True
        streaming = agent_card.capabilities.streaming

        while continue_loop:
            task_id = uuid4().hex
            print('=========  開始新任務 ======== ')
            continue_loop = await complete_task(
                client,
                streaming,
                task_id,
                context_id,
                debug,
            )

            if history and continue_loop:
                print('========= 歷史記錄 ======== ')
                get_task_response = await client.get_task(
                    GetTaskRequest(
                        id=str(uuid4()),
                        params=TaskQueryParams(id=task_id, history_length=10),
                    )
                )
                print(
                    get_task_response.root.model_dump_json(
                        include={'result': {'history': True}}
                    )
                )


def create_send_params(
    text: str, task_id: str | None = None, context_id: str | None = None
) -> MessageSendParams:
    """用於建立傳送任務之承載的輔助函式。"""
    send_params: dict[str, Any] = {
        'message': {
            'role': 'user',
            'parts': [{'type': 'text', 'text': text}],
            'messageId': uuid4().hex,
        },
        'configuration': {
            'acceptedOutputModes': ['text'],
        },
    }

    if task_id:
        send_params['message']['taskId'] = task_id

    if context_id:
        send_params['message']['contextId'] = context_id

    return MessageSendParams(**send_params)


async def complete_task(
    client: A2AClient,
    streaming: bool,
    task_id: str,
    context_id: str,
    debug: bool = False,
) -> bool:
    prompt = click.prompt(
        '\n您想傳送什麼給代理 (Agent)？（:q 或 quit 退出）'
    )

    if prompt == ':q' or prompt == 'quit':
        return False

    send_params = create_send_params(
        text=prompt,
        task_id=task_id,
        context_id=context_id,
    )

    task = None
    if streaming:
        stream_response = client.send_message_streaming(
            SendStreamingMessageRequest(id=str(uuid4()), params=send_params)
        )
        async for chunk in stream_response:
            result = chunk.root.result
            print(
                f'串流事件 => {chunk.root.model_dump_json(exclude_none=True)}'
                if debug
                else (
                    next(
                        (
                            f'串流訊息 => 角色：{result.role.value}，類型：{part.root.type}，文字：{part.root.text}'
                            for part in result.parts
                            if isinstance(part.root, TextPart)
                        ),
                        '',
                    )
                    if isinstance(result, Message)
                    else next(
                        (
                            f'串流訊息 => 角色：{msg.role.value}，類型：{part.root.type}，文字：{part.root.text}'
                            for msg in result.history or []
                            for part in msg.parts
                            if isinstance(part.root, TextPart)
                        ),
                        '',
                    )
                    if isinstance(result, Task)
                    else next(
                        (
                            f'串流訊息 => 角色：{result.status.message.role.value}，類型：{part.root.type}，文字：{part.root.text}'
                            for part in (
                                result.status.message.parts
                                if result.status.message
                                else []
                            )
                            if isinstance(part.root, TextPart)
                        ),
                        '',
                    )
                    if isinstance(result, TaskStatusUpdateEvent)
                    else next(
                        (
                            f'串流產物 => 類型：{part.root.type}，文字：{part.root.text}'
                            for part in result.artifact.parts
                            if isinstance(part.root, TextPart)
                        ),
                        '',
                    )
                    if isinstance(result, TaskArtifactUpdateEvent)
                    else ''
                )
            )

        get_task_response = await client.get_task(
            GetTaskRequest(id=str(uuid4()), params=TaskQueryParams(id=task_id))
        )
        task = get_task_response.root.result
    else:
        send_message_response = await client.send_message(
            SendMessageRequest(id=str(uuid4()), params=send_params)
        )
        task = send_message_response.root.result
        print(f'\n{task.model_dump_json(exclude_none=True)}')

    # 如果結果是需要更多輸入，則再次迴圈。
    if task.status.state == TaskState.input_required:
        return await complete_task(
            client,
            streaming,
            task_id,
            context_id,
            debug,
        )

    # 任務已完成
    return True


if __name__ == '__main__':
    asyncio.run(cli())
