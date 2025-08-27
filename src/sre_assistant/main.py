# src/sre_assistant/main.py
"""
此檔案是 SRE Assistant 的主應用程式伺服器，基於 FastAPI 框架。

它主要負責設定和運行一個符合 Agent-to-Agent (A2A) 通訊協定的伺服器，
並定義了用於接收、執行和串流回應 SRE 任務的 API 端點。

目前的實現包含了一些模擬的 A2A SDK 元件，這使得在沒有實際專有 SDK
的情況下，開發和測試伺服器結構成為可能。
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
# 使用絕對路徑以確保在作為可執行腳本時能正確解析模組。
from sre_assistant.workflow import SREWorkflow
from sre_assistant.a2a.protocol import StreamingChunk
from sre_assistant.config.config_manager import config_manager, SessionBackend
from sre_assistant.session.firestore_task_store import FirestoreTaskStore


# --- 模擬 ADK/A2A SDK 元件 ---
# 以下是模擬類別，用於在無法存取實際專有 A2A SDK 的情況下，
# 模擬其核心行為和資料結構，從而讓伺服器可以獨立運行和測試。

class MockA2AContext:
    """模擬 A2A 請求的上下文物件。"""
    def __init__(self, task_id, context_id, message, streaming=True):
        self.task_id = task_id
        self.context_id = context_id
        self.message = message
        self._supports_streaming = streaming

    def get_user_input(self) -> str:
        """獲取使用者的原始輸入查詢。"""
        return self.message

    def supports_streaming(self) -> bool:
        """檢查客戶端是否支援串流回應。"""
        return self._supports_streaming

class MockEventQueue:
    """模擬的事件隊列，用於將 Agent 產生的事件發送到外部系統。"""
    async def enqueue_event(self, event: Dict):
        """
        將一個事件加入到隊列中（此處僅為印出）。

        Args:
            event (Dict): 要加入隊列的事件物件。
        """
        print(f"事件已加入隊列: {event}")

class MockA2AStarletteApplication:
    """模擬的 A2A 應用程式，用於構建 FastAPI 伺服器。"""
    def __init__(self, agent_card, http_handler):
        self.app = FastAPI()
        self.agent_card = agent_card
        self.http_handler = http_handler
        self._setup_routes()

    def _setup_routes(self):
        """設定 FastAPI 的 API 路由。"""
        @self.app.get("/.well-known/agent.json")
        async def get_agent_card():
            """返回 Agent 的能力描述卡。"""
            return self.agent_card

        @self.app.post("/execute")
        async def execute(request: dict):
            """接收並開始執行一個新的 SRE 任務。"""
            context = MockA2AContext(
                task_id=str(uuid.uuid4()),
                context_id=str(uuid.uuid4()),
                message=request.get("query")
            )
            event_queue = MockEventQueue()
            # 非同步地開始執行任務，不會阻塞 API 回應
            asyncio.create_task(self.http_handler.agent_executor.execute(context, event_queue))
            return {"status": "execution_started", "task_id": context.task_id}

    def build(self) -> FastAPI:
        """返回構建好的 FastAPI 應用程式實例。"""
        return self.app

class DefaultRequestHandler:
    """模擬的預設請求處理器。"""
    def __init__(self, agent_executor, task_store):
        self.agent_executor = agent_executor
        self.task_store = task_store

class InMemoryTaskStore:
    """模擬的記憶體任務存儲，用於本地開發。"""
    pass

class AgentCard(BaseModel):
    """定義 Agent 能力描述卡的 Pydantic 模型。"""
    name: str
    version: str
    description: str
    url: str

# --- 核心實現 ---

class StreamingHandler:
    """
    處理 A2A 串流的核心邏輯。

    負責處理背壓 (backpressure) 和冪等性 (idempotency)，
    確保串流數據的可靠傳輸。
    """
    def __init__(self, event_queue: MockEventQueue, context: MockA2AContext):
        """
        初始化 StreamingHandler。

        Args:
            event_queue (MockEventQueue): 用於發送事件的隊列。
            context (MockA2AContext): 當前請求的上下文。
        """
        self.event_queue = event_queue
        self.context = context
        self.buffer: Deque[StreamingChunk] = deque(maxlen=100) # 有限緩衝區
        self.seen_tokens: set[str] = set() # 用於冪等性檢查

    async def handle_with_flow_control(self, chunk: StreamingChunk):
        """
        處理單個串流數據塊 (chunk)，包含冪等性檢查。

        Args:
            chunk (StreamingChunk): 要處理的數據塊。
        """
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
    """SRE Assistant 執行器，負責接收 A2A 請求並調用核心工作流程。"""
    def __init__(self, agent: SREWorkflow):
        """
        初始化執行器。

        Args:
            agent (SREWorkflow): 要執行的核心 SRE 工作流程代理。
        """
        self.agent = agent

    async def execute(self, context: MockA2AContext, event_queue: MockEventQueue):
        """
        根據上下文，選擇串流或批次模式來執行任務。

        Args:
            context (MockA2AContext): 請求上下文。
            event_queue (MockEventQueue): 事件隊列。
        """
        query = context.get_user_input()
        if context.supports_streaming():
            await self._execute_with_streaming(context, event_queue, query)
        else:
            await self._execute_batch(context, event_queue, query)

    async def _execute_with_streaming(self, context: MockA2AContext, event_queue: MockEventQueue, query: str):
        """（模擬）執行串流式回應。"""
        handler = StreamingHandler(event_queue, context)
        task_id = context.task_id
        print("開始串流執行...")
        i = 0
        # 注意: SREWorkflow 沒有 `execute_streaming` 方法，此處為模擬。
        async def mock_streaming_execution(q):
            for i in range(5):
                yield {"step": i+1, "query": q}
                await asyncio.sleep(0.1)

        async for chunk_data in mock_streaming_execution(query):
            i += 1
            chunk = StreamingChunk(
                type="partial_result", partial_result=chunk_data,
                progress=(i / 5.0), idempotency_token=f"sre_stream_{task_id}_{i}"
            )
            await handler.handle_with_flow_control(chunk)
        final_chunk = StreamingChunk(
            type="final_result", final_result={"status": "completed"},
            progress=1.0, idempotency_token=f"sre_stream_{task_id}_final"
        )
        await handler.handle_with_flow_control(final_chunk)
        await event_queue.enqueue_event({"event_type": "completed_task", "task_id": context.task_id})

    async def _execute_batch(self, context: MockA2AContext, event_queue: MockEventQueue, query: str):
        """（模擬）執行批次式回應。"""
        # 注意: SREWorkflow 沒有 `execute` 方法，此處為模擬。
        result = {"status": "completed", "final_answer": "batch mode result"}
        await event_queue.enqueue_event({"event_type": "completed_task", "task_id": context.task_id, "result": result})

def create_agent_card(host="0.0.0.0", port=8080) -> AgentCard:
    """
    建立 AgentCard，用於向其他 Agent 宣告自己的能力和端點。

    Returns:
        AgentCard: 包含 Agent 描述資訊的 Pydantic 模型。
    """
    return AgentCard(
        name="sre_assistant", version="1.0.0",
        description="由 AI 驅動的 SRE 助理，用於自動化操作和維護",
        url=os.getenv("HOST_OVERRIDE") or f"http://{host}:{port}/",
    )

def get_task_store():
    """
    根據配置創建並返回對應的 TaskStore 實例。
    TaskStore 用於持久化長時間運行的任務狀態。

    Raises:
        ValueError: 如果配置為 Firestore 但缺少必要的專案 ID。

    Returns:
        一個 TaskStore 實例 (FirestoreTaskStore 或 InMemoryTaskStore)。
    """
    if config_manager.config.session_backend == SessionBackend.FIRESTORE:
        project_id = config_manager.config.firestore_project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError("Firestore 後端需要在設定檔中提供 'firestore_project_id' 或設置 GOOGLE_CLOUD_PROJECT 環境變數。")
        return FirestoreTaskStore(project_id=project_id, collection=config_manager.config.firestore_collection)
    return InMemoryTaskStore()

# --- 應用程式設定與實例化 ---

# 實例化主工作流程代理
sre_agent = SREWorkflow(config=config_manager.config.model_dump())

# 組合 A2A 伺服器所需的核心元件
executor = SREAssistantExecutor(agent=sre_agent)
request_handler = DefaultRequestHandler(agent_executor=executor, task_store=get_task_store())
server = MockA2AStarletteApplication(agent_card=create_agent_card(), http_handler=request_handler)

# 最終的 FastAPI 應用程式實例
app = server.build()


# --- 主執行區塊 ---
if __name__ == "__main__":
    """
    當此檔案作為主腳本直接執行時，啟動 uvicorn 伺服器。
    這使得可以透過 `python -m src.sre_assistant.main` 來啟動服務。
    """
    uvicorn.run(app, host="0.0.0.0", port=8080)
