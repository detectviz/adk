# SRE Assistant 專案 ADK 關鍵參考範例

**文件目的**: 本文件旨在為 SRE Assistant 的開發團隊提供一份精選的 Google Agent Development Kit (ADK) 範例列表。這些範例經過首席架構師的審慎評估，被認為對本專案的成功，特別是 **Phase 1 (後端優先與核心能力建設)** 階段，具有最高的技術參考價值。

**使用指南**: 開發人員在執行 `TASKS.md` 中指定的任務時，應優先參考此處對應的範例，以確保實現方式符合 ADK 的最佳實踐和本專案的架構設計。

---

## 核心 Provider 實現 (Core Provider Implementations)

這些範例是完成 `TASK-P1-CORE-01` 到 `TASK-P1-CORE-03` 的基石，直接關係到 `ARCHITECTURE.md` 中定義的 ADK 原生擴展性。

- ### **檔案路徑**: `docs/references/adk-examples/providers_auth_config/`
  - **參考原因**: 此範例是實現 **`TASK-P1-CORE-03: 實現 AuthProvider (OAuth 2.0)`** 的**首要參考**。它清晰地展示了如何透過 `root_agent.yaml` 配置，來注入一個自定義的認證提供者 (`AuthProvider`)。這對於我們對接 Grafana 的 OAuth 2.0/OIDC 認證體系至關重要，是保障系統安全的第一道門。

- ### **檔案路徑**: `docs/references/adk-examples/providers_memory_config/`
  - **參考原因**: 此範例是實現 **`TASK-P1-CORE-01: 實現 MemoryProvider (RAG)`** 的關鍵。它演示了如何配置和集成一個外部記憶體後端。我們需要借鑒其模式，以實現與 Weaviate 向量數據庫的對接，為 SRE Assistant 提供強大的 RAG (檢索增強生成) 能力，這是其智能診斷的核心。

- ### **檔案路徑**: `docs/references/adk-examples/providers_session_config/`
  - **參考原因**: 此範例是實現 **`TASK-P1-CORE-02: 實現 session_service_builder (持久化會話)`** 的直接指南。它展示了如何實現一個自定義的會話服務，以滿足我們將會話狀態持久化到 Redis/PostgreSQL 的需求。一個穩定、可恢復的會話層是提供流暢多輪對話體驗和執行長時間運行的自動化任務的基礎。

## 自定義工具與整合 (Custom Tools & Integration)

這些範例展示了如何構建與外部系統互動的工具，是完成 `TASK-P1-TOOL-01` 到 `TASK-P1-TOOL-03` 的核心參考。

- ### **檔案路徑**: `docs/references/adk-examples/jira_agent/`
  - **參考原因**: 這是實現 **`TASK-P1-TOOL-01/02/03` (Prometheus/Loki/GitHub 工具)** 的**最佳實踐範本**。`jira_agent/tools.py` 完美演示了如何封裝一個與第三方 REST API 互動的工具，並包含了處理認證、參數傳遞和結果解析的完整邏輯。其結構和錯誤處理模式應被我們所有共享工具所遵循，以符合 `SPEC.md` 的標準化介面要求。

- ### **檔案路徑**: `docs/references/adk-examples/adk_answering_agent/`
  - **參考原因**: 這是一個將**記憶體 (RAG)** 和**工具**結合的綜合性範例。它展示了一個完整的 Agent 如何利用 RAG (`upload_docs_to_vertex_ai_search.py`) 來增強其知識，並透過工具 (`tools.py`) 與外部服務互動。這為我們設計 `SREWorkflow`，使其能同時協調 RAG 檢索和工具調用提供了寶貴的架構參考。

## 部署與測試 (Deployment & Testing)

這些範例是確保專案工程品質和可交付性的關鍵。

- ### **檔案路徑**: `docs/references/adk-examples/providers_docker_build/`
  - **參考原因**: 此範例直接對應 **`TASK-P1-INFRA-01: 創建 docker-compose.yml`** 中的容器化需求。它提供了為 ADK Agent 創建 `Dockerfile` 的官方最佳實踐，確保我們能構建出最小化、安全且高效的容器映像，以便在本地和生產環境中進行標準化部署。

- ### **檔案路徑**: `docs/references/adk-examples/testing_basic/`
  - **參考原因**: 此範例是完成 **`TASK-P1-DEBT-01: 增加測試覆蓋率`** 的入門指南。它展示了為 Agent 和 Tools 編寫單元測試和整合測試的基本模式。遵循其方法，我們可以為所有核心模組建立起堅實的測試套件，確保代碼品質和未來重構的安全性。

## 進階參考 (Advanced References)

- ### **檔案路徑**: `docs/references/adk-examples/spec_driven_development/`
  - **參考原因**: 此範例與 `SPEC.md` 中對**標準化工具介面**的要求高度契合。它演示了如何強制工具的輸出嚴格遵守預定義的 Pydantic 模型。在開發我們的共享工具時，應採用此模式來確保 `ToolResult` 和 `ToolError` 的結構一致性，從而提升系統的穩定性和可預測性。

- ### **檔案路徑**: `docs/references/adk-examples/tool_auth_gcp/`
  - **參考原因**: SRE Assistant 需要與多個 Google Cloud 服務（如 BigQuery, Vertex AI）互動。此範例演示了如何為工具配置和管理 GCP 服務的認證憑據。這為我們實現一個安全、統一的 Google Cloud 工具集提供了範本。

---

## Phase 1 & 2: 核心能力與 Grafana 整合 (Core Capabilities & Grafana Integration)

- ### **檔案路徑**: `docs/references/adk-examples/callbacks/`
  - **參考原因**: 此範例對於**提升系統可觀測性**和**實現 Phase 2 的 Grafana ChatOps 介面**至關重要。它展示了如何註冊回調函數來監聽 Agent 的內部事件（如工具調用、LLM 請求）。我們能藉此將詳細的執行追蹤實時推送到 Loki，並在 Grafana UI 中為用戶提供透明的進度更新。

- ### **檔案路徑**: `docs/references/adk-examples/live_bidi_streaming_tools_agent/`
  - **參考原因**: 這是實現**無縫 Grafana ChatOps 體驗**的關鍵技術。範例展示了如何將工具執行的中間輸出以流式（Streaming）方式傳回客戶端。這將允許用戶在 Grafana 介面中實時看到長時間運行任務（如日誌分析、數據庫查詢）的進展，而不是長時間的等待，極大地提升了用戶體驗。

- ### **檔案路徑**: `docs/references/adk-examples/human_in_loop/`
  - **參考原因**: 直接對應 `ARCHITECTURE.md` 中定義的 **P0 級事件需要人類介入** 的核心安全要求。此範例提供了實現手動審批環節的標準模式。我們將參考它來設計 SRE Assistant 在執行高風險修復操作前的“請求人類批准”工作流。

- ### **檔案例項**: `docs/references/adk-examples/tool_auth_gcp/`
  - **參考原因**: SRE Assistant 需要與多個 Google Cloud 服務（如 BigQuery, Vertex AI）互動。此範例演示了如何為工具配置和管理 GCP 服務的認證憑據。這為我們實現一個安全、統一的 Google Cloud 工具集提供了範本。

## Phase 3 & 4: 聯邦化與進階工作流 (Federation & Advanced Workflows)

- ### **檔案路徑**: `docs/references/adk-examples/a2a_basic/` 和 `a2a_auth/`
  - **參考原因**: 這兩個範例是實現 **Phase 3 聯邦化架構**的基石。`a2a_basic` 演示了 Agent-to-Agent (A2A) 通信的基礎，而 `a2a_auth` 則在其之上增加了認證機制。這為我們將 `PostmortemAgent` 等專業化代理從主服務中分離出來，並透過安全的 gRPC 協議進行協同工作提供了清晰的實現路徑。

- ### **檔案路徑**: `docs/references/adk-examples/multi_agent_seq_config/` 和 `multi_agent_loop_config/`
  - **參考原因**: 隨著 SRE Assistant 功能的擴展，我們需要編排由多個 Agent 參與的複雜工作流。這兩個範例分別展示了**順序執行**和**循環執行**兩種多 Agent 協作模式。這對於實現 `ROADMAP.md` 中提到的多步驟自動化修復流程 (Runbooks) 和需要迭代優化的任務（如報告生成）至關重要。

- ### **檔案路徑**: `docs/references/adk-examples/workflow_structured_output/`
  - **參考原因**: 為了確保複雜工作流輸出的可靠性和一致性，我們需要一個標準化的方式來定義其數據結構。此範例展示了如何使用 Pydantic 模型來定義工作流的最終輸出。這與 `spec_driven_development` 範例相輔相成，共同確保了從單個工具到整個工作流的端到端數據一致性。

---

## 進階工作流與工程實踐 (Advanced Workflow & Engineering Practices)

這些範例專注於提升 SRE Assistant 的智能、彈性和工程品質，是實現 Phase 2 和 Phase 3 路線圖中複雜功能與長期穩定性的關鍵。

- ### **檔案路徑**: `docs/references/adk-examples/code_execution/`
  - **參考原因**: 直接賦予 Agent **執行自動化修復腳本**的能力，是 `SPEC.md` 中定義的 `KubernetesOperationTool` 和 `TerraformTool` 等操作工具的基礎。此範例提供了在安全的沙箱環境中執行程式碼的標準模式，是將 SRE Assistant 從“分析者”變為“行動者”的核心技術，對實現真正的**監控閉環 (Monitoring Closed-Loop)** 至關重要。

- ### **檔案路徑**: `docs/references/adk-examples/workflow_chain_of_thought/`
  - **參考原因**: 要實現 `SPEC.md` 中複雜的**根因分析 (Root Cause Analysis)**，Agent 不能只靠單一工具的輸出，而需要進行多步驟的推理。此範例展示了如何構建一個具備“思維鏈”能力的 Agent，它能自我提問、分解問題、並依序執行工具來得出結論。這是提升我們 `IncidentHandlerAgent` 智能水平的關鍵。

- ### **檔案路徑**: `docs/references/adk-examples/workflow_conditional_routing/`
  - **參考原因**: 這是實現 **`TASK-P2-REFACTOR-01: 智慧分診系統`** 的核心技術藍圖。SRE Assistant 需要根據事件的類型和嚴重性，將任務分派給不同的專家 Agent。此範例提供了實現**條件路由 (Conditional Routing)** 的標準方法，讓 `SREWorkflow` 能夠根據上下文動態決策，是構建聯邦化系統的關鍵一步。

- ### **檔案路徑**: `docs/references/adk-examples/testing_mock_api/`
  - **參考原因**: 隨著工具集的擴展，我們的整合測試會變得越來越慢且不穩定。此範例是完成 **`TASK-P1-DEBT-01`** 並保證長期工程品質的**必備實踐**。它演示瞭如何使用 `httpx-mock` 來模擬外部 API，使我們能夠在不依賴網路或第三方服務的情況下，快速、可靠地測試工具和 Agent 的核心邏輯。

---

## 工程實踐與開發體驗 (Engineering Practices & Developer Experience)

這些範例專注於改善開發流程、提升使用者體驗和增強系統的工程品質，是確保專案可維護性和擴展性的關鍵。

- ### **檔案路徑**: `docs/references/adk-examples/providers_http_endpoint/`
  - **參考原因**: 此範例是實現 **`TASK-P1-SVC-01: 實現核心 SREAssistant Agent 服務`** 的基礎。`ARCHITECTURE.md` 明確後端服務將透過 HTTP 與 Grafana 插件通訊。此範例展示了如何配置 ADK 以啟動一個 HTTP 服務端點，這是讓 Agent 能夠被外部（如 Grafana 插件或 curl）呼叫的第一步。

- ### **檔案路徑**: `docs/references/adk-examples/history_management/`
  - **參考原因**: 此範例是對 **`TASK-P1-CORE-02: 實現持久化會話`** 的重要補充。`providers_session_config` 範例展示了如何**實現**一個持久化會話的後端，而此範例則展示了如何在**應用層面**有效**使用和管理**對話歷史。這對於處理 LLM 的上下文視窗限制、實現長期對話記憶至關重要。

- ### **檔案路徑**: `docs/references/adk-examples/live_tool_callbacks_agent/`
  - **參考原因**: 這是實現 **Phase 2 Grafana 原生體驗**中**即時反饋**功能的關鍵。`live_bidi_streaming_tools_agent` 範例展示了如何流式返回**最終結果**，而此範例則展示了如何在工具執行過程中，透過回調**即時串流中間日誌和進度**。這將極大地提升用戶在 Grafana UI 上執行長時間任務（如日誌分析）時的體驗。

- ### **檔案路徑**: `docs/references/adk-examples/testing_advanced/`
  - **參考原因**: 為了達成 **`TASK-P1-DEBT-01`** 中 >80% 的測試覆蓋率目標，僅有基礎測試是不夠的。此範例是對 `testing_basic` 和 `testing_mock_api` 的進階補充，它可能涵蓋了如何測試複雜的工作流、多 Agent 交互或非同步操作等高級場景，為我們建立全面且可靠的測試套件提供了範本。
