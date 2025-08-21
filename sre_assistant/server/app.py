
# -*- coding: utf-8 -*-
# FastAPI 伺服器：以 ADK Runner（InMemoryRunner + SessionService）執行對話。
# - 對齊官方 runtime/sessions/events API 與最佳實踐
from __future__ import annotations
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from ..core.telemetry import init_tracing
init_tracing()

from ..adk_app.runtime import run_chat  # 以 Runner.run_async 實作對話流程
from ..core.auth import require_api_key, AuthError
from ..core.debounce import DEBOUNCER
from ..core.persistence import DB
from ..core.slo_guard import SLOGuardian

app = FastAPI(title="SRE Assistant API (ADK Runner)")
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
