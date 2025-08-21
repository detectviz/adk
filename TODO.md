# 剩餘缺口與優先級：

最高優先
====

*   真實整合層
    *   `tools/promql.py`、`tools/k8s.py`、`tools/grafana.py` 仍為示例實作，缺正式後端對接（Prometheus HTTP API、K8s client、Grafana API）。
    *   工具錯誤碼映射：各工具需在例外時拋出 `ExecutionError(E_TIMEOUT/E_BACKEND/E_BAD_QUERY…)`，使 YAML `errors` 與執行器一致。
*   決策關聯
    *   `core/assistant.py` `execute()` 期間產生 `decision_id`，`insert_tool_execution()` 目前以 `None` 寫入。需在插入 decisions 之前先建立 `decision_id` 並傳遞關聯。
*   規格契約測試（合約測試）
    *   針對每個 YAML：參數必填、型別、`returns_schema`、`timeout_seconds`、`retry`、`require_approval`、`risk_level`，新增 `tests/test_tool_contracts.py`。
*   安全策略覆核
    *   `policy.py` 僅做基本黑白名單與 namespace 限制。需補：參數白名單、值域（regex、枚舉）、批次操作限額、變更窗口檢查。

高優先
===

*   觀測性深度
    *   Trace/Span：在工具呼叫與規劃步驟建立 span（如 OpenTelemetry），將入參摘要與錯誤碼寫入 attributes。
    *   SLO 守門：E2E P95 檢測與自動降級策略（模型/路徑切換）未實作。
*   HITL 流程測試
    *   新增 `tests/test_hitl_flow.py`：建立審批→拒絕/核准→`/execute` 執行→檢查審批與執行記錄。
*   RAG 真實檢索
    *   `core/rag.py` 為簡化實作。需接 Vertex AI Retrieval 或向量庫（pgvector/FAISS），並保留版本與狀態欄位。
*   身分與金鑰治理
    *   `core/auth.py` 目前內建 `devkey`。需：金鑰儲存（DB）、權限模型、金鑰輪替、審計。

中優先
===

*   部署產物
    *   `Dockerfile`、`docker-compose.yml`、K8s Manifests（Deployment/Service/HPA/NetworkPolicy/ConfigMap/Secret）。
    *   健康檢查 `/health/ready` 與 `/health/live` 區分。
*   DX 腳手架
    *   `scripts/scaffold_tool.py`、`scripts/scaffold_expert.py`：自動產生 `*.yaml`、骨架程式與測試樣板。
*   CLI 擴充
    *   CLI 支援：`rag add/approve/retrieve`、`decisions list`、`tool-execs list`。
*   去抖與快取策略
    *   去抖目前以訊息雜湊為鍵，需加入 session 維度；快取應依工具語義設 TTL 預設值並在 YAML 補齊 `cache_ttl_seconds`。

低優先
===

*   OpenAPI 補完
    *   在 FastAPI 啟動時載入 `tags`、`securitySchemes`、範例回應；產生離線 `openapi.json`。
*   資料庫抽象
    *   `core/persistence.py` 僅 SQLite。抽象成介面，增補 PostgreSQL 實作與遷移腳本（Alembic）。
*   回放與重跑
    *   目前僅查詢記錄。補「重跑某 decision」與「步驟 diff 視圖」API。

必要檔案與測試待新增（清單）
==============

*   `Dockerfile`、`docker-compose.yml`、`k8s/`（Deployment, Service, HPA, ConfigMap, Secret, NetworkPolicy）。
*   `tests/test_tool_contracts.py`（逐 YAML 驗證）
*   `tests/test_hitl_flow.py`（核准/拒絕分支）
*   `tests/test_policy_enforcement.py`（受保護 namespace、長度限制、require\_approval 來自 YAML）
*   `scripts/scaffold_tool.py`、`scripts/scaffold_expert.py`
*   `docs/OPERATIONS.md`（HITL 作業手冊、回滾流程）
*   `docs/SECURITY.md`（API Key 流程、金鑰輪替、審計事件）

補齊順序：**真實工具對接 → 決策關聯 → 合約測試 → 安全策略加固 → RAG 真檢索 → 部署與健康檢查**。
