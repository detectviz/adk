# SRE Assistant 專案之 ADK 範例參考指南

**版本**: 1.0.0
**狀態**: 生效中
**維護者**: SRE Platform Team

## 1. 總覽

本文件旨在為 SRE Assistant 的開發團隊提供一份精選的 Google Agent Development Kit (ADK) 範例清單。這些範例都經過了系統性的評估，以確保它們與我們的核心文件 (`ARCHITECTURE.md`, `ROADMAP.md`, `SPEC.md`, `TASKS.md`) 高度相關。每個範例都附有詳細的「參考原因」，說明其為何對本專案至關重要，以及如何借鑑其設計與實現來加速我們的開發進程。

---

## 2. 核心參考範例

### 2.1. SRE / DevOps 領域與核心架構

*   **檔案路徑**: `docs/references/adk-agent-samples/sre-bot/`
*   **參考原因**:
    **這是與本專案最相關的範例，可作為 Phase 1 開發的主要藍圖。** 它在領域、技術棧和架構上與 SRE Assistant 高度重疊。
    *   **關鍵參考點**:
        *   **工具實現**: `agents/sre_agent/kube_agent.py` 提供了 `KubernetesOperationTool` 的完整實現，其模式可直接應用於 `SPEC.md` 中定義的 `PrometheusQueryTool` 和 `LokiLogQueryTool`。
        *   **持久化會話**: `agents/sre_agent/agent.py` 中的 `DatabaseSessionService` 實例，以及 `docker-compose.yml` 中的 PostgreSQL 服務，為 `TASK-P1-CORE-02` (實現持久化會話) 提供了直接的程式碼參考。其 README 中對 `user_id` 和 `session_id` 管理的詳細說明，對我們至關重要。
        *   **基礎設施即代碼**: 根目錄下的 `docker-compose.yml` 和 `Dockerfile` 是完成 `TASK-P1-INFRA-01` (創建 `docker-compose.yml`) 的絕佳起點。
        *   **專案結構**: `agents/sre_agent/` 的子代理結構，為我們在 `TASKS.md` 中規劃的目標目錄結構提供了實踐範例。
    *   **對專案的價值**: 加速 Phase 1 核心功能的開發，特別是在工具和持久化會話的實現上，可大量借鑑其成熟的模式，降低開發風險。

### 2.2. 檢索增強生成 (RAG) 與評估

*   **檔案路徑**: `docs/references/adk-agent-samples/RAG/`
*   **參考原因**:
    **此範例是實現 SRE Assistant 知識庫（RAG）和評估框架的關鍵參考。** 它詳細展示了如何將外部向量數據庫與 ADK 整合。
    *   **關鍵參考點**:
        *   **MemoryProvider 模式**: `rag/agent.py` 中使用的 `VertexAiRagRetrieval` 工具展示了整合外部 RAG 服務的模式。我們可以遵循此模式，將其替換為我們的首選方案 Weaviate，以完成 `TASK-P1-CORE-01` (實現 `MemoryProvider`)。
        *   **語料庫管理**: `rag/shared_libraries/prepare_corpus_and_data.py` 提供了一個用於上傳文檔到向量數據庫的腳本，我們可以借鑑此方法來管理我們的 Runbook 和事件歷史文檔。
        *   **評估框架**: `eval/` 目錄下的完整評估方案 (`test_eval.py`, `conversation.test.json`) 是我們建立自身評估體系、完成 `TASK-P1-DEBT-01` (增加測試覆蓋率) 的最佳實踐範例。
        *   **部署與權限**: `deployment/grant_permissions.sh` 腳本提醒並展示了如何處理代理服務與數據庫之間的授權問題，這是一個關鍵的安全實踐。
    *   **對專案的價值**: 為專案的 RAG 功能提供了清晰的實現路徑，並建立了一套科學的評估方法，確保代理的回答品質。

### 2.3. 聯邦化多代理架構 (A2A)

*   **檔案路徑**: `docs/references/adk-agent-samples/a2a_mcp/`
*   **參考原因**:
    **此範例是實現 SRE Assistant 長期聯邦化願景的架構藍圖。** 它展示了如何構建一個由協調器和多個專業代理協同工作的複雜系統。
    *   **關鍵參考點**:
        *   **聯邦化設計**: 該範例中的「協調者代理 (Orchestrator Agent)」和多個「任務代理 (Task Agents)」的設計，完美對應了 `ARCHITECTURE.md` 中定義的聯邦化生態系統。
        *   **代理發現**: 使用 **MCP (Model Content Protocol) 伺服器** 作為「代理卡 (Agent Card)」的註冊中心，為我們在 Phase 3/4 中實現動態代理發現提供了強大的設計模式。
        *   **A2A 通訊**: 該範例是 `TASK-P3-A2A-01` (實現 gRPC A2A 通訊協議) 的直接技術參考。
    *   **對專案的價值**: 確保我們在 Phase 1 的設計能夠平滑地演進到 Phase 3/4 的聯邦化架構，避免走彎路。為未來的 `Federal Coordinator` 和專業化代理的開發奠定了理論和實踐基礎。

### 2.4. 認證 (OAuth 2.0)

*   **檔案路徑**: `docs/references/adk-agent-samples/headless_agent_auth/`
*   **參考原因**:
    **此範例為 `TASK-P1-CORE-03` (實現 `AuthProvider`) 提供了具體的 OAuth 2.0 實現參考。**
    *   **關鍵參考點**:
        *   **AuthProvider 模式**: 該範例展示了如何在 ADK 代理中整合標準的第三方 OIDC 供應商（如此處的 Auth0），這與我們需要對接 Grafana 認證的場景完全一致。
        *   **多種授權流程**: 同時展示了「客戶端憑證流程」(適用於未來 A2A 通訊) 和「CIBA 流程」(一種無頭瀏覽器的用戶授權模式)，為我們處理不同場景下的認證需求提供了靈活的參考方案。
        *   **程式碼結構**: `oauth2_middleware.py` 的實現方式可作為我們自定義 `AuthProvider` 的樣板。
    *   **對專案的價值**: 大幅簡化了 OAuth 2.0 整合的複雜性，提供了經過驗證的實現模式，有助於我們快速、安全地完成認證功能的開發。

### 2.5. 特定工具實現

*   **檔案路徑**: `docs/references/adk-agent-samples/github-agent/`
*   **參考原因**:
    **為 `TASK-P1-TOOL-03` (實現 `GitHubTool`) 提供了即用型的程式碼參考。**
    *   **關鍵參考點**:
        *   **`github_toolset.py`**: 該文件中的 `get_user_repositories`, `get_recent_commits` 等函式，可以直接或稍作修改後用於我們的 `GitHubTool`，以滿足 `SPEC.md` 中定義的 `create_issue` 等功能需求。
    *   **對專案的價值**: 節省了從零開始編寫 GitHub API 客戶端的時間，讓我們可以專注於將其整合到 SRE 的工作流程中。

---
