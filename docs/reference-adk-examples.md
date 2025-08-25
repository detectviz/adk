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
