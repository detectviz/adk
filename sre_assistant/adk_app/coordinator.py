
# -*- coding: utf-8 -*-
# 以 Google ADK 官方風格實作之協調器（Coordinator）：
# - 採用 LoopAgent + BuiltInPlanner 作為頂層協調器
# - 主代理（Main LlmAgent）負責規劃、路由與最終回覆
# - 子專家代理（Diagnostic/Remediation/Postmortem）以 AgentTool 方式掛載
# - 工具以 FunctionTool 顯式聲明（Pydantic 模型定義 I/O），避免隱式裝飾器魔法
#
# 注意：本檔案假設執行環境已安裝 Google ADK（google.adk.*）。若未安裝將拋出 ImportError。
from __future__ import annotations
import os, time, json
from typing import Any, List
from pydantic import BaseModel, Field

# --- 匯入 ADK 核心類別 ---
from google.adk.agents import LoopAgent, LlmAgent
from google.adk.planners import BuiltInPlanner
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.function_tool import FunctionTool
# RAG 官方工具（可選，若未配置 RAG_CORPUS 則仍可用 pgvector 工具）
try:
    from google.genai import rag as vertex_rag
    from google.adk.tools.rag import VertexAiRagRetrieval
    _HAS_VERTEX_RAG = True
except Exception:
    _HAS_VERTEX_RAG = False

# --- 匯入既有的外部系統實作（Prometheus/K8s/Grafana/RAG pgvector） ---
from ..tools.promql import promql_query_tool as _promql_impl
from ..tools.k8s_long_running import k8s_rollout_restart_long_running_tool
from ..tools.grafana import grafana_create_dashboard_tool as _grafana_create_impl
from ..tools.knowledge_ingestion import knowledge_ingestion_tool as _ingest_impl
from ..tools.rag_retrieve import rag_retrieve_vector_tool as _rag_vector_impl

# === Pydantic I/O Schema 定義（明確介面，利於長期維護）===

class PromQueryArgs(BaseModel):
    # PromQL 查詢參數：查詢語句與時間範圍（RFC3339 start,end,step）
    query: str = Field(..., description="PromQL 查詢語句")
    range: str = Field(..., description="start,end,step 組合，RFC3339 與步長")

class PromQueryRet(BaseModel):
    # 查詢結果：多序列與統計資訊
    series: list[dict] = Field(default_factory=list, description="時間序列結果陣列")
    stats: dict | None = Field(default=None, description="統計資訊如 samples、elapsed_ms")

class K8sRestartArgs(BaseModel):
    namespace: str = Field(..., description="Kubernetes 命名空間")
    deployment_name: str = Field(..., description="Deployment 名稱")
    reason: str | None = Field(default=None, description="重啟原因，留存於審計註解")

class K8sRestartRet(BaseModel):
    success: bool
    message: str

class GrafanaCreateArgs(BaseModel):
    service_type: str = Field(..., description="服務型別，例如 web/api/batch")

class GrafanaCreateRet(BaseModel):
    success: bool
    dashboard_uid: str | None = None
    message: str | None = None

class KnowledgeIngestArgs(BaseModel):
    title: str
    content: str
    tags: list[str] | None = None
    status: str = "draft"

class KnowledgeIngestRet(BaseModel):
    ok: bool
    entry_id: int
    chunks: int
    vectorized: bool
    backend: str

class RAGRetrieveArgs(BaseModel):
    query: str
    top_k: int = 5
    status_filter: list[str] | None = None

class RAGRetrieveRet(BaseModel):
    query: str
    hits: list[dict]
    backend: str | None = None

# === ADK FunctionTool 定義（顯式綁定 I/O Schema 與函式）===

promql_tool = FunctionTool(
    name="PromQLQueryTool",
    description="以 PromQL 查詢指標（ADK FunctionTool）",
    args_schema=PromQueryArgs,
    returns_schema=PromQueryRet,
    func=lambda query, range: _promql_impl(query=query, range=range),
    timeout_seconds=30,
    idempotent=True
)

k8s_restart_tool = k8s_rollout_restart_long_running_tool

grafana_create_tool = FunctionTool(
    name="GrafanaDashboardTool",
    description="建立或套用 Grafana 儀表板模板（ADK FunctionTool）",
    args_schema=GrafanaCreateArgs,
    returns_schema=GrafanaCreateRet,
    func=lambda service_type: _grafana_create_impl(service_type=service_type),
    timeout_seconds=30,
    idempotent=True
)

ingest_tool = FunctionTool(
    name="KnowledgeIngestionTool",
    description="知識匯入：切片→嵌入→寫入 pgvector（ADK FunctionTool）",
    args_schema=KnowledgeIngestArgs,
    returns_schema=KnowledgeIngestRet,
    func=lambda title, content, tags=None, status="draft": _ingest_impl(title=title, content=content, tags=tags, status=status),
    timeout_seconds=120,
    idempotent=False
)

# 檢索工具：優先使用 Vertex RAG，否則回退 pgvector 工具
if _HAS_VERTEX_RAG and os.getenv("RAG_CORPUS"):
    rag_tool = VertexAiRagRetrieval(
        name="RAGRetrieveTool",
        rag_resources=[vertex_rag.RagResource(rag_corpus=os.environ["RAG_CORPUS"])],
        similarity_top_k=int(os.getenv("RAG_TOPK", "10")),
        vector_distance_threshold=float(os.getenv("RAG_DIST", "0.6")),
    )
else:
    rag_tool = FunctionTool(
        name="RAGRetrieveTool",
        description="向量檢索（pgvector 優先，無則 FTS）",
        args_schema=RAGRetrieveArgs,
        returns_schema=RAGRetrieveRet,
        func=lambda query, top_k=5, status_filter=None: _rag_vector_impl(query=query, top_k=top_k, status_filter=status_filter),
        timeout_seconds=15,
        idempotent=True
    )


# === 官方建議：使用 before_tool_callback 作為政策防護與審計 ===

from google.adk.agents.callback_context import CallbackContext
try:
    from google.adk.tools.tool_context import ToolContext
except Exception:
    ToolContext = object  # 以防環境未安裝完整 ADK 模組

def _guard_before_tool(callback_context: CallbackContext, tool_context: ToolContext):
    """
    簡易政策檢查：示範如何攔截高風險工具與參數。
    回傳 None 代表允許執行；回傳 dict 可直接取代實際工具回傳以跳過執行。
    在正式環境，請整合你的 CaMeL/Policy 規則與審批流程。
    """
    tool_name = getattr(tool_context, "tool_name", "")
    args = getattr(tool_context, "arguments", {}) or {}
    # 範例：禁止在 production 命名空間執行 rollout restart，需先經過 HITL
    # 若需正式 HITL：可在此呼叫 tool_context.request_credential(auth_config) 以觸發認證/審批互動（官方建議）
    if tool_name == "K8sRolloutRestartTool" and args.get("namespace") in {"prod","production"}:
        return {"success": False, "message": "政策阻擋：禁止直接在 production 環境執行重啟，請先走 HITL。"}  # 跳過實際工具
    return None

# === 子專家代理（LlmAgent）===

diagnostic_expert = LlmAgent(
    name="DiagnosticExpert",
    model=os.getenv("AGENT_MODEL", "gemini-2.5-flash"),
    instruction=(
        "你是 SRE 診斷專家。"
        "步驟：1) 明確化症狀與範圍 2) 用 PromQL 拉取對應指標 3) 交叉 RAG 搜索既有處置 4) 產出初診結論與後續行動。"
        "回覆時附上採用的證據與引用。"
    ),
    tools=[promql_tool, rag_tool]
)

remediation_expert = LlmAgent(
    name="RemediationExpert",
    model=os.getenv("AGENT_MODEL", "gemini-2.5-flash"),
    instruction=(
        "你是 SRE 修復專家。"
        "在 HITL 前提下生成安全修復方案，包含風險、回滾、驗證步驟。"
    ),
    tools=[k8s_restart_tool, grafana_create_tool]
)

postmortem_expert = LlmAgent(
    name="PostmortemExpert",
    model=os.getenv("AGENT_MODEL", "gemini-2.5-flash"),
    instruction=(
        "你是 SRE 覆盤專家。"
        "總結事件時間線、根因、影響範圍、緩解手段與行動項。"
    ),
    tools=[rag_tool]
)

# === 主代理（LlmAgent）與 AgentTool 掛載 ===

main_llm = LlmAgent(
    name="SREMainAgent",
    model=os.getenv("AGENT_MODEL", "gemini-2.5-flash"),
    instruction=(
        "你是 SRE Assistant 協調器，負責：理解意圖、規劃步驟、選擇專家與工具、整合回應。"
        "若屬於診斷問題，指派 DiagnosticExpert；修復則 RemediationExpert；覆盤則 PostmortemExpert。"
        "確保輸出可追溯，必要時請用工具取得證據。"
    ),
    before_tool_callback=_guard_before_tool,
    tools=[
        AgentTool(name="diagnostic", agent=diagnostic_expert, description="診斷專家"),
        AgentTool(name="remediation", agent=remediation_expert, description="修復專家"),
        AgentTool(name="postmortem", agent=postmortem_expert, description="覆盤專家"),
        # 主代理直接可用的共通工具（非必要）
        rag_tool, promql_tool
    ]
)

# === 頂層協調器（LoopAgent + BuiltInPlanner）===

coordinator = LoopAgent(
    agents=[main_llm],
    planner=BuiltInPlanner(),
    max_iterations=int(os.getenv("MAX_ITERS","10"))
))
)

def run_chat(message: str) -> dict:
    """
    便利方法：呼叫 ADK 協調器執行對話。
    回傳：統一格式 { response: str, actions_taken: [], metrics: {...} }
    """
    t0 = time.time()
    result = coordinator.run(message)  # 依官方 ADK 介面呼叫
    dt = int((time.time()-t0)*1000)
    # 依照專案既有的 API 慣例整形輸出
    return {
        "response": getattr(result, "text", str(result)),
        "actions_taken": getattr(result, "actions", []),
        "metrics": {"duration_ms": dt}
    }
