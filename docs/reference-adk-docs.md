# SRE Assistant 專案 ADK 關鍵參考文件

作為 SRE Assistant 專案的架構核心，我們必須基於 Google Agent Development Kit (ADK) 的穩固基礎進行開發。以下文件是從 ADK 官方文檔中，根據本專案的 `ARCHITECTURE.md`, `ROADMAP.md`, `SPEC.md` 和 `TASKS.md` 精心挑選出的關鍵參考，團隊成員應優先研讀以完成 Phase 1 的交付目標。

---

## 核心框架與自訂擴展 (Core Framework & Custom Extensions)

這部分文件是實現 `ARCHITECTURE.md` 中定義的 ADK 原生擴展 (`AuthProvider`, `MemoryProvider`, `session_service_builder`) 的技術基礎，直接對應 `TASKS.md` 中的 `TASK-P1-CORE-*` 系列任務。

- **檔案路徑**: `docs/references/adk-docs/tools-auth.md`
  - **參考原因**: **[高度相關]** 這是實現 **`TASK-P1-CORE-03` (AuthProvider (OAuth 2.0))** 的核心指南。文件詳細說明了如何自訂 `AuthProvider` 以整合外部身份驗證系統（如我們規劃的 OIDC Provider），是保障整個 SRE Assistant 安全性的基石。

- **檔案路徑**: `docs/references/adk-docs/tools-sessions.md`
  - **參考原因**: **[高度相關]** 此文件是完成 **`TASK-P1-CORE-02` (session_service_builder)** 的關鍵。它闡述了如何透過自訂會話後端來實現持久化會話，這對於我們使用 PostgreSQL/Redis 存儲多輪對話上下文的架構至關重要。

- **檔案路徑**: `docs/references/adk-docs/tools-memory.md`
  - **參考原因**: **[高度相關]** 直接對應 **`TASK-P1-CORE-01` (MemoryProvider (RAG))** 任務。文件提供了實現自訂 `MemoryProvider` 的方法，指導我們如何將 ADK 的記憶體抽象層對接到後端的 Weaviate 向量數據庫，以實現 RAG 功能。

- **檔案路徑**: `docs/references/adk-docs/tools-creating-a-tool.md`
  - **參考原因**: **[高度相關]** 這是所有 `TASK-P1-TOOL-*` 任務的基礎。`SPEC.md` 要求所有工具遵循標準化介面 (`ToolResult`)，此文件詳細介紹了創建、註冊和實現自訂工具的最佳實踐，是確保工具集品質和一致性的必讀文檔。

## 代理與工作流 (Agent & Workflow)

- **檔案路徑**: `docs/references/adk-docs/agents-workflow-agents.md`
  - **參考原因**: **[中度相關]** 我們的 `SREWorkflow` 是一個複雜的工作流程。此文件介紹了如何組織和協調工具的調用順序，雖然我們初期不一定會用到最複雜的 `SequentialAgent` 或 `LoopAgent`，但其設計思想對我們構建穩健的 `workflow.py` 極具參考價值。

- **檔案路徑**: `docs/references/adk-docs/context.md`
  - **參考原因**: **[高度相關]** `InvocationContext` 是 ADK 中串聯所有組件的「神經系統」。`TASKS.md` 中的重構任務 **`TASK-P1-REFACTOR-01`** 明確要求將狀態管理移至 `InvocationContext`。此文檔解釋了其結構和用法，是實現無狀態服務和正確傳遞上下文的關鍵。

## 可觀測性與部署 (Observability & Deployment)

- **檔案路徑**: `docs/references/adk-docs/observability-logging.md`
  - **參考原因**: **[高度相關]** `ARCHITECTURE.md` 將可觀測性列為核心原則，並採用 LGTM 技術棧。此文件說明了如何配置 ADK 的日誌系統，以生成結構化的、可被 Loki 高效採集和查詢的日誌，是實現我們可觀測性目標的基礎。

- **檔案路徑**: `docs/references/adk-docs/observability-cloud-trace.md`
  - **參考原因**: **[高度相關]** 除了日誌，分散式追蹤對於理解複雜的工作流程至關重要。此文件指導如何整合 OpenTelemetry/Cloud Trace，這與我們使用 Tempo 的目標一致，能幫助我們快速定位性能瓶頸和錯誤。

- **檔案路徑**: `docs/references/adk-docs/deploy-cloud-run.md`
  - **參考原因**: **[高度相關]** 我們的目標目錄結構中包含了 `deployment/cloud_run/`，表明 Cloud Run 是潛在的部署目標。此文檔提供了將 ADK 應用容器化並部署到 Cloud Run 的官方指南，對我們規劃 CI/CD 和生產環境架構有直接幫助。

## 開發與測試 (Development & Testing)

- **檔案路徑**: `docs/references/adk-docs/ui.md`
  - **參考原因**: **[高度相關]** `ROADMAP.md` 和 `TASKS.md` 明確指出 Phase 1 將使用 **ADK Web UI** 進行開發和驗證。此文件是了解、配置和使用這個內建工具的唯一官方指南，對於提高開發效率至關重要。

- **檔案路徑**: `docs/references/adk-docs/get-started-testing.md`
  - **參考原因**: **[高度相關]** **`TASK-P1-DEBT-01`** 要求為核心模組增加測試覆蓋率。此文件介紹了 ADK 的測試框架和最佳實踐，指導我們如何為自訂的 `AuthProvider`、`MemoryProvider` 和工具編寫有效的單元測試和整合測試。
