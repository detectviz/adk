
# -*- coding: utf-8 -*-
# FastAPI 伺服器：API Key + RBAC + 限流；對話、HITL、RAG 端點。
from __future__ import annotations
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from ..core.assistant import SREAssistant
from ...adk_runtime.main import build_registry
from ..core.hitl import APPROVALS
from ..core.auth import require_api_key, require_role, AuthError
from ..core.rag import rag_create_entry, rag_update_status, rag_retrieve_tool

app = FastAPI(title="SRE Assistant API")
registry = build_registry()
assistant = SREAssistant(registry)

# 依賴：驗證 API Key 並返回角色
def auth_dep(x_api_key: str = Header(default="", alias="X-API-Key")) -> str:
    try:
        return require_api_key(x_api_key)
    except AuthError as e:
        raise HTTPException(status_code=401 if str(e)=="invalid api key" else 429, detail=str(e))

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

@app.post("/api/v1/chat")
async def chat(req: ChatRequest, role: str = Depends(auth_dep)):
    return await assistant.chat(req.message)

# HITL 模型
class ApprovalDecision(BaseModel):
    status: str  # approved | denied
    decided_by: str
    reason: str | None = None

@app.get("/api/v1/approvals/{aid}")
def get_approval(aid: int, role: str = Depends(auth_dep)):
    a = APPROVALS.get(aid)
    if not a: raise HTTPException(status_code=404, detail="not found")
    return a.__dict__

@app.post("/api/v1/approvals/{aid}/decision")
def decide_approval(aid: int, body: ApprovalDecision, role: str = Depends(auth_dep)):
    if not require_role(role, "operator"):
        raise HTTPException(status_code=403, detail="forbidden")
    if body.status not in {"approved","denied"}:
        raise HTTPException(status_code=400, detail="invalid status")
    a = APPROVALS.decide(aid, status=body.status, decided_by=body.decided_by, reason=body.reason)
    return a.__dict__

@app.post("/api/v1/approvals/{aid}/execute")
async def execute_approval(aid: int, role: str = Depends(auth_dep)):
    if not require_role(role, "operator"):
        raise HTTPException(status_code=403, detail="forbidden")
    res = await assistant.execute_approval(aid)
    if not res.get("ok"):
        raise HTTPException(status_code=400, detail=res)
    return res

# RAG 管理端點（簡化）：需要 admin
class RagCreate(BaseModel):
    title: str
    content: str
    tags: list[str] | None = None

@app.post("/api/v1/rag/entries")
def create_rag_entry(body: RagCreate, role: str = Depends(auth_dep)):
    if not require_role(role, "admin"):
        raise HTTPException(status_code=403, detail="forbidden")
    e = rag_create_entry(body.title, body.content, author="api", tags=body.tags or [], status="draft")
    return {"ok": True, "entry": e}

class RagApprove(BaseModel):
    status: str  # draft|approved|archived

@app.post("/api/v1/rag/entries/{entry_id}/status")
def set_rag_status(entry_id: int, body: RagApprove, role: str = Depends(auth_dep)):
    if not require_role(role, "admin"):
        raise HTTPException(status_code=403, detail="forbidden")
    e = rag_update_status(entry_id, body.status)
    if not e: raise HTTPException(status_code=404, detail="not found")
    return {"ok": True, "entry": e}

class RagQuery(BaseModel):
    query: str
    top_k: int = 5
    status_filter: list[str] | None = None

@app.post("/api/v1/rag/retrieve")
def rag_retrieve(body: RagQuery, role: str = Depends(auth_dep)):
    return rag_retrieve_tool(body.query, top_k=body.top_k, status_filter=body.status_filter)

# Prometheus 指標
try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
except Exception:
    pass
