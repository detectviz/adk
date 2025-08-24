# type: ignore

import json
import logging
import os
import re

from collections.abc import AsyncIterable
from typing import Any

from a2a_mcp.common.agent_runner import AgentRunner
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import get_mcp_server_config, init_api_key
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.genai import types as genai_types


logger = logging.getLogger(__name__)


class TravelAgent(BaseAgent):
    """由 ADK 支援的旅行代理。"""

    def __init__(self, agent_name: str, description: str, instructions: str):
        init_api_key()

        super().__init__(
            agent_name=agent_name,
            description=description,
            content_types=['text', 'text/plain'],
        )

        logger.info(f'初始化 {self.agent_name}')

        self.instructions = instructions
        self.agent = None

    async def init_agent(self):
        logger.info(f'正在初始化 {self.agent_name} 的元資料')
        config = get_mcp_server_config()
        logger.info(f'MCP 伺服器 url={config.url}')
        tools = await MCPToolset(
            connection_params=SseServerParams(url=config.url)
        ).get_tools()

        for tool in tools:
            logger.info(f'已載入工具 {tool.name}')
        generate_content_config = genai_types.GenerateContentConfig(
            temperature=0.0
        )
        LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini/gemini-2.0-flash')
        self.agent = Agent(
            name=self.agent_name,
            instruction=self.instructions,
            model=LiteLlm(model=LITELLM_MODEL),
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            generate_content_config=generate_content_config,
            tools=tools,
        )
        self.runner = AgentRunner()

    async def invoke(self, query, session_id) -> dict:
        logger.info(f'正在為會話 {session_id} 運行 {self.agent_name}')

        raise NotImplementedError('請使用串流函式')

    async def stream(
        self, query, context_id, task_id
    ) -> AsyncIterable[dict[str, Any]]:
        logger.info(
            f'正在為會話 {context_id} {task_id} - {query} 運行 {self.agent_name} 串流'
        )

        if not query:
            raise ValueError('查詢不能為空')

        if not self.agent:
            await self.init_agent()
        async for chunk in self.runner.run_stream(
            self.agent, query, context_id
        ):
            logger.info(f'收到的區塊 {chunk}')
            if isinstance(chunk, dict) and chunk.get('type') == 'final_result':
                response = chunk['response']
                yield self.get_agent_response(response)
            else:
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': f'{self.agent_name}: 正在處理請求...',
                }

    def format_response(self, chunk):
        patterns = [
            r'```\n(.*?)\n```',
            r'```json\s*(.*?)\s*```',
            r'```tool_outputs\s*(.*?)\s*```',
        ]

        for pattern in patterns:
            match = re.search(pattern, chunk, re.DOTALL)
            if match:
                content = match.group(1)
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return content
        return chunk

    def get_agent_response(self, chunk):
        logger.info(f'回應類型 {type(chunk)}')
        data = self.format_response(chunk)
        logger.info(f'格式化後的回應 {data}')
        try:
            if isinstance(data, dict):
                if 'status' in data and data['status'] == 'input_required':
                    return {
                        'response_type': 'text',
                        'is_task_complete': False,
                        'require_user_input': True,
                        'content': data['question'],
                    }
                return {
                    'response_type': 'data',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': data,
                }
            return_type = 'data'
            try:
                data = json.loads(data)
                return_type = 'data'
            except Exception as json_e:
                logger.error(f'Json 轉換錯誤 {json_e}')
                return_type = 'text'
            return {
                'response_type': return_type,
                'is_task_complete': True,
                'require_user_input': False,
                'content': data,
            }
        except Exception as e:
            logger.error(f'在 get_agent_response 中發生錯誤: {e}')
            return {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': '無法完成預訂/任務。請再試一次。',
            }
