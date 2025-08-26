# SRE Assistant 專案架構

本文件旨在說明 SRE Assistant 專案的具體架構，為開發者提供一個清晰的指南。本專案遵循 Google ADK 的核心原則，並根據 SRE 自動化的特定需求進行了客製化。

### 核心理念

SRE Assistant 的核心是一個以 **Grafana 為統一操作介面**、由**多個專業化智能代理協同工作**的**聯邦化 SRE 生態系統**。我們的目標是打造一個不僅能自動化解決問題，更能預測和預防未來故障的智能平台。

- **程式碼優先 (Code-First)**: 所有代理、工具和工作流程都在 Python 程式碼中定義。
- **模組化與聯邦化 (Modularity & Federation)**: 複雜的 SRE 工作流程由一個主協調器 (`SREWorkflow`) 調用多個小型、專業的子代理來完成。
- **可擴展的服務 (Extensible Services)**: 認證、記憶體和會話管理等核心服務被設計為可插拔的提供者 (Provider) 模式，以適應不同的生產環境。

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

以上是為 SRE Assistant 專案量身打造的架構說明。