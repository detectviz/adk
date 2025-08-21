# 完整檔案說明

*   **Makefile**  
    開發腳本。安裝依賴、啟動 API、執行測試、執行 CLI 範例。
*   **README.md**  
    使用說明。啟動步驟、端點列表、測試指令。
*   **SPEC.md**  
    產品規格與設計原則來源文件。
*   **adk_runtime/**
    *   **main.py**  
        建立 `ToolRegistry` 並以「YAML + 函式」顯式註冊所有工具。提供 `build_registry()` 供執行期引用。
*   **sre_assistant/**init**.py**  
    專案封裝檔。暴露套件版本與基本匯入。
*   **sre_assistant/version.py**  
    版本字串與變更註記集中管理。
*   **sre_assistant/adk_compat/**
    *   **agents.py**  
        ADK 代理接口相容層的占位與範例掛載點。
    *   **executor.py**  
        工具執行器。JSON Schema 驗證、超時、重試、標準化錯誤碼、Prometheus 指標。
    *   **registry.py**  
        工具註冊表。`register_from_yaml()`、`register_dir()`、規格驗證與重複註冊保護。
*   **sre_assistant/cli.py**  
    命令列工具。`chat` 對話、`approve` 審批並執行。
*   **sre_assistant/core/**
    *   **assistant.py**  
        主協調器。意圖→規劃→政策門關→HITL→工具執行→知識回寫→審計/指標/快取。
    *   **auth.py**  
        API Key 認證、RBAC 授權、Token Bucket 速率限制（可由環境變數配置）。
    *   **cache.py**  
        TTL 快取。以參數雜湊作鍵，支援每工具 `cache_ttl_seconds`。
    *   **config.py**  
        統一讀取環境變數。API 埠口、資料庫路徑、限流、去抖、快取 TTL 等。
    *   **debounce.py**  
        去抖動與重複抑制。根據訊息內容在短時間拒絕相同請求。
    *   **hitl.py**  
        HITL 審批資料模型與存取。基於資料庫的持久化審批流程。
    *   **intents.py**  
        `Intent/Step/StepResult` Pydantic 模型。含 `schema_version` 版本治理欄位。
    *   **memory.py**  
        Session/State 輕量存取。跨步驟資料暫存。
    *   **observability.py**  
        Prometheus 指標計數與延遲直方圖。事件日誌輕量記錄。
    *   **persistence.py**  
        SQLite 持久化。`decisions`、`tool_executions`、`approvals` 三表與查詢 API。
    *   **planner.py**  
        內建規劃器。依意圖產出步驟序列與條件流程。
    *   **policy.py**  
        安全策略門關。結合工具 YAML 推導 `risk_level`/`require_approval` 與動態規則。
    *   **rag.py**  
        RAG 知識庫示範。版本化、狀態（draft/approved/archived）、檢索與匯入工具。
    *   **router.py**  
        簡單意圖分類器。將輸入映射為 `diagnostic/remediation/...`。
*   **sre_assistant/experts/**
    *   **diagnostic.py**  
        診斷專家代理。聚焦讀取指標/日誌與初步歸因。
    *   **feedback.py**  
        反饋專家。將成功處理流程沉澱為 runbook 草稿（寫入 RAG）。
    *   **postmortem.py**  
        覆盤專家骨架。事故資料彙整與知識化的掛點。
    *   **provisioning.py**  
        佈署/開箱專家骨架。儀表板與基礎監控生成流程。
    *   **remediation.py**  
        修復專家骨架。變更類操作的規劃輸出與 HITL 對接。
*   **sre_assistant/server/**
    *   **app.py**  
        FastAPI 服務。`/health`、`/api/v1/chat`、HITL 決策與執行、RAG 管理/檢索、回放查詢、`/metrics`。
*   **sre_assistant/tools/**
    *   **grafana.py**  
        `GrafanaDashboardTool` 的實作函式。從 YAML 規格綁定執行。
    *   **k8s.py**  
        `K8sRolloutRestartTool` 的實作函式。參數校驗與回傳結構遵循規格。
    *   **promql.py**  
        `PromQLQueryTool` 的實作函式。模擬查詢與聚合輸出。
    *   **runbook.py**  
        `RunbookLookupTool` 的實作函式。以 RAG 或內建集合回傳對應步驟。
    *   **specs/**
        *   **GrafanaDashboardTool.yaml**  
            工具契約。參數、回傳、錯誤碼、超時、是否需審批、可選 `cache_ttl_seconds`、`risk_level`。
        *   **K8sRolloutRestartTool.yaml**  
            工具契約。K8s rollout restart 的輸入/輸出與錯誤碼。
        *   **KnowledgeIngestionTool.yaml**  
            工具契約。知識匯入到 RAG 的欄位與狀態。
        *   **PromQLQueryTool.yaml**  
            工具契約。PromQL 查詢輸入、統計彙總輸出。
        *   **RAGRetrieveTool.yaml**  
            工具契約。檢索查詢、`top_k`、狀態過濾。
        *   **RunbookLookupTool.yaml**  
            工具契約。以服務名查 runbook 步驟清單。
*   **tests/**
    *   **test_chat.py**  
        端到端基本對話測試。SLO 與回傳欄位存在性檢查。
    *   **test_persistence_and_policy.py**  
        `decisions` 持久化驗證、快取流程 smoke 測試。
    *   **test_planner_and_rag.py**  
        規劃器步驟數驗證、RAG 版本與狀態檢索測試。
