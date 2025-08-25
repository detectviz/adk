# SRE Assistant - ADK 參考資料導引

**目的**: 本文件旨在作為一座橋樑，將 SRE Assistant 的核心概念與 `docs/references` 目錄中豐富的 ADK 官方範例和文檔連接起來。當您需要實現某個特定功能時，請查閱本文件以快速定位最相關的程式碼範例和設計指南。

## 1. 核心工作流程架構 (Incident Handling Assistant)

本節對應 SRE Assistant 的四階段事件處理工作流程。

### 1.1. 順序工作流 (Sequential Workflow)
- **概念**: 整個 SRE Assistant 是一個 `SequentialAgent`，負責按順序協調四個主要階段。
- **參考資料**:
    - **核心文檔**: `adk-docs/agents-workflow-agents-sequential-agents.md`
    - **基礎範例**: `adk-examples/simple_sequential_agent/`
    - **進階範例**: `adk-examples/workflow_agent_seq/`

### 1.2. 並行診斷 (Parallel Diagnostics - Phase 1)
- **概念**: 在第一階段，系統使用 `ParallelAgent` 同時運行多個診斷工具（如日誌、指標、追蹤分析），以大幅縮短問題定位時間。
- **參考資料**:
    - **核心文檔**: `adk-docs/agents-workflow-agents-parallel-agents.md`
    - **程式碼範例**: `adk-examples/parallel_functions/`
    - **程式碼片段**: `snippets/agents/workflow-agents/parallel_agent_web_research.py`

### 1.3. 智慧分診與條件修復 (Intelligent Triage - Phase 2)
- **概念**: 在第二階段，系統需要根據診斷結果，動態地選擇下一步操作（如自動修復、請求人工審批）。
- **參考資料**:
    - **核心模式 (Dispatcher)**: `adk-agent-samples/google-adk-workflows/dispatcher/`
    - **基礎文檔**: `adk-docs/agents-custom-agents.md`

### 1.4. 迭代優化 (Iterative Optimization - Phase 4)
- **概念**: 在第四階段，系統使用 `LoopAgent` 持續運行優化任務，直到滿足 SLO 目標。
- **參考資料**:
    - **核心文檔**: `adk-docs/agents-workflow-agents-loop-agents.md`
    - **程式碼範例**: `adk-examples/multi_agent_loop_config/`
    - **程式碼片段**: `snippets/agents/workflow-agents/loop_agent_doc_improv_agent.py`

### 1.5. 修復後驗證 (Post-Remediation Verification)
- **概念**: 在修復操作後，增加一個驗證步驟來評估修復是否成功，以及是否引入了新的問題。
- **參考資料**:
    - **核心模式 (Self-Criticism)**: `adk-agent-samples/google-adk-workflows/self_critic/`

## 2. 關鍵基礎設施與通用模式

本節涵蓋了支撐整個 SRE Assistant 的核心基礎設施和通用設計模式。

### 2.1. 狀態管理 (State Management)
- **概念**: 如何在可擴展的、多實例的環境中管理會話、用戶和應用程式級別的狀態。**這是修復 `AuthManager` 缺陷的關鍵**。
- **參考資料**:
    - **核心文檔**: `adk-docs/sessions-state.md`
    - **程式碼範例**: `adk-examples/session_state_agent/`

### 2.2. 認證與授權 (Authentication & Authorization)
- **概念**: 如何為工具或代理本身增加安全驗證層。
- **參考資料**:
    - **核心文檔**: `adk-docs/tools-authentication.md`
    - **程式碼範例 (OAuth)**: `adk-examples/oauth_calendar_agent/`

### 2.3. 人工介入 (Human-in-the-Loop - HITL)
- **概念**: 對於高風險操作，暫停工作流程並請求人工審批。
- **參考資料**:
    - **核心文檔**: `adk-docs/tools-function-tools.md` (提及 `LongRunningFunctionTool`)
    - **程式碼範例**: `adk-examples/human_in_loop/`
    - **程式碼片段**: `snippets/tools/function-tools/human_in_the_loop.py`

### 2.4. 檢索增強生成 (RAG)
- **概念**: 透過從知識庫（如歷史事件、Runbook）中檢索信息，來增強 LLM 的決策能力。
- **參考資料**:
    - **核心文檔**: `adk-docs/grounding-vertex_ai_search_grounding.md`
    - **完整範例**: `adk-agent-samples/RAG/`

## 3. 未來願景：聯邦化代理架構

本節對應 `ROADMAP.md` 中的長期願景，即建立一個由多個專業化 SRE 代理組成的生態系統。

### 3.1. 代理間通訊 (Agent-to-Agent - A2A)
- **概念**: 讓不同的專門化代理（如事件處理代理、成本優化代理）能夠互相發現和調用。
- **參考資料**:
    - **核心文檔**: `adk-docs/a2a.md`
    - **基礎範例**: `adk-examples/a2a_basic/`
    - **進階範例 (MCP 協議)**: `adk-agent-samples/a2a_mcp/`

### 3.2. 專業化代理架構參考
- **概念**: 如何設計和構建一個完整的、特定領域的代理，例如部署管理、混沌工程等。
- **參考資料**:
    - **SRE 領域範例**: `adk-agent-samples/sre-bot/`
    - **軟體工程領域範例**: `adk-agent-samples/software-bug-assistant/`
    - **機器學習領域範例**: `adk-agent-samples/machine-learning-engineering/`

## 4. SRE 核心原則

- **概念**: SRE Assistant 的所有功能都根植於 Google 的 SRE 文化和原則。
- **參考資料**:
    - **SLO (服務水平目標)**: `google-sre-book/Chapter-04-Service-Level-Objectives.md`
    - **事後檢討 (Postmortems)**: `google-sre-book/Chapter-15-Postmortem-CultureLearning-from-Failure.md`
    - **消除瑣事 (Eliminating Toil)**: `google-sre-book/Chapter-05-Eliminating-Toil.md`
    - **監控與警報**: `google-sre-book/Chapter-06-Monitoring-Distributed-Systems.md` 及 `Chapter-10-Practical-Alerting.md`
