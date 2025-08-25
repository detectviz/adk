# SRE Assistant ADK 範例參考指南

**版本**: 1.0.0
**狀態**: 生效中

## 1. 導覽

本文件旨在為 SRE Assistant 專案的開發團隊提供一份精選的 Google Agent Development Kit (ADK) 範例參考列表。這些範例都經過仔細評估，被認為與本專案的架構願景、功能規格和開發任務高度相關。

開發團隊在實作新功能時，應優先參考這些範例，以確保技術選型與架構設計的一致性，並加速開發進程。

---

## 2. 核心參考範例

以下是三個核心的 ADK 範例，它們分別對應了 SRE Assistant 架構的三大支柱：**聯邦化多代理協同**、**RAG 記憶體**和**複雜工作流協調**。

### 2.1. A2A 與 MCP (代理發現與協同)

- **範例路徑**: `docs/references/adk-agent-samples/a2a_mcp/`
- **參考原因**:
    - **對應架構**: 此範例完美地詮釋了 `ARCHITECTURE.md` 中定義的**聯邦化設計 (Federated Design)**。它展示了一個「協調者代理 (Orchestrator Agent)」如何透過一個「模型內容協議 (MCP) 伺服器」作為註冊中心，來動態發現並呼叫多個專業化的「任務代理 (Task Agents)」。
    - **技術關聯**:
        - **A2A 通訊**: 直接對應 `ROADMAP.md` 中 Phase 3 的 `A2A Communication Protocol v1` 交付物。
        - **代理註冊與發現**: MCP 伺服器的角色，為未來 `Phase 4` 的「服務發現與註冊」提供了具體的實作思路。
        - **動態工作流**: 協調者代理根據任務動態選擇並呼叫不同代理的能力，是實現 `SPEC.md` 中定義的 `Incident Handler Assistant` 等複雜工作流程的基礎。
    - **開發指導**: 在開發 `SREWorkflow` (`workflow.py`) 以及未來獨立的 `SREIntelligentDispatcher` 時，應深入參考此範例中協調者代理的設計模式。

### 2.2. RAG (檢索增強生成)

- **範例路徑**: `docs/references/adk-agent-samples/RAG/`
- **參考原因**:
    - **對應架構**: 此範例是 `ARCHITECTURE.md` 中**統一記憶庫 (Unified Memory)**，特別是利用向量資料庫進行 RAG 的核心實踐。它展示了如何將外部文件（如：技術文件、Runbook）整合進代理的知識體系中。
    - **技術關聯**:
        - **核心記憶體功能**: 直接對應 `TASKS.md` 中的 `TASK-P1-CORE-01: 實現 MemoryProvider (RAG)`。此範例提供了使用 Vertex AI RAG Engine 的完整流程，包括資料上傳、工具實作和 LLM 整合。
        - **引用與溯源**: 範例中包含的引文功能，對於 SRE Assistant 生成的每一個診斷或建議，提供可信的來源依據至關重要。
        - **評估框架**: 該範例包含一個完整的評估套件 (`eval/`)，為我們自己的評估框架 (`sre_assistant/eval/`) 提供了絕佳的參考。
    - **開發指導**: 在實作 `sre_assistant/memory/backend_factory.py` 和相關的 RAG 工具時，應參考此範例的程式碼結構、部署腳本和評估方法。

### 2.3. Google ADK Workflows (多代理工作流模式)

- **範例路徑**: `docs/references/adk-agent-samples/google-adk-workflows/`
- **參考原因**:
    - **對應架構**: 如果說 `a2a_mcp` 範例解決了「如何發現代理」，那麼此範例則解答了「**如何組織和協調代理**」。它提供了四種不同的工作流協調模式（簡單、分派、並行、自我批判），這對於實現 `SPEC.md` 中定義的各種 SRE Assistant 至關重要。
    - **技術關聯**:
        - **複雜工作流**: `SelfCriticAgent` 模式中包含的「審查-驗證」循環，是 `TASKS.md` 中「修復後驗證 (Post-Remediation Verification)」功能的直接參考。
        - **智慧分派**: `DispatcherAgent` 為 `TASK-P2-REFACTOR-01: 智慧分診系統` 提供了初始的設計藍圖。
        - **效率優化**: `ParallelAgent` 展示的並行處理能力，可用於優化需要同時從多個數據源（如 Loki, Prometheus）拉取資料的診斷流程。
        - **模組化與可擴展性**: 將核心能力封裝為可重用的 `subagent.py` 的做法，與我們 `sre_assistant/sub_agents/` 的目標目錄結構高度一致。
    - **開發指導**: 團隊在設計和實作 `SREWorkflow` (`workflow.py`) 以及各個 `sub_agents` 之間的互動邏輯時，應將此範例作為首要的模式參考。
