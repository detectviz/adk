# references.md - SRE Assistant 核心參考文件

## 總覽

本文件旨在整理和歸納對 SRE Assistant 專案開發具有高度參考價值的內部文件。這些文件為我們的架構決策、技術實現和長期願景提供了基礎。

---

## 1. Google ADK 官方核心文件 (`docs/references/adk-docs/`)

這部分是 Google Agent Development Kit 的官方文檔，是我們使用框架的「第一手資料」。

- **檔案路徑**: `docs/references/adk-docs/get-started-quickstart.md`
  - **參考原因**: 提供了 ADK 的基本安裝、配置和「Hello World」級別的範例，是團隊成員入門的必讀文件，有助於快速建立本地開發環境。

- **檔案路徑**: `docs/references/adk-docs/agents-workflow-agents.md`
  - **參考原因**: 詳細介紹了如何構建工作流代理（Sequential, Parallel, Loop），這與我們 `ARCHITECTURE.md` 中定義的 `SREWorkflow` 核心概念直接相關，是實現多步驟SRE自動化流程的基礎。

- **檔案路徑**: `docs/references/adk-docs/context.md`
  - **參考原因**: 解釋了 `InvocationContext` 的作用，這對於我們實現無狀態服務、管理會話和安全傳遞狀態至關重要，直接關係到 `TASK-P1-REFACTOR-01` 的重構任務。

- **檔案路徑**: `docs/references/adk-docs/runtime-config-memory.md` & `runtime-config-sessions.md` & `runtime-config-auth.md`
  - **參考原因**: 這三份文件分別詳細說明了如何透過 `adk.yaml` 配置記憶體、會話和認證提供者。它們是實現 `TASK-P1-CORE-01` (MemoryProvider), `TASK-P1-CORE-02` (session_service_builder), 和 `TASK-P1-CORE-03` (AuthProvider) 的關鍵技術指南。

- **檔案路徑**: `docs/references/adk-docs/a2a.md`
  - **參考原因**: 闡述了 Agent-to-Agent (A2A) 的通訊協議和模式。雖然這是 Phase 3 的任務，但提前理解其設計有助於我們在 Phase 1 設計出更具前瞻性的介面。

---

## 2. Google SRE 理念與實踐 (`docs/references/google-sre-book/`)

這本書提供了 Google SRE 的核心理念，是我們設計所有代理行為和邏輯的「思想鋼領」。

- **檔案路徑**: `docs/references/google-sre-book/Chapter-06-Monitoring-Distributed-Systems.md`
  - **參考原因**: 提供了關於監控哲學的深刻見解，指導我們如何設計 `PrometheusQueryTool` 和 `LokiLogQueryTool`，確保代理不僅是執行命令，更是像一個真正的 SRE 一樣「思考」。

- **檔案路徑**: `docs/references/google-sre-book/Chapter-14-Managing-Incidents.md`
  - **參考原因**: 詳細描述了事件管理的生命週期，是我們設計 `Incident Handler` 專業化代理的行為藍本，確保我們的事件處理流程符合業界最佳實踐。

- **檔案路徑**: `docs/references/google-sre-book/Chapter-15-Postmortem-CultureLearning-from-Failure.md`
  - **參考原因**: 為 Phase 3 的 `PostmortemAgent` 提供了設計思路，強調了無指責文化和從失敗中學習的重要性，這將體現在我們自動生成的覆盤報告中。

---

## 3. ADK 代理實作範例 (`docs/references/adk-agent-samples/`)

這部分包含了完整的、可運行的代理專案，是將理論轉化為程式碼的最佳參考。

- **檔案路徑**: `docs/references/adk-agent-samples/sre-bot/`
  - **參考原因**: **極度相關**。這是一個 SRE Bot 的範例，其結構、工具和代理設計對我們的專案有最直接的借鑑意義。應作為我們專案結構和程式碼風格的優先參考。

- **檔案路徑**: `docs/references/adk-agent-samples/RAG/`
  - **參考原因**: 提供了完整的 RAG (Retrieval-Augmented Generation) 實現範例，包含向量數據庫的交互和文檔處理，是完成 `TASK-P1-CORE-01` (MemoryProvider) 的關鍵程式碼參考。

- **檔案路徑**: `docs/references/adk-agent-samples/headless_agent_auth/`
  - **參考原因**: 展示了如何在無 UI 的後端服務中實現 OAuth 2.0 認證流程，這對我們完成 `TASK-P1-CORE-03` (AuthProvider) 並與 Grafana 整合至關重要。

- **檔案路徑**: `docs/references/adk-agent-samples/github-agent/`
  - **參考原因**: 提供了一個與 GitHub API 互動的具體範例，可直接用於 `TASK-P1-TOOL-03` (`GitHubTool`) 的開發。

- **檔案路徑**: `docs/references/adk-agent-samples/google-adk-workflows/`
  - **參考原因**: 提供了多種工作流（串行、並行、分派）的具體代碼實現，是我們構建 `SREWorkflow` 的重要實踐參考。

---

## 4. ADK 功能程式碼片段 (`docs/references/adk-examples/`)

這部分提供了針對特定功能的、簡潔的程式碼片段，便於快速查詢和複製。

- **檔案路徑**: `docs/references/adk-examples/core_basic_config/`
  - **參考原因**: 展示了最基礎的 `root_agent.yaml` 配置方法，有助於理解 ADK 的配置驅動模式。

- **檔案路徑**: `docs/references/adk-examples/multi_agent_basic_config/`
  - **參考原因**: 提供了多代理（Multi-Agent）的 YAML 配置範例，對我們規劃未來的聯邦化架構 (`sub_agents/`) 提供了配置層面的參考。
