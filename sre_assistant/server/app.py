
# -*- coding: utf-8 -*-
# FastAPI 伺服器（v14）：
# - /api/v1/chat：一次性呼叫（阻塞），供簡單用例
# - /api/v1/chat_sse：SSE 串流事件（建議與前端配套），可接收 adk_request_credential
# - /api/v1/resume_sse：提交 FunctionResponse（如 OAuth 回調/核可資訊）後繼續串流
from __future__ import annotations
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
import json
from ..core.telemetry import init_tracing
from ..core.profiling_pyroscope import init_pyroscope
from ..core.otel_logging import init_otel_logging
init_tracing()
init_pyroscope()
init_otel_logging()

from ..adk_app.runtime import RUNNER, run_chat  # Runner 與同步封裝
from ..core.auth import require_api_key, AuthError
from ..core.debounce import DEBOUNCER
from ..core.persistence import DB
from ..core.slo_guard import SLOGuardian

from google.genai.types import Content, Part, FunctionResponse

app = FastAPI(title="SRE Assistant API (ADK Runner + SSE)")
slo_guard = SLOGuardian(p95_ms=30000)

def auth_dep(x_api_key: str = Header(default="", alias="X-API-Key")) -> str:
    try:
        return require_api_key(x_api_key)
    except AuthError as e:
        raise HTTPException(status_code=401 if str(e)=="invalid api key" else 429, detail=str(e))

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str = "user"

@app.get("/health/ready")
def health_ready():
    try:
        DB.list_decisions(limit=1)
        return {"ok": True, "db": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"db not ready: {e}")

@app.post("/api/v1/chat")
def chat(req: ChatRequest, _: str = Depends(auth_dep)):
    if not DEBOUNCER.allow_msg(req.message, req.session_id):
        raise HTTPException(status_code=409, detail="debounced")
    res = run_chat(user_id=req.user_id, session_id=req.session_id, message=req.message)
    adv = slo_guard.evaluate(res["metrics"]["duration_ms"])
    res["slo_advice"] = adv.__dict__
    return res

# --- SSE 串流工具函式 ---
async def _stream_events(user_id: str, session_id: str, content: Content) -> AsyncGenerator[bytes, None]:
    """將 ADK Runner 的事件以 SSE 形式回拋前端。"""
    async for event in RUNNER.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # 以最簡 JSON 形式傳遞（前端自行判斷是否為 adk_request_credential）
        yield f"data: {json.dumps(event.to_dict() if hasattr(event, 'to_dict') else event.__dict__, ensure_ascii=False)}\n\n".encode("utf-8")

@app.get("/api/v1/chat_sse")
async def chat_sse(message: str, session_id: str, user_id: str = "user", _: str = Depends(auth_dep)):
    """以 SSE 串流事件：初始對話。"""
    content = Content(parts=[Part(text=message)], role="user")
    return StreamingResponse(_stream_events(user_id=user_id, session_id=session_id, content=content), media_type="text/event-stream")

@app.get("/api/v1/resume_sse")
async def resume_sse(function_call_id: str, session_id: str, user_id: str = "user", auth_response_uri: str = "", redirect_uri: str = "", _: str = Depends(auth_dep)):
    """以 SSE 串流事件：提交 FunctionResponse 後繼續執行。
    - 針對 'adk_request_credential' 事件：依官方規範，需要回傳相同 name 與原 function_call_id
    - 這裡以 OAuth 類型欄位命名（與官方教學一致）；核可/審批場景可沿用此欄位承載
    """
    auth_config = {
        "exchanged_auth_credential": {
            "oauth2": {
                "auth_response_uri": auth_response_uri,
                "redirect_uri": redirect_uri
            }
        }
    }
    content = Content(parts=[
        Part(function_response=FunctionResponse(
            id=function_call_id,
            name="adk_request_credential",
            response=auth_config
        ))
    ], role="user")
    return StreamingResponse(_stream_events(user_id=user_id, session_id=session_id, content=content), media_type="text/event-stream")

# 提供簡單核可頁（教學用，實務應用自家前端處理 OAuth/HITL UI）
@app.get("/ui/approve.html")
def approve_page():
    html = """
    <!doctype html>
    <html><head><meta charset="utf-8"><title>核可測試頁</title></head>
    <body>
      <h3>高風險操作核可</h3>
      <p>此頁僅示意。實務請以自家 OAuth/審批頁替代。</p>
      <button onclick="approved()">核可</button>
      <script>
        function approved(){
          const uri = location.href + "?approved=true";
          // 模擬 OAuth 回跳：將完整 URL 當作 auth_response_uri 回傳
          alert("請回到原前端並提交此 URL 作為 auth_response_uri:\n\n" + uri);
        }
      </script>
    </body></html>
    """
    return HTMLResponse(html)
