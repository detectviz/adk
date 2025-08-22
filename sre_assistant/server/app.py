# ADK 標準 FastAPI 伺服器介面層
from __future__ import annotations
import uuid
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

# 匯入已配置好的 ADK Runner 和標準認證模組
from ..adk_app.runtime import RUNNER
from ..core.adk_auth import get_auth_context, SRERole, require_roles

# 初始化 FastAPI 應用
app = FastAPI(
    title="SRE Assistant - ADK Standard Server",
    description="一個遵循 ADK 官方規範的標準化伺服器介面。"
)

class ChatRequest(BaseModel):
    """聊天請求的標準資料結構。"""
    message: str
    session_id: Optional[str] = None

async def stream_run_events(message: str, session_id: str):
    """將 ADK Runner 的事件非同步地轉換為 SSE 格式的 byte 字串。"""
    # 使用 runner.stream() 來處理請求並取得非同步事件產生器
    async for event in RUNNER.stream(message, session_id=session_id):
        # 將每個事件物件序列化為 JSON 字串
        event_data = json.dumps(event.to_dict(), ensure_ascii=False)
        # 遵循 SSE 格式: "data: {...}\n\n"
        yield f"data: {event_data}\n\n".encode("utf-8")

@app.post("/api/v1/chat/stream")
@require_roles([SRERole.VIEWER, SRERole.OPERATOR, SRERole.ADMIN])
async def chat_stream(
    req: ChatRequest,
    auth_context: dict = Depends(get_auth_context) # 注入認證上下文
):
    """標準的聊天串流端點。
    
    接收使用者訊息，呼叫 ADK Runner，並以 Server-Sent Events (SSE) 格式串流回傳所有事件。
    客戶端（如官方 Dev UI）可以監聽這些事件來即時更新介面。
    """
    try:
        # 如果客戶端未提供 session_id，則建立一個新的
        session_id = req.session_id or str(uuid.uuid4())
        # 回傳一個 StreamingResponse，其內容來自我們的非同步事件產生器
        return StreamingResponse(
            stream_run_events(req.message, session_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        # 在發生錯誤時回傳標準的 HTTP 錯誤
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """提供一個簡單的健康檢查端點。"""
    return {"status": "ok"}