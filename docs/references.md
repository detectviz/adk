# SRE Assistant 核心參考文件總覽

## 1. 總覽

本文件旨在作為 SRE Assistant 專案的**唯一參考來源 (Single Source of Truth)**，整理和歸納了所有對專案開發具有高度價值的參考資料。內容涵蓋 SRE 核心理念、Google ADK 官方文件、可運行的完整專案範例，以及針對特定功能的程式碼片段。所有內容均已經過重新分類和整合，以消除重複並提高可讀性。

---

## 2. SRE 核心理念與實踐 (來自 Google SRE Book)

這部分內容提供了 Google SRE 的核心理念，是我們設計所有代理行為和邏輯的「思想鋼領」。

*   **檔案路徑**: `docs/references/google-sre-book/Chapter-04-Service-Level-Objectives.md`
    *   **參考原因**: SRE Assistant 的核心目標是圍繞 SLO/SLI 進行決策。本章為 `Incident Handler` 和 `Predictive Maintenance` 代理的行為（如自動修復、告警）提供了理論基礎。

*   **檔案路徑**: `docs/references/google-sre-book/Chapter-05-Eliminating-Toil.md`
    *   **參考原因**: SRE Assistant 的存在價值是**消除瑣務 (Toil)**。本章指導我們確保開發的自動化功能能有效減少 SRE 的手動、重複性工作。

*   **檔案路徑**: `docs/references/google-sre-book/Chapter-06-Monitoring-Distributed-Systems.md`
    *   **參考原因**: 本章闡述了監控的哲學，對於設計 `PrometheusQueryTool` 和 `LokiLogQueryTool` 至關重要，確保代理能提出有意義的問題。

*   **檔案路徑**: `docs/references/google-sre-book/Chapter-12-Effective-Troubleshooting.md`
    *   **參考原因**: 本章為 `SREWorkflow` 中的診斷與修復流程提供了清晰的藍圖，我們的代理應模仿其方法論執行根因分析。

*   **檔案路徑**: `docs/references/google-sre-book/Chapter-14-Managing-Incidents.md` & `Chapter-13-Emergency-Response.md`
    *   **參考原因**: 這兩章是設計 `Incident Handler` 專業代理的行為藍本，確保事件處理流程符合業界最佳實踐。

*   **檔案路徑**: `docs/references/google-sre-book/Chapter-15-Postmortem-CultureLearning-from-Failure.md` & `Appendix-D-Example-Postmortem.md`
    *   **參考原因**: 為 Phase 3 的 `PostmortemAgent` 提供了理論來源和實作範本，強調了「無指責」文化，並提供了覆盤報告的目標格式。

---

## 3. Google ADK 官方核心文件

這部分是 Google ADK 的官方文檔，是我們使用框架的「第一手資料」，對應核心功能的開發任務。

*   **主題：入門與測試**
    *   **檔案路徑**: `docs/references/adk-docs/get-started-quickstart.md`
    *   **檔案路徑**: `docs/references/adk-docs/get-started-testing.md`
    *   **檔案路徑**: `docs/references/adk-docs/ui.md`
    *   **參考原因**: 提供 ADK 的入門、測試框架和 Web UI 指南，是建立本地開發環境、提高開發效率和確保程式碼品質的基礎。

*   **主題：核心框架與擴展**
    *   **檔案路徑**: `docs/references/adk-docs/context.md`
    *   **檔案路徑**: `docs/references/adk-docs/tools-auth.md` & `runtime-config-auth.md`
    *   **檔案路徑**: `docs/references/adk-docs/tools-sessions.md` & `runtime-config-sessions.md`
    *   **檔案路徑**: `docs/references/adk-docs/tools-memory.md` & `runtime-config-memory.md`
    *   **參考原因**: 這些文件是實現 `TASK-P1-CORE-*` 系列任務的關鍵，詳細說明了如何擴展和配置 ADK 的核心組件，如 `InvocationContext`、`AuthProvider`、`SessionService` 和 `MemoryProvider`。

*   **主題：工具、代理與工作流**
    *   **檔案路徑**: `docs/references/adk-docs/tools-creating-a-tool.md`
    *   **檔案路徑**: `docs/references/adk-docs/agents-workflow-agents.md`
    *   **檔案路徑**: `docs/references/adk-docs/a2a.md`
    *   **參考原因**: 介紹了如何創建自定義工具、組織複雜工作流以及實現 Agent-to-Agent (A2A) 通訊，是實現 `SREWorkflow` 和未來聯邦化架構的基礎。

*   **主題：可觀測性與部署**
    *   **檔案路徑**: `docs/references/adk-docs/observability-logging.md` & `observability-cloud-trace.md`
    *   **檔案路徑**: `docs/references/adk-docs/deploy-cloud-run.md`
    *   **參考原因**: 指導如何整合結構化日誌和分散式追蹤，以對接我們的 LGTM 技術棧。同時提供了將應用容器化並部署到雲環境的官方指南。

---

## 4. ADK 完整專案範例

這部分包含了完整的、可運行的代理專案，是將理論轉化為程式碼的最佳參考。

*   **檔案路徑**: `docs/references/adk-agent-samples/sre-bot/`
    *   **參考原因**: **[最相關]** 一個 SRE Bot 範例，其領域、技術棧和專案結構與 SRE Assistant 高度重疊，可作為 Phase 1 開發的主要藍圖。

*   **檔案路徑**: `docs/references/adk-agent-samples/RAG/`
    *   **參考原因**: **[核心功能]** 實現 SRE Assistant 知識庫 (RAG) 的關鍵參考。它詳細展示了如何整合外部向量數據庫（如 Weaviate），並提供了從數據上傳、`MemoryProvider` 實現到評估框架的完整流程。

*   **檔案路徑**: `docs/references/adk-agent-samples/a2a_mcp/`
    *   **參考原因**: **[未來架構]** 實現 SRE Assistant 長期聯邦化願景的架構藍圖。它展示了如何使用協調器代理和 MCP 伺服器來構建一個多代理協同工作的複雜系統。

*   **檔案路徑**: `docs/references/adk-agent-samples/google-adk-workflows/`
    *   **參考原因**: **[工作流模式]** 提供了多種複雜工作流的協調模式（分派、並行、自我批判），是設計 `SREWorkflow` 以處理複雜事件流程的首要模式參考。

*   **檔案路徑**: `docs/references/adk-agent-samples/headless_agent_auth/`
    *   **參考原因**: **[認證]** 為 `TASK-P1-CORE-03` (實現 `AuthProvider`) 提供了具體的 OAuth 2.0 實現參考，展示了如何在後端服務中處理無頭認證流程。

*   **檔案路徑**: `docs/references/adk-agent-samples/github-agent/`
    *   **參考原因**: **[工具實現]** 為 `TASK-P1-TOOL-03` (實現 `GitHubTool`) 提供了即用型的程式碼參考，節省了從零開始編寫 GitHub API 客戶端的時間。

---

## 5. ADK 特定功能範例與程式碼片段

這部分提供了針對特定功能的、簡潔的程式碼片段，便於快速查詢和複製，以加速開發。

*   **主題：核心 Provider 配置**
    *   **檔案路徑**: `docs/references/adk-examples/providers_auth_config/`
    *   **檔案路徑**: `docs/references/adk-examples/providers_memory_config/`
    *   **檔案路徑**: `docs/references/adk-examples/providers_session_config/`
    *   **參考原因**: 展示了如何透過 `root_agent.yaml` 配置文件來注入自定義的 `AuthProvider`, `MemoryProvider`, 和 `SessionProvider`。

*   **主題：工具開發模式**
    *   **檔案路徑**: `docs/references/snippets/tools/openapi_tool.py`
    *   **參考原因**: **[推薦]** 展示了如何從 OpenAPI 規格自動生成工具，是加速 `GrafanaIntegrationTool` 開發的首選方案。
    *   **檔案路徑**: `docs/references/snippets/tools/function-tools/func_tool.py`
    *   **參考原因**: 對於沒有 OpenAPI 規格的服務（如 Prometheus, Loki），此範例提供了手動創建標準工具的基礎模式。
    *   **檔案路徑**: `docs/references/adk-examples/spec_driven_development/`
    *   **參考原因**: 演示了如何強制工具的輸出嚴格遵守預定義的 Pydantic 模型，以確保 `ToolResult` 的結構一致性。

*   **主題：安全與工作流控制**
    *   **檔案路徑**: `docs/references/snippets/tools/function-tools/human_in_the_loop.py`
    *   **參考原因**: 提供了實現「人工確認」安全機制的模式，在執行高風險修復操作前，可暫停工作流以等待使用者授權。
    *   **檔案路徑**: `docs/references/snippets/agents/workflow-agents/sequential_agent_code_development_agent.py`
    *   **參考原因**: 展示了如何使用 `SequentialAgent` 將多個獨立的子代理串聯起來，並透過共享狀態傳遞資訊。
