# SRE Assistant 適用的 ADK Agent 範例參考指南

**版本**: 1.0.0
**狀態**: Alpha
**目的**: 本文件提供一份精選的 ADK Agent 範例清單，旨在為 SRE Assistant 專案的開發提供指引。每個範例都因其與專案特定的架構目標、路線圖階段和技術任務的相關性而被選中。

---

## 1. 多代理 (Multi-Agent) 與協調 (Orchestration) (Phase 3+)

### 1.1. 使用 MCP 作為註冊中心的 A2A
- **檔案路徑**: `docs/references/adk-agent-samples/a2a_mcp/`
- **參考原因**:
  - **聯邦式架構的主要參考**: 此範例是專案長期 (Phase 3+) 聯邦式、多代理生態系統願景最關鍵的參考。它提供了一個完整、可運作的 **Orchestrator Agent (協調代理)** 實作，該代理能動態地發現、溝通並協調專業的 **Task Agents (任務代理)**。
  - **服務發現模式**: 它介紹了使用 **模型內容協議 (MCP) 伺服器** 作為代理服務註冊中心的概念。這是一個穩健的模式，直接解決了架構中提出的「服務發現」機制的需求。SRE Assistant 專案應採用此模式來滿足其代理註冊和發現的需求。
  - **A2A 通訊流程**: 它展示了完整的代理對代理 (A2A) 通訊生命週期：協調者在註冊中心查詢代理的「名片 (card)」，然後使用該資訊建立直接通訊。
  - **重點研究檔案**:
    - `src/a2a_mcp/agents/orchestrator_agent.py`: 協調者的核心邏輯。
    - `src/a2a_mcp/mcp/server.py`: 代理註冊中心的實作。
    - `agent_cards/`: 代理元資料的結構。

### 1.2. 使用 gRPC 的骰子代理
- **檔案路徑**: `docs/references/adk-agent-samples/dice_agent_grpc/`
- **參考原因**:
  - **簡化的 gRPC 範例**: 雖然 `a2a_mcp` 展示了一個複雜的系統，但此範例提供了一個極簡、專注的單一代理透過 **gRPC** 公開服務的範例。
  - **A2A 的初始實作**: 這對於 A2A 協議的初始實作 (根據 `ROADMAP.md` 中的 Phase 3) 是一個寶貴的參考，該協議將連接主要的 SRE Assistant 與第一個專業化代理 (例如 `PostmortemAgent`)。它讓開發人員在處理完整的協調模型之前，能先理解 ADK 中 gRPC 的核心機制。

---
## 2. 核心 ADK 供應商 (Providers) 與服務 (Phase 1)

### 2.1. 無頭代理驗證
- **檔案路徑**: `docs/references/adk-agent-samples/headless_agent_auth/`
- **參考原因**:
  - **驗證功能的主要參考**: 這是 **TASK-P1-CORE-03: 實現 `AuthProvider` (OAuth 2.0)** 的最佳參考。
  - **OAuth 2.0 流程**: 它展示了客戶端憑證和以使用者為中心的 (CIBA) OAuth 2.0 流程，為 SRE Assistant 的驗證需求提供了基本的建構模塊。
  - **自訂供應商模式**: `oauth2_middleware.py` 檔案是一個具體的範例，說明如何在 ADK 的 Web 伺服器中實現並整合自訂的 `AuthProvider`，這正是 SRE Assistant 為支援其 OIDC 供應商所需執行的工作。

### 2.2. RAG (檢索增強生成)
- **檔案路徑**: `docs/references/adk-agent-samples/RAG/`
- **參考原因**:
  - **RAG 功能的主要參考**: 此範例是 **TASK-P1-CORE-01: 實現 `MemoryProvider` (RAG)** 的關鍵參考。
  - **檢索工具模式**: 儘管它使用 Vertex AI 的 RAG 引擎，但其建立專用檢索工具 (`VertexAiRagRetrieval`) 並將其整合到代理推理過程的核心模式，可直接轉移到專案計劃使用的 Weaviate 後端。
  - **最佳實踐**: 其專案結構包含了專用的 `deployment` 和 `eval` 目錄，可作為 SRE Assistant 自身儲存庫結構和 CI/CD 流程的最佳實踐模型。

### 2.3. 客戶服務代理
- **檔案路徑**: `docs/references/adk-agent-samples/customer-service/`
- **參考原因**:
  - **會話管理的主要參考**: 此範例是 **TASK-P1-CORE-02: 實現 `session_service_builder` (持久化會話)** 必要性的最佳說明。
  - **有狀態對話範例**: 它展示了一個有狀態的對話，其中代理會記住客戶的上下文（姓名、購物車、歷史記錄）。這為 SRE Assistant 在使用者互動中維持上下文的需求提供了清晰的用例和概念模型。
  - **狀態管理的程式碼指標**: README 文件指向 `customer_service/entities/customer.py` 並討論了從 CRM 加載狀態。這為開發人員設計和實現將連接到 Redis 和 PostgreSQL 的自訂 `session_service_builder` 提供了堅實的起點。

---
## 3. 工具實作

### 3.1. GitHub 代理
- **檔案路徑**: `docs/references/adk-agent-samples/github-agent/`
- **參考原因**:
  - **直接的工具範例**: 這為 **TASK-P1-TOOL-03: 實現 `GitHubTool`** 提供了一個直接、相關的範例。
  - **程式碼模板**: `github_toolset.py` 檔案可作為 SRE Assistant 自身 `GitHubTool` 的直接模板或強力參考，該工具是根據 `SPEC.md` 中定義的、在 GitHub 中創建和管理事件相關問題的必要組件。
