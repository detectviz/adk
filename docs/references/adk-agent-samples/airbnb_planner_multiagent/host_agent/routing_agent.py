# pylint: disable=logging-fstring-interpolation
import asyncio
import json
import os
import uuid

from typing import Any

import httpx

from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    Part,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext
from remote_agent_connection import (
    RemoteAgentConnections,
    TaskUpdateCallback,
)


load_dotenv()


def convert_part(part: Part, tool_context: ToolContext):
    """將一個部分轉換為文字。僅支援文字部分。"""
    if part.type == 'text':
        return part.text

    return f'未知類型：{part.type}'


def convert_parts(parts: list[Part], tool_context: ToolContext):
    """將多個部分轉換為文字。"""
    rval = []
    for p in parts:
        rval.append(convert_part(p, tool_context))
    return rval


def create_send_message_payload(
    text: str, task_id: str | None = None, context_id: str | None = None
) -> dict[str, Any]:
    """建立傳送任務之酬載的輔助函式。"""
    payload: dict[str, Any] = {
        'message': {
            'role': 'user',
            'parts': [{'type': 'text', 'text': text}],
            'messageId': uuid.uuid4().hex,
        },
    }

    if task_id:
        payload['message']['taskId'] = task_id

    if context_id:
        payload['message']['contextId'] = context_id
    return payload


class RoutingAgent:
    """路由代理 (Routing agent)。

    此代理 (Agent) 負責選擇要將任務傳送給哪些遠端銷售代理 (remote seller agents)
    並協調其工作。
    """

    def __init__(
        self,
        task_callback: TaskUpdateCallback | None = None,
    ):
        self.task_callback = task_callback
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        self.agents: str = ''

    async def _async_init_components(
        self, remote_agent_addresses: list[str]
    ) -> None:
        """初始化的非同步部分。"""
        # 為提高效率，所有卡片解析都使用單一的 httpx.AsyncClient
        async with httpx.AsyncClient(timeout=30) as client:
            for address in remote_agent_addresses:
                card_resolver = A2ACardResolver(
                    client, address
                )  # 建構函式是同步的
                try:
                    card = (
                        await card_resolver.get_agent_card()
                    )  # get_agent_card 是非同步的

                    remote_connection = RemoteAgentConnections(
                        agent_card=card, agent_url=address
                    )
                    self.remote_agent_connections[card.name] = remote_connection
                    self.cards[card.name] = card
                except httpx.ConnectError as e:
                    print(
                        f'錯誤：無法從 {address} 取得代理卡 (agent card)：{e}'
                    )
                except Exception as e:  # 捕捉其他潛在錯誤
                    print(
                        f'錯誤：無法初始化 {address} 的連線：{e}'
                    )

        # 使用原始 __init__ 的邏輯（透過 list_remote_agents）填入 self.agents
        agent_info = []
        for agent_detail_dict in self.list_remote_agents():
            agent_info.append(json.dumps(agent_detail_dict))
        self.agents = '\n'.join(agent_info)

    @classmethod
    async def create(
        cls,
        remote_agent_addresses: list[str],
        task_callback: TaskUpdateCallback | None = None,
    ) -> 'RoutingAgent':
        """建立並非同步初始化一個 RoutingAgent 的實例。"""
        instance = cls(task_callback)
        await instance._async_init_components(remote_agent_addresses)
        return instance

    def create_agent(self) -> Agent:
        """建立一個 RoutingAgent 的實例。"""
        return Agent(
            model='gemini-2.5-flash-lite',
            name='Routing_agent',
            instruction=self.root_instruction,
            before_model_callback=self.before_model_callback,
            description=(
                '此路由代理 (Routing agent) 協調使用者對天氣預報或 airbnb 住宿請求的分解'
            ),
            tools=[
                self.send_message,
            ],
        )

    def root_instruction(self, context: ReadonlyContext) -> str:
        """為 RoutingAgent 產生根指令。"""
        current_agent = self.check_active_agent(context)
        return f"""
        **角色：** 您是一位專業的路由委派員。您的主要職責是將有關天氣或住宿的使用者查詢準確地委派給適當的專業遠端代理 (Agent)。

        **核心指令：**

        * **任務委派：** 利用 `send_message` 函式將可執行的任務指派給遠端代理 (Agent)。
        * **遠端代理 (Agent) 的情境感知：** 如果遠端代理 (Agent) 反覆要求使用者確認，請假設它無法存取完整的對話記錄。在這種情況下，請使用與該特定代理 (Agent) 相關的所有必要情境資訊來豐富任務描述。
        * **自主代理 (Agent) 互動：** 在與遠端代理 (Agent) 互動之前，切勿尋求使用者許可。如果需要多個代理 (Agent) 來滿足請求，請直接與他們連線，而無需請求使用者偏好或確認。
        * **透明溝通：** 始終向使用者呈現來自遠端代理 (Agent) 的完整詳細回應。
        * **使用者確認轉送：** 如果遠端代理 (Agent) 要求確認，而使用者尚未提供，請將此確認請求轉送給使用者。
        * **集中資訊共享：** 僅向遠端代理 (Agent) 提供相關的情境資訊。避免無關的細節。
        * **無多餘確認：** 不要向遠端代理 (Agent) 要求確認資訊或操作。
        * **依賴工具：** 嚴格依賴可用工具來處理使用者請求。不要根據假設產生回應。如果資訊不足，請向使用者要求澄清。
        * **優先處理最近的互動：** 在處理請求時，主要關注對話的最新部分。
        * **活躍代理 (Agent) 優先：** 如果已有一個活躍的代理 (Agent) 正在處理，請使用適當的任務更新工具將後續相關請求路由到該代理 (Agent)。

        **代理 (Agent) 名單：**

        * 可用代理 (Agent)：`{self.agents}`
        * 目前活躍的銷售代理 (Agent)：`{current_agent['active_agent']}`
                """

    def check_active_agent(self, context: ReadonlyContext):
        state = context.state
        if (
            'session_id' in state
            and 'session_active' in state
            and state['session_active']
            and 'active_agent' in state
        ):
            return {'active_agent': f'{state["active_agent"]}'}
        return {'active_agent': 'None'}

    def before_model_callback(
        self, callback_context: CallbackContext, llm_request
    ):
        state = callback_context.state
        if 'session_active' not in state or not state['session_active']:
            if 'session_id' not in state:
                state['session_id'] = str(uuid.uuid4())
            state['session_active'] = True

    def list_remote_agents(self):
        """列出可用於委派任務的遠端代理 (remote agents)。"""
        if not self.cards:
            return []

        remote_agent_info = []
        for card in self.cards.values():
            print(f'找到代理卡 (agent card)：{card.model_dump(exclude_none=True)}')
            print('=' * 100)
            remote_agent_info.append(
                {'name': card.name, 'description': card.description}
            )
        return remote_agent_info

    async def send_message(
        self, agent_name: str, task: str, tool_context: ToolContext
    ):
        """將任務傳送給遠端銷售代理 (remote seller agent)。

        這將會向名為 agent_name 的遠端代理 (remote agent) 傳送一則訊息。

        Args:
            agent_name: 要將任務傳送給的代理 (Agent) 名稱。
            task: 關於使用者查詢和購買請求的全面對話上下文摘要
                和要達成的目標。
            tool_context: 此方法執行所在的工具上下文。

        Yields:
            一個 JSON 資料字典。
        """
        if agent_name not in self.remote_agent_connections:
            raise ValueError(f'找不到代理 (Agent) {agent_name}')
        state = tool_context.state
        state['active_agent'] = agent_name
        client = self.remote_agent_connections[agent_name]

        if not client:
            raise ValueError(f'{agent_name} 的客戶端不可用')
        task_id = state['task_id'] if 'task_id' in state else str(uuid.uuid4())

        if 'context_id' in state:
            context_id = state['context_id']
        else:
            context_id = str(uuid.uuid4())

        message_id = ''
        metadata = {}
        if 'input_message_metadata' in state:
            metadata.update(**state['input_message_metadata'])
            if 'message_id' in state['input_message_metadata']:
                message_id = state['input_message_metadata']['message_id']
        if not message_id:
            message_id = str(uuid.uuid4())

        payload = {
            'message': {
                'role': 'user',
                'parts': [
                    {'type': 'text', 'text': task}
                ],  # 在此處使用 'task' 引數
                'messageId': message_id,
            },
        }

        if task_id:
            payload['message']['taskId'] = task_id

        if context_id:
            payload['message']['contextId'] = context_id

        message_request = SendMessageRequest(
            id=message_id, params=MessageSendParams.model_validate(payload)
        )
        send_response: SendMessageResponse = await client.send_message(
            message_request=message_request
        )
        print(
            'send_response',
            send_response.model_dump_json(exclude_none=True, indent=2),
        )

        if not isinstance(send_response.root, SendMessageSuccessResponse):
            print('收到非成功回應。正在中止取得任務')
            return None

        if not isinstance(send_response.root.result, Task):
            print('收到非任務回應。正在中止取得任務')
            return None

        return send_response.root.result


def _get_initialized_routing_agent_sync() -> Agent:
    """同步建立並初始化 RoutingAgent。"""

    async def _async_main() -> Agent:
        routing_agent_instance = await RoutingAgent.create(
            remote_agent_addresses=[
                os.getenv('AIR_AGENT_URL', 'http://localhost:10002'),
                os.getenv('WEA_AGENT_URL', 'http://localhost:10001'),
            ]
        )
        return routing_agent_instance.create_agent()

    try:
        return asyncio.run(_async_main())
    except RuntimeError as e:
        if '無法從執行中的事件迴圈呼叫 asyncio.run()' in str(e):
            print(
                f'警告：無法使用 asyncio.run() 初始化 RoutingAgent：{e}。'
                '如果事件迴圈已在執行中（例如，在 Jupyter 中），可能會發生這種情況。'
                '請考慮在應用程式的非同步函式中初始化 RoutingAgent。'
            )
        raise


root_agent = _get_initialized_routing_agent_sync()
