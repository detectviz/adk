
# 檔案：sre_assistant/server/events.py
# 角色：簡易事件匯流排（SSE 用）。每個事件結構遵循 ADK: request_credential 協議。
from __future__ import annotations
import asyncio
from typing import AsyncIterator, Dict, Any

class EventBus:
    """
    {ts}
    函式用途：非持久化的簡易事件匯流排。支援多個 listener 並發送 dict 事件。
    參數說明：無。
    回傳：無。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    def __init__(self):
        self._q: asyncio.Queue[dict] = asyncio.Queue()

    async def publish(self, ev: Dict[str, Any]) -> None:
        await self._q.put(ev)

    async def subscribe(self) -> AsyncIterator[Dict[str, Any]]:
        while True:
            ev = await self._q.get()
            yield ev

BUS = EventBus()
