# ADK 專案參考範例 (SRE Assistant)

**版本**: 1.0.0
**狀態**: 草案
**維護者**: SRE Platform Team

## 總覽

本文件旨在為 SRE Assistant 的開發者提供一份精選的 Google ADK (Agent Development Kit) 範例列表。這些範例經過精心挑選，旨在展示與 SRE Assistant 架構、功能和長期願景最相關的核心模式與實踐。

在開發新功能或模組時，請優先參考此處列出的範例，它們將為您提供符合我們在 `ARCHITECTURE.md` 和 `TASKS.md` 中所定義的最佳實踐的程式碼藍圖。

---

## 核心範例精選

### 1. 工作流程與協調模式 (Workflow & Orchestration)

#### 範例: `google-adk-workflows`

- **簡介**: 此範例是**多代理協調模式的寶庫**。它透過一個旅遊規劃的場景，展示了四種不同的、由一個主代理協調多個專業化子代理（航班、飯店、景點）的工作流程。
- **與 SRE Assistant 的關聯性**:
    - **`DispatcherAgent`**: 完美對應了我們在 Phase 2 規劃的 `SREIntelligentDispatcher`。它展示瞭如何根據使用者請求，智慧地將任務路由到最合適的工具或子代理。
    - **`ParallelAgent`**: 展示了如何並行執行獨立任務（如同時預訂航班和飯店）。此模式可直接應用於 SRE Assistant 的診斷流程，例如**同時查詢指標 (Prometheus) 和日誌 (Loki)**，以縮短回應時間。
    - **`SelfCriticAgent`**: 實現了一個內建的審查與驗證循環。這為我們規劃的「修復後驗證 (Post-Remediation Verification)」階段提供了絕佳的參考。
    - **程式碼結構**: 其將專業化子代理放在 `subagent.py` 中，並為每種協調策略建立獨立資料夾的模式，是 `sre_assistant/sub_agents/` 模組可以效仿的最佳實踐。

---

### 2. 聯邦化架構與服務發現 (Federated Architecture & Service Discovery)

#### 範例: `a2a_mcp`

- **簡介**: 此範例實現了一個真正的**聯邦化多代理系統**。它展示了一個協調者代理 (Orchestrator) 如何透過查詢一個中央註冊中心 (MCP Server) 來動態發現其他專業代理，並透過 A2A (Agent-to-Agent) 協議與它們通訊。
- **與 SRE Assistant 的關聯性**:
    - **長期願景藍圖**: 這完全符合 `ARCHITECTURE.md` 中描述的長期聯邦化生態系統願景。它為 Phase 3 及以後的開發（例如，將覆盤報告生成重構為獨立的 `PostmortemAgent`）提供了具體的實現範本。
    - **動態服務發現**: 使用 MCP 作為代理註冊中心，解決了在分散式系統中如何新增、移除或更新代理而無需修改核心協調器程式碼的關鍵問題。

---

### 3. 安全與認證 (Security & Authentication)

#### 範例: `headless_agent_auth`

- **簡介**: 這是所有 **OAuth 2.0 和安全相關實踐**的首選參考。它使用 Auth0 來展示兩種在無頭 (Headless) 環境中至關重要的認證流程。
- **與 SRE Assistant 的關聯性**:
    - **`TASK-P1-CORE-03` 的核心參考**:
        - **用戶端憑證流程 (Client Credentials Flow)**: 精確地展示了 SRE Assistant 的一個客戶端（如 Grafana Plugin）應如何向後端 API 進行安全的機器對機器 (M2M) 認證。
        - **CIBA 流程 (Client-Initiated Backchannel Authentication)**: 展示了一種強大的**使用者同意**模式。例如，當 SRE Assistant 需要執行一個高權限的修復操作時，它可以觸發一個推播通知到 SRE 工程師的手機上請求批准。這是未來實現更安全的自動化操作的關鍵。
    - **API 安全**: 整個範例圍繞著使用存取權杖來保護代理和其呼叫的 API，這與 `ARCHITECTURE.md` 中定義的安全模型完全一致。

---

### 4. 檢索增強生成 (RAG) 與記憶體

#### 範例: `RAG`

- **簡介**: 此範例端到端地展示了如何建構一個基於 **Vertex AI RAG 引擎**的問答代理，使其回答能夠基於提供的文件內容，並附上引用來源。
- **與 SRE Assistant 的關聯性**:
    - **`TASK-P1-CORE-01` 的直接對應**: 這是實現 `MemoryProvider` 的核心參考。雖然 SRE Assistant 使用 Weaviate/PostgreSQL 而非 Vertex AI RAG，但其架構模式是完全可轉移的。
    - **核心 RAG 流程**: 展示了從擷取、將文件片段注入提示 (Prompt)，到最終生成有根據的回應的完整流程。
    - **數據注入**: `prepare_corpus_and_data.py` 腳本為我們如何建立自己的數據注入管道以填充 Weaviate 向量數據庫提供了良好範本。
    - **可信度**: 強調**引文 (Citation)** 的重要性，這對於確保 SRE Assistant 的回答是可信且可驗證的至關重要。

---

### 5. 可觀測性與追蹤 (Observability & Tracing)

#### 範例: `a2a_telemetry`

- **簡介**: 此範例完美詮釋了 `ARCHITECTURE.md` 中定義的「可觀測性驅動」原則。它展示如何設定 OpenTelemetry 以在 A2A 呼叫中產生**分散式追蹤**，並將其匯出至 Jaeger/Grafana 進行視覺化。
- **與 SRE Assistant 的關聯性**:
    - **LGTM 技術棧實踐**: 提供了將我們的 LGTM (Loki, Grafana, Tempo, Mimir) 願景變為現實的具體程式碼。雖然範例使用 Jaeger，但其原理與 Tempo 完全相同。
    - **問題排查**: 在複雜的多代理系統中，分散式追蹤是理解請求流程、診斷延遲和排查錯誤的生命線。
    - **IaC 整合**: 包含一個 `docker-compose.yaml` 來一鍵啟動可觀測性後端，與 `TASK-P1-INFRA-01` 的要求一致。

---

### 6. 部署與雲端整合 (Deployment & Cloud Integration)

#### 範例: `adk_cloud_run`

- **簡介**: 提供了一個從開發到生產的完整**部署指南**。它詳細介紹了如何將一個 ADK 代理部署到 Google Cloud Run，並涵蓋了安全和數據庫整合的最佳實踐。
- **與 SRE Assistant 的關聯性**:
    - **生產環境藍圖**: 這是將 SRE Assistant 部署到雲端的首選參考。
    - **安全最佳實踐**: 展示瞭如何使用專用的 IAM 服務帳號、透過 Secret Manager 管理密鑰，以及設定服務對服務的認證。
    - **配置管理**: 示範瞭如何透過環境變數和 secrets 來管理不同環境的配置，這對於我們的 `config/environments/` 設計至關重要。

---

### 7. 工具開發 (Tool Development)

#### 範例: `github-agent`

- **簡介**: 一個簡潔明瞭的範例，展示瞭如何實現一個與**第三方 REST API** (GitHub API) 互動的工具集。
- **與 SRE Assistant 的關聯性**:
    - **`TASK-P1-TOOL-03` 的樣板程式碼**: 為實現 `GitHubTool` 提供了直接的範本。
    - **通用 API 工具模式**: `github_toolset.py` 的結構（處理認證、API 呼叫、錯誤處理）可以作為任何與外部 API（如 Prometheus, Loki, Grafana OnCall）互動的工具的基礎。

---

### 8. 領域特定工作流程 (Domain-Specific Workflows)

#### 範例: `software-bug-assistant`

- **簡介**: 一個與 SRE Assistant 主題非常相似的代理。它接收一個軟體錯誤，並使用一個 `triage_agent`（分診代理）來決定是應該呼叫 `code_analyzer`（程式碼分析工具）還是 `solution_proposer`（解決方案建議工具）。
- **與 SRE Assistant 的關聯性**:
    - **簡單的路由模式**: `triage_agent` 是 `DispatcherAgent` 模式的一個輕量級、易於理解的實現，非常適合作為理解智慧路由概念的起點。
    - **問題分解**: 展示瞭如何將一個複雜的問題（修復錯誤）分解為更小的、由專門工具處理的步驟。

#### 範例: `langgraph`

- **簡介**: 此範例展示了如何使用 LangGraph 函式庫來建構**有狀態、可循環的複雜代理工作流程**。
- **與 SRE Assistant 的關聯性**:
    - **`SREWorkflow` 的進階實現**: LangGraph 提供了一種比簡單的順序或並行鏈更強大、更靈活的方式來定義我們的核心 `SREWorkflow`。它特別擅長處理需要根據前一步結果動態決定下一步，甚至需要回頭修改之前步驟的複雜場景。

#### 範例: `data-science`

- **簡介**: 一個複雜的、包含多個子代理的工作流程，用於執行數據科學任務。它包含用於規劃、數據分析、程式碼生成和結果驗證的代理。
- **與 SRE Assistant 的關聯性**:
    - **技術任務模式**: 其工作流程非常類似於 SRE Assistant 需要執行的技術任務，例如**根因分析**或**生成修復腳本**。其中的 `coder_agent` 和 `code_validator_agent` 為我們如何自動生成和驗證程式碼提供了很好的參考。

#### 範例: `customer-service`

- **簡介**: 此範例展示了一個從數據庫 (`tools/sql_tool.py`) 檢索結構化資訊以回答使用者問題的工作流程。
- **與 SRE Assistant 的關聯性**:
    - **結構化數據查詢**: SRE Assistant 需要從 PostgreSQL 數據庫中查詢事件歷史、Runbook 等結構化數據。此範例中的 `sql_tool.py` 提供了一個很好的起點。

#### 範例: `llm-auditor`

- **簡介**: 這是一個專門用於**審計和驗證**其他 LLM 輸出的代理。它可以檢查輸出的安全性、品質和準確性。
- **與 SRE Assistant 的關relation**:
    - **輸出品質保證**: 此模式與 `google-adk-workflows` 中的 `SelfCriticAgent` 相輔相成，為 SRE Assistant 的「驗證階段」提供了另一種實現思路。我們可以有一個 `RemediationAuditor` 代理來審查由其他代理生成的修復計畫或覆盤報告，確保其符合我們的工程標準。

---

### 9. A2A 通訊協定 (A2A Communication Protocols)

#### 範例: `dice_agent_grpc`

- **簡介**: 這是一個極簡但至關重要的範例，它展示如何透過 **gRPC** 而非預設的 REST/HTTP 來提供 ADK 代理服務。
- **與 SRE Assistant 的關聯性**:
    - **Phase 3 的核心技術**: `ROADMAP.md` 和 `ARCHITECTURE.md` 明確指出，Phase 3 的聯邦化架構將採用 gRPC 作為 A2A (Agent-to-Agent) 通訊協定。此範例是實現 `TASK-P3-A2A-01` 的**直接樣板**。
    - **高效能通訊**: 為團隊提供了如何在 ADK 中設定和使用 gRPC Server 的基礎知識，這對於實現低延遲、高效能的內部代理通訊至關重要。

---

### 10. 全端整合與前端開發 (Full-Stack & Frontend Integration)

#### 範例: `gemini-fullstack`

- **簡介**: 一個生產級的藍圖，展示如何建構一個包含 **React 前端**和由 ADK 驅動的 **FastAPI 後端**的複雜全端應用。
- **與 SRE Assistant 的關聯性**:
    - **Phase 2 的完美藍圖**: 這是為 Phase 2 開發 **Grafana 插件**最直接、最全面的參考。它完美地展示了前端 (Grafana Plugin) 如何與後端 (SRE Assistant API) 進行互動、傳遞狀態和顯示結果。
    - **前後端分離實踐**: 其清晰的目錄結構 (`/app` 為後端, `/frontend` 為前端) 和 `make dev` 的啟動方式，為開發團隊提供了組織和管理全端應用的最佳實踐。
    - **人在環節 (Human-in-the-Loop)**: 其「規劃-審批-執行」的工作流程，是 SRE Assistant 在執行高風險操作前需要使用者確認的絕佳實現範例。

#### 範例: `personal-expense-assistant-adk`

- **簡介**: 另一個優秀的全端應用範例，使用 **Gradio** 作為前端，FastAPI 作為後端，並整合了 Firestore 作為資料庫。
- **與 SRE Assistant 的關聯性**:
    - **替代架構模式**: 提供了與 `gemini-fullstack` 不同的前端技術棧 (Gradio)，讓開發團隊在為 Grafana 插件設計 UI 互動時有更多的參考。
    - **資料庫整合與回呼**: 清楚地展示了如何將代理與一個真實的、持久化的資料庫（Firestore）整合，這對於實現 `TASK-P1-CORE-01` (`MemoryProvider`) 和 `TASK-P1-CORE-02` (`session_service_builder`) 極具參考價值。其 `callbacks.py` 檔案也為如何在 UI 中即時串流顯示代理的「思考過程」提供了範本。

---

### 11. 機器學習與預測分析 (Machine Learning & Predictive Analysis)

#### 範例: `machine-learning-engineering`

- **簡介**: 一個基於研究論文的、極其複雜和強大的多代理系統，專門用於**自動化解決機器學習工程任務**。
- **與 SRE Assistant 的關聯性**:
    - **`PredictiveMaintenanceAgent` 的架構藍圖**: 這是為 Phase 3 `PredictiveMaintenanceAgent` 提供的**黃金標準**參考。該代理的目標（例如，根據歷史指標預測未來故障）本質上就是一個機器學習任務。
    - **從規劃到部署的完整週期**: 它展示了一個完整的 ML 任務生命週期：定義任務、產生和執行訓練程式碼、評估結果、迭代優化程式碼，最後產生模型。這為 SRE Assistant 如何實現一個能夠自我改進的預測模型提供了完整的思路。
    - **複雜的多代理協調**: 其包含的 `frontdoor_agent`、`refinement_agent`、`ensemble_agent` 等多個專業化子代理，為 SRE Assistant 在未來如何建構更複雜的、特定領域的專家代理提供了進階的架構範例。

---

### 12. 關鍵模式與第三方框架整合 (Key Patterns & 3rd-Party Framework Integration)

#### 範例: `marvin`

- **簡介**: 此範例展示如何使用 **Marvin** 框架從非結構化文字中**提取結構化資料** (Pydantic 模型)。
- **與 SRE Assistant 的關聯性**:
    - **核心工具實現模式**: SRE Assistant 的許多工具 (如 `PrometheusQueryTool`, `KubernetesOperationTool`) 都需要結構化的輸入。此範例為如何將自然語言（來自使用者或日誌）可靠地轉換為工具可以使用的 Pydantic 物件提供了一個強大的模式。
    - **結構化資料提取**: 對於從告警描述或事件日誌中解析主機名稱、錯誤代碼和時間戳等特定實體至關重要。
    - **多輪對話狀態**: 該範例還展示了如何透過多輪對話來收集所有必要的資訊，這對於需要澄清使用者意圖的複雜命令非常有用。

#### 範例: `mindsdb`

- **簡介**: 此範例展示如何將自然語言查詢轉換為 SQL，以查詢和分析來自 **MindsDB** 所連接的聯合資料來源的資料。
- **與 SRE Assistant 的關聯性**:
    - **自然語言資料庫查詢**: 為 SRE Assistant 提供了直接透過自然語言查詢其內部 **PostgreSQL** 資料庫（例如，查詢歷史事件或 Runbook）的能力藍圖。
    - **`PredictiveMaintenanceAgent` 的未來參考**: MindsDB 專為資料庫內機器學習而設計。此範例是 Phase 3 `PredictiveMaintenanceAgent` 如何分析歷史時間序列資料以進行故障預測的絕佳概念證明。
    - **資料聯邦**: 其跨多個資料來源進行查詢的能力，與 SRE Assistant 需要整合內部資料庫和外部可觀測性平台（如 Prometheus）的理念相符。

#### 範例: `analytics`

- **簡介**: 一個使用 `matplotlib` 和 `crewai` 將自然語言轉換為**數據視覺化圖表**的代理。
- **與 SRE Assistant 的關聯性**:
    - **補充 `GrafanaIntegrationTool`**: 雖然主要目標是嵌入 Grafana 圖表，但此範例提供了一種內建的、輕量級的圖表生成能力。這對於在 ChatOps 介面中進行快速、即時的資料視覺化非常有用。
    - **工具鏈模式**: 展示了一個清晰的工具鏈：LLM 解析請求 -> Pandas 處理數據 -> Matplotlib 產生圖表。這是 SRE Assistant 許多診斷流程可以遵循的模式。

#### 範例: `semantickernel`

- **簡介**: 此範例展示如何將微軟的 **Semantic Kernel** 代理框架與 ADK 的 A2A 伺服器整合。
- **與 SRE Assistant 的關聯性**:
    - **架構靈活性**: 與 `crewai` 和 `langgraph` 範例一樣，它展示了 SRE Assistant 的核心架構可以與各種第三方代理框架**互操作**。開發團隊可以為不同的專業化代理選擇最適合的工具。
    - **外掛程式與串流**: 其對「外掛程式」（工具）和串流回應的清晰使用，為 `SREWorkflow` 和工具的實現提供了寶貴的參考。

#### 範例: `a2a-mcp-without-framework`

- **簡介**: 一個**不依賴 ADK 框架**的、最簡化的 A2A 協定客戶端/伺服器實現。
- **與 SRE Assistant 的關聯性**:
    - **底層協定理解**: 這是供開發人員深入理解 A2A 協定本身運作方式的完美教育資源。當需要對 Phase 3 的聯邦化通訊進行低階除錯時，此範例將非常寶貴。
    - **基礎知識**: 透過剝離所有框架的抽象，它揭示了請求/回應結構、任務管理和資料模型的本質，有助於鞏固團隊對核心架構的理解。
