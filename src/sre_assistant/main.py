# src/sre_assistant/main.py
"""
SRE Assistant - FastAPI 服務入口點

本檔案負責：
1. 建立 FastAPI 應用程式。
2. 實例化核心的 SRE 工作流程 (EnhancedSREWorkflow)。
3. 定義 API 端點 (例如 /execute)，用於接收請求並觸發工作流程。
4. 使用 uvicorn 啟動服務。
"""

import asyncio
import uvicorn
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

from .workflow import EnhancedSREWorkflow
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# --- 1. 定義 API 的請求與回應模型 ---

class ExecuteRequest(BaseModel):
    """定義 /execute 端點的請求 Body 格式"""
    user_query: str
    session_id: str = "default_session"
    user_id: str = "api_user"

class ExecuteResponse(BaseModel):
    """定義 /execute 端點的回應格式"""
    status: str
    session_id: str
    message: str


# --- 2. 初始化應用程式和核心服務 ---

app = FastAPI(
    title="SRE Assistant API",
    description="用於與 SRE Assistant 智能代理工作流程互動的 API。",
    version="1.0.0"
)

# 實例化核心 SRE 工作流程
sre_workflow = EnhancedSREWorkflow()

# 實例化 ADK Runner 和會話服務 (暫時使用記憶體實現)
# TODO: TASK-P1-CORE-02 要求將其替換為持久化的 PostgreSQL 會話服務
session_service = InMemorySessionService()
runner = Runner(agent=sre_workflow, session_service=session_service, app_name="sre_assistant_app")


# --- 3. 定義非同步執行工作流程的函式 ---

async def run_workflow_in_background(request: ExecuteRequest):
    """
    一個非同步函式，用於在背景執行 ADK Runner。
    這避免了阻塞 API 回應。
    """
    print(f"Received request for session '{request.session_id}'. Query: '{request.user_query}'")
    
    # 創建或獲取會話
    session = await session_service.get_or_create_session(
        app_name=runner.app_name,
        user_id=request.user_id,
        session_id=request.session_id
    )
    
    # 創建 ADK 的內容物件
    user_content = types.Content(role="user", parts=[types.Part(text=request.user_query)])
    
    # 異步執行並迭代事件（實際的執行發生在此處）
    # 在真實應用中，可以將這些事件推送到 WebSocket 或日誌系統
    final_response = ""
    async for event in runner.run_async(session_id=session.id, new_message=user_content):
        if event.content and event.content.parts:
            text = "".join(part.text or "" for part in event.content.parts)
            if text:
                print(f"[{event.author}] {text}")
                if event.author == sre_workflow.name:
                    final_response = text

    print(f"Workflow for session '{request.session_id}' completed. Final response: {final_response}")


# --- 4. 定義 API 端點 ---

@app.post("/execute", response_model=ExecuteResponse)
async def execute_workflow(request: ExecuteRequest, background_tasks: BackgroundTasks):
    """
    接收使用者查詢並在背景啟動 SRE 工作流程。
    此端點會立即回傳，而實際的工作流程會在背景執行。
    """
    background_tasks.add_task(run_workflow_in_background, request)
    
    return ExecuteResponse(
        status="accepted",
        session_id=request.session_id,
        message="SRE workflow has been accepted and is running in the background."
    )

@app.get("/")
def read_root():
    """一個簡單的根端點，用於健康檢查或基本測試。"""
    return {"message": "SRE Assistant API is running."}


# --- 5. 服務啟動邏輯 ---

def start():
    """使用 uvicorn 啟動 FastAPI 應用程式。"""
    uvicorn.run(
        "sre_assistant.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )

if __name__ == "__main__":
    # 這使得我們可以透過 `python -m src.sre_assistant.main` 來啟動服務
    start()
