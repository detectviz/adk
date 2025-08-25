"""具有日曆功能的 AI Foundry Agent 實作。
從 ADK 代理 (Agent) 模式改編以與 Azure AI Foundry 搭配使用。
"""

import asyncio
import datetime
import json
import logging
import os
import time

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


logger = logging.getLogger(__name__)


class FoundryCalendarAgent:
    """具有日曆管理功能的 AI Foundry Agent。
    此類別將 ADK 日曆代理 (Agent) 模式改編以適用於 Azure AI Foundry。
    """

    def __init__(self):
        self.endpoint = os.environ['AZURE_AI_FOUNDRY_PROJECT_ENDPOINT']
        self.credential = DefaultAzureCredential()
        self.agent: Agent | None = None
        self.threads: dict[str, str] = {}  # thread_id -> thread_id mapping

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

        with self._get_client() as client:
            self.agent = client.create_agent(
                model=os.environ['AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME'],
                name='foundry-calendar-agent',
                instructions=self._get_calendar_instructions(),
                tools=self._get_calendar_tools(),
            )
            logger.info(f'已建立 AI Foundry 代理 (Agent)：{self.agent.id}')
            return self.agent

    def _get_calendar_instructions(self) -> str:
        """取得從 ADK 日曆代理 (Agent) 改編的代理 (Agent) 指令。"""
        return f"""
您是一個由 Azure AI Foundry 提供支援的智慧日曆管理代理 (Agent)。

您的功能包括：
- 檢查日曆可用性
- 管理日曆活動
- 提供排程洞見
- 協助時間管理

主要指南：
- 如果未指定，則假設使用者想要有關其「主要」日曆的資訊
- 對所有日期/時間操作使用格式正確的 RFC3339 時間戳記
- 積極主動地建議最佳會議時間
- 始終與使用者確認重要的排程操作

目前日期與時間：{datetime.datetime.now().isoformat()}

當使用者詢問有關可用性、排程或日曆管理的問題時，請使用您的日曆工具提供準確且有幫助的回應。
"""

    def _get_calendar_tools(self) -> list[dict[str, Any]]:
        """為代理 (Agent) 定義日曆工具（為示範而模擬）。"""
        return [
            {
                'type': 'function',
                'function': {
                    'name': 'check_availability',
                    'description': "檢查使用者的日曆中是否有可用的時間空檔",
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'start_time': {
                                'type': 'string',
                                'description': 'RFC3339 格式的開始時間',
                            },
                            'end_time': {
                                'type': 'string',
                                'description': 'RFC3339 格式的結束時間',
                            },
                            'calendar_id': {
                                'type': 'string',
                                'description': "日曆 ID (預設為 'primary')",
                                'default': 'primary',
                            },
                        },
                        'required': ['start_time', 'end_time'],
                    },
                },
            },
            {
                'type': 'function',
                'function': {
                    'name': 'get_upcoming_events',
                    'description': "從使用者的日曆中取得即將到來的活動",
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'max_results': {
                                'type': 'integer',
                                'description': '要傳回的最大活動數',
                                'default': 10,
                            },
                            'time_range_hours': {
                                'type': 'integer',
                                'description': '從現在起要檢查的小時數',
                                'default': 24,
                            },
                        },
                    },
                },
            },
        ]

    async def create_thread(self, thread_id: str | None = None) -> AgentThread:
        """建立或擷取對話執行緒。"""
        if thread_id and thread_id in self.threads:
            # 傳回執行緒資訊 - 我們每次都需要重新取得
            pass

        with self._get_client() as client:
            thread = client.threads.create()
            self.threads[thread.id] = thread.id
            logger.info(f'已建立執行緒：{thread.id}')
            return thread

    async def send_message(
        self, thread_id: str, content: str, role: str = 'user'
    ) -> ThreadMessage:
        """向對話執行緒傳送訊息。"""
        with self._get_client() as client:
            message = client.messages.create(
                thread_id=thread_id, role=role, content=content
            )
            logger.info(f'已在執行緒 {thread_id} 中建立訊息：{message.id}')
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
                logger.debug(
                    f'執行狀態：{run.status} (疊代 {iterations})'
                )

                if run.status == 'failed':
                    logger.error(f'輪詢期間執行失敗：{run.last_error}')
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
                        logger.error(f'處理工具呼叫時發生錯誤：{e}')
                        # 如果工具處理失敗，將執行標示為失敗
                        return [f'處理工具呼叫時發生錯誤：{e!s}']

            if run.status == 'failed':
                logger.error(f'執行失敗：{run.last_error}')
                return [f'錯誤：{run.last_error}']

            if iterations >= max_iterations:
                logger.error(f'執行在 {max_iterations} 次疊代後逾時')
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

    async def _handle_tool_calls(self, run: ThreadRun, thread_id: str):
        """在代理 (Agent) 執行期間處理工具呼叫。"""
        logger.info('正在處理工具呼叫（為示範而模擬）')

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

            # 處理每個工具呼叫
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                arguments = tool_call.function.arguments

                logger.info(
                    f'正在處理工具呼叫：{function_name}，參數為：{arguments}'
                )
                logger.debug(f'工具呼叫 ID：{tool_call.id}')

                # 模擬日曆工具回應
                if function_name == 'check_availability':
                    output = {
                        'available': True,
                        'message': '請求的時間段似乎可用。',
                    }
                elif function_name == 'get_upcoming_events':
                    output = {
                        'events': [
                            {
                                'title': '團隊會議',
                                'start': '2025-05-27T14:00:00Z',
                                'end': '2025-05-27T15:00:00Z',
                            },
                            {
                                'title': '專案審查',
                                'start': '2025-05-27T16:00:00Z',
                                'end': '2025-05-27T17:00:00Z',
                            },
                        ]
                    }
                else:
                    output = {'error': f'未知函式：{function_name}'}

                # 確保我們有一個有效的 tool_call_id
                if not hasattr(tool_call, 'id') or not tool_call.id:
                    logger.error(f'工具呼叫缺少 ID：{tool_call}')
                    continue

                tool_outputs.append(
                    {
                        'tool_call_id': tool_call.id,
                        'output': json.dumps(
                            output
                        ),  # 確保輸出為 JSON 字串
                    }
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
                logger.info(f'已刪除代理 (Agent)：{self.agent.id}')
                self.agent = None


async def create_foundry_calendar_agent() -> FoundryCalendarAgent:
    """用於建立和初始化 Foundry 日曆代理 (Agent) 的工廠函式。"""
    agent = FoundryCalendarAgent()
    await agent.create_agent()
    return agent


# 用於測試的範例用法
async def demo_agent_interaction():
    """示範如何使用 Foundry 日曆代理 (Agent) 的函式。"""
    agent = await create_foundry_calendar_agent()

    try:
        # 建立一個對話執行緒
        thread = await agent.create_thread()

        # 互動範例
        test_messages = [
            '你好！可以幫我處理我的日曆嗎？',
            '我明天下午 2 點到 3 點有空嗎？',
            '我今天有哪些即將到來的會議？',
        ]

        for message in test_messages:
            print(f'\n使用者：{message}')
            responses = await agent.run_conversation(thread.id, message)
            for response in responses:
                print(f'助理：{response}')

    finally:
        await agent.cleanup_agent()


if __name__ == '__main__':
    asyncio.run(demo_agent_interaction())
