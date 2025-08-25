import json
import logging
import os
import time

from collections.abc import AsyncGenerator
from typing import Any

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    Agent,
    AgentThread,
    ListSortOrder,
    ThreadMessage,
    ThreadRun,
    ToolOutput,
)
from azure.identity import DefaultAzureCredential
from utils.mcp_tool_manager import MCPToolManager


class CurrencyAgent:
    logger = logging.getLogger(__name__)

    INSTRUCTION = (
        '你是一位專門處理貨幣換算的助理。'
        "你唯一的目的是使用 'get_exchange_rate' 工具來回答有關匯率的問題。"
        '如果使用者詢問貨幣換算或匯率以外的任何問題，'
        '請禮貌地說明你無法協助該主題，只能協助處理與貨幣相關的查詢。'
        '不要嘗試回答無關的問題或將工具用於其他目的。'
        '如果使用者需要提供更多資訊，請將回應狀態設定為 input_required。'
        '如果處理請求時發生錯誤，請將回應狀態設定為 error。'
        '如果請求已完成，請將回應狀態設定為 completed。'
    )

    def __init__(self):
        # 檢查是否已設定必要的環境變數
        if 'AZURE_AI_FOUNDRY_PROJECT_ENDPOINT' not in os.environ:
            raise ValueError(
                'AZURE_AI_FOUNDRY_PROJECT_ENDPOINT 環境變數未設定。'
                '請設定您的 Azure AI Foundry 端點。'
            )

        self.endpoint = os.environ['AZURE_AI_FOUNDRY_PROJECT_ENDPOINT']

        # 檢查端點值是否有效
        if not self.endpoint or not self.endpoint.strip():
            raise ValueError(
                'AZURE_AI_FOUNDRY_PROJECT_ENDPOINT 環境變數為空。'
                '請提供一個有效的 Azure AI Foundry 端點。'
            )

        self.credential = DefaultAzureCredential()
        self.agent: Agent | None = None
        self.threads: dict[str, str] = {}  # thread_id -> thread_id mapping
        self.mcp_server_url = os.environ.get('MCP_ENDPOINT')
        self.mcp_tool_manager: MCPToolManager | None = (
            None  # Placeholder for MCPToolManager or similar
        )

    def _get_client(self) -> AgentsClient:
        """取得一個新的 AgentsClient 實例以在內容管理員中使用。"""
        return AgentsClient(
            endpoint=self.endpoint,
            credential=self.credential,
        )

    async def create_agent(self) -> Agent:
        """使用日曆指令建立 AI Foundry 代理 (Agent)。"""
        if self.agent:
            return self.agent

        logger = logging.getLogger(__name__)

        self.mcp_tool_manager = MCPToolManager(self.mcp_server_url)

        # 初始化 MCP 工具管理員（不使用非同步內容管理員）
        await self.mcp_tool_manager.initialize()

        # 取得所有可用的工具定義
        mcp_tools = self.mcp_tool_manager.get_tools()

        if not mcp_tools:
            raise ValueError(
                '找不到有效的 MCP 工具。請檢查您的 MCP 伺服器設定。'
            )

        logger.info(
            f'找到 {len(mcp_tools)} 個 MCP 工具：{list(mcp_tools.keys())}'
        )

        # 將 MCP 工具轉換為 Azure AI Agents 格式
        azure_tools = []
        for tool_name, tool_def in mcp_tools.items():
            logger.info(f'正在處理工具：{tool_name}')
            logger.info(f'工具定義：{tool_def}')

            azure_tool_def = {
                'type': 'function',
                'function': {
                    'name': tool_def['name'],
                    'description': tool_def['description'],
                    'parameters': tool_def['input_schema'],
                },
            }
            azure_tools.append(azure_tool_def)
            logger.info(f'已轉換為 Azure 工具：{azure_tool_def}')

        with self._get_client() as client:
            self.agent = client.create_agent(
                model=os.environ['AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME'],
                name='currency-agent',
                instructions=self.INSTRUCTION,
                tools=azure_tools,
            )
            return self.agent

    async def create_thread(self, thread_id: str | None = None) -> AgentThread:
        """建立或擷取對話執行緒。"""
        if thread_id and thread_id in self.threads:
            # 傳回執行緒資訊 - 我們每次都需要重新取得
            pass

        with self._get_client() as client:
            thread = client.threads.create()
            self.threads[thread.id] = thread.id
            return thread

    async def send_message(
        self, thread_id: str, content: str, role: str = 'user'
    ) -> ThreadMessage:
        """向對話執行緒傳送訊息。"""
        with self._get_client() as client:
            message = client.messages.create(
                thread_id=thread_id, role=role, content=content
            )
            return message

    async def run_conversation(
        self, thread_id: str, user_message: str
    ) -> list[str]:
        """與代理 (Agent) 執行一個完整的對話週期。"""
        if not self.agent:
            await self.create_agent()

        # 傳送使用者訊息
        await self.send_message(thread_id, user_message)

        # 建立並執行代理 (Agent)
        with self._get_client() as client:
            run = client.runs.create(
                thread_id=thread_id, agent_id=self.agent.id
            )

            # 輪詢直到完成
            max_iterations = 30  # 防止無限迴圈
            iterations = 0

            while (
                run.status in ['queued', 'in_progress', 'requires_action']
                and iterations < max_iterations
            ):
                iterations += 1
                time.sleep(1)
                run = client.runs.get(thread_id=thread_id, run_id=run.id)

                if run.status == 'failed':
                    break

                # 如果需要，處理工具呼叫
                if run.status == 'requires_action':
                    try:
                        await self._handle_tool_calls(run, thread_id)
                        # 工具提交後取得更新的執行狀態
                        run = client.runs.get(
                            thread_id=thread_id, run_id=run.id
                        )
                    except Exception as e:
                        # logger.error(f"處理工具呼叫時發生錯誤：{e}")
                        # 如果工具處理失敗，將執行標示為失敗
                        return [f'處理工具呼叫時發生錯誤：{e!s}']

            if run.status == 'failed':
                # logger.error(f"執行失敗：{run.last_error}")
                return [f'錯誤：{run.last_error}']

            if iterations >= max_iterations:
                # logger.error(f"執行在 {max_iterations} 次疊代後逾時")
                return ['錯誤：請求逾時']

            # 取得回應訊息
            messages = client.messages.list(
                thread_id=thread_id, order=ListSortOrder.DESCENDING
            )

            responses = []
            for msg in messages:
                if msg.role == 'assistant' and msg.text_messages:
                    for text_msg in msg.text_messages:
                        responses.append(text_msg.text.value)
                    break  # 只取得最新的助理回應

            return responses if responses else ['未收到回應']

    async def stream(
        self, user_query: str, context_id: str = None
    ) -> AsyncGenerator[dict[str, Any], None]:
        """從代理 (Agent) 串流回應。

        Args:
            user_query: 使用者的查詢文字
            context_id: 用於對話追蹤的選用內容 ID

        Yields:
            包含串流回應資訊的字典
        """
        # 如果需要，建立執行緒或重複使用現有執行緒
        if not context_id or context_id not in self.threads:
            thread = await self.create_thread()
            thread_id = thread.id
            if context_id:
                self.threads[context_id] = thread_id
        else:
            thread_id = self.threads[context_id]

        # 確保代理 (Agent) 存在
        if not self.agent:
            await self.create_agent()

        # 傳送使用者訊息
        await self.send_message(thread_id, user_query)

        # 初始回應，表示正在處理中
        yield {
            'content': '正在處理您的請求...',
            'require_user_input': False,
            'is_task_complete': False,
        }

        # 建立並執行代理 (Agent)
        with self._get_client() as client:
            run = client.runs.create(
                thread_id=thread_id, agent_id=self.agent.id
            )

            max_iterations = 30
            iterations = 0

            while (
                run.status in ['queued', 'in_progress', 'requires_action']
                and iterations < max_iterations
            ):
                iterations += 1
                time.sleep(0.5)  # 較短的輪詢間隔以進行串流

                run = client.runs.get(thread_id=thread_id, run_id=run.id)

                # 如果我們需要工具呼叫，請處理它們
                if run.status == 'requires_action':
                    try:
                        yield {
                            'content': '正在處理資料來源...',
                            'require_user_input': False,
                            'is_task_complete': False,
                        }
                        await self._handle_tool_calls(run, thread_id)
                        run = client.runs.get(
                            thread_id=thread_id, run_id=run.id
                        )
                    except Exception as e:
                        yield {
                            'content': f'處理工具呼叫時發生錯誤：{e!s}',
                            'require_user_input': False,
                            'is_task_complete': True,
                        }
                        return

            # 處理任何終端狀態
            if run.status == 'failed':
                yield {
                    'content': f'錯誤：{run.last_error}',
                    'require_user_input': False,
                    'is_task_complete': True,
                }
                return

            if iterations >= max_iterations:
                yield {
                    'content': '錯誤：請求逾時',
                    'require_user_input': False,
                    'is_task_complete': True,
                }
                return

            # 取得最終回應
            messages = client.messages.list(
                thread_id=thread_id, order=ListSortOrder.DESCENDING
            )

            for msg in messages:
                if msg.role == 'assistant' and msg.text_messages:
                    for text_msg in msg.text_messages:
                        yield {
                            'content': text_msg.text.value,
                            'require_user_input': False,
                            'is_task_complete': True,
                        }
                    return

            # 如果找不到訊息，則執行後備方案
            yield {
                'content': '未收到來自代理 (Agent) 的回應。',
                'require_user_input': False,
                'is_task_complete': True,
            }

    async def _handle_tool_calls(self, run: ThreadRun, thread_id: str):
        """在代理 (Agent) 執行期間使用 MCP 工具管理員處理工具呼叫。"""
        import logging

        logger = logging.getLogger(__name__)
        logger.info('正在處理 MCP 工具呼叫')

        if not hasattr(run, 'required_action') or not run.required_action:
            logger.warning('在執行中找不到必要的動作')
            return

        required_action = run.required_action
        if (
            not hasattr(required_action, 'submit_tool_outputs')
            or not required_action.submit_tool_outputs
        ):
            logger.warning('不需要提交工具輸出')
            return

        try:
            tool_calls = required_action.submit_tool_outputs.tool_calls
            if not tool_calls:
                logger.warning('在必要的動作中找不到工具呼叫')
                return

            tool_outputs = []

            # 確保 MCP 工具管理員已初始化並連線
            if not self.mcp_tool_manager:
                logger.warning('MCP 工具管理員未初始化，正在立即建立')
                self.mcp_tool_manager = MCPToolManager(self.mcp_server_url)
                await self.mcp_tool_manager.initialize()
            elif (
                not self.mcp_tool_manager._connection
                or not self.mcp_tool_manager._connection.is_connected
            ):
                logger.warning(
                    'MCP Tool Manager connection not available, reinitializing'
                )
                await self.mcp_tool_manager.initialize()

            # 處理每個工具呼叫
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                arguments_str = tool_call.function.arguments

                logger.info(
                    f'正在處理 mcp 工具呼叫：{function_name}，參數為：{arguments_str}'
                )

                try:
                    # 從 JSON 字串解析參數並進行防禦性處理
                    if not arguments_str or arguments_str.strip() == '':
                        logger.warning(
                            f'工具 {function_name} 的參數為空或 null，使用空字典'
                        )
                        arguments = {}
                    else:
                        try:
                            arguments = json.loads(arguments_str)
                            logger.info(f'已解析參數：{arguments}')
                            logger.info(f'參數類型：{type(arguments)}')
                            logger.info(
                                f'參數鍵：{list(arguments.keys()) if isinstance(arguments, dict) else "非字典"}'
                            )
                        except json.JSONDecodeError as json_error:
                            logger.error(
                                f'為工具 {function_name} 解析 JSON 參數失敗：{json_error}'
                            )
                            logger.error(
                                f"原始參數字串：'{arguments_str}'"
                            )
                            # 嘗試使用空參數恢復或跳過此工具呼叫
                            arguments = {}
                            logger.warning(
                                f'由於 JSON 解析錯誤，為工具 {function_name} 使用空參數'
                            )

                    # 檢查函式是否存在於 MCP 工具中
                    available_tools = self.mcp_tool_manager.get_tools()
                    if function_name in available_tools:
                        logger.info(
                            f'正在執行 MCP 工具函式：{function_name}，參數為：{arguments}'
                        )

                        # 偵錯：記錄確切的參數值
                        if isinstance(arguments, dict):
                            for key, value in arguments.items():
                                logger.info(
                                    f"  參數 '{key}': '{value}' (類型：{type(value)})"
                                )

                        # 在使用連線前確保其存在
                        if not self.mcp_tool_manager._connection:
                            logger.error(
                                '初始化後 MCP 連線為 None'
                            )
                            output = {'error': 'MCP 連線不可用'}
                        else:
                            # 直接使用連線執行 MCP 工具
                            output = await self.mcp_tool_manager._connection.execute_tool(
                                function_name, arguments
                            )
                            logger.info(f'MCP 工具執行結果：{output}')
                    else:
                        output = {'error': f'未知函式：{function_name}'}
                        logger.error(
                            f'請求了未知函式：{function_name}'
                        )
                        logger.error(
                            f'可用工具：{list(available_tools.keys())}'
                        )

                except json.JSONDecodeError as e:
                    output = {'error': f'無效的參數 JSON：{e!s}'}
                    logger.error(
                        f'工具 {function_name} 的 JSON 解析錯誤：{e!s}'
                    )
                except Exception as e:
                    output = {
                        'error': f'執行工具 {function_name} 時發生錯誤：{e!s}'
                    }
                    logger.error(f'工具執行期間發生錯誤：{e!s}')
                    logger.error(f'例外類型：{type(e).__name__}')
                    import traceback

                    logger.error(f'完整追蹤記錄：{traceback.format_exc()}')

                # 確保我們有一個有效的 tool_call_id
                if not hasattr(tool_call, 'id') or not tool_call.id:
                    logger.error(f'工具呼叫缺少 ID：{tool_call}')
                    continue

                # 如果輸出還不是 JSON 字串，則將其轉換
                if isinstance(output, str):
                    output_str = output
                else:
                    output_str = json.dumps(output)

                tool_outputs.append(
                    {'tool_call_id': tool_call.id, 'output': output_str}
                )

            if not tool_outputs:
                logger.error('未產生有效的工具輸出')
                return

            logger.debug(f'要提交的工具輸出：{tool_outputs}')

        except Exception as e:
            logger.error(f'處理工具呼叫時發生錯誤：{e}')
            logger.error(f'必要的動作結構：{required_action}')
            raise

        # 提交工具輸出
        with self._get_client() as client:
            try:
                # 以預期格式建立工具輸出
                formatted_outputs = []
                for output in tool_outputs:
                    formatted_outputs.append(
                        ToolOutput(
                            tool_call_id=output['tool_call_id'],
                            output=output['output'],
                        )
                    )

                logger.debug(
                    f'正在提交格式化的工具輸出：{formatted_outputs}'
                )

                client.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=formatted_outputs,
                )
                logger.info(f'已提交 {len(formatted_outputs)} 個工具輸出')
            except Exception as e:
                logger.error(f'提交工具輸出失敗：{e}')
                logger.error(f'原始工具輸出結構：{tool_outputs}')
                # 嘗試使用原始 dict 格式進行後備提交
                try:
                    logger.info(
                        '正在嘗試使用原始 dict 格式進行後備提交'
                    )
                    client.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs,
                    )
                    logger.info('後備提交成功')
                except Exception as e2:
                    logger.error(f'後備提交也失敗：{e2}')
                    raise e

    async def cleanup_agent(self):
        """清理代理 (Agent) 資源。"""
        if self.agent:
            with self._get_client() as client:
                client.delete_agent(self.agent.id)
                # logger.info(f"已刪除代理 (Agent)：{self.agent.id}")
                self.agent = None

        # 清理 MCP 連線
        if self.mcp_tool_manager:
            await self.mcp_tool_manager.close()
            self.mcp_tool_manager = None


async def create_foundry_calendar_agent() -> CurrencyAgent:
    """用於建立和初始化 Foundry 日曆代理 (Agent) 的工廠函式。"""
    agent = CurrencyAgent()
    await agent.create_agent()
    return agent
