### **Google ADK 多代理系統 - 標準專案架構範本**

**文件ID:** ADK-ARCH-TPL-V2.1
**版本:** 2.1
**狀態:** 草案
**作者:** Jules, ADK 首席架構師

---

### **1. 系統總覽 (System Overview & Concept)**
- **架構背景與目標 (Purpose & Goal):**
  本文件定義了使用 Google Agent Development Kit (ADK) 構建多代理系統 (Multi-Agentic System) 的標準技術架構。其旨在提供一個可重複使用的範本，確保專案在技術棧、組件設計、通訊協議和開發生命週期上的一致性與高品質。
- **適用業務場景 (Business Scenarios):**
  適用於需要自動化複雜工作流、整合多種工具與資料來源，並能進行多步驟推理的場景，例如：智慧客服、自動化 SRE 維運、複雜數據分析與報告生成等。
- **高階流程圖 (High-Level Architecture Diagram):**
  此架構分為四個主要層次：使用者介面 (UI)、ADK 執行時 (Runtime)、代理系統 (Agent System) 和基礎組件 (Foundation Components)，與 `docs/references/adk-architecture/adk-high-level-architecture.png` 中所示一致。

---

### **2. 組件設計 (Component Architecture)**
- **設計原則 (Design Principles):**
  - **代理 (Agent):** 每個代理都是一個專注的、可獨立測試的推理單元。
  - **工具 (Tool):** 工具必須是無狀態且確定性的，作為代理與外部世界的接口。
  - **狀態 (State):** 代理本身無狀態，所有上下文皆通過 `State` 物件在調用間顯式傳遞。
- **核心組件定義 (Core Components):**
  - **`Agent` (代理):** 負責執行推理循環 (`Thought -> Action -> Observation`) 的核心類。其類型包括：LLM 代理 (推理決策)、工作流代理 (流程協調)、自訂代理 (專門行為)。
  - **`Tool` (工具):** 代理可以執行的原子化功能，通過 Python 函數和型別提示自動生成結構化描述。
  - **`Runner` (執行器):** ADK 的事件循環與協調核心，管理代理的生命週期。
  - **`Session` & `Memory` (會話與記憶):** `Session` 提供短期記憶 (in-memory 或 DB-backed)，而 `Memory` 提供長期記憶 (e.g., VectorDB for RAG)，實現上下文的持久化。

---

### **3. 多代理協作與通訊 (Multi-Agent Collaboration & Messaging)**
- **多代理分層規劃 (Hierarchy & Patterns):**
  - **`Orchestrator-Worker` (編排器-工作者模式):** 最常見的模式。編排器作為元代理，將複雜任務分解並路由給專職的 Worker Agent。
  - **`Sequential & Parallel` (循序與並行模式):** `Workflow Agents` (工作流代理) 負責管理任務流。`SequentialAgent` 按順序執行，而 `ParallelAgent` 則並發執行獨立的子任務。
  - **`LoopAgent` (循環代理):** 用於需要迭代改進的任務，如程式碼修復或自我批判。
- **A2A (Agent-to-Agent) 通訊協定:**
  - **共享狀態 (Shared State):** 代理通過讀寫共享的 `session.state` 進行隱式通訊。
  - **顯式調用 (Explicit Call):** 一個代理可以將另一個代理封裝為 `AgentTool` 並直接調用它。
  - **事件驅動 (Event-Driven):** 代理可以發出事件，由 `Runner` 或其他代理監聽並觸發相應行為。
- **S-Expression 消息格式:**
  - ADK 內部使用 S-Expression 在代理與 LLM 之間進行結構化通訊，確保指令的精確性和可預測性。

---

### **4. 工具與外部服務整合 (Tooling & External Integration)**
- **工具/模型註冊與管理 (Registration & Management):**
  - 工具應在一個集中的註冊表 (e.g., `tool_registry.py`) 中定義，便於共享和管理。
  - ADK 支持多種類型的工具：`FunctionTools` (標準函數), `AgentTools` (代理作為工具), 和 `LongRunningFunctionTools` (用於異步任務，如人類介入)。
- **外部整合方式 (External Integration):**
  - 通過為外部服務 (e.g., Grafana API, Google Calendar API) 編寫包裝函數 (wrapper functions) 並用 `@tool` 裝飾，可以輕鬆將其整合為 ADK 工具。
- **授權與安全 (Authorization & Security):**
  - API Key 和其他敏感憑證應通過安全的秘密管理服務傳遞，而不是硬編碼在程式碼中。
  - 可以使用 `before_tool_callback` 回調函數來實現對工具執行的細粒度權限控制。

---

### **5. 工作流與事件處理 (Workflow & Event Handling)**
- **事件驅動機制 (Event-Driven Mechanism):**
  - ADK 的執行是事件驅動的。`Runner` 在每個步驟（如模型調用前後、工具執行前後）都會發出事件。
- **事件類型 (Event Types):**
  - **`before/after_agent_callback`:** 在代理每次 `invoke` 的前後觸發。
  - **`before/after_model_callback`:** 在與 LLM 通訊的前後觸發。
  - **`before/after_tool_callback`:** 在工具執行的前後觸發。
- **狀態追蹤與錯誤處理 (State Tracking & Error Handling):**
  - 每個事件都包含當前的 `State` 快照，允許開發者完整地追蹤執行軌跡 (trace)。
  - 可以在回調函數中實現自訂的錯誤處理和重試邏輯，例如，當工具執行失敗時，可以捕獲異常並返回一個錯誤訊息給代理，讓其決定下一步。

---

### **6. 記憶體架構與知識管理 (Memory & Knowledge Management)**
- **記憶體策略 (Memory Strategy):**
  - **短期記憶 (Short-Term Memory):** 由 `Session` 服務提供，通常用於保存單次對話的歷史記錄。ADK 提供 `InMemorySessionService` (用於測試) 和 `DatabaseSessionService` (用於生產環境的持久化)。
  - **長期記憶 (Long-Term Memory):** 通過 `MemoryProvider` 實現，用於跨越多個會話的知識存儲和檢索。
- **外部知識庫整合 (External Knowledge Base Integration):**
  - 這是實現 RAG (檢索增強生成) 的關鍵。可以創建一個自訂工具，該工具負責查詢外部知識庫 (如 Vector Search, Elasticsearch) 並將檢索到的上下文返回給代理。
- **記憶與檢索介面設計 (Interface Design):**
  - 應設計清晰的工具接口，例如 `search_knowledge_base(query: str) -> str`，讓代理可以自然地使用檢索功能。

---

### **7. 部署安排與伸縮性 (Deployment & Scalability)**
- **部署架構藍圖 (Deployment Blueprint):**
  - ADK 應用被設計為無狀態的，易於容器化 (e.g., Docker) 並部署到任何雲端平台。
  - **推薦平台:** Google Cloud Run (用於無伺服器部署), Google Kubernetes Engine (GKE) (用於需要更複雜網路和協調的場景)。
- **負載均衡與擴展 (Load Balancing & Scaling):**
  - Cloud Run 和 GKE 原生支持基於請求的自動擴展 (auto-scaling) 和負載均衡。
  - 由於代理是無狀態的，可以輕鬆地水平擴展實例數量以應對高流量。
- **版本控管策略 (Versioning Strategy):**
  - 建議使用 Git 進行原始碼版本控制，並使用容器映像檔標籤 (image tags) 來管理部署版本。

---

### **8. 監控、測試與評估 (Observability, Testing & Evaluation)**
- **監控指標 (Monitoring Metrics):**
  - **可觀測性 (Observability):** ADK 可以與 OpenTelemetry 整合，將執行軌跡導出到監控系統 (如 Google Cloud Trace)。
  - **關鍵指標:** 請求延遲 (latency)、Token 使用量 (token usage)、工具調用成功/失敗率、錯誤率。
- **測試框架 (Testing Framework):**
  - **單元測試:** 應為每個 `Tool` 編寫單元測試以確保其功能的確定性。
  - **整合測試:** 應為每個 `Agent` 編寫整合測試，通過模擬 `State` 輸入來驗證其推理和決策邏輯。
- **評估管道 (Evaluation Pipeline):**
  - ADK 提供 `AgentEvaluator` 框架，用於評估代理在「金標」測試集上的表現，衡量軌跡的準確性和最終回應的品質。

---

### **9. 安全性與合規 (Security & Compliance)**
- **權限劃分 (Permission Scopes):**
  - 每個代理應被授予最小權限原則 (Principle of Least Privilege)，只註冊其完成任務所必需的工具。
- **機敏信息保護 (Sensitive Data Protection):**
  - 絕不能在程式碼或日誌中儲存敏感資訊 (API Keys, PII)。應使用秘密管理工具。
  - 可以利用 `before/after_model_callback` 來過濾或遮罩進出 LLM 的敏感數據。
- **操作稽核與可追蹤性 (Auditing & Traceability):**
  - 通過整合日誌和追蹤系統，可以為所有代理的決策和行動提供完整的稽核記錄。

---

### **10. 系統維運與文件管理 (Operations & Documentation)**
- **常見維運工作 (SOPs):**
  - 應建立標準作業程序 (SOP) 用於部署新版本、監控儀表板和處理警報。
- **日誌與問題回報 (Logging & Issue Reporting):**
  - 使用結構化日誌 (Structured Logging) 記錄關鍵事件和狀態變化。
  - 建立清晰的問題回報和故障排除流程。
- **文件管理 (Documentation):**
  - 本架構文件應作為核心文件，並隨著專案演進持續更新。
  - 每個代理和工具的 docstring 都應保持清晰和最新，因為它們會直接影響代理的行為。
