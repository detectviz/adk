# ADK Agent 範例參考指南

**文件作者**: Google ADK 首席架構師
**目標讀者**: SRE Assistant 專案開發團隊
**目的**: 本指南旨在從現有的 ADK Agent 範例中，篩選出與 SRE Assistant 專案高度相關的參考實現，以加速開發進程、統一技術選型、並遵循 ADK 最佳實踐。所有參考原因均直接鏈接到 `ARCHITECTURE.md`, `ROADMAP.md`, `SPEC.md`, 和 `TASKS.md` 中定義的具體要求。

---

## 總覽：核心推薦範例

| 類別 | 推薦範例 | 主要參考價值 | 對應階段 |
| :--- | :--- | :--- | :--- |
| **A2A 與多代理** | `a2a_mcp` | **聯邦化架構的黃金標準**，演示了協調器與多個專家代理的協同工作模式。 | Phase 3+ |
| **核心 ADK 擴展** | `headless_agent_auth` | **OAuth 2.0 認證** (`AuthProvider`) 的最直接實現。 | Phase 1 |
| **核心 ADK 擴展** | `RAG` | **RAG 與記憶體** (`MemoryProvider`) 的標準實現。 | Phase 1 |
| **A2A 通訊協議**| `dice_agent_grpc` | **gRPC A2A 通訊** 的最簡潔範例，適合入門。 | Phase 3 |
| **基礎設施** | `a2a_telemetry` | **Docker Compose** 環境設置的最佳實踐。 | Phase 1 |
| **工具開發** | `github-agent` | **標準化工具** 開發的清晰範例。 | Phase 1 |
| **工作流模式** | `google-adk-workflows`| **複雜工作流** (分發、並行、評判) 的權威指南。 | Phase 2+ |
| **整體架構** | `customer-service` | 遵循**目標目錄結構**和 Pydantic 合約的優秀範例。 | Phase 1+ |

---

## 1. 核心 ADK 功能擴展 (Phase 1)

此類別的範例專注於 `TASKS.md` 中 Phase 1 的核心服務 (`CORE`) 任務，是實現 SRE Assistant 後端服務的基石。

### 1.1. 認證 (Authentication)

- **檔案路徑**: `docs/references/adk-agent-samples/headless_agent_auth/`
- **參考原因**:
    - **直接對應 `TASK-P1-CORE-03: 實現 AuthProvider (OAuth 2.0)`**。
    - 該範例中的 `oauth2_middleware.py` 提供了一個清晰的、基於 FastAPI 中間件的 OAuth 2.0 令牌驗證流程。
    - 這是實現 `ARCHITECTURE.md` 中定義的、與 Grafana 整合的 SSO 認證流程的關鍵參考。
    - `test_client.py` 演示了如何編寫與需要認證的 Agent 服務互動的測試客戶端。

### 1.2. 記憶體 (Memory / RAG)

- **檔案路徑**: `docs/references/adk-agent-samples/RAG/`
- **參考原因**:
    - **直接對應 `TASK-P1-CORE-01: 實現 MemoryProvider (RAG)`**。
    - 完整演示了從文檔加載、向量化、存儲到檢索的完整 RAG 流程。
    - `rag/agent.py` 展示瞭如何將 RAG 作為代理的核心能力來回答問題，這與 SRE Assistant 的診斷流程高度相關。
    - `deployment/` 目錄下的腳本展示了如何部署一個依賴向量數據庫的 Agent，為我們的部署提供了參考。

### 1.3. 會話管理 (Session Management)

- **檔案路徑**: `docs/references/adk-agent-samples/crewai/`
- **參考原因**:
    - **間接對應 `TASK-P1-CORE-02: 實現 session_service_builder`**。
    - 雖然此範例未使用 ADK 的 `session_service_builder`，但 `in_memory_cache.py` 實現了一個自定義的會話緩存機制。
    - 開發團隊可以參考其設計模式，來實現我們自己的、基於 Redis/PostgreSQL 的持久化會d話服務，將其封裝在 `SessionProvider` 中。

---

## 2. A2A 與多代理模式 (Phase 3+)

此類別的範例是實現 `ARCHITECTURE.md` 中長期聯邦化願景的關鍵。

### 2.1. 聯邦化協調器 (Federated Orchestrator)

- **檔案路徑**: `docs/references/adk-agent-samples/a2a_mcp/`
- **參考原因**:
    - **是 `Phase 3` 中 `SRE Orchestrator` 和 `PostmortemAgent` 協同工作的最佳原型**。
    - `src/a2a_mcp/orchestrator_agent.py` 完美演示了協調器如何接收任務，並將其路由給不同的專家代理（`air_ticketing_agent`, `car_rental_agent` 等）。
    - 這是對 `ARCHITECTURE.md` 中聯邦化設計最直接、最權威的參考實現。
    - `agent_cards/` 目錄展示了如何定義每個代理的能力，這對我們的服務發現機制有啟發意義。

### 2.2. gRPC A2A 通訊

- **檔案路徑**: `docs/references/adk-agent-samples/dice_agent_grpc/`
- **參考原因**:
    - **直接對應 `TASK-P3-A2A-01: 實現 gRPC A2A 通訊協議`**。
    - 提供了一個最簡潔的、使用 gRPC 與 ADK Agent 通訊的範例。
    - `test_client.py` 展示了 gRPC 客戶端的寫法，是開發 `SRE Orchestrator` 調用 `PostmortemAgent` 時的絕佳參考。
    - 幫助團隊快速掌握 ADK 中 A2A 的基礎知識，然後再去理解 `a2a_mcp` 中更複雜的模式。

### 2.3. 工作流與順序執行

- **檔案路徑**: `docs/references/adk-agent-samples/google-adk-workflows/`
- **參考原因**:
    - **為 `SPEC.md` 中定義的 `事件處理 Assistant` 這種複雜工作流提供了權威實現**。
    - `dispatcher/`: 演示了如何根據輸入動態路由到不同的子代理，這對 `SREIntelligentDispatcher` 的重構任務有重要價值。
    - `self_critic/`: 演示了“評判者”模式，即一個代理檢查另一個代理的輸出，這與我們規劃的 `VerificationCriticAgent` 完全一致。
    - `parallel/`: 演示了並行執行，可用於同時查詢日誌和指標的場景。

---

## 3. 工具、基礎設施與測試

此類別的範例專注於支撐整個專案的工程實踐。

### 3.1. 基礎設施即代碼

- **檔案路徑**: `docs/references/adk-agent-samples/a2a_telemetry/`
- **參考原因**:
    - **直接對應 `TASK-P1-INFRA-01: 創建 docker-compose.yml`**。
    - `docker-compose.yaml` 文件提供了一個包含多個服務（在本例中是 OpenTelemetry Collector）的完整、可運行的環境範例。
    - 這是我們構建本地開發環境的最佳起點。

### 3.2. 標準化工具開發

- **檔案路徑**: `docs/references/adk-agent-samples/github-agent/`
- **參考原因**:
    - **直接對應 `TASK-P1-TOOL-03: 實現 GitHubTool`**。
    - `github_toolset.py` 展示了如何將多個相關功能（如 `create_issue`, `get_repo_info`）組織在一個工具集 `GitHubToolset` 中。
    - 其清晰的結構和單一職責原則是我們實現 `PrometheusQueryTool`, `LokiLogQueryTool` 等所有工具的典範。

### 3.3. 配置管理

- **檔案路徑**: `docs/references/adk-agent-samples/personal-expense-assistant-adk/`
- **參考原因**:
    - `settings.yaml.example` 和 `settings.py` 展示了一種從 YAML 文件加載配置的常用模式。
    - 這為我們實現 `config/config_manager.py` 提供了一個簡單直接的參考。

### 3.4. 整體結構與合約

- **檔案路徑**: `docs/references/adk-agent-samples/customer-service/`
- **參考原因**:
    - **提供了與 `TASKS.md` 中定義的 `目標目錄結構` 高度一致的範例**。
    - `customer_service/entities/` 目錄類似於我們的 `contracts.py`，展示了如何使用 Pydantic 來定義數據實體。
    - `customer_service/tools/` 和 `customer_service/config.py` 的組織方式都值得我們借鑒。
    - `eval/` 和 `tests/` 目錄的存在，強調了測試和評估在 Agent 開發中的重要性，符合 `TASK-P1-DEBT-01` 的要求。
