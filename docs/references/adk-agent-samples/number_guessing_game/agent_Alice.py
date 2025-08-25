"""agent_Alice.py
愛麗絲代理 (AgentAlice) – 玩具 A2A 猜數字遊戲示範中的評估者。

此代理在程序啟動時會挑選一個介於 1 到 100 之間的秘密整數，
並評估透過 A2A `message/send` 操作傳送過來的猜測。
對於每個猜測，它會回覆以下提示之一：

* ``"Go higher"`` – 猜測的數字比秘密數字小。
* ``"Go lower"``  – 猜測的數字比秘密數字大。
* ``"correct! attempts: <n>"`` – 猜測正確；``n`` 是到目前為止的嘗試次數。

此模組公開一個單一的公開可呼叫函式 :pyfunc:`alice_handler`，
它透過 A2A SDK 伺服器堆疊，使用 :pyfunc:`utils.server.run_agent_blocking` 執行，
並在 ``__main__`` 區塊中啟動的 HTTP 伺服器內執行。

此代理是使用官方的 A2A Python SDK 和一個小型的輔助層實作的
– 程式碼專注於遊戲邏輯，而非協定細節。
"""

import uuid

from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks.task_updater import TaskUpdater
from a2a.types import AgentCard, Part, TextPart
from a2a.utils.message import get_message_text
from config import AGENT_ALICE_PORT
from utils.game_logic import process_guess
from utils.server import run_agent_blocking


# ------------------ 代理卡 (Agent card) ------------------

alice_skills = [
    {
        'id': 'number_guess_evaluator',
        'name': '數字猜測評估器',
        'description': '根據一個秘密數字評估數字猜測 (1-100)，並回覆指引（更高/更低/正確）。',
        'tags': ['遊戲', '示範'],
        'inputModes': ['text/plain'],
        'outputModes': ['text/plain'],
        'examples': ['50'],
    }
]

alice_card_dict = {
    'name': '愛麗絲代理',
    'description': '透過挑選一個秘密數字並對猜測進行評分來主持猜數字遊戲。',
    'url': f'http://localhost:{AGENT_ALICE_PORT}/a2a/v1',
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
    'skills': alice_skills,
}
alice_card = AgentCard.model_validate(alice_card_dict)

# ------------------ 內部輔助工具 (Internal helpers) ------------------


class NumberGuessExecutor(AgentExecutor):
    """直接實作猜數字邏輯的 AgentExecutor。"""

    async def execute(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """處理從對等代理收到的新訊息。"""
        raw_text = get_message_text(context.message) if context.message else ''
        response_text = process_guess(raw_text)

        updater = TaskUpdater(
            event_queue,
            task_id=context.task_id or str(uuid.uuid4()),
            context_id=context.context_id or str(uuid.uuid4()),
        )
        # 告知客戶端任務已開始，然後發布答案，
        # 最後將其標記為已完成，以便鮑伯能看到一個附加了成品的完整任務物件。
        await updater.submit()
        await updater.add_artifact([Part(root=TextPart(text=response_text))])
        await updater.complete()

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """如果提供了參考任務，則拒絕該任務。"""
        if context.task_id:
            updater = TaskUpdater(
                event_queue,
                task_id=context.task_id,
                context_id=context.context_id or str(uuid.uuid4()),
            )
            await updater.reject()


if __name__ == '__main__':
    run_agent_blocking(
        name='愛麗絲代理',
        port=AGENT_ALICE_PORT,
        agent_card=alice_card,
        executor=NumberGuessExecutor(),
    )
