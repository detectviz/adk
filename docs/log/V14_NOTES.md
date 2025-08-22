<!-- DEPRECATION: superseded by v15.7.x -->
# 注意：此文件紀錄 v14 時期說明，已被 v15.7.x 架構取代。
請優先參考 README.md、docs/GCP_OTEL.md、docs/EXTENDING.md。


# v14 調整說明（依 ADK 官方最佳實踐）

## 1) Session 後端可切換
- 以環境變數 `SESSION_BACKEND` 控制 `memory|db`。
- `db` 模式使用官方 `DatabaseSessionService`，並由 `SESSION_DB_URI` 指定連線（支援 sqlite/postgres/mysql）。
- 依據官方建議，生產環境應採 DB 或 Agent Engine Sessions。

## 2) HITL 改為 request_credential
- 取消以 before_tool_callback 硬阻擋 prod 的政策閘；改在工具內以 `tool_context.request_credential(...)` 觸發互動事件。
- 前端透過 SSE 收到 `adk_request_credential` 後，將核可資訊以 `FunctionResponse(name='adk_request_credential', id=<原id>)` 回傳（`/api/v1/resume_sse`）。
- 工具在 `poll_func` 透過 `tool_context.get_auth_response(...)` 讀取核可後繼續執行（教學示意以 OAuth 欄位承載）。

## 3) 映射表檢核（python.zip 範例 → SRE 模組）
- camel/ → SecurityPolicy：已保留政策引擎位置，但 HITL 走 ADK 官方 `request_credential` 流。安全邊界測試請覆蓋注入案例。 
- software-bug-assistant/ → DiagnosticExpert：維持 AgentTool 架構；RAG/外部源整合規劃不變。
- travel-concierge/ → RemediationExpert：以 LongRunningFunctionTool 展示多階段工作流（start/poll）。
- fomc-research/ → PostmortemExpert：文件分析/RAG 持續採用。
- personalized-shopping/ → MainAgent：透過 Runner + SessionService 管理多輪對話與偏好。
- machine-learning-engineering/ → AutoRemediation：可套用於調參/自動修復策略。
- marketing-agency/ → ConfigExpert：生成/校驗配置。
- auto-insurance-agent/ → PolicyEngine：可延伸成規則/審批器，但權限互動統一走 `request_credential`。
- data-science/ → MetricsAnalyzer：時序分析/異常偵測工具位於工具層。
- image-scoring/ → ComplianceChecker：合規檢查工具。
- vertex-ai-retrieval-agent/ → KnowledgeBase：RAG 檢索一律附來源。

## 4) 注意事項
- **gRPC/Proto**：ADK Python 層無公開 gRPC 介面；請勿自訂 proto。若部署到 Agent Engine，遵循其官方 API。
- **工具說明**：請勿在 docstring 中描述 `tool_context` 參數（官方建議會自動注入）。
- **子代理唯一掛載**：同一 agent 實例僅能掛一次，需多處使用請建立新實例。
