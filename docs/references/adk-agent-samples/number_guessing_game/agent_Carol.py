"""agent_Carol.py
卡蘿代理 (AgentCarol) – 視覺化或洗牌鮑伯猜測歷史的輔助代理。

卡蘿從鮑伯代理接收純文字 JSON 酬載，並根據請求回傳
(1) 一個目前為止猜測的人類可讀表格，或 (2) 一個條目被隨機洗牌的 JSON 列表。
此功能刻意保持簡單，以將重點放在 A2A 訊息流上。
"""

import json
import random
import uuid

from typing import Any

from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks.task_updater import TaskUpdater
from a2a.types import AgentCard, Part, TextPart
from a2a.utils.message import get_message_text
from config import AGENT_CAROL_PORT
from utils import try_parse_json
from utils.game_logic import process_history_payload
from utils.server import run_agent_blocking


# ------------------ 代理卡 (Agent card) ------------------

carol_skills = [
    {
        'id': 'history_visualiser',
        'name': '猜測歷史視覺化工具',
        'description': '產生猜測/回應歷史的格式化文字摘要以協助玩家。',
        'tags': ['視覺化', '示範'],
        'inputModes': ['text/plain'],
        'outputModes': ['text/plain'],
        'examples': ['[{"guess": 25, "response": "Go higher"}]'],
    },
    {
        'id': 'history_shuffler',
        'name': '猜測歷史洗牌工具',
        'description': '隨機洗牌提供的歷史列表中猜測/回應條目的順序並回傳 JSON。',
        'tags': ['洗牌', '示範'],
        'inputModes': ['text/plain'],
        'outputModes': ['text/plain'],
        'examples': [
            '{"action": "shuffle", "history": [{"guess": 25, "response": "Go higher"}]}'
        ],
    },
]

carol_card = AgentCard.model_validate(
    {
        'name': '卡蘿代理',
        'description': '以可讀的表格格式視覺化來自愛麗絲代理的猜測和提示歷史。',
        'url': f'http://localhost:{AGENT_CAROL_PORT}/a2a/v1',
        'preferredTransport': 'JSONRPC',
        'protocolVersion': '0.3.0',
        'version': '1.0.0',
        'capabilities': {
            'streaming': False,
            'pushNotifications': False,
            'stateTransitionHistory': False,
        },
        'defaultInputModes': ['text/plain'],
        'defaultOutputModes': ['text/plain'],
        'skills': carol_skills,
    }
)

# ------------------ SDK AgentExecutor 實作 ------------------


class HistoryHelperExecutor(AgentExecutor):
    """實作卡蘿視覺化/洗牌功能的 AgentExecutor。"""

    @staticmethod
    def _print_guesses(label: str, history: list[dict[str, Any]]) -> None:
        """工具程式：僅列印 *history* 中的數字猜測以供除錯。"""
        try:
            guesses = [int(item.get('guess', '?')) for item in history]
        except Exception:
            guesses = []
        print(f'[卡蘿] {label}: {guesses}')

    def __init__(self) -> None:
        # 保留最後的歷史列表，以便我們可以在後續訊息中重新洗牌。
        self._last_history: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # 內部輔助方法
    # ------------------------------------------------------------------

    async def _handle_followup(
        self, context: RequestContext, raw_text: str, event_queue: EventQueue
    ) -> None:
        """處理參考現有任務的後續訊息。"""
        task_id = context.task_id or (
            context.message.reference_task_ids[0]  # type: ignore[index]
            if context.message and context.message.reference_task_ids
            else str(uuid.uuid4())
        )
        updater = TaskUpdater(
            event_queue,
            task_id=task_id,
            context_id=context.context_id or str(uuid.uuid4()),
        )

        if raw_text.lower().startswith('well done'):
            print('[卡蘿] 收到「做得好」 – 正在完成任務')
            await updater.complete()
            return

        # 任何其他文字 → 再次洗牌並要求更多輸入
        print('[卡蘿] 再次洗牌並回傳列表')
        random.shuffle(self._last_history)
        # 回傳給鮑伯前進行除錯列印
        self._print_guesses('洗牌後的列表', self._last_history)
        response_text = json.dumps(self._last_history)
        await updater.add_artifact([Part(root=TextPart(text=response_text))])
        # 要求另一個輸入並發信號表示這是此次呼叫的最後一個事件
        await updater.requires_input(final=True)

    async def _handle_initial(
        self, raw_text: str, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """處理新對話中的第一則訊息。"""
        response_text = (
            process_history_payload(raw_text) if raw_text else '無效的輸入。'
        )

        # 如果提供了歷史列表，則記住它，以便稍後可以再次洗牌
        success, parsed = try_parse_json(raw_text)
        if (
            success
            and isinstance(parsed, dict)
            and parsed.get('action') == 'shuffle'
        ):
            hist = parsed.get('history', [])
            if isinstance(hist, list):
                self._last_history = hist

        task_id = context.task_id or str(uuid.uuid4())
        updater = TaskUpdater(
            event_queue,
            task_id=task_id,
            context_id=context.context_id or str(uuid.uuid4()),
        )
        # 發送初始回應前進行除錯列印
        try:
            if success and isinstance(parsed, list):
                self._print_guesses('初始列表', parsed)
            else:
                self._print_guesses('初始列表', self._last_history)
        except Exception:
            pass
        await updater.add_artifact([Part(root=TextPart(text=response_text))])
        # 要求鮑伯提供進一步的輸入
        await updater.requires_input(final=True)

    # ------------------------------------------------------------------
    # AgentExecutor 介面
    # ------------------------------------------------------------------

    async def execute(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """處理傳入的訊息並分派給適當的處理常式。"""
        raw_text = get_message_text(context.message) if context.message else ''
        is_followup = bool(
            context.message and context.message.reference_task_ids
        )

        if is_followup:
            await self._handle_followup(context, raw_text, event_queue)
        else:
            await self._handle_initial(raw_text, context, event_queue)

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """根據對等代理的明確請求取消正在進行的任務。"""
        if context.task_id:
            print(
                f'[卡蘿] 任務 {context.task_id} 已根據對等代理的請求取消'
            )
            updater = TaskUpdater(
                event_queue,
                task_id=context.task_id,
                context_id=context.context_id or str(uuid.uuid4()),
            )
            await updater.cancel()


if __name__ == '__main__':
    run_agent_blocking(
        name='卡蘿代理',
        port=AGENT_CAROL_PORT,
        agent_card=carol_card,
        executor=HistoryHelperExecutor(),
    )
