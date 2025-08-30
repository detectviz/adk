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
- [✅] **TASK-P0-FEAT-01**: **實現標準化的人類介入工具 (HITL)**
    - **來源**: `docs/references/snippets/salvaged_code.md` (P0)
    - **任務**: 根據 `SPEC.md` 的定義，使用 ADK 的 `LongRunningFunctionTool` 實現 `HumanApprovalTool`。
    - **依賴**: 無
    - **參考**:
        - [ADK Examples: human_in_loop](docs/reference-adk-examples.md#phase-1--2-核心能力與-grafana-整合-core-capabilities--grafana-integration)
        - [ADK Snippets: human_in_the_loop.py](docs/reference-snippets.md#23-安全的自動化修復模式-safe-automated-remediation-pattern)
    - **驗收標準**:
        - [✅] **暫停與回調**: `HumanApprovalTool` 已在 `src/sre_assistant/tools/human_approval_tool.py` 中實現，並繼承 `LongRunningFunctionTool`。
        - [✅] **處理審批結果**: `RemediationExecutor` 代理已在 `workflow.py` 中實現，其指令要求檢查審批狀態，並已將 `HumanApprovalTool` 作為其工具。
        - [✅] **整合**: 新的 `RemediationExecutor` 代理已整合至 `EnhancedSREWorkflow` 的執行序列中。

### P0 - 重構 (Refactoring)
- [✅] **TASK-P0-REFACTOR-01**: **重構 AuthManager 為無狀態工具**
    - **來源**: `docs/references/snippets/salvaged_code.md` (P0)
    - **任務**: 將 `src/sre_assistant/auth/auth_manager.py` 重構為一個或多個符合 ADK 規範的、無狀態的 `FunctionTool`。
    - **依賴**: 無 (已完成)
    - **驗收標準**:
        - [✅] 新的 `AuthenticationTool` 是無狀態的。
        - [✅] 憑證和令牌等狀態通過 `tool_context.session_state` 進行管理。
        - [✅] 舊的 `AuthManager` 被移除。
- [✅] **TASK-P0-REFACTOR-02**: **為關鍵代理實現結構化輸出**
    - **來源**: `docs/references/snippets/salvaged_code.md` (P2, 提升為 P0)
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
│       ├── main.py             # 應用程式主入口點 (FastAPI 伺服器)
│       ├── auth/               # 認證提供者模組
│       │   ├── __init__.py
│       │   ├── auth_factory.py         # 根據配置創建 AuthProvider
│       │   └── tools.py                # 無狀態的認證與授權工具
│       ├── config/                     # 應用程式自身的設定管理
│       │   ├── __init__.py
│       │   ├── config_manager.py
│       │   └── environments/
│       │       ├── development.yaml
│       │       └── production.yaml
│       ├── memory/                     # 長期記憶體 (RAG) 提供者模組
│       │   ├── __init__.py
│       │   └── backend_factory.py      # 根據配置創建 MemoryProvider
│       ├── session/                    # 會話 (短期記憶體) 提供者模組
│       │   ├── __init__.py
│       │   └── backend_factory.py      # 根據配置創建 SessionProvider
│       └── sub_agents/                 # 未來的專業化子代理 (聯邦化階段)
│           └── __init__.py
│
└── tests/                              # 測試套件 (應與 src 平行)
    ├── __init__.py
    ├── test_agent.py
    ├── test_contracts.py
    ├── test_session.py
    └── test_tools.py
```

### 關鍵元件

- **`src/sre_assistant/main.py`**: 這是應用程式的主入口點，負責啟動 FastAPI 伺服器並處理 A2A 請求。
- **`src/sre_assistant/workflow.py`**: 這是系統的**核心協調器**。它定義了主工作流程，負責接收使用者請求，並按順序調用不同的工具或子代理來完成診斷、修復和報告等任務。
    
- **`src/sre_assistant/tool_registry.py`**: 這裡定義了所有**共享工具**。例如 `PrometheusQueryTool`、`LokiLogQueryTool`、`GitHubTool` 等。遵循「代理即工具 (Agent-as-Tool)」的原則，未來的子代理也會被封裝成 `AgentTool` 並在此處註冊。
    
- **`src/sre_assistant/contracts.py`**: 定義了專案中所有標準化的資料結構，主要使用 Pydantic 模型。例如，`ToolResult`、`IncidentReport` 等，確保各元件間的資料交換有固定的格式。
    
- **`src/sre_assistant/auth/`**: 實現了 ADK 的 `AuthProvider`。`auth_factory.py` 會根據設定建立並返回一個合適的認證提供者，而 `tools.py` 中則包含了無狀態的認證與授權工具函式。
    
- **`src/sre_assistant/memory/`**: 實現了 ADK 的 `MemoryProvider`，負責**長期記憶體**和 RAG。它連接到向量資料庫（如 Weaviate），提供從歷史事件和文件中進行語義搜索的能力。
    
- **`src/sre_assistant/session/`**: 實現了 ADK 的 `session_service_builder`，負責**短期記憶體**（會話狀態）。它連接到持久化儲存（如 Redis 或 PostgreSQL），確保在多實例部署或服務重啟時，用戶的對話上下文不會遺失。
    
- **`src/sre_assistant/sub_agents/`**: 這是未來**聯邦化架構**的基礎。每個子目錄都代表一個專業化的代理。
    

### 開發與測試流程

- **本地開發**: 使用根目錄的 `docker-compose.yml` 啟動所有本地依賴（例如 PostgreSQL, Weaviate）。
- **互動測試**: 執行 `python -m src.sre_assistant.main` 啟動本地 FastAPI 伺服器。
- **單元與整合測試**: 所有測試都位於 `tests/` 目錄下，使用 `poetry run pytest` 執行。CI/CD 流程會自動運行這些測試。
- **評估**: 程式化的評估腳本位於 `eval/` 目錄下，用於衡量 Agent 的端到端表現和品質。

---

## Phase 1: MVP - 後端優先與核心能力建設 (預計 1-2 個月)

### P1 - 新功能 (New Features)

- **基礎設施 (Infrastructure)**
    - [✅] **TASK-P1-INFRA-01**: 創建 `docker-compose.yml`
      - **依賴**: 無
      - **驗收標準**:
        - [✅] 能夠透過 `docker-compose up` 成功啟動所有服務 (postgres, prometheus, grafana, loki, redis, weaviate)。
        - [✅] 服務之間網絡互通。
        - [✅] 數據卷掛載正確，數據可持久化。
      - **參考**:
        - **基礎結構參考**: [ADK Agent Samples: gemini-fullstack](docs/reference-adk-agent-samples.md#11-全端整合與前端開發-full-stack--frontend-integration) (其 `docker-compose.yml` 結構清晰，是絕佳的入門選擇)
        - **生產級範例**: [ADK Agent Samples: sre-bot](docs/reference-adk-agent-samples.md#19-sre-實踐與整合-sre-practices--integrations) (展示如何掛載本地憑證)
        - **可觀測性整合**: [ADK Agent Samples: a2a_telemetry](docs/reference-adk-agent-samples.md#6-可觀測性與追蹤-observability--tracing) (展示如何整合 LGTM Stack)
    - [✅] **TASK-P1-INFRA-02**: 編寫開發環境的啟動與使用文檔
      - **依賴**: [TASK-P1-INFRA-01]
      - **驗收標準**:
        - [✅] 文檔應包含環境要求、啟動步驟、停止步驟和常見問題排查。
        - [✅] 新成員能夠根據文檔獨立完成環境設置。

- **後端服務 (Backend Service)**
    - [✅] **TASK-P1-SVC-01**: 實現核心 `SREAssistant` Agent 服務
      - **依賴**: [TASK-P1-INFRA-01]
      - **參考**:
        - **主要藍圖**: `docs/references/snippets/salvaged_code.md` 中的 `EnhancedSREWorkflow` 程式碼範例。
        - **狀態傳遞模式**: [ADK Examples: workflow_agent_seq](docs/reference-adk-examples.md#開發團隊補充建議參考-additional-team-proposed-references) (展示 `SequentialAgent` 如何透過 `output_key` 在子代理之間傳遞狀態)。
        - **並行診斷模式**: [ADK Examples: parallel_functions](docs/reference-adk-examples.md#開發團隊補充建議參考-additional-team-proposed-references) (實現並行工具調用的關鍵模式)。
        - **宏觀架構**: [ADK Agent Samples: sre-bot](docs/reference-adk-agent-samples.md#19-sre-實踐與整合-sre-practices--integrations) (提供一個完整的 SRE Bot 應用架構)。
      - **驗收標準**:
        - [✅] 服務能成功啟動並監聽指定端口 (`poetry run python -m src.sre_assistant.main`)。
        - [✅] 在 `workflow.py` 中實現了 `EnhancedSREWorkflow` 的基本骨架。
        - [✅] 工作流程包含並行診斷、分診和驗證三個階段的佔位符代理。
        - [✅] `main.py` 中實現了 FastAPI 入口點，並提供 `/execute` 端點。
    - [✅] **TASK-P1-SVC-02**: 實現無認證模式
      - **依賴**: [TASK-P1-SVC-01]
      - **驗收標準**:
        - [✅] `main.py` 已整合 `AuthFactory`，並透過 FastAPI 依賴注入 `get_current_user`。
        - [✅] `development.yaml` 中設定 `auth.provider: "none"`。
        - [✅] 執行時，`NoAuthProvider` 會被載入，並在無 token 的情況下返回一個模擬用戶，API 請求成功。
    - [✅] **TASK-P1-SVC-03**: **核心服務本地化依賴與互動**
      - **依賴**: [TASK-P1-SVC-01]
      - **說明**: 由於 Docker 環境不穩，此任務放棄了原有的 `weaviate` 容器，改為使用本地安裝的 `PostgreSQL` (會話)、`Redis` (快取) 和 `ChromaDB` (記憶體)，以確保核心服務能夠穩定啟動並互動。
      - **驗收標準**:
        - [✅] `pyproject.toml` 已加入 `chromadb` 和 `sentence-transformers`。
        - [✅] 已實現 `ChromaBackend` 作為新的 `MemoryProvider`。
        - [✅] `development.yaml` 已更新，`memory.backend` 指向 `chroma`，`session_backend` 指向 `postgresql`。
        - [✅] 服務能成功啟動 (`poetry run python -m src.sre_assistant.main`)。
        - [✅] 透過 `curl` 測試 `/execute` 端點，服務能正確回應。

- **核心工具 (Core Tools)**
    - [ ] **TASK-P1-TOOL-01**: 實現 `PrometheusQueryTool`
      - **依賴**: [TASK-P1-SVC-01]
      - **參考**:
        - **主要實踐範本**: [ADK Examples: jira_agent](docs/reference-adk-examples.md#自定義工具與整合-custom-tools--integration) (提供了封裝 REST API 工具的最佳實踐)。
        - **最簡起點**: [ADK Snippets: func_tool.py](docs/reference-snippets.md#32-標準工具開發手動實現-standard-tool-development-manual-implementation) (展示了將 Python 函式轉換為工具的最快方式)。
        - **時間序列數據處理**: [ADK Agent Samples: fomc-research](docs/reference-adk-agent-samples.md#18-韌性與時間序列分析-resilience--time-series-analysis) (展示了處理時間序列數據的架構模式)。
        - **領域知識**: [Google SRE Book: Chapter 6](docs/reference-google-sre-book.md#part-ii-事件處理與可靠性實踐-incident-handling--reliability-practices) (SRE 的四大黃金訊號)。
        - **(挽救的程式碼) 在未來實現 SLO 相關功能時，可參考 `docs/references/snippets/salvaged_code.md` 中的 SLO 錯誤預算計算邏輯。**
      - **驗收標準**:
        - [ ] 能夠成功查詢 Prometheus 並返回指標數據。
        - [ ] 遵循 `SPEC.md` 中定義的 `ToolResult` 格式。
        - [ ] 有對應的單元測試。
    - [ ] **TASK-P1-TOOL-02**: 實現 `LokiLogQueryTool`
      - **依賴**: [TASK-P1-SVC-01]
      - **參考**: (同 TASK-P1-TOOL-01)
      - **驗收標準**:
        - [ ] 能夠成功查詢 Loki 並返回日誌數據。
        - [ ] 遵循 `SPEC.md` 中定義的 `ToolResult` 格式。
        - [ ] 有對應的單元測試。
    - [ ] **TASK-P1-TOOL-03**: 實現 `GitHubTool`
      - **依賴**: [TASK-P1-SVC-01]
      - **參考**:
        - **主要藍圖**: [ADK Agent Samples: github-agent](docs/reference-adk-agent-samples.md#8-工具開發-tool-development) (提供了最直接的範例)。
        - **備用參考**: [ADK Examples: jira_agent](docs/reference-adk-examples.md#自定義工具與整合-custom-tools--integration) (提供了類似的 API 工具封裝模式)。
      - **驗收標準**:
        - [ ] 能夠成功在指定的 GitHub Repo 中創建 Issue。
        - [ ] 遵循 `SPEC.md` 中定義的 `ToolResult` 格式。
        - [ ] 有對應的單元測試，並使用 mock 進行隔離。

- **核心服務 (Core Services)**
    - [ ] **TASK-P1-CORE-01**: 實現 `MemoryProvider` (RAG)
      - **依賴**: [TASK-P1-INFRA-01]
      - **參考**:
        - **主要藍圖**: [ADK Agent Samples: RAG](docs/reference-adk-agent-samples.md#5-檢索增強生成-rag-與記憶體) (提供了完整的 RAG 流程)。
        - **理論基礎**: [ADK Docs: Memory](docs/reference-adk-docs.md#核心框架與自訂擴展-core-framework--custom-extensions) (解釋了 `MemoryProvider` の概念)。
        - **擴展用例**: [ADK Agent Samples: llama_index_file_chat](docs/reference-adk-agent-samples.md#5-檢索增強生成-rag-與記憶體) (用於處理臨時上傳的檔案)。
        - **(挽救的程式碼) 在設計 RAG 最終輸出時，可參考 `docs/references/snippets/salvaged_code.md` 中的引用格式化邏輯。**
      - **驗收標準**:
        - [ ] 能夠將文檔向量化並存儲到 Weaviate。
        - [ ] 能夠根據查詢進行語義搜索並返回相關文檔片段。
        - [ ] 有整合測試驗證 RAG 流程。
    - [✅] **TASK-P1-CORE-02**: **實現 `session_service_builder` (PostgreSQL 持久化會話)**
      - **依賴**: [TASK-P1-INFRA-01]
      - **任務**: 實現一個 `session_service_builder`，它能根據配置返回一個基於 `DatabaseSessionService` 的 **PostgreSQL** 會話提供者。
      - **參考**:
        - **主要藍圖**: [ADK Agent Samples: customer-service](docs/reference-adk-agent-samples.md#9-領域特定工作流程-domain-specific-workflows) (展示了有狀態對話的必要性)。
        - **理論基礎**: [ADK Docs: Sessions](docs/reference-adk-docs.md#核心框架與自訂擴展-core-framework--custom-extensions) (解釋了 `session_service_builder` 的技術細節)。
        - **狀態管理實踐**: [ADK Examples: session_state_agent](docs/reference-adk-examples.md#開發者實踐補充範例-developers-cookbook) (展示了如何讀寫 `context.state`)。
        - **歷史使用實踐**: [ADK Examples: history_management](docs/reference-adk-examples.md#工程實踐與開發體驗-engineering-practices-developer-experience) (展示了如何在應用層使用歷史記錄)。
      - **驗收標準**:
        - [✅] `config_manager.py` 已更新，`SessionBackend` 枚舉中增加了 `POSTGRESQL` 選項，並添加了 `@model_validator` 來驗證相依性。
        - [✅] `session/backend_factory.py` 中已實現 `SessionFactory`，可根據配置創建 `DatabaseSessionService`。
        - [✅] `main.py` 已改為使用 `SessionFactory` 來動態創建 `session_service`。
        - [✅] `development.yaml` 已配置為使用 `session_backend: "postgresql"`。
    - [ ] **TASK-P1-CORE-03**: 實現 `AuthProvider` (OAuth 2.0)
      - **依賴**: [TASK-P1-SVC-01]
      - **參考**:
        - **主要藍圖**: [ADK Agent Samples: headless_agent_auth](docs/reference-adk-agent-samples.md#4-安全與認證-security--authentication) (展示了 M2M 認證流程)。
        - **工具層實踐**: [ADK Examples: oauth_calendar_agent](docs/reference-adk-examples.md#開發團隊補充建議參考-additional-team-proposed-references) (展示了工具如何使用認證憑證)。
        - **理論基礎**: [ADK Docs: Auth](docs/reference-adk-docs.md#核心框架與自訂擴證-core-framework--custom-extensions)。
        - **核心實踐**: `docs/references/snippets/salvaged_code.md` 關於 AuthManager 的重構建議。
      - **驗收標準**:
        - [ ] 實現一個**無狀態**的 `AuthProvider`，而不是一個有狀態的管理器。
        - [ ] 能夠與一個 OIDC Provider (如 Google) 完成認證流程。
        - [ ] 成功獲取並驗證 `id_token` 和 `access_token`。
        - [ ] 有整合測試（可使用 mock OIDC server）。
    - [ ] **TASK-P1-CORE-04**: **實現工作流程回調機制**
      - **依賴**: [TASK-P1-SVC-01]
      - **參考**:
          - **主要藍圖**: [ADK Examples: callbacks](docs/reference-adk-examples.md#phase-1--2-核心能力與-grafana-整合-core-capabilities--grafana-integration) (提供了最直接的 `before/after` 回調範例)。
          - **進階模式**: [ADK Examples: live_tool_callbacks_agent](docs/reference-adk-examples.md#工程實踐與開發體驗-engineering-practices-developer-experience) (用於即時串流進度更新)。
          - **理論基礎**: [ADK Docs: Callbacks](docs/reference-adk-docs.md#核心框架與自訂擴展-core-framework--custom-extensions)。
          - **原始需求**: `docs/references/snippets/salvaged_code.md` 中的 `_workflow_pre_check` 和 `_workflow_post_process` 範例。
      - **驗收標準**:
          - [ ] 前置檢查失敗時，能夠提前終止工作流程。
          - [ ] 工作流程結束後，能夠觸發後處理邏輯。

### P1 - 重構 (Refactoring)

- [✅] **TASK-P1-REFACTOR-01**: **(已移除)** ~~AuthManager 狀態管理~~
    - **說明**: 此任務已與 `TASK-P0-REFACTOR-01` 合併，因為它們都涉及將舊的 AuthManager 重構為無狀態工具。

### P1 - 技術債 (Technical Debt)

- [ ] **TASK-P1-DEBT-01**: 增加測試覆蓋率
    - **依賴**: [TASK-P1-CORE-01], [TASK-P1-CORE-02], [TASK-P1-CORE-03], [TASK-P1-TOOL-01], [TASK-P1-TOOL-02], [TASK-P1-TOOL-03]
    - **參考**:
        - [ADK Docs: Testing](docs/reference-adk-docs.md#開發與測試-development--testing)
    - **驗收標準**:
        - [ ] `pytest --cov` 報告顯示核心模組測試覆蓋率 > 80%。
        - [ ] CI 流水線中包含測試覆蓋率檢查步驟。
- [ ] **TASK-P1-DEBT-02**: **重構工具以實現標準化輸出**
    - **來源**: `docs/references/snippets/salvaged_code.md`, `SPEC.md`
    - **依賴**: [TASK-P1-TOOL-01], [TASK-P1-TOOL-02]
    - **參考**:
        - **直接實現**: [ADK Examples: output_schema_with_tools](docs/reference-adk-examples.md#開發者實踐補充範例-developers-cookbook) (提供了將 Pydantic 模型設為工具輸出的標準模式)。
        - **規格定義**: `SPEC.md` 中的「標準化介面、錯誤處理與版本管理」章節。
    - **驗收標準**:
        - [ ] 在 `contracts.py` 中定義了 `ToolResult` 和 `ToolError` Pydantic 模型。
        - [ ] 專案中定義了 `BaseTool` 協議 (Protocol)。
        - [ ] 所有工具的 `execute` 方法簽名都符合 `BaseTool` 協議，並返回 `ToolResult`。
        - [ ] 成功和失敗的工具調用都能返回結構化的 `ToolResult`，包含清晰的 `error.code`。
- [ ] **TASK-P1-DEBT-03**: **實現工具與代理的版本化管理**
    - **來源**: `docs/references/snippets/salvaged_code.md`
    - **依賴**: 無
    - **參考**:
        - **規格定義**: `SPEC.md` 中的「版本管理策略」章節。
    - **驗收標準**:
        - [ ] 專案的 `__init__.py` 或 `_version.py` 中定義了總體版本號。
        - [ ] 核心代理與工具的日誌或元數據中包含其版本號。
        - [ ] `CHANGELOG.md` 被建立並記錄了版本變更。

---

## Phase 2: Grafana 原生體驗 (預計 2-3 個月)

### P2 - 新功能 (New Features)

- **Grafana 插件 (Plugin Development)**
    - [ ] **TASK-P2-PLUGIN-01**: 開發 SRE Assistant Grafana App Plugin v1.0。
        - **參考**: [ADK Agent Samples: gemini-fullstack](docs/reference-adk-agent-samples.md#11-全端整合與前端開發-full-stack--frontend-integration)
    - [ ] **TASK-P2-PLUGIN-02**: 在插件中實現 ChatOps 面板。
        - **參考**:
          - [ADK Examples: callbacks](docs/reference-adk-examples.md#phase-1--2-核心能力與-grafana-整合-core-capabilities--grafana-integration) (用於提供進度更新)
          - [ADK Agent Samples: navigoAI_voice_agent_adk](docs/reference-adk-agent-samples.md#17-即時-ui-串流-real-time-ui-streaming) (WebSocket 串流的最佳實踐)
    - [ ] **TASK-P2-PLUGIN-03**: 實現插件與後端服務的 WebSocket / RESTful 安全通訊。
        - **參考**:
          - **主要藍圖**: [ADK Agent Samples: navigoAI_voice_agent_adk](docs/reference-adk-agent-samples.md#17-即時-ui-串流-real-time-ui-streaming) (WebSocket 的最佳實踐)。
          - **備用模式**: [ADK Examples: mcp_sse_agent](docs/reference-adk-examples.md#phase-1--2-核心能力與-grafana-整合-core-capabilities--grafana-integration) (展示了 Server-Sent Events 技術)。
          - **串流工具結果**: [ADK Examples: live_bidi_streaming_tools_agent](docs/reference-adk-examples.md#phase-1--2-核心能力與-grafana-整合-core-capabilities--grafana-integration) (串流最終結果)。
          - **串流工具進度**: [ADK Examples: live_tool_callbacks_agent](docs/reference-adk-examples.md#工程實踐與開發體驗-engineering-practices-developer-experience) (串流中間日誌)。
- **Grafana 整合 (Deep Integration)**
    - [ ] **TASK-P2-INTEG-01**: 實現 `GrafanaIntegrationTool` 的 `embed_panel` 功能。
        - **參考**: [ADK Snippets: OpenAPI Toolset](docs/reference-snippets.md#31-加速工具開發openapi-規格優先-accelerated-tool-development-openapi-spec-first)
        - **架構師建議**: 強烈建議採用 OpenAPI 優先的方法。在 `docker-compose.yml` 中為 Grafana 啟用 `swaggerUi` 旗標，然後使用 `OpenAPIToolset` 從其 `/swagger-ui` 端點自動生成此工具，而非手動編寫。
    - [ ] **TASK-P2-INTEG-02**: 實現 `GrafanaIntegrationTool` 的 `create_annotation` 功能。
        - **參考**: (同 TASK-P2-INTEG-01)
    - [ ] **TASK-P2-INTEG-03**: 實現 `GrafanaOnCallTool`。
        - **參考**: [Google SRE Book: Chapter 13](docs/reference-google-sre-book.md#part-ii-事件處理與可靠性實踐-incident-handling--reliability-practices)
- **DevOps 工具 (DevOps Tools)**
    - [ ] **TASK-P2-DEVOPS-01**: 實現 `TerraformTool`。
        - **參考**: [ADK Examples: code_execution](docs/reference-adk-examples.md#進階工作流與工程實踐-advanced-workflow--engineering-practices)
- **修復後驗證 (Post-Remediation Verification)**
    - [ ] **TASK-P2-VERIFY-01**: **實現修復後驗證代理 (Verification Agent)**
        - **參考**:
            - **主要模式**: [ADK Agent Samples: google-adk-workflows](docs/reference-adk-agent-samples.md#2-工作流程與協調模式-workflow--orchestration) (其 `SelfCriticAgent` 是此模式的黃金標準)。
            - **另一種思路**: [ADK Agent Samples: qa-test-planner-agent](docs/reference-adk-agent-samples.md#14-文件驅動的規劃與生成-documentation-driven-planning) (展示了代理如何讀取文件並生成結構化的驗證計畫)。
            - **原始需求**: `docs/references/snippets/salvaged_code.md` 中的 `VerificationAgent` 類別範例。
- **事件管理 (Incident Management)**
    - [ ] **TASK-P2-INCIDENT-01**: 整合 `GitHubTool`，實現從事件到 Issue 的自動創建。
        - **參考**: [ADK Agent Samples: github-agent](docs/reference-adk-agent-samples.md#8-工具開發-tool-development)
- **雲端整合工具 (Cloud Integration Tools)**
    - [ ] **TASK-P2-TOOL-04**: **實現 AppHubTool**
        - **參考**:
          - **主要藍圖**: [ADK Examples: jira_agent](docs/references/adk-examples/jira_agent/) (是封裝 REST API 工具的最佳實踐範本)。
          - **宏觀架構**: [ADK Agent Samples: sre-bot](docs/reference-adk-agent-samples.md#19-sre-實踐與整合-sre-practices--integrations) (提供了完整的 SRE Bot 架構)。
          - **理論基礎**: [Application monitoring in Google Cloud](https://cloud.google.com/blog/products/management-tools/get-to-know-cloud-observability-application-monitoring)。
    - [ ] **TASK-P2-TOOL-05**: **實現 GoogleCloudHealthTool**
        - **參考**: (同 TASK-P2-TOOL-04)

### P2 - 新功能 (New Features)
- **Agent 評估 (Agent Evaluation)**
    - [ ] **TASK-P2-EVAL-01**: **整合 ADK 評估框架**
        - **來源**: `docs/references/snippets/salvaged_code.md`
        - **依賴**: [TASK-P1-SVC-01]
        - **參考**:
            - **主要藍圖**: `docs/references/snippets/salvaged_code.md` 中的「實現 ADK 評估框架」程式碼範例。
            - **理論基礎**: `SPEC.md` 中的「代理可靠性評估」和「代理人評估策略」章節。
        - **驗收標準**:
            - [ ] `eval/` 目錄下包含一個基於 `google.adk.eval.EvaluationFramework` 的評估腳本。
            - [ ] 專案包含一個 `eval/golden_dataset.jsonl` 黃金數據集。
            - [ ] 評估腳本能夠運行並輸出準確性、延遲、成本等核心指標。
            - [ ] CI/CD 流程中包含一個可選的、用於執行評估的步驟。

### P2 - 重構 (Refactoring)

- [ ] **TASK-P2-REFACTOR-01**: **實現智能分診器 (Intelligent Dispatcher)**:
    - **來源**: `docs/references/snippets/salvaged_code.md`
    - **參考**:
        - **真實世界藍圖**: [ADK Agent Samples: brand-search-optimization](docs/reference-adk-agent-samples.md#16-進階工作流程與整合-advanced-workflows--integrations) (提供了最貼近真實應用的路由器範例)。
        - **基礎模式**: [ADK Agent Samples: google-adk-workflows](docs/reference-adk-agent-samples.md#2-工作流程與協調模式-workflow--orchestration) (其 `DispatcherAgent` 是此模式的基礎)。
        - **輕量化實現**: [ADK Examples: workflow_triage](docs/reference-adk-examples.md#開發團隊補充建議參考-additional-team-proposed-references) (提供了最簡潔的分診器實現)。
        - **原始需求**: `docs/references/snippets/salvaged_code.md` 中的 `IntelligentDispatcher` 類別範例。
- [ ] **TASK-P2-REFACTOR-02**: **實現增強型 SRE 工作流程 (Enhanced SRE Workflow)**
    - **來源**: `docs/references/snippets/salvaged_code.md`
    - **依賴**: [TASK-P1-SVC-01], [TASK-P2-REFACTOR-01], [TASK-P2-VERIFY-01]
    - **參考**:
        - **主要藍圖**: `docs/references/snippets/salvaged_code.md` 中的 `EnhancedSREWorkflow` 程式碼範例。
        - **理論基礎**: `ARCHITECTURE.md` 中的「核心工作流程代理」章節。
    - **驗收標準**:
        - [ ] `SREWorkflow` 被重構為 `EnhancedSREWorkflow`。
        - [ ] 並行診斷階段 (`ParallelAgent`) 使用了 `aggregation_strategy="custom"`。
        - [ ] 工作流程實現了 `before_agent_callback` 和 `after_agent_callback` 進行前置檢查和後處理。
        - `LoopAgent` 階段有明確的 `max_iterations` 和 `termination_condition`。
        - [ ] 工作流程中整合了 `VerificationAgent` 進行修復後驗證。

### P2 - 技術債 (Technical Debt)

- [ ] **TASK-P2-DEBT-01**: **令牌儲存安全強化**:
    - **參考**:
        - [ADK Agent Samples: adk_cloud_run](docs/reference-adk-agent-samples.md#7-部署與雲端整合-deployment--cloud-integration) (展示瞭如何使用 Secret Manager 管理密鑰)。
- [ ] **TASK-P2-DEBT-02**: **文檔更新**:
    - **任務**: 更新所有面向使用者的文檔，引導使用者從 ADK Web UI 過渡到 Grafana 插件。

---

## Phase 3 & 4: 聯邦化與未來 (Federation & Future)

- [ ] **TASK-P3-AGENT-01**: **(P3) 專業化代理**: 將覆盤報告生成功能重構為第一個獨立的 `PostmortemAgent`。
    - **參考**:
        - **理論基礎**: [Google SRE Book: Chapter 15 & Appendix D](docs/reference-google-sre-book.md#part-ii-事件處理與可靠性實踐-incident-handling--reliability-practices)。
        - **聯邦化架構**: [ADK Agent Samples: a2a_mcp](docs/reference-adk-agent-samples.md#3-聯邦化架構與服務發現-federated-architecture--service-discovery)。
- [ ] **TASK-P3-A2A-01**: **(P3) A2A 通訊**: 實現 gRPC A2A 通訊協議。
    - **參考**:
        - **主要藍圖**: [ADK Agent Samples: dice_agent_grpc](docs/reference-adk-agent-samples.md#10-a2a-通訊協定-a2a-communication-protocols)。
        - **基礎範例**: [ADK Examples: a2a_basic](docs/reference-adk-examples.md#phase-3--4-聯邦化與進階工作流-federation--advanced-workflows)。
- [ ] **TASK-P3-PREVENTION-01**: **(P3) 主動預防**: 整合機器學習模型。
    - **參考**:
        - **主要藍圖**: [ADK Agent Samples: machine-learning-engineering](docs/reference-adk-agent-samples.md#12-機器學習與預測分析-machine-learning--predictive-analysis)。
- [ ] **TASK-P3-MONITOR-01**: **(P3) 監控閉環**: 實現 `PrometheusConfigurationTool`。

### P3 - Agent 可觀測性 (Agent Observability)
- [ ] **TASK-P3-OBSERVE-01**: **實現 LLM 可觀測性追蹤**
    - **參考**:
        - **理論基礎**: [Datadog LLM Observability](https://docs.datadoghq.com/llm_observability/)。
        - **學術視野**: `docs/agents-companion-v2-zh-tw.md` (代理人評估)。
- [ ] **TASK-P3-OBSERVE-02**: **建立 LLM 可觀測性儀表板**
    - **參考**: `docs/agents-companion-v2-zh-tw.md` (代理人成功指標與評估)。

- [ ] **TASK-P4-ORCH-01**: **(P4) 聯邦協調器**: 開發功能完備的 SRE Orchestrator 服務。
    - **參考**: [ADK Agent Samples: a2a_mcp](docs/reference-adk-agent-samples.md#3-聯邦化架構與服務發現-federated-architecture--service-discovery)。
- [ ] **TASK-P4-AGENT-01**: **(P4) 代理矩陣**: 開發並部署 `CostOptimizationAgent` 和 `ChaosEngineeringAgent`。
    - **參考**: [ADK Agent Samples: any_agent_adversarial_multiagent](docs/reference-adk-agent-samples.md#15-自我對抗與韌性測試-self-adversarial--resilience-testing)。
- [ ] **TASK-P4-DISCOVERY-01**: **(P4) 服務發現**: 建立代理註冊中心。
    - **參考**: [ADK Agent Samples: a2a_mcp](docs/reference-adk-agent-samples.md#3-聯邦化架構與服務發現-federated-architecture--service-discovery)。