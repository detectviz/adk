# type: ignore

import logging

from collections.abc import AsyncIterable
from typing import Any, Literal

from a2a_mcp.common import prompts
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.types import TaskList
from a2a_mcp.common.utils import init_api_key
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field


memory = MemorySaver()
logger = logging.getLogger(__name__)


class ResponseFormat(BaseModel):
    """以這種格式回應使用者。"""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    question: str = Field(
        description='產生計畫所需的使用者輸入'
    )
    content: TaskList = Field(
        description='計畫產生後的任務列表'
    )


class LangGraphPlannerAgent(BaseAgent):
    """由 LangGraph 支援的規劃器代理。"""

    def __init__(self):
        init_api_key()

        logger.info('正在初始化 LanggraphPlannerAgent')

        super().__init__(
            agent_name='PlannerAgent',
            description='將使用者請求分解為可執行的任務',
            content_types=['text', 'text/plain'],
        )

        self.model = ChatGoogleGenerativeAI(
            model='gemini-2.0-flash', temperature=0.0
        )

        self.graph = create_react_agent(
            self.model,
            checkpointer=memory,
            prompt=prompts.PLANNER_COT_INSTRUCTIONS,
            # prompt=prompts.TRIP_PLANNER_INSTRUCTIONS_1,
            response_format=ResponseFormat,
            tools=[],
        )

    def invoke(self, query, sessionId) -> str:
        config = {'configurable': {'thread_id': sessionId}}
        self.graph.invoke({'messages': [('user', query)]}, config)
        return self.get_agent_response(config)

    async def stream(
        self, query, sessionId, task_id
    ) -> AsyncIterable[dict[str, Any]]:
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': sessionId}}

        logger.info(
            f'正在為會話 {sessionId} {task_id} 運行 LanggraphPlannerAgent 串流，輸入為 {query}'
        )

        for item in self.graph.stream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if isinstance(message, AIMessage):
                yield {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': message.content,
                }
        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(
            structured_response, ResponseFormat
        ):
            if (
                structured_response.status == 'input_required'
                # and structured_response.content.tasks
            ):
                return {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.question,
                }
            if structured_response.status == 'error':
                return {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.question,
                }
            if structured_response.status == 'completed':
                return {
                    'response_type': 'data',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.content.model_dump(),
                }
        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': '我們目前無法處理您的請求。請再試一次。',
        }
