# ADK 代理範例參考指南 (SRE Assistant)

**版本**: 1.0.0
**維護者**: SRE Platform Team
**目的**: 本文件旨在為 SRE Assistant 專案的開發團隊提供一份精選的 Google ADK 範例參考列表。每個範例都經過評估，以確保其與我們的架構 (`ARCHITECTURE.md`)、路線圖 (`ROADMAP.md`) 和具體開發任務 (`TASKS.md`) 高度相關。

---

## 總覽

本指南中的範例涵蓋了 SRE Assistant 專案在 Phase 1 及未來階段所需的關鍵技術和架構模式。開發人員在執行特定任務時，應優先參考這些範例，以加速開發進程、統一實施標準並遵循 ADK 最佳實踐。

---

## 核心架構與服務 (Core Architecture & Services)

### 1. 檢索增強生成 (RAG) 與記憶體

- **範例路徑**: `docs/references/adk-agent-samples/RAG/`
- **參考原因**:
    - **直接對應**: 此範例是實現 `MemoryProvider` 的權威參考，該提供者是 SRE Assistant 進行知識庫檢索的核心。
    - **技術細節**: 展示了如何整合向量數據庫（如 Weaviate），以及如何構建索引、檢索和生成流程。
    - **關聯任務**:
        - **[TASK-P1-CORE-01]**: 實現 `MemoryProvider` (RAG)。開發此任務時，應直接借鑒此範例的 `rag/agent.py` 和數據處理流程。

### 2. 無頭認證 (Headless Authentication)

- **範例路徑**: `docs/references/adk-agent-samples/headless_agent_auth/`
- **參考原因**:
    - **關鍵功能**: SRE Assistant 需要與 Grafana 的 OAuth 2.0 流程整合。此範例展示了如何在後端服務中處理基於 Token 的無頭認證，這與我們的需求完全一致。
    - **實現細節**: 提供了 `oauth2_middleware.py`，這是一個實現 OAuth 2.0 驗證中間件的絕佳範本。它演示了如何解析和驗證 Bearer Token。
    - **關聯任務**:
        - **[TASK-P1-CORE-03]**: 實現 `AuthProvider` (OAuth 2.0)。此範例是實現該任務的主要參考。

### 3. 部署 (Deployment)

- **範例路徑**: `docs/references/adk-agent-samples/adk_cloud_run/`
- **參考原因**:
    - **容器化實踐**: 提供了將 ADK 應用程式容器化的標準 `Dockerfile`。
    - **雲原生部署**: 展示了如何將代理部署到 Google Cloud Run，這為我們未來的生產環境部署提供了清晰的指引。
    - **基礎設施即代碼**: 雖然 SRE Assistant 初期使用 `docker-compose`，但此範例中的部署腳本和容器化方法對 CI/CD 流程的建設極具參考價值。
    - **關聯任務**:
        - **[TASK-P1-INFRA-01]**: 創建 `docker-compose.yml`。雖然不直接相關，但其 `Dockerfile` 是我們服務容器化的基礎。

---

## 多代理與工作流 (Multi-Agent & Workflows)

### 1. Agent-to-Agent (A2A) 通訊

- **範例路徑**: `docs/references/adk-agent-samples/a2a_mcp/`
- **參考原因**:
    - **未來架構**: 這是實現我們聯邦化架構願景 (Phase 3 & 4) 的核心技術範例。
    - **協作模式**: 清晰地展示了協調器 (Orchestrator) 如何與多個專業化代理 (Planner, Car Rental, Hotel Booking) 透過 A2A 協議進行通訊和協作。
    - **協議細節**: 提供了 Agent Card (`agent_cards/*.json`) 的定義和使用方式，這對於我們設計 `SPEC.md` 中的專業化代理介面至關重要。
    - **關聯任務**:
        - **(P3) A2A 通訊**: 實現 gRPC A2A 通訊協議。
        - **(P4) 聯邦協調器**: 開發 SRE Orchestrator 服務。

### 2. 複雜工作流模式

- **範例路徑**: `docs/references/adk-agent-samples/google-adk-workflows/`
- **參考原因**:
    - **模式多樣性**: 提供了三種對 SRE Assistant 極具價值的複雜工作流模式：
        1.  **Dispatcher**: 類似於我們的 `SREIntelligentDispatcher` 構想，根據輸入動態路由到不同的子代理。
        2.  **Parallel**: 允許並行執行多個工具或子任務，對提高診斷效率至關重要。
        3.  **Self-Critic**: 引入了“自我批評”的循環，讓代理可以評估和修正自己的輸出，這對於提高覆盤報告和修復建議的質量非常有幫助。
    - **架構模式**: 這些模式可以直接應用於 `sre_assistant/workflow.py` 的設計中，以處理複雜的事件處理流程。

### 3. 包含子代理的階層式代理

- **範例路徑**: `docs/references/adk-agent-samples/data-science/`
- **參考原因**:
    - **結構化設計**: 這是如何將一個複雜任務（如數據科學分析）分解為一個主代理和多個子代理 (`sub_agents/`) 的絕佳範例。
    - **代碼組織**: 其目錄結構 (`data_science/sub_agents/*`) 與我們在 `TASKS.md` 中定義的目標結構高度一致，為我們組織 `sre_assistant/sub_agents/` 提供了實踐範本。
    - **任務分解**: 展示了主代理如何規劃任務，並將其委派給專門的子代理（如 `problem_definition_agent`, `data_collection_agent`）來執行。

---

## 工具與整合 (Tools & Integrations)

### 1. GitHub 工具整合

- **範例路path**: `docs/references/adk-agent-samples/github-agent/`
- **參考原因**:
    - **直接對應**: 此範例完美地展示了如何實現一個與 GitHub API 互動的工具集 (`github_toolset.py`)。
    - **最佳實踐**: 提供了完整的工具定義、函數簽名和錯誤處理，是實現我們自己的 `GitHubTool` 的理想起點。
    - **關聯任務**:
        - **[TASK-P1-TOOL-03]**: 實現 `GitHubTool`。開發此任務時，應直接參考此範例的實現。

### 2. 可觀測性與遙測

- **範例路徑**: `docs/references/adk-agent-samples/a2a_telemetry/`
- **參考原因**:
    - **監控整合**: 此範例展示瞭如何從 ADK 代理中導出遙測數據 (Telemetry)，並將其發送到監控後端（如此處的 `otel-collector`)。
    - **LGTM 整合**: 雖然它使用的是通用 OpenTelemetry，但其原理與我們整合 LGTM Stack (Loki, Grafana, Tempo, Mimir) 的目標完全相同。它為我們實現“可觀測性驅動”的設計原則提供了技術基礎。
    - **關聯架構**: 直接支持 `ARCHITECTURE.md` 中定義的“可觀測性”組件。
