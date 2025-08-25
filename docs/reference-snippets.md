# reference-snippets.md - ADK 參考程式碼片段分析

**版本**: 1.0.0
**狀態**: 生效中
**維護者**: SRE Platform Team

## 1. 總覽

本文件旨在為 SRE Assistant 專案的開發提供一組經過嚴格評估的關鍵程式碼片段參考。這些片段來自 `docs/references/snippets` 目錄，每一個都因其與我們在 `ARCHITECTURE.md`、`ROADMAP.md` 和 `SPEC.md` 中定義的架構、路線圖和規格高度相關而被選中。

本文件的目標是加速開發、統一實作模式並確保我們遵循 Google ADK 的最佳實踐。

---

## 2. 核心功能參考

### 2.1. 主要工作流程實現 (Main Workflow Implementation)

- **檔案路徑**: `docs/references/snippets/agents/workflow-agents/sequential_agent_code_development_agent.py`
- **參考原因**:
    - **直接對應**: 此範例是 `SREWorkflow` (`sre_assistant/workflow.py`) 的核心參考。它展示了如何使用 `SequentialAgent` 將多個獨立的子代理（`LlmAgent`）串聯起來，形成一個有序的工作流程。
    - **狀態管理**: 清楚地演示了代理之間如何透過共享的 `state` 傳遞資訊（例如，一個代理的 `output_key` 成為下一個代理的輸入）。這對於在我們的診斷 -> 修復 -> 覆盤流程中傳遞事件上下文至關重要。
    - **任務關聯**: 直接支援 `TASKS.md` 中 `TASK-P1-SVC-01: 實現核心 SREAssistant Agent 服務` 的開發。

### 2.2. 認證提供者實現 (Authentication Provider Implementation)

- **檔案路徑**: `docs/references/snippets/tools/auth/tools_and_agent.py`
- **參考原因**:
    - **關鍵任務**: 這是實現 `TASK-P1-CORE-03: 實現 AuthProvider (OAuth 2.0)` 的權威指南。
    - **框架整合**: 展示了如何使用 `OpenIdConnectWithConfig` 和 `AuthCredential` 來定義 OIDC/OAuth2 認證流程，並將其與 `OpenAPIToolset` 或其他工具集綁定。
    - **自動化流程**: 該範例揭示了 ADK 框架如何自動處理令牌獲取、刷新和附加到 API 請求的流程，這將極大地簡化我們在 `sre_assistant/auth/` 模組中的開發工作。

### 2.3. 安全的自動化修復模式 (Safe Automated Remediation Pattern)

- **檔案路徑**: `docs/references/snippets/tools/function-tools/human_in_the_loop.py`
- **參考原因**:
    - **SRE 核心原則**: 對於需要人工介入確認的、有風險的修復操作（例如，重啟服務、執行資料庫遷移），此範例至關重要。它體現了 "先確認，後執行" 的安全原則。
    - **技術實現**: 展示了如何使用 `LongRunningFunctionTool` 來暫停工作流程，等待外部事件（例如，SRE 在 Grafana 介面點擊 "核准" 按鈕）觸發後續操作。
    - **功能規格**: 直接對應 `SPEC.md` 中對 `RemediationAgent` 的要求，即在執行高風險修復前必須獲得使用者授權。

### 2.4. RAG 與記憶體提供者 (RAG and Memory Provider)

- **檔案路徑**: `docs/references/adk-agent-samples/RAG/` (整個目錄)
- **參考原因**:
    - **核心功能**: `TASK-P1-CORE-01: 實現 MemoryProvider (RAG)` 是 Phase 1 的核心交付物之一。此目錄下的範例展示了如何整合向量資料庫（如 Weaviate）並透過 RAG 為代理提供上下文知識。
    - **架構對齊**: 這些範例是實現 `ARCHITECTURE.md` 中定義的「統一記憶庫 (Unified Memory)」的基礎，特別是與 Weaviate 的互動部分。
    - **實踐指南**: 提供了從文檔加載、向量化到檢索的完整流程，是開發 `sre_assistant/memory/` 模組的關鍵參考。

---

## 3. 工具開發策略

### 3.1. 加速工具開發：OpenAPI 規格優先 (Accelerated Tool Development: OpenAPI Spec First)

- **檔案路徑**: `docs/references/snippets/tools/openapi_tool.py`
- **參考原因**:
    - **效率提升**: 該範例展示了使用 `OpenAPIToolset` 從 OpenAPI/Swagger 規格自動生成工具集的強大能力。這可以極大地加速 `GrafanaIntegrationTool` 的開發。
    - **行動建議**: 建議在執行 `TASK-P1-INFRA-01` 建立本地 `docker-compose.yml` 時，為 Grafana 服務啟用 `swaggerUi` 功能旗標。一旦 Grafana 啟動，我們就可以從其 `/swagger-ui` 端點獲取 API 規格，並使用此範例中的模式快速生成一個功能完備的 `GrafanaIntegrationTool`。
    - **未來擴展**: 對於未來需要整合的其他任何提供 OpenAPI 規格的內部或外部服務，此模式都將是我們的首選方案。

### 3.2. 標準工具開發：手動實現 (Standard Tool Development: Manual Implementation)

- **檔案路徑**: `docs/references/snippets/tools/function-tools/func_tool.py`
- **參考原因**:
    - **基礎模式**: 對於沒有 OpenAPI 規格的服務（根據我們的研究，包括 Prometheus 和 Loki），我們需要手動實現其工具。此檔案提供了使用 `@tool` 裝飾器創建自定義工具的最基本、最清晰的範例。
    - **任務關聯**: 這是實現 `TASK-P1-TOOL-01: PrometheusQueryTool` 和 `TASK-P1-TOOL-02: LokiLogQueryTool` 的基礎。開發人員應參考此模式，並結合官方的 Prometheus/Loki HTTP API 文件來完成工具的邏輯。
