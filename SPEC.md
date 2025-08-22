# SRE Assistant 技術白皮書

狀態：穩定（Ready）

對齊：Google Agent Development Kit (ADK) — LoopAgent / BuiltInPlanner / LlmAgent / AgentTool / FunctionTool / LongRunningFunctionTool / Runner / SessionService / Dev UI

## 執行摘要

* 單一協調器：LoopAgent 搭配 BuiltInPlanner。**官方說明**：BuiltInPlanner 會將規劃步驟的「思考過程」完全交由 LlmAgent 自身的推理能力決定，而非一個獨立的、基於規則的規劃器。主代理為 SREMainAgent。  
* 子專家：診斷、修復、覆盤，以 AgentTool 掛載。  
* 工具：PromQL、K8s、Grafana、RAG、知識匯入，皆為顯式 FunctionTool；變更類操作使用 LongRunningFunctionTool。  
* HITL：以 tool_context.request_credential(...) → FunctionResponse(name='adk_request_credential') → get_auth_response(...) 實作。  
* Session：SESSION_BACKEND=memory|db 切換 InMemorySessionService | DatabaseSessionService。  
* Dev UI：提供 ADK Web Dev UI 檢視 Sessions/Events/State/Tools。

### SLO

* 對話 P95 < 2s；工具 P95 < 10s；端到端 P95 < 30s。

## 架構

User ←→ REST API (/api/v1/chat|chat_sse|resume_sse)  
            │  
            ▼  
        ADK Runner  ── SessionService(memory|db)  
            │ run_async(events)  
            ▼  
       LoopAgent (SREMainAgent)  
            │ AgentTool  
   ┌─────────┼─────────┐  
   ▼         ▼         ▼  
Diagnostic  Remediation  Postmortem  (LlmAgent)  
            │  
        FunctionTool / LongRunningFunctionTool  
            │  
 Prometheus / Kubernetes / Grafana / PostgreSQL(pgvector) / Vertex RAG

## 代理與工具（精要）

* SREMainAgent：規劃與路由，掛 AgentTool(diagnostic|remediation|postmortem)；通用工具可直掛（RAG/PromQL）。  
* DiagnosticExpert：PromQL + RAG 檢索，產出初診與建議。  
* RemediationExpert：K8sRolloutRestartLongRunningTool，必要時觸發 HITL。  
* PostmortemExpert：文件/RAG 蒐證與覆盤輸出。

## 安全

* 低風險直接執行；高風險走 HITL（request_credential）。  
* API 以 X-API-Key 驗證；工具皆有超時、冪等與錯誤碼。

## RAG

* 兩路徑：VertexAiRagRetrieval 或 pgvector（core/vectorstore_pg.py）。  
* 回覆附來源與信心分數。

## 部署

* make dev opt adk 安裝依賴。  
* API：make api → http://localhost:8000。  
* Dev UI：make adk-web → http://localhost:8080。

## 驗收

* make accept 執行 v14.1 真連接驗收（Prometheus/K8s/Grafana）。  
* tests/e2e/test_real_integrations.py 以環境變數控制是否跳過。

### 入口與角色

* ADK 模式主入口：sre_assistant/adk_app/runtime.py。  
* 備援協調器：sre_assistant/core/assistant.py（非 ADK 模式）。  
* 政策閘（before_tool_callback 等效）僅負責靜態拒絕與審計；HITL 觸發改由工具內部實作，門檻由 adk.yaml.policy.risk_threshold 決定。  
* 專家工具由 adk.yaml.experts.*.tools_allowlist 管理，協調器於啟動時載入。  
* 專家代理已分拆至 sre_assistant/experts/*.py，由 runtime.py 集中裝配；專家模型可在 adk.yaml.experts.*.model 覆蓋。  
* 新增 experts/*.yaml 外掛化設定，runtime 啟動時自動合併，降低改動程式碼需求，符合 ADK 可配置化最佳實踐。