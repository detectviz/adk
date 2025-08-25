import json
import os
import random
from typing import Optional

from collections.abc import AsyncIterable
from typing import Any

from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types


# Local cache of created request_ids for demo purposes.
request_ids = set()


def create_request_form(
    date: Optional[str] = None,
    amount: Optional[str] = None,
    purpose: Optional[str] = None,
) -> dict[str, Any]:
    """為員工建立一個請求表單以供填寫。

    Args:
        date (str): 請求的日期。可以是空字串。
        amount (str): 請求的金額。可以是空字串。
        purpose (str): 請求的目的。可以是空字串。

    Returns:
        dict[str, Any]: 一個包含請求表單資料的字典。
    """
    request_id = 'request_id_' + str(random.randint(1000000, 9999999))
    request_ids.add(request_id)
    return {
        'request_id': request_id,
        'date': '<交易日期>' if not date else date,
        'amount': '<交易金額>' if not amount else amount,
        'purpose': '<業務理由/交易目的>'
        if not purpose
        else purpose,
    }


def return_form(
    form_request: dict[str, Any],
    tool_context: ToolContext,
    instructions: Optional[str] = None,
) -> dict[str, Any]:
    """傳回一個結構化的 json 物件，表示要完成的表單。

    Args:
        form_request (dict[str, Any]): 請求表單資料。
        tool_context (ToolContext): 工具運作的上下文。
        instructions (str): 處理表單的說明。可以是空字串。

    Returns:
        dict[str, Any]: 表單回應的 JSON 字典。
    """
    if isinstance(form_request, str):
        form_request = json.loads(form_request)

    tool_context.actions.skip_summarization = True
    tool_context.actions.escalate = True
    form_dict = {
        'type': 'form',
        'form': {
            'type': 'object',
            'properties': {
                'date': {
                    'type': 'string',
                    'format': 'date',
                    'description': '費用日期',
                    'title': '日期',
                },
                'amount': {
                    'type': 'string',
                    'format': 'number',
                    'description': '費用金額',
                    'title': '金額',
                },
                'purpose': {
                    'type': 'string',
                    'description': '費用目的',
                    'title': '目的',
                },
                'request_id': {
                    'type': 'string',
                    'description': '請求 ID',
                    'title': '請求 ID',
                },
            },
            'required': list(form_request.keys()),
        },
        'form_data': form_request,
        'instructions': instructions,
    }
    return json.dumps(form_dict)


def reimburse(request_id: str) -> dict[str, Any]:
    """根據給定的 request_id 將款項報銷給員工。"""
    if request_id not in request_ids:
        return {
            'request_id': request_id,
            'status': '錯誤：無效的 request_id。',
        }
    return {'request_id': request_id, 'status': '已核准'}


class ReimbursementAgent:
    """處理報銷請求的代理 (Agent)。"""

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self):
        self._agent = self._build_agent()
        self._user_id = 'remote_agent'
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def get_processing_message(self) -> str:
        return '正在處理報銷請求...'

    def _build_agent(self) -> LlmAgent:
        """為報銷代理 (Agent) 建立 LLM 代理 (Agent)。"""
        LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini/gemini-2.0-flash-001')
        return LlmAgent(
            model=LiteLlm(model=LITELLM_MODEL),
            name='reimbursement_agent',
            description=(
                '此代理 (Agent) 根據員工提供的報銷金額和目的，處理報銷流程。'
            ),
            instruction="""
    你是一個處理員工報銷流程的代理 (Agent)。

    當你收到報銷請求時，應首先使用 create_request_form() 建立一個新的請求表單。僅當使用者提供預設值時才提供，否則使用空字串作為預設值。
      1. '日期'：交易日期。
      2. '金額'：交易的美元金額。
      3. '業務理由/目的'：報銷的原因。

    建立表單後，你應傳回呼叫 return_form 的結果，並附上來自 create_request_form 呼叫的表單資料。

    從使用者那裡收到填寫完畢的表單後，你應檢查表單是否包含所有必要資訊：
      1. '日期'：交易日期。
      2. '金額'：所請求報銷的金額值。
      3. '業務理由/目的'：報銷的項目/物件/產物。

    如果你沒有所有資訊，應直接透過呼叫 request_form 方法拒絕請求，並提供缺少的欄位。


    對於有效的報銷請求，你可以接著使用 reimburse() 來為員工報銷。
      * 在你的回應中，你應包含 request_id 和報銷請求的狀態。

    """,
            tools=[
                create_request_form,
                reimburse,
                return_form,
            ],
        )

    async def stream(self, query, session_id) -> AsyncIterable[dict[str, Any]]:
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id,
        )
        content = types.Content(
            role='user', parts=[types.Part.from_text(text=query)]
        )
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                state={},
                session_id=session_id,
            )
        async for event in self._runner.run_async(
            user_id=self._user_id, session_id=session.id, new_message=content
        ):
            if event.is_final_response():
                response = ''
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                ):
                    response = '\n'.join(
                        [p.text for p in event.content.parts if p.text]
                    )
                elif (
                    event.content
                    and event.content.parts
                    and any(
                        [
                            True
                            for p in event.content.parts
                            if p.function_response
                        ]
                    )
                ):
                    response = next(
                        p.function_response.model_dump()
                        for p in event.content.parts
                    )
                yield {
                    'is_task_complete': True,
                    'content': response,
                }
            else:
                yield {
                    'is_task_complete': False,
                    'updates': self.get_processing_message(),
                }
