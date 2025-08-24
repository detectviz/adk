# 代理開發套件 (Agent Development Kit, ADK)

<div style="text-align:center;">**無縫地建構、評估和部署代理！**</div>

ADK 旨在使開發人員能夠建構、管理、評估和部署由 AI 驅動的代理。它為創建能夠處理複雜任務和工作流程的對話式和非對話式代理提供了一個強大而靈活的環境。

![intro_components.png](../assets/adk-components.png)

## 核心概念

ADK 圍繞一些關鍵的基本元素和概念建構，使其功能強大且靈活。以下是其要點：

* **代理 (Agent):** 專為特定任務設計的基本工作單元。代理可以使用語言模型 (`LlmAgent`) 進行複雜的推理，或作為執行的確定性控制器，稱為「[工作流程代理](agents-workflow-agents.md)」 (`SequentialAgent`、`ParallelAgent`、`LoopAgent`)。
* **工具 (Tool):** 賦予代理超越對話的能力，讓它們與外部 API 互動、搜尋資訊、執行程式碼或呼叫其他服務。
* **回呼 (Callbacks):** 您提供的自訂程式碼片段，在代理流程的特定點執行，以進行檢查、記錄或行為修改。
* **會話管理 (`Session` & `State`):** 處理單一對話的上下文 (`Session`)，包括其歷史記錄 (`Events`) 和代理在該對話中的工作記憶體 (`State`)。
* **記憶體 (Memory):** 使代理能夠在*多個*會話中回憶有關使用者的資訊，提供長期上下文（與短期會話 `State` 不同）。
* **產物管理 (`Artifact`):** 允許代理儲存、載入和管理與會話或使用者相關的檔案或二進位資料（如影像、PDF）。
* **程式碼執行 (Code Execution):** 代理（通常透過工具）生成和執行程式碼以執行複雜計算或操作的能力。
* **規劃 (Planning):** 一種進階功能，代理可以將複雜的目標分解為更小的步驟，並像 ReAct 規劃器一樣規劃如何實現它們。
* **模型 (Models):** 驅動 `LlmAgent` 的底層大型語言模型 (LLM)，使其具備推理和語言理解能力。
* **事件 (Event):** 代表會話期間發生的事情（使用者訊息、代理回覆、工具使用）的基本通訊單元，構成對話歷史記錄。
* **執行器 (Runner):** 管理執行流程、根據事件協調代理互動以及與後端服務協調的引擎。

***注意：** 多式聯運串流 (Multimodal Streaming)、評估 (Evaluation)、部署 (Deployment)、除錯 (Debugging) 和追蹤 (Trace) 等功能也是更廣泛的 ADK 生態系統的一部分，支援即時互動和開發生命週期。*

## 主要功能

ADK 為建構代理應用程式的開發人員提供了幾個關鍵優勢：

1. **多代理系統設計 (Multi-Agent System Design):** 輕鬆建構由多個專業代理組成的分層應用程式。代理可以協調複雜的任務，使用大型語言模型 (LLM) 驅動的轉移或明確的 `AgentTool` 調用來委派子任務，從而實現模組化和可擴展的解決方案。
2. **豐富的工具生態系統 (Rich Tool Ecosystem):** 為代理配備多樣化的功能。ADK 支援整合自訂函式 (`FunctionTool`)、將其他代理用作工具 (`AgentTool`)、利用程式碼執行等內建功能，以及與外部資料來源和 API（例如搜尋、資料庫）互動。對長時間執行工具的支援可有效處理非同步操作。
3. **靈活的協調 (Flexible Orchestration):** 使用內建的工作流程代理 (`SequentialAgent`、`ParallelAgent`、`LoopAgent`) 和大型語言模型 (LLM) 驅動的動態路由來定義複雜的代理工作流程。這允許 sowohl 可預測的管線和適應性代理行為。
4. **整合的開發人員工具 (Integrated Developer Tooling):** 輕鬆地在本地進行開發和迭代。ADK 包括命令列介面 (CLI) 和開發人員 UI 等工具，用於執行代理、檢查執行步驟（事件、狀態變更）、除錯互動和視覺化代理定義。
5. **原生串流支援 (Native Streaming Support):** 透過對雙向串流（文字和音訊）的原生支援，建構即時、互動式的體驗。這與底層功能（如 [Gemini 開發者 API 的多式聯運即時 API](https://ai.google.dev/gemini-api/docs/live)（或 [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/multimodal-live)））無縫整合，通常只需簡單的組態變更即可啟用。
6. **內建代理評估 (Built-in Agent Evaluation):** 系統地評估代理性能。該框架包括用於建立多輪評估資料集和在本地（透過 CLI 或開發人員 UI）執行評估以衡量品質和指導改進的工具。
7. **廣泛的大型語言模型 (LLM) 支援 (Broad LLM Support):** 雖然針對 Google 的 Gemini 模型進行了優化，但該框架設計靈活，允許透過其 `BaseLlm` 介面與各種大型語言模型（可能包括開源或微調模型）整合。
8. **產物管理 (Artifact Management):** 使代理能夠處理檔案和二進位資料。該框架提供了代理在執行期間儲存、載入和管理版本化產物（如影像、文件或生成的報告）的機制 (`ArtifactService`、上下文方法）。
9. **可擴展性和互通性 (Extensibility and Interoperability):** ADK 促進了一個開放的生態系統。在提供核心工具的同時，它允許開發人員輕鬆整合和重複使用來自其他流行代理框架（包括 LangChain 和 CrewAI）的工具。
10. **狀態和記憶體管理 (State and Memory Management):** 自動處理由 `SessionService` 管理的 `Session` 中的短期對話記憶體 (`State`)。為長期 `Memory` 服務提供整合點，允許代理在多個會話中回憶使用者資訊。

![intro_components.png](../assets/adk-lifecycle.png)

## 開始使用

* 準備好建構您的第一個代理了嗎？ [嘗試快速入門](get-started-quickstart.md)
