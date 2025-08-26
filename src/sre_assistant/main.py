# src/sre_assistant/main.py
"""
此檔案包含 SRE Assistant 的主應用程式伺服器 (FastAPI)。
它負責設定 A2A (Agent-to-Agent) 伺服器並定義 API 端點。
此邏輯已從 __init__.py 移至此處，以防止循環匯入錯誤。
"""

import os
import uuid
import asyncio
from datetime import datetime
from collections import deque
from typing import Literal, Optional, Dict, Deque

from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

# --- 專案級別匯入 ---
# 由於這是一個套件內的可執行腳本，我們使用絕對路徑匯入。
from sre_assistant.workflow import SREWorkflow
from sre_assistant.a2a.protocol import StreamingChunk
from sre_assistant.config.config_manager import config_manager, SessionBackend
from sre_assistant.session.firestore_task_store import FirestoreTaskStore


# --- 模擬 ADK/A2A SDK 元件 ---
# 這些是模擬類別，讓伺服器結構在無法存取實際專有 SDK 的情況下也能運行。

class MockA2AContext:
    def __init__(self, task_id, context_id, message, streaming=True):
        self.task_id = task_id
        self.context_id = context_id
        self.message = message
        self._supports_streaming = streaming

    def get_user_input(self):
        return self.message

    def supports_streaming(self):
        return self._supports_streaming

class MockEventQueue:
    async def enqueue_event(self, event):
        # 模擬將事件加入隊列
        print(f"事件已加入隊列: {event}")

class MockA2AStarletteApplication:
    def __init__(self, agent_card, http_handler):
        self.app = FastAPI()
        self.agent_card = agent_card
        self.http_handler = http_handler
        self._setup_routes()

    def _setup_routes(self):
        @self.app.get("/.well-known/agent.json")
        async def get_agent_card():
            return self.agent_card

        @self.app.post("/execute")
        async def execute(request: dict):
            # 模擬執行流程
            context = MockA2AContext(
                task_id=str(uuid.uuid4()),
                context_id=str(uuid.uuid4()),
                message=request.get("query")
            )
            event_queue = MockEventQueue()
            await self.http_handler.agent_executor.execute(context, event_queue)
            return {"status": "execution_started"}

    def build(self):
        return self.app

class DefaultRequestHandler:
    def __init__(self, agent_executor, task_store):
        self.agent_executor = agent_executor
        self.task_store = task_store

class InMemoryTaskStore:
    pass

class AgentCard(BaseModel):
    name: str
    version: str
    description: str
    url: str

# --- 核心實現 ---

class StreamingHandler:
    """處理 A2A Streaming 的背壓 (backpressure) 和冪等性 (idempotency)"""
    def __init__(self, event_queue: MockEventQueue, context: MockA2AContext):
        self.event_queue = event_queue
        self.context = context
        self.buffer: Deque[StreamingChunk] = deque(maxlen=100)
        self.seen_tokens: set[str] = set()

    async def handle_with_flow_control(self, chunk: StreamingChunk):
        if chunk.idempotency_token in self.seen_tokens:
            print(f"跳過重複的 chunk: {chunk.idempotency_token}")
            return

        self.seen_tokens.add(chunk.idempotency_token)
        self.buffer.append(chunk)

        await self.event_queue.enqueue_event({
            "event_type": "streaming_update",
            "task_id": self.context.task_id,
            "chunk": chunk.model_dump_json()
        })

class SREAssistantExecutor:
    """SRE Assistant 執行器，用於處理 A2A 請求"""
    def __init__(self, agent: SREWorkflow):
        self.agent = agent

    async def execute(self, context: MockA2AContext, event_queue: MockEventQueue):
        query = context.get_user_input()
        if context.supports_streaming():
            await self._execute_with_streaming(context, event_queue, query)
        else:
            await self._execute_batch(context, event_queue, query)

    async def _execute_with_streaming(self, context: MockA2AContext, event_queue: MockEventQueue, query: str):
        handler = StreamingHandler(event_queue, context)
        task_id = context.task_id
        print("開始串流執行...")
        i = 0
        # 注意: SREWorkflow 沒有 `execute_streaming` 方法。這是一個模擬。
        async def mock_streaming_execution(q):
            for i in range(5):
                yield {"step": i+1, "query": q}
                await asyncio.sleep(0.1)

        async for chunk_data in mock_streaming_execution(query):
            i += 1
            chunk = StreamingChunk(
                type="partial_result",
                partial_result=chunk_data,
                progress=(i / 5.0),
                idempotency_token=f"sre_stream_{task_id}_{i}"
            )
            await handler.handle_with_flow_control(chunk)

        final_chunk = StreamingChunk(
            type="final_result",
            final_result={"status": "completed"},
            progress=1.0,
            idempotency_token=f"sre_stream_{task_id}_final"
        )
        await handler.handle_with_flow_control(final_chunk)

        await event_queue.enqueue_event({
            "event_type": "completed_task",
            "task_id": context.task_id
        })

    async def _execute_batch(self, context: MockA2AContext, event_queue: MockEventQueue, query: str):
        # 注意: SREWorkflow 沒有 `execute` 方法。這是一個模擬。
        result = {"status": "completed", "final_answer": "batch mode result"}
        await event_queue.enqueue_event({
            "event_type": "completed_task",
            "task_id": context.task_id,
            "result": result
        })

def create_agent_card(host="0.0.0.0", port=8080) -> AgentCard:
    """建立 AgentCard，定義 SRE Assistant 的能力"""
    return AgentCard(
        name="sre_assistant",
        version="1.0.0",
        description="由 AI 驅動的 SRE 助理，用於自動化操作和維護",
        url=os.getenv("HOST_OVERRIDE") or f"http://{host}:{port}/",
    )

# --- 應用程式設定 ---

def get_task_store():
    """根據配置創建並返回對應的 TaskStore 實例"""
    if config_manager.config.session_backend == SessionBackend.FIRESTORE:
        project_id = config_manager.config.firestore_project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError(
                "Firestore 後端需要在設定檔中提供 'firestore_project_id' "
                "或設置 GOOGLE_CLOUD_PROJECT 環境變數。"
            )
        return FirestoreTaskStore(
            project_id=project_id,
            collection=config_manager.config.firestore_collection
        )
    return InMemoryTaskStore()

# 實例化主工作流程
sre_agent = SREWorkflow(config=config_manager.config.model_dump())

# 組合 A2A 伺服器元件
executor = SREAssistantExecutor(agent=sre_agent)
request_handler = DefaultRequestHandler(
    agent_executor=executor,
    task_store=get_task_store(),
)
server = MockA2AStarletteApplication(
    agent_card=create_agent_card(),
    http_handler=request_handler
)
app = server.build()


# --- 用於直接執行的主函數 ---
if __name__ == "__main__":
    import asyncio
    uvicorn.run(app, host="0.0.0.0", port=8080)
