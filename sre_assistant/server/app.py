
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from ..core.assistant import SREAssistant
from ...adk_runtime.main import build_registry
from ..core.hitl import APPROVALS

app = FastAPI(title="SRE Assistant API")
registry = build_registry()
assistant = SREAssistant(registry)

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

@app.post("/api/v1/chat")
async def chat(req: ChatRequest):
    return await assistant.chat(req.message)

class ApprovalDecision(BaseModel):
    status: str  # approved | denied
    decided_by: str
    reason: str | None = None

@app.get("/api/v1/approvals/{aid}")
def get_approval(aid: int):
    a = APPROVALS.get(aid)
    if not a: raise HTTPException(status_code=404, detail="not found")
    return a.__dict__

@app.post("/api/v1/approvals/{aid}/decision")
def decide_approval(aid: int, body: ApprovalDecision):
    if body.status not in {"approved","denied"}:
        raise HTTPException(status_code=400, detail="invalid status")
    a = APPROVALS.decide(aid, status=body.status, decided_by=body.decided_by, reason=body.reason)
    return a.__dict__

try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
except Exception:
    pass
