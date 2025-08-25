import json
import logging

from typing import Any

from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    AgentCard,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils.errors import ServerError
from openai import AsyncOpenAI


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class OpenAIAgentExecutor(AgentExecutor):
    """執行基於 OpenAI 的代理 (Agent) 的 AgentExecutor。"""

    def __init__(
        self,
        card: AgentCard,
        tools: dict[str, Any],
        api_key: str,
        system_prompt: str,
    ):
        self._card = card
        self.tools = tools
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url='https://openrouter.ai/api/v1',
            default_headers={
                'HTTP-Referer': 'http://localhost:10007',
                'X-Title': 'GitHub Agent',
            },
        )
        self.model = 'anthropic/claude-3.5-sonnet'
        self.system_prompt = system_prompt

    async def _process_request(
        self,
        message_text: str,
        context: RequestContext,
        task_updater: TaskUpdater,
    ) -> None:
        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'user', 'content': message_text},
        ]

        # 將工具轉換為 OpenAI 格式
        openai_tools = []
        for tool_name, tool_instance in self.tools.items():
            if hasattr(tool_instance, tool_name):
                func = getattr(tool_instance, tool_name)
                # 從方法中提取函式結構
                schema = self._extract_function_schema(func)
                openai_tools.append({'type': 'function', 'function': schema})

        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            try:
                # 呼叫 OpenAI API
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=openai_tools if openai_tools else None,
                    tool_choice='auto' if openai_tools else None,
                    temperature=0.1,
                    max_tokens=4000,
                )

                message = response.choices[0].message

                # 將助理的回應新增至訊息
                messages.append(
                    {
                        'role': 'assistant',
                        'content': message.content,
                        'tool_calls': message.tool_calls,
                    }
                )

                # 檢查是否有要執行的工具呼叫
                if message.tool_calls:
                    # 執行工具呼叫
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)

                        logger.debug(
                            f'Calling function: {function_name} with args: {function_args}'
                        )

                        # 執行函式
                        if function_name in self.tools:
                            tool_instance = self.tools[function_name]
                            # 從實例取得方法
                            if hasattr(tool_instance, function_name):
                                method = getattr(tool_instance, function_name)
                                result = method(**function_args)
                            else:
                                result = {
                                    'error': f'在工具實例上找不到方法 {function_name}'
                                }
                        else:
                            result = {
                                'error': f'找不到函式 {function_name}'
                            }

                        # 正確序列化結果 - 處理 Pydantic 模型
                        if hasattr(result, 'model_dump'):
                            # 這是一個 Pydantic 模型，使用 model_dump() 將其轉換為字典
                            result_json = json.dumps(result.model_dump())
                        elif isinstance(result, dict):
                            # 這是一個常規字典
                            result_json = json.dumps(result)
                        else:
                            # 作為備用方案轉換為字串
                            result_json = str(result)

                        # 將工具結果新增至訊息
                        messages.append(
                            {
                                'role': 'tool',
                                'tool_call_id': tool_call.id,
                                'content': result_json,
                            }
                        )

                    # 傳送更新以顯示我們正在處理
                    await task_updater.update_status(
                        TaskState.working,
                        message=task_updater.new_agent_message(
                            [TextPart(text='正在處理工具呼叫...')]
                        ),
                    )

                    # 繼續迴圈以取得最終回應
                    continue
                # 沒有更多工具呼叫，這是最終回應
                if message.content:
                    parts = [TextPart(text=message.content)]
                    logger.debug(f'Yielding final response: {parts}')
                    await task_updater.add_artifact(parts)
                    await task_updater.complete()
                break

            except Exception as e:
                logger.error(f'Error in OpenAI API call: {e}')
                error_parts = [
                    TextPart(
                        text=f'抱歉，處理請求時發生錯誤：{e!s}'
                    )
                ]
                await task_updater.add_artifact(error_parts)
                await task_updater.complete()
                break

        if iteration >= max_iterations:
            error_parts = [
                TextPart(
                    text='抱歉，請求已超過最大迭代次數。'
                )
            ]
            await task_updater.add_artifact(error_parts)
            await task_updater.complete()

    def _extract_function_schema(self, func):
        """從 Python 函式中提取 OpenAI 函式結構"""
        import inspect

        # 取得函式簽章
        sig = inspect.signature(func)

        # 取得文件字串
        docstring = inspect.getdoc(func) or ''

        # 從文件字串中提取描述和參數資訊
        lines = docstring.split('\n')
        description = lines[0] if lines else func.__name__

        # 建置參數結構
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            param_type = 'string'  # 預設類型
            param_description = f'參數 {param_name}'

            # 嘗試從註釋推斷類型
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = 'integer'
                elif param.annotation == float:
                    param_type = 'number'
                elif param.annotation == bool:
                    param_type = 'boolean'
                elif param.annotation == list:
                    param_type = 'array'
                elif param.annotation == dict:
                    param_type = 'object'

            # 檢查參數是否有預設值
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

            properties[param_name] = {
                'type': param_type,
                'description': param_description,
            }

        return {
            'name': func.__name__,
            'description': description,
            'parameters': {
                'type': 'object',
                'properties': properties,
                'required': required,
            },
        }

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        # 執行代理 (Agent) 直到完成
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        # 立即通知任務已提交。
        if not context.current_task:
            await updater.submit()
        await updater.start_work()

        # 從訊息部分提取文字
        message_text = ''
        for part in context.message.parts:
            if isinstance(part.root, TextPart):
                message_text += part.root.text

        await self._process_request(message_text, context, updater)
        logger.debug('[GitHub Agent] execute exiting')

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        # 理想情況下：終止任何進行中的任務。
        raise ServerError(error=UnsupportedOperationError())
