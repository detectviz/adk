# src/sre_assistant/main.py
"""
此檔案是 SRE Assistant 的主應用程式伺服器，基於 FastAPI 框架。

它主要負責設定和運行一個符合 Agent-to-Agent (A2A) 通訊協定的伺服器，
並定義了用於接收、執行和串流回應 SRE 任務的 API 端點。
"""

import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# --- 專案級別匯入 ---
# 使用了新的 SREWorkflowFactory 和實際的執行函式
from sre_assistant.workflow import SREWorkflowFactory, run_sre_workflow_and_simulate_human

# --- Pydantic 模型 ---

class ExecuteRequest(BaseModel):
    """定義 /execute 端點的請求主體。"""
    action: str
    reason: str

class AgentCard(BaseModel):
    """定義 Agent 能力描述卡的 Pydantic 模型。"""
    name: str
    version: str
    description: str
    url: str

# --- 核心 FastAPI 應用程式 ---

app = FastAPI(
    title="SRE Assistant API",
    description="由 AI 驅動的 SRE 助理，用於自動化操作和維護",
    version="1.0.0"
)

# --- API 端點 ---

@app.get("/.well-known/agent.json", response_model=AgentCard)
async def get_agent_card():
    """返回 Agent 的能力描述卡。"""
    host = os.getenv("HOST_OVERRIDE", "localhost")
    port = os.getenv("PORT_OVERRIDE", "8080")
    return AgentCard(
        name="sre_assistant",
        version="1.0.0",
        description="由 AI 驅動的 SRE 助理，用於自動化操作和維護",
        url=f"http://{host}:{port}/",
    )

@app.post("/execute")
async def execute(request: ExecuteRequest):
    """
    接收並開始執行一個新的 SRE 任務，並模擬 HITL 流程。
    """
    try:
        # 非同步地開始執行任務，不會阻塞 API 回應。
        # 這會觸發包含 HITL 流程的完整工作流程。
        print(f"收到執行請求: action={request.action}, reason={request.reason}")
        asyncio.create_task(run_sre_workflow_and_simulate_human(
            action=request.action,
            reason=request.reason
        ))
        # API 立即回傳，告知任務已在背景開始。
        return {"status": "execution_started", "action": request.action, "reason": request.reason}
    except Exception as e:
        # 處理潛在的錯誤
        raise HTTPException(status_code=500, detail=str(e))


# --- 主執行區塊 ---
if __name__ == "__main__":
    """
    當此檔案作為主腳本直接執行時，啟動 uvicorn 伺服器。
    這使得可以透過 `python -m src.sre_assistant.main` 來啟動服務。
    """
    uvicorn.run(app, host="0.0.0.0", port=8080)
