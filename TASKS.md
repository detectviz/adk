# TASKS.md - SRE Assistant 統一任務清單

**版本**: 2.0.0
**狀態**: 生效中 (Active)
**關聯架構**: [ARCHITECTURE.md](ARCHITECTURE.md)
**關聯路線圖**: [ROADMAP.md](ROADMAP.md)
**關聯規格**: [SPEC.md](SPEC.md)

## 總覽

本文件是 SRE Assistant 專案的**唯一真實來源 (Single Source of Truth)**，用於追蹤所有開發任務。它根據 [ROADMAP.md](ROADMAP.md) 的階段進行組織，並整合了所有新功能、重構計畫和已知的技術債。

開發團隊在執行任務時，應優先參考以下專案內部的高階指南以尋找相關的程式碼範例與實作教學：
- **核心參考**: **[SRE Assistant 參考資料庫 (docs/README.md)](docs/README.md)**

---

## Phase 0: 優先技術債修正 (Priority Tech-Debt Remediation)

### P0 - 新功能 (New Features)
- [ ] **TASK-P0-FEAT-01**: **實現標準化的人類介入工具 (HITL)**
    - **來源**: `review.md` (P0)
    - **任務**: 根據 `SPEC.md` 的定義，使用 ADK 的 `LongRunningFunctionTool` 實現 `HumanApprovalTool`。
    - **依賴**: 無
    - **參考**:
        - [ADK Examples: human_in_loop](docs/reference-adk-examples.md#phase-1--2-核心能力與-grafana-整合-core-capabilities--grafana-integration)
        - [ADK Snippets: human_in_the_loop.py](docs/reference-snippets.md#23-安全的自動化修復模式-safe-automated-remediation-pattern)
    - **驗收標準**:
        - [ ] 工具能夠暫停工作流程，等待外部回調。
        - [ ] 能夠正確處理批准、拒絕和超時三種情況。
        - [ ] 有對應的單元測試。

### P0 - 重構 (Refactoring)
- [✅] **TASK-P0-REFACTOR-01**: **重構 AuthManager 為無狀態工具**
    - **來源**: `review.md` (P0)
    - **任務**: 將 `src/sre_assistant/auth/auth_manager.py` 重構為一個或多個符合 ADK 規範的、無狀態的 `FunctionTool`。
    - **依賴**: 無 (已完成)
    - **驗收標準**:
        - [✅] 新的 `AuthenticationTool` 是無狀態的。
        - [✅] 憑證和令牌等狀態通過 `tool_context.session_state` 進行管理。
        - [✅] 舊的 `AuthManager` 被移除。
- [✅] **TASK-P0-REFACTOR-02**: **為關鍵代理實現結構化輸出**
    - **來源**: `review.md` (P2, 提升為 P0)
    - **任務**: 為核心的診斷代理（如 `MetricsAnalyzer`, `LogAnalyzer`）定義 Pydantic `output_schema`。
    - **依賴**: 無 (已完成)
    - **驗收標準**:
        - [✅] 代理的輸出是可預測的、有固定結構的 Pydantic 模型。
        - [✅] `SREWorkflow` 中的下游代理可以安全地依賴此結構。

---

## 目標目錄結構 (Target Directory Structure)

所有開發任務應朝著以下目標目錄結構進行，此結構符合 ADK 最佳實踐並反映了我們的聯邦化架構。

### 專案結構

本專案採用現代化的 `src` 目錄結構，以確保原始碼和專案設定檔的清晰分離。

```bash
.
├── .github/              # CI/CD 工作流程 (例如 GitHub Actions)
├── .gitignore
├── AGENT.md
├── ARCHITECTURE.md
├── Dockerfile            # 用於將最終應用程式容器化
├── LICENSE               # 專案授權條款
├── Makefile              # 用於自動化常用指令 (例如 setup, test, run)
├── README.md
├── ROADMAP.md
├── SPEC.md
├── TASKS.md
├── config/               # 外部基礎設施設定 (例如 Prometheus, Grafana)
│   └── ...
├── deployment/           # 部署相關設定 (例如 Kubernetes, Cloud Run)
│   └── ...
├── docker-compose.yml    # 用於一鍵啟動本地開發環境
├── docs/                 # 專案文件
│   └── ...
├── eval/                 # 程式化的評估腳本
│   └── evaluation.py
├── pyproject.toml        # Python 專案定義與依賴管理
├── src/                  # 主要的原始碼目錄
│   └── sre_assistant/    # 您的 Python 套件
│       ├── __init__.py
│       ├── workflow.py         # 核心工作流程協調器
│       ├── contracts.py        # Pydantic 資料模型
│       ├── prompts.py          # Prompt 模板
│       ├── tool_registry.py    # 共享工具註冊表
│       ├── auth/               # 認證提供者模組
│       │   ├── __init__.py
│       │   ├── auth_factory.py         # 根據配置創建 AuthProvider
│       │   └── auth_manager.py         # 統一管理認證流程
│       ├── config/                     # 應用程式自身的設定管理
│       │   ├── config_manager.py
│       │   └── environments/
│       │       ├── development.yaml
│       │       └── production.yaml
│       ├── memory/                     # 長期記憶體 (RAG) 提供者模組
│       │   └── backend_factory.py      # 根據配置創建 MemoryProvider
│       ├── session/                    # 會話 (短期記憶體) 提供者模組
│       │   └── backend_factory.py      # 根據配置創建 SessionProvider
│       └── sub_agents/                 # 未來的專業化子代理 (聯邦化階段)
│           ├── __init__.py
│           ├── incident_handler/       # 事件處理 Assistant
│           │   ├── __init__.py
│           │   ├── agent.py
│           │   ├── prompts.py
│           │   └── tools.py            # incident_handler 專用工具
│           └── predictive_maintenance/ # 預測維護 Assistant
│               ├── __init__.py
│               ├── agent.py
│               └── ...

└── tests/                              # 測試套件 (應與 src 平行)
    ├── __init__.py
    ├── test_workflow.py
    └── ...
```

### 關鍵元件

- **`src/sre_assistant/workflow.py`**: 這是系統的主入口點和**核心協調器**。它定義了主工作流程（例如，一個 `SequentialAgent` 或 `Workflow`），負責接收使用者請求，並按順序調用不同的工具或子代理來完成診斷、修復和報告等任務。
    
- **`src/sre_assistant/tool_registry.py`**: 這裡定義了所有**共享工具**。例如 `PrometheusQueryTool`、`LokiLogQueryTool`、`GitHubTool` 等。遵循「代理即工具 (Agent-as-Tool)」的原則，未來的子代理也會被封裝成 `AgentTool` 並在此處註冊。
    
- **`src/sre_assistant/contracts.py`**: 定義了專案中所有標準化的資料結構，主要使用 Pydantic 模型。例如，`ToolResult`、`IncidentReport` 等，確保各元件間的資料交換有固定的格式。
    
- **`src/sre_assistant/auth/`**: 實現了 ADK 的 `AuthProvider`。根據設定（例如 `config/production.yaml`），`auth_factory.py` 會建立並返回一個合適的認證提供者（例如 `None` 用於本地測試，`OAuth2` 用於生產環境）。
    
- **`src/sre_assistant/memory/`**: 實現了 ADK 的 `MemoryProvider`，負責**長期記憶體**和 RAG。它連接到向量資料庫（如 Weaviate），提供從歷史事件和文件中進行語義搜索的能力。
    
- **`src/sre_assistant/session/`**: 實現了 ADK 的 `session_service_builder`，負責**短期記憶體**（會話狀態）。它連接到持久化儲存（如 Redis 或 PostgreSQL），確保在多實例部署或服務重啟時，用戶的對話上下文不會遺失。
    
- **`src/sre_assistant/sub_agents/`**: 這是未來**聯邦化架構**的基礎。每個子目錄都代表一個專業化的代理（例如 `incident_handler`），它有自己的 `agent.py`、`prompts.py` 和專用工具。
    

### 開發與測試流程

- **本地開發**: 使用根目錄的 `docker-compose.yml` 啟動所有本地依賴（例如 PostgreSQL, Weaviate）。
- **互動測試**: 使用 `adk web` 指令啟動本地 API 伺服器和前端 UI，進行快速的互動式除錯。
- **單元與整合測試**: 所有測試都位於 `tests/` 目錄下，使用 `pytest` 執行。CI/CD 流程會自動運行這些測試。
- **評估**: 程式化的評估腳本位於 `eval/` 目錄下，用於衡量 Agent 的端到端表現和品質。

---

## Phase 1: MVP - 後端優先與核心能力建設 (預計 1-2 個月)

### P1 - 新功能 (New Features)

- **基礎設施 (Infrastructure)**
    - [ ] **TASK-P1-INFRA-01**: 創建 `docker-compose.yml`
      - **依賴**: 無
      - **參考**:
        - [ADK Agent Samples: a2a_telemetry](docs/reference-adk-agent-samples.md#6-可觀測性與追蹤-observability--tracing)
        - [ADK Agent Samples: brand-search-optimization](docs/reference-adk-agent-samples.md#16-進階工作流程與整合-advanced-workflows--integrations)
        - [ADK Agent Samples: sre-bot](docs/reference-adk-agent-samples.md#19-sre-實踐與整合-sre-practices--integrations)
      - **驗收標準**:
        - [ ] 能夠透過 `docker-compose up` 成功啟動所有服務。
        - [ ] 服務之間網絡互通。
        - [ ] 數據卷掛載正確，數據可持久化。
    - [ ] **TASK-P1-INFRA-02**: 編寫開發環境的啟動與使用文檔
      - **依賴**: [TASK-P1-INFRA-01]
      - **驗收標準**:
        - [ ] 文檔應包含環境要求、啟動步驟、停止步驟和常見問題排查。
        - [ ] 新成員能夠根據文檔獨立完成環境設置。

- **後端服務 (Backend Service)**
    - [ ] **TASK-P1-SVC-01**: 實現核心 `SREAssistant` Agent 服務
      - **依賴**: [TASK-P1-INFRA-01]
      - **參考**:
        - **主要藍圖**: `review.md` 中的 `EnhancedSREWorkflow` 程式碼範例。
        - **進階模式**: [ADK Examples: workflow_agent_seq](docs/reference-adk-examples.md#開發團隊補充建議參考-additional-team-proposed-references) (展示狀態傳遞)
        - **並行診斷**: [ADK Examples: parallel_functions](docs/reference-adk-examples.md#開發團隊補充建議參考-additional-team-proposed-references) (實現並行工具調用)
        - **宏觀架構**: [ADK Agent Samples: sre-bot](docs/reference-adk-agent-samples.md#19-sre-實踐與整合-sre-practices--integrations)
      - **驗收標準**:
        - [ ] 服務能成功啟動並監聽指定端口。
        - [ ] `SREWorkflow` 的結構遵循 `EnhancedSREWorkflow` 的模式，包含並行診斷、自定義聚合、條件回呼等。
    - [ ] **TASK-P1-SVC-02**: 實現無認證模式
      - **依賴**: [TASK-P1-SVC-01]
      - **驗收標準**:
        - [ ] 當 `auth.provider` 設置為 `None` 時，所有請求無需認證即可通過。
        - [ ] `InvocationContext` 中有模擬的用戶資訊。
    - [ ] **TASK-P1-SVC-03**: 使用 ADK Web UI 進行開發與互動
      - **依賴**: [TASK-P1-SVC-01]
      - **參考**:
        - [ADK Docs: UI](docs/reference-adk-docs.md#開發與測試-development--testing)
      - **驗收標準**:
        - [ ] 可透過 ADK Web UI 與後端服務進行問答互動。
        - [ ] 能夠正確顯示工具調用和最終結果。

- **核心工具 (Core Tools)**
    - [ ] **TASK-P1-TOOL-01**: 實現 `PrometheusQueryTool`
      - **依賴**: [TASK-P1-SVC-01]
      - **參考**:
        - **領域知識**: [SRE 的四大黃金訊號](https://sre.google/sre-book/monitoring-distributed-systems/#xref_monitoring_golden-signals), [Google SRE Book: Chapter 6](docs/reference-google-sre-book.md#part-ii-事件處理與可靠性實踐-incident-handling--reliability-practices)
        - **架構模式**: [ADK Agent Samples: fomc-research](docs/reference-adk-agent-samples.md#18-韌性與時間序列分析-resilience--time-series-analysis) (查詢時間序列數據與韌性模式)
        - **基礎實現**: [ADK Docs: Creating a tool](docs/reference-adk-docs.md#核心框架與自訂擴展-core-framework--custom-extensions), [ADK Snippets: Standard Tool Development](docs/reference-snippets.md#32-標準工具開發手動實現-standard-tool-development-manual-implementation)
        - **(挽救的程式碼) 在未來實現 SLO 相關功能時，可參考 `docs/references/snippets/salvaged_code.md` 中的 SLO 錯誤預算計算邏輯。**
      - **驗收標準**:
        - [ ] 能夠成功查詢 Prometheus 並返回指標數據。
        - [ ] 遵循 `SPEC.md` 中定義的 `ToolResult` 格式。
        - [ ] 有對應的單元測試。
    - [ ] **TASK-P1-TOOL-02**: 實現 `LokiLogQueryTool`
      - **依賴**: [TASK-P1-SVC-01]
      - **參考**:
        - (同 TASK-P1-TOOL-01)
      - **驗收標準**:
        - [ ] 能夠成功查詢 Loki 並返回日誌數據。
        - [ ] 遵循 `SPEC.md` 中定義的 `ToolResult` 格式。
        - [ ] 有對應的單元測試。
    - [ ] **TASK-P1-TOOL-03**: 實現 `GitHubTool`
      - **依賴**: [TASK-P1-SVC-01]
      - **參考**:
        - [ADK Agent Samples: github-agent](docs/reference-adk-agent-samples.md#8-工具開發-tool-development)
        - [ADK Examples: jira_agent](docs/reference-adk-examples.md#自定義工具與整合-custom-tools--integration)
      - **驗收標準**:
        - [ ] 能夠成功在指定的 GitHub Repo 中創建 Issue。
        - [ ] 遵循 `SPEC.md` 中定義的 `ToolResult` 格式。
        - [ ] 有對應的單元測試，並使用 mock 進行隔離。

- **核心服務 (Core Services)**
    - [ ] **TASK-P1-CORE-01**: 實現 `MemoryProvider` (RAG)
      - **依賴**: [TASK-P1-INFRA-01]
      - **參考**:
        - **主要藍圖**: [ADK Agent Samples: RAG](docs/reference-adk-agent-samples.md#5-檢索增強生成-rag-與記憶體)
        - **理論基礎**: [ADK Docs: Memory](docs/reference-adk-docs.md#核心框架與自訂擴展-core-framework--custom-extensions)
        - **整合範例**: [ADK Examples: adk_answering_agent](docs/reference-adk-examples.md#自定義工具與整合-custom-tools--integration)
        - **擴展用例**: [ADK Agent Samples: llama_index_file_chat](docs/reference-adk-agent-samples.md#5-檢索增強生成-rag-與記憶體) (用於臨時文件分析)
        - **(挽救的程式碼) 在設計 RAG 最終輸出時，可參考 `docs/references/snippets/salvaged_code.md` 中的引用格式化邏輯。**
      - **驗收標準**:
        - [ ] 能夠將文檔向量化並存儲到 Weaviate。
        - [ ] 能夠根據查詢進行語義搜索並返回相關文檔片段。
        - [ ] 有整合測試驗證 RAG 流程。
    - [ ] **TASK-P1-CORE-02**: **實現 `session_service_builder` (PostgreSQL 持久化會話)**
      - **依賴**: [TASK-P1-INFRA-01]
      - **任務**: 實現一個 `session_service_builder`，它能根據配置返回一個基於 `DatabaseSessionService` 的 **PostgreSQL** 會話提供者。
      - **參考**:
        - **概念部落格**: [Remember this: Agent state and memory with ADK](https://cloud.google.com/blog/topics/developers-practitioners/remember-this-agent-state-and-memory-with-adk)
        - **主要藍圖**: [ADK Agent Samples: customer-service](docs/reference-adk-agent-samples.md#9-領域特定工作流程-domain-specific-workflows)
        - **理論基礎**: [ADK Docs: Sessions](docs/reference-adk-docs.md#核心框架與自訂擴展-core-framework--custom-extensions)
        - **應用層實踐**: [ADK Examples: history_management](docs/reference-adk-examples.md#工程實踐與開發體驗-engineering-practices-developer-experience) (如何使用歷史)
        - **狀態管理**: [ADK Examples: session_state_agent](docs/reference-adk-examples.md#開發者實踐補充範例-developers-cookbook) (如何讀寫自定義狀態)
      - **驗收標準**:
        - [ ] 多輪對話的上下文能夠被正確保存和讀取到 PostgreSQL。
        - [ ] 服務重啟後，可以從 PostgreSQL 中恢復會話狀態。
        - [ ] 有整合測試驗證會話持久化。
    - [ ] **TASK-P1-CORE-03**: 實現 `AuthProvider` (OAuth 2.0)
      - **依賴**: [TASK-P1-SVC-01]
      - **參考**:
        - **核心實踐**: `review.md` 關於 AuthManager 的重構建議。
        - **主要藍圖**: [ADK Agent Samples: headless_agent_auth](docs/reference-adk-agent-samples.md#4-安全與認證-security--authentication)
        - **工具層實踐**: [ADK Examples: oauth_calendar_agent](docs/reference-adk-examples.md#開發團隊補充建議參考-additional-team-proposed-references) (展示工具如何使用憑證)
        - **理論基礎**: [ADK Docs: Auth](docs/reference-adk-docs.md#核心框架與自訂擴證-core-framework--custom-extensions)
      - **驗收標準**:
        - [ ] 實現一個**無狀態**的 `AuthProvider`，而不是一個有狀態的管理器。
        - [ ] 能夠與一個 OIDC Provider (如 Google) 完成認證流程。
        - [ ] 成功獲取並驗證 `id_token` 和 `access_token`。
        - [ ] 有整合測試（可使用 mock OIDC server）。
    - [ ] **TASK-P1-CORE-04**: **實現工作流程回調機制**
      - **來源**: `review.md` (P1)
      - **任務**: 為 `SREWorkflow` 實現 `before_agent_callback` 和 `after_agent_callback`，用於執行前置檢查（權限、速率限制）和後處理（審計、指標更新）。
      - **依賴**: [TASK-P1-SVC-01]
      - **參考**:
          - `review.md` 中的 `_workflow_pre_check` 和 `_workflow_post_process` 範例。
          - **進階模式**: [ADK Examples: live_tool_callbacks_agent](docs/reference-adk-examples.md#工程實踐與開發體驗-engineering-practices-developer-experience) (用於即時串流進度)
          - **理論基礎**: [ADK Docs: Callbacks](docs/reference-adk-docs.md#核心框架與自訂擴展-core-framework--custom-extensions)
      - **驗收標準**:
          - [ ] 前置檢查失敗時，能夠提前終止工作流程。
          - [ ] 工作流程結束後，能夠觸發後處理 logique。

### P1 - 重構 (Refactoring)

- [✅] **TASK-P1-REFACTOR-01**: AuthManager 狀態管理
    - **來源**: `REFACTOR_PLAN.md`
    - **任務**: 將 `AuthManager` 重構為無狀態服務，所有狀態透過 `InvocationContext` 讀寫，並由 `SessionService` 持久化。
    - **依賴**: 無 (已完成)
    - **驗收標準**:
        - [ ] `AuthManager` 內部不再持有 `_auth_cache` 或 `_rate_limits` 等實例變數。
        - [ ] 狀態讀寫均通過 `InvocationContext`。

### P1 - 技術債 (Technical Debt)

- [ ] **TASK-P1-DEBT-01**: 增加測試覆蓋率
    - **來源**: `TASKS.md` (舊)
    - **任務**: 為 Phase 1 開發的核心模組（Auth, Memory, Session, Tools）增加單元和整合測試。
    - **依賴**: [TASK-P1-CORE-01], [TASK-P1-CORE-02], [TASK-P1-CORE-03], [TASK-P1-TOOL-01], [TASK-P1-TOOL-02], [TASK-P1-TOOL-03]
    - **參考**:
        - [ADK Docs: Testing](docs/reference-adk-docs.md#開發與測試-development--testing)
    - **驗收標準**:
        - [ ] `pytest --cov` 報告顯示核心模組測試覆蓋率 > 80%。
        - [ ] CI 流水線中包含測試覆蓋率檢查步驟。
- [ ] **TASK-P1-DEBT-02**: **重構工具以實現標準化輸出**
    - **來源**: `SPEC.md` (Section 4.1)
    - **任務**: 重構所有現有的工具 (例如 `PrometheusQueryTool`, `LokiLogQueryTool`)，使其返回 `SPEC.md` 中定義的標準化 `ToolResult` Pydantic 模型，而不是臨時的元組。
    - **依賴**: [TASK-P1-TOOL-01], [TASK-P1-TOOL-02]
    - **參考**:
        - **直接實現**: [ADK Examples: output_schema_with_tools](docs/reference-adk-examples.md#開發者實踐補充範例-developers-cookbook)
    - **驗收標準**:
        - [ ] 專案中定義了 `ToolResult` 和 `ToolError` Pydantic 模型。
        - [ ] 所有工具的 `execute` 方法簽名都符合 `BaseTool` 協議。
        - [ ] 成功和失敗的工具調用都能返回結構化的 `ToolResult`。

---

## Phase 2: Grafana 原生體驗 (預計 2-3 個月)

### P2 - 新功能 (New Features)

- **Grafana 插件 (Plugin Development)**
    - [ ] **TASK-P2-PLUGIN-01**: 開發 SRE Assistant Grafana App Plugin v1.0。
        - **參考**: [ADK Agent Samples: gemini-fullstack](docs/reference-adk-agent-samples.md#11-全端整合與前端開發-full-stack--frontend-integration)
    - [ ] **TASK-P2-PLUGIN-02**: 在插件中實現 ChatOps 面板。
        - **參考**:
          - [ADK Examples: callbacks](docs/reference-adk-examples.md#phase-1--2-核心能力與-grafana-整合-core-capabilities--grafana-integration)
          - [ADK Agent Samples: navigoAI_voice_agent_adk](docs/reference-adk-agent-samples.md#17-即時-ui-串流-real-time-ui-streaming)
          - [Gemini Cloud Assist with Personalized Service Health](https://cloud.google.com/blog/products/devops-sre/gemini-cloud-assist-integrated-with-personalized-service-health)
    - [ ] **TASK-P2-PLUGIN-03**: 實現插件與後端服務的 WebSocket / RESTful 安全通訊。
        - **參考**: [ADK Agent Samples: navigoAI_voice_agent_adk](docs/reference-adk-agent-samples.md#17-即時-ui-串流-real-time-ui-streaming), [ADK Examples: live_bidi_streaming_tools_agent](docs/reference-adk-examples.md#phase-1--2-核心能力與-grafana-整合-core-capabilities--grafana-integration)
- **Grafana 整合 (Deep Integration)**
    - [ ] **TASK-P2-INTEG-01**: 實現 `GrafanaIntegrationTool` 的 `embed_panel` 功能，並在聊天中提供對應指令。
        - **參考**: [ADK Snippets: OpenAPI Toolset](docs/reference-snippets.md#31-加速工具開發openapi-規格優先-accelerated-tool-development-openapi-spec-first)
    - [ ] **TASK-P2-INTEG-02**: 實現 `GrafanaIntegrationTool` 的 `create_annotation` 功能，並在聊天中提供對應指令。
        - **參考**: (同 TASK-P2-INTEG-01)
    - [ ] **TASK-P2-INTEG-03**: 實現 `GrafanaOnCallTool`，用於創建告警升級和獲取值班人員。
        - **參考**: [Google SRE Book: Chapter 13](docs/reference-google-sre-book.md#part-ii-事件處理與可靠性實踐-incident-handling--reliability-practices)
- **DevOps 工具 (DevOps Tools)**
    - [ ] **TASK-P2-DEVOPS-01**: 實現 `TerraformTool`，用於基礎設施即代碼的管理。
        - **參考**: [ADK Examples: code_execution](docs/reference-adk-examples.md#進階工作流與工程實踐-advanced-workflow--engineering-practices)
- **修復後驗證 (Post-Remediation Verification)**
    - [ ] **TASK-P2-VERIFY-01**: **實現修復後驗證代理 (Verification Agent)**
        - **來源**: `review.md`, `ARCHITECTURE.md`
        - **任務**: 根據 `ARCHITECTURE.md` 中 `VerificationAgent` 的定義，實現一個 `Self-Critic` 模式的驗證代理，確保修復操作的有效性。
        - **參考**:
            - `review.md` 中的 `VerificationAgent` 類別範例。
            - [ADK Agent Samples: google-adk-workflows](docs/reference-adk-agent-samples.md#2-工作流程與協調模式-workflow--orchestration) (SelfCriticAgent)
- **事件管理 (Incident Management)**
    - [ ] **TASK-P2-INCIDENT-01**:
        - **來源**: `TASKS.md` (舊)
        - **任務**: 整合 `GitHubTool`，實現從事件到 Issue 的自動創建和狀態同步。
        - **參考**: [ADK Agent Samples: github-agent](docs/reference-adk-agent-samples.md#8-工具開發-tool-development)
- **雲端整合工具 (Cloud Integration Tools)**
    - [ ] **TASK-P2-TOOL-04**: **實現 AppHubTool**
        - **描述**: 實現一個工具，用於查詢 Google Cloud App Hub，以獲取應用程式的拓撲結構（例如，一個應用程式包含哪些服務和負載均衡器）。這是實現「以應用程式為中心的診斷」的前提。
        - **參考**:
          - [Application monitoring in Google Cloud](https://cloud.google.com/blog/products/management-tools/get-to-know-cloud-observability-application-monitoring)
          - [ADK Agent Samples: sre-bot](docs/reference-adk-agent-samples.md#19-sre-實踐與整合-sre-practices--integrations)
    - [ ] **TASK-P2-TOOL-05**: **實現 GoogleCloudHealthTool**
        - **描述**: 實現一個工具，用於查詢 Google Cloud 的 Personalized Service Health (PSH) API。在診斷流程開始時，應首先調用此工具，以檢查是否存在已知的、可能影響當前專案的 Google Cloud 平台事件。
        - **參考**:
          - [Personalized Service Health integrated with Gemini Cloud Assist](https://cloud.google.com/blog/products/devops-sre/gemini-cloud-assist-integrated-with-personalized-service-health)
          - [ADK Agent Samples: sre-bot](docs/reference-adk-agent-samples.md#19-sre-實踐與整合-sre-practices--integrations)

### P2 - 重構 (Refactoring)

- [ ] **TASK-P2-REFACTOR-01**: **實現智能分診器 (Intelligent Dispatcher)**:
    - **來源**: `review.md`, `ARCHITECTURE.md`
    - **任務**: 根據 `ARCHITECTURE.md` 中 `IntelligentDispatcher` 的定義，使用基於 LLM 的路由器替換靜態的條件判斷邏輯，以動態選擇最合適的專家代理。
    - **參考**:
        - `review.md` 中的 `IntelligentDispatcher` 類別範例。
        - **真實世界藍圖**: [ADK Agent Samples: brand-search-optimization](docs/reference-adk-agent-samples.md#16-進階工作流程與整合-advanced-workflows--integrations)
        - **基礎模式**: [ADK Agent Samples: google-adk-workflows](docs/reference-adk-agent-samples.md#2-工作流程與協調模式-workflow--orchestration)
        - **輕量化實現**: [ADK Examples: workflow_triage](docs/reference-adk-examples.md#開發團隊補充建議參考-additional-team-proposed-references)
    - **驗收標準**: 系統能夠根據診斷摘要，動態調度在 `SPEC.md` 中定義的專家代理。

### P2 - 技術債 (Technical Debt)

- [ ] **TASK-P2-DEBT-01**: **令牌儲存安全強化**:
    - **來源**: `TASKS.md` (舊)
    - **任務**: 將敏感的認證令牌（特別是 Refresh Token）從會話狀態中移出，存儲到 Google Secret Manager 或 HashiCorp Vault 中。
    - **參考**:
        - [ADK Agent Samples: adk_cloud_run](docs/reference-adk-agent-samples.md#7-部署與雲端整合-deployment--cloud-integration)
    - **驗收標準**: `context.state` 中只儲存對秘密的引用。
- [ ] **TASK-P2-DEBT-02**: **文檔更新**:
    - **任務**: 更新所有面向使用者的文檔，引導使用者從 ADK Web UI 過渡到 Grafana 插件。

---

## Phase 3 & 4: 聯邦化與未來 (Federation & Future)

*(註：此處為高階史詩級任務，將在 P1/P2 完成後進一步細化)*

- [ ] **TASK-P3-AGENT-01**: **(P3) 專業化代理**: 將覆盤報告生成功能重構為第一個獨立的 `PostmortemAgent`。
    - **參考**: [Google SRE Book: Chapter 15 & Appendix D](docs/reference-google-sre-book.md#part-ii-事件處理與可靠性實踐-incident-handling--reliability-practices), [ADK Agent Samples: a2a_mcp](docs/reference-adk-agent-samples.md#3-聯邦化架構與服務發現-federated-architecture--service-discovery)
- [ ] **TASK-P3-A2A-01**: **(P3) A2A 通訊**: 實現 gRPC A2A 通訊協議，用於協調器與 `PostmortemAgent` 的通訊。
    - **參考**: [ADK Agent Samples: dice_agent_grpc](docs/reference-adk-agent-samples.md#10-a2a-通訊協定-a2a-communication-protocols), [ADK Examples: a2a_basic](docs/reference-adk-examples.md#phase-3--4-聯邦化與進階工作流-federation--advanced-workflows)
- [ ] **TASK-P3-PREVENTION-01**: **(P3) 主動預防**: 整合機器學習模型，實現異常檢測和趨勢預測能力。
    - **參考**: [ADK Agent Samples: machine-learning-engineering](docs/reference-adk-agent-samples.md#12-機器學習與預測分析-machine-learning--predictive-analysis)
- [ ] **TASK-P3-MONITOR-01**: **(P3) 監控閉環**: 實現 `PrometheusConfigurationTool` 以動態更新監控目標。

### P3 - Agent 可觀測性 (Agent Observability)
- [ ] **TASK-P3-OBSERVE-01**: **實現 LLM 可觀測性追蹤**
    - **描述**: 根據 `SPEC.md` 中定義的 LLM 可觀測性原則，為 SRE Assistant 的核心工作流程實現端到端的 OpenTelemetry 追蹤。
    - **驗收標準**:
        - [ ] 每個使用者請求都會生成一個包含多個跨度 (Span) 的完整追蹤 (Trace)。
        - [ ] 追蹤中應清晰地標示出 `SREWorkflow` 的執行、每次工具調用、以及每次對 LLM 的 API 調用。
        - [ ] 關鍵元數據（如 Token 數、工具參數、LLM 回應）應作為屬性 (Attribute) 附加到對應的跨度上。
    - **參考**:
        - [Datadog LLM Observability](https://docs.datadoghq.com/llm_observability/)
        - `docs/agents-companion-v2-zh-tw.md` (代理人評估)
- [ ] **TASK-P3-OBSERVE-02**: **建立 LLM 可觀測性儀表板**
    - **描述**: 根據 `TASK-P3-OBSERVE-01` 收集到的追蹤數據，在 Grafana 中建立一個專門的儀表板，用於監控 SRE Assistant 自身的健康狀況。
    - **驗收標準**:
        - [ ] 儀表板應包含以下面板：總請求數、錯誤率、p90/p95/p99 延遲。
        - [ ] 儀表板應包含按工具或代理名稱分類的成本（Token 使用量）面板。
        - [ ] 能夠下鑽到單個追蹤，以查看詳細的執行流程。
    - **參考**:
        - `docs/agents-companion-v2-zh-tw.md` (代理人成功指標與評估)

- [ ] **TASK-P4-ORCH-01**: **(P4) 聯邦協調器**: 開發功能完備的 SRE Orchestrator 服務。
    - **參考**: [ADK Agent Samples: a2a_mcp](docs/reference-adk-agent-samples.md#3-聯邦化架構與服務發現-federated-architecture--service-discovery)
- [ ] **TASK-P4-AGENT-01**: **(P4) 代理矩陣**: 開發並部署 `CostOptimizationAgent` 和 `ChaosEngineeringAgent`。
    - **參考**: [ADK Agent Samples: any_agent_adversarial_multiagent](docs/reference-adk-agent-samples.md#15-自我對抗與韌性測試-self-adversarial--resilience-testing)
- [ ] **TASK-P4-DISCOVERY-01**: **(P4) 服務發現**: 建立代理註冊中心。
    - **參考**: [ADK Agent Samples: a2a_mcp](docs/reference-adk-agent-samples.md#3-聯邦化架構與服務發現-federated-architecture--service-discovery)