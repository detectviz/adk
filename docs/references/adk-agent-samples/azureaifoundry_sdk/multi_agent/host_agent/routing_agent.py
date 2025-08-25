import asyncio
import json
import os
import time
import uuid

from typing import Any, Dict, List, Optional

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
    TaskState,
)
from remote_agent_connection import (
    RemoteAgentConnections,
    TaskUpdateCallback,
)
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder, ToolSet
from dotenv import load_dotenv


load_dotenv()


class AzureAgentContext:
    """用於取代 Google ADK ReadonlyContext 的上下文類別。"""
    def __init__(self):
        self.state: Dict[str, Any] = {}


def convert_part(part: Part) -> str:
    """將一個部分轉換為文字。僅支援文字部分。"""
    if part.type == 'text':
        return part.text

    return f'未知類型：{part.type}'


def convert_parts(parts: list[Part]) -> List[str]:
    """將多個部分轉換為文字。"""
    rval = []
    for p in parts:
        rval.append(convert_part(p))
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
    並使用 Azure AI Agents 協調其工作。
    """

    def __init__(
        self,
        task_callback: TaskUpdateCallback | None = None,
    ):
        self.task_callback = task_callback
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        self.agents: str = ''
        self.context = AzureAgentContext()
        
        # Initialize Azure AI Agents client
        self.agents_client = AgentsClient(
            endpoint=os.environ["AZURE_AI_AGENT_ENDPOINT"],
            credential=DefaultAzureCredential(),
        )
        self.azure_agent = None
        self.current_thread = None

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

    def create_agent(self):
        """建立一個 Azure AI Agent 實例。"""
        instructions = self.get_root_instruction()
        
        try:
            # 使用更佳的錯誤處理建立 Azure AI Agent
            model_name = os.environ.get("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME", "gpt-4")
            print(f"正在使用模型建立代理 (Agent)：{model_name}")
            print(f"指令長度：{len(instructions)} 個字元")

            # Create tool definition for send_message function
            from azure.ai.agents.models import FunctionTool

            tools = [{
                "type": "function",
                "function": {
                    "name": "send_message",
                    "description": "Sends a task to a remote seller agent",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "agent_name": {
                                "type": "string",
                                "description": "The name of the agent to send the task to"
                            },
                            "task": {
                                "type": "string",
                                "description": "The comprehensive conversation context summary and goal to be achieved"
                            }
                        },
                        "required": ["agent_name", "task"]
                    }
                }
            }]
 

            # toolset = ToolSet()
            # toolset.add(send_message_tool)
            
            self.azure_agent = self.agents_client.create_agent(
                model=model_name,
                name="routing-agent",
                instructions=instructions,
                tools=tools
            )
            print(f"已建立 Azure AI 代理 (Agent)，代理 (Agent) ID：{self.azure_agent.id}")
            
            # 建立對話執行緒
            self.current_thread = self.agents_client.threads.create()
            print(f"已建立執行緒，執行緒 ID：{self.current_thread.id}")
            
            return self.azure_agent
            
        except Exception as e:
            print(f"建立 Azure AI 代理 (Agent) 時發生錯誤：{e}")
            print(f"使用的模型名稱：{model_name}")
            print(f"指令：{instructions[:200]}...")
            raise

    def get_root_instruction(self) -> str:
        """為 RoutingAgent 產生根指令。"""
        current_agent = self.check_active_agent()
        return f"""您是一位專業的路由委派員，可協助使用者處理天氣和住宿請求。

您的角色：
- 將使用者查詢委派給適當的專業遠端代理 (Agent)
- 向使用者提供清晰且有幫助的回應
- 將使用者與天氣代理 (Agent) 連線以進行天氣查詢
- 將使用者與住宿代理 (Agent) 連線以進行預訂請求

可用代理 (Agent)：{self.agents}
目前活躍的代理 (Agent)：{current_agent['active_agent']}

始終樂於助人，並將請求路由到最合適的代理 (Agent)。"""

    def check_active_agent(self):
        """檢查目前活躍的代理 (Agent)。"""
        state = self.context.state
        if (
            'session_id' in state
            and 'session_active' in state
            and state['session_active']
            and 'active_agent' in state
        ):
            return {'active_agent': f'{state["active_agent"]}'}
        return {'active_agent': 'None'}

    def initialize_session(self):
        """初始化一個新工作階段。"""
        state = self.context.state
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
        self, agent_name: str, task: str
    ):
        """將任務傳送給遠端銷售代理 (remote seller agent)。

        這將會向名為 agent_name 的遠端代理 (remote agent) 傳送一則訊息。

        Args:
            agent_name: 要將任務傳送給的代理 (Agent) 名稱。
            task: 關於使用者查詢和購買請求的全面對話上下文摘要
                和要達成的目標。

        Returns:
            一個來自遠端代理 (remote agent) 回應的 Task 物件。
        """
        if agent_name not in self.remote_agent_connections:
            raise ValueError(f'找不到代理 (Agent) {agent_name}')
        
        state = self.context.state
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
        print('send_response', send_response.model_dump_json(exclude_none=True, indent=2))

        if not isinstance(send_response.root, SendMessageSuccessResponse):
            print('收到非成功回應。正在中止取得任務')
            return

        if not isinstance(send_response.root.result, Task):
            print('收到非任務回應。正在中止取得任務')
            return

        return send_response.root.result

    async def process_user_message(self, user_message: str) -> str:
        """透過 Azure AI Agent 處理使用者訊息並傳回回應。"""
        if not hasattr(self, 'azure_agent') or not self.azure_agent:
            return "Azure AI Agent 未初始化。請確保代理 (Agent) 已正確建立。"
        
        if not hasattr(self, 'current_thread') or not self.current_thread:
            return "Azure AI 執行緒未初始化。請確保代理 (Agent) 已正確建立。"
        
        try:
            # 如果需要，初始化工作階段
            self.initialize_session()
            
            print(f"正在處理訊息：{user_message[:50]}...")
            
            # 在執行緒中建立訊息
            message = self.agents_client.messages.create(
                thread_id=self.current_thread.id, 
                role="user", 
                content=user_message
            )
            print(f"已建立訊息，訊息 ID：{message.id}")

            # 建立並執行代理 (Agent)
            print(f"正在使用代理 (Agent) ID 建立執行：{self.azure_agent.id}")
            run = self.agents_client.runs.create(
                thread_id=self.current_thread.id, 
                agent_id=self.azure_agent.id
            )
            print(f"已建立執行，執行 ID：{run.id}")

            # 輪詢執行直到完成
            max_iterations = 60  # 60 秒逾時
            iteration = 0
            while run.status in ["queued", "in_progress", "requires_action"] and iteration < max_iterations:
                # 如果需要，處理函式呼叫
                if run.status == "requires_action":
                    await self._handle_required_actions(run)
                
                time.sleep(1)
                iteration += 1
                run = self.agents_client.runs.get(
                    thread_id=self.current_thread.id, 
                    run_id=run.id
                )
                print(f"執行狀態：{run.status} (疊代 {iteration})")

            if iteration >= max_iterations:
                return "請求在 60 秒後逾時。請再試一次。"

            if run.status == "failed":
                error_info = f"執行錯誤：{run.last_error}"
                print(error_info)
                
                # 嘗試取得更詳細的錯誤資訊
                if hasattr(run, 'last_error') and run.last_error:
                    if hasattr(run.last_error, 'code'):
                        error_info += f" (代碼：{run.last_error.code})"
                    if hasattr(run.last_error, 'message'):
                        error_info += f" (訊息：{run.last_error.message})"
                
                return f"處理請求時發生錯誤：{error_info}"

            # 取得最新訊息
            messages = self.agents_client.messages.list(
                thread_id=self.current_thread.id, 
                order=ListSortOrder.DESCENDING
            )
            
            # 傳回助理的回應
            for msg in messages:
                if msg.role == "assistant" and msg.text_messages:
                    last_text = msg.text_messages[-1]
                    return last_text.text.value
            
            return "未收到來自代理 (Agent) 的回應。"
            
        except Exception as e:
            error_msg = f"process_user_message 中發生錯誤：{e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return f"處理您的訊息時發生錯誤：{str(e)}"

    async def _handle_required_actions(self, run):
        """處理 Azure AI Agent 所需的函式呼叫。"""
        try:
            if hasattr(run, 'required_action') and run.required_action:
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"正在執行函式：{function_name}，參數為：{function_args}")
                    
                    if function_name == "send_message":
                        try:
                            # 呼叫我們的 send_message 方法
                            result = await self.send_message(
                                agent_name=function_args["agent_name"],
                                task=function_args["task"]
                            )
                            # 將結果轉換為 JSON 字串
                            output = json.dumps(result.model_dump() if hasattr(result, 'model_dump') else str(result))
                        except Exception as e:
                            output = json.dumps({"error": str(e)})
                    else:
                        output = json.dumps({"error": f"未知函式：{function_name}"})
                    
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": output
                    })
                
                # 提交工具輸出
                self.agents_client.runs.submit_tool_outputs(
                    thread_id=self.current_thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                print(f"已提交 {len(tool_outputs)} 個工具輸出")
                
        except Exception as e:
            print(f"處理必要動作時發生錯誤：{e}")
            import traceback
            traceback.print_exc()

    def cleanup(self):
        """清理 Azure AI 代理 (Agent) 資源。"""
        try:
            if hasattr(self, 'azure_agent') and self.azure_agent and hasattr(self, 'agents_client') and self.agents_client:
                self.agents_client.delete_agent(self.azure_agent.id)
                print(f"已刪除 Azure AI 代理 (Agent)：{self.azure_agent.id}")
        except Exception as e:
            print(f"清理代理 (Agent) 時發生錯誤：{e}")
        finally:
            # 關閉用戶端以清理資源
            if hasattr(self, 'agents_client') and self.agents_client:
                try:
                    self.agents_client.close()
                    print("Azure AI 用戶端已關閉")
                except Exception as e:
                    print(f"關閉用戶端時發生錯誤：{e}")
            
            if hasattr(self, 'azure_agent'):
                self.azure_agent = None
            if hasattr(self, 'current_thread'):
                self.current_thread = None

    def __del__(self):
        """解構函式以確保清理。"""
        self.cleanup()


def _get_initialized_routing_agent_sync() -> RoutingAgent:
    """同步建立並初始化 RoutingAgent。"""

    async def _async_main() -> RoutingAgent:
        routing_agent_instance = await RoutingAgent.create(
            remote_agent_addresses=[
                os.getenv('TOOL_AGENT_URL', 'http://localhost:10002'),
                os.getenv('PLAYWRIGHT_AGENT_URL', 'http://localhost:10001'),
            ]
        )
        # Create the Azure AI agent
        routing_agent_instance.create_agent()
        return routing_agent_instance

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


# Initialize the routing agent
routing_agent = _get_initialized_routing_agent_sync()
