## 0. Introduction (引言)

本文件旨在提供一份全面且深入的 Google Agent Development Kit (ADK) 專案架構指南。作為一名務實且經驗豐富的 Google Agent Development Kit (ADK) 官方首席架構師，我將從技術實現的視角，詳細闡述 ADK 的核心組件、消息傳遞機制、代理程式層次結構、部署策略、測試與評估方法，以及本地開發與調試工具。本文件將作為未來開發 ADK Agent 的標準模板，旨在確保所有團隊成員都能清晰理解其技術棧、運作流程、整體生命週期和完整閉環，從而為 AI Coding 提供明確的方向，並完整構建高效的 Multi-Agentic System。

本文件將詳細參考 Google 官方文檔、Codelabs 教程、GitHub 專案倉庫以及相關技術博客，確保內容的權威性和實用性。我們將深入探討 ADK 如何賦能開發者構建、管理、評估和部署智能 AI 代理程式，並強調其「程式碼優先」的設計理念、模塊化和可組合的架構優勢。

通過閱讀本文件，開發者將能夠：

*   掌握 ADK 的核心概念和組件，理解每個部分在整個系統中的作用。
*   了解不同類型的代理程式及其適用場景，學會如何設計多代理程式協作系統。
*   熟悉 ADK 的消息傳遞機制，包括事件和代理程式間通信協議。
*   理解 ADK 代理程式的部署選項和生產環境的最佳實踐。
*   掌握 ADK 的測試與評估策略，確保代理程式的質量和性能。
*   利用 ADK 提供的開發與調試工具，提高開發效率。

本文件將力求清晰、精確、全面，旨在成為所有 ADK 開發者不可或缺的參考資料。

# Google Agent Development Kit (ADK) 專案架構文件

## 1. 核心概念與組件 (Core Concepts & Components)

Google Agent Development Kit (ADK) 旨在賦能開發者構建、管理、評估和部署 AI 驅動的代理程式。它提供了一個強大且靈活的環境，用於創建對話式和非對話式代理，能夠處理複雜的任務和工作流程。ADK 的核心圍繞著以下幾個關鍵原語和概念構建：

### 1.1. Agent (代理程式)

Agent 是 ADK 中最基本的工作單元，專為特定任務設計。Agent 可以利用大型語言模型 (LLM) 進行複雜的推理 (`LlmAgent`)，也可以作為執行流程的確定性控制器，這些被稱為「工作流代理程式」(Workflow Agents)，例如 `SequentialAgent` (順序代理程式)、`ParallelAgent` (並行代理程式) 和 `LoopAgent` (循環代理程式)。

### 1.2. Tool (工具)

Tool 賦予 Agent 超越對話的能力，讓它們能夠與外部 API 交互、搜索信息、執行程式碼或調用其他服務。ADK 支持集成自定義函數 (`FunctionTool`)，使用其他 Agent 作為工具 (`AgentTool`)，以及利用內置功能，如程式碼執行和與外部數據源及 API (例如，搜索、數據庫) 的交互。對長時間運行工具的支持允許有效處理異步操作。

### 1.3. Runner (運行器)

Runner 是執行引擎。它協調「推理-行動」(Reason-Act) 循環，管理 LLM 調用，並執行工具。它是整個 Agent 系統運作的協調者。

### 1.4. Session (會話)

Session 管理單次對話的上下文，包括其歷史記錄 (`Events`) 和 Agent 在該對話中的工作記憶 (`State`)。它確保了單次交互的連貫性和上下文感知。

### 1.5. Memory (記憶)

Memory 使 Agent 能夠跨多個會話回憶有關用戶的信息，提供長期上下文 (與短期會話 `State` 不同)。這對於構建能夠學習和適應用戶偏好的持久性 Agent 至關重要。

### 1.6. Artifact Management (工件管理)

Artifact Management 允許 Agent 保存、加載和管理與會話或用戶相關的文件或二進制數據 (如圖像、PDF)。這使得 Agent 能夠處理非文本數據並在任務執行過程中生成或消費各種媒體類型。

### 1.7. Events (事件)

Event 是基本的通信單元，表示會話期間發生的事情 (用戶消息、Agent 回覆、工具使用)，形成對話歷史記錄。所有 Agent 的交互和內部操作都通過事件流進行表示和追蹤。

### 1.8. Code Execution (程式碼執行)

Agent 能夠 (通常通過 Tool) 生成和執行程式碼，以執行複雜的計算或操作。這為 Agent 提供了強大的計算能力和靈活性。

### 1.9. Planning (規劃)

Planning 是一種高級能力，Agent 可以將複雜的目標分解為更小的步驟，並像 ReAct 規劃器一樣規劃如何實現它們。

### 1.10. Models (模型)

Models 是驅動 `LlmAgent` 的底層 LLM，使其具備推理和語言理解能力。ADK 雖然針對 Google 的 Gemini 模型進行了優化，但也設計為靈活的，允許通過其 `BaseLlm` 接口集成各種 LLM (可能包括開源或微調模型)。

## 2. Agent Hierarchy (代理程式層次結構)

ADK 支持不同類型的代理程式，每種類型都針對特定用例進行了優化，並可以協同工作以實現複雜的目標：

### 2.1. LlmAgent (大型語言模型代理程式)

`LlmAgent` 是 ADK 中最靈活的代理程式類型，它利用大型語言模型 (LLM) 進行動態決策。這些代理程式能夠理解自然語言、對複雜問題進行推理，並動態決定何時以及如何使用工具。

**關鍵特性：**
*   基於上下文的動態工具選擇。
*   自然語言理解和生成能力。
*   迭代推理能力。
*   對意外情況的適應性。

**典型用例：**
*   客戶服務自動化。
*   內容創建和編輯。
*   研究和分析任務。
*   交互式問題解決。

### 2.2. SequentialAgent (順序代理程式)

順序代理程式擅長處理需要特定操作順序的任務。它們非常適合數據處理管道、多步驟表單填充或任何需要嚴格按順序執行的工作流程。

**關鍵特性：**
*   按照預定義的順序執行一系列步驟。
*   每個步驟的輸出可以作為下一個步驟的輸入。
*   適用於可預測且線性的工作流程。

**典型用例：**
*   自動化數據清洗和轉換流程。
*   逐步引導用戶完成複雜的配置。
*   按順序執行多個 API 調用。

### 2.3. ParallelAgent (並行代理程式)

並行代理程式能夠同時運行多個操作，以提高性能和效率。它們適用於可以獨立執行且其結果可以合併的任務。

**關鍵特性：**
*   同時執行多個子任務。
*   等待所有子任務完成後再繼續。
*   適用於需要同時處理多個數據源或執行多個獨立操作的場景。

**典型用例：**
*   同時從多個來源獲取信息。
*   並行處理圖像或視頻幀。
*   在多個數據庫中執行並行查詢。

### 2.4. LoopAgent (循環代理程式)

循環代理程式執行迭代操作，直到滿足特定條件。它們對於需要重複執行直到達到某個狀態或處理完所有項目為止的任務非常有用。

**關鍵特性：**
*   重複執行一系列操作，直到滿足退出條件。
*   支持基於條件的循環控制。
*   適用於需要迭代優化或處理列表數據的場景。

**典型用例：**
*   重複嘗試直到成功 (例如，重試失敗的 API 調用)。
*   遍歷列表中的每個項目並執行操作。
*   基於用戶反饋進行迭代改進。

### 2.5. Custom Agents (自定義代理程式)

ADK 允許開發者根據特定需求實現自定義代理程式。這提供了最大的靈活性，可以為獨特的用例或複雜的行為模式構建量身定制的代理程式。

**關鍵特性：**
*   完全控制代理程式的內部邏輯和行為。
*   可以集成任何 Python 庫或外部服務。
*   適用於標準代理程式類型無法滿足的特定業務邏輯。

**典型用例：**
*   集成專有算法或模型。
*   實現複雜的決策樹或狀態機。
*   與非標準協議或系統交互。

### 2.6. Multi-Agent System Design (多代理程式系統設計)

ADK 的一個核心優勢是能夠輕鬆構建由多個專業代理程式組成的多代理程式系統，這些代理程式可以分層排列。代理程式可以協調複雜的任務，使用 LLM 驅動的轉移或顯式的 `AgentTool` 調用委派子任務，從而實現模塊化和可擴展的解決方案。

**關鍵特性：**
*   代理程式之間的協作和任務委派。
*   支持層次化結構，實現複雜任務的分解。
*   通過 `AgentTool` 實現代理程式間的通信和協調。

**典型用例：**
*   複雜的客戶服務流程，由多個專業代理程式協同處理不同類型的查詢。
*   自動化項目管理，由規劃代理程式、執行代理程式和審核代理程式協同工作。
*   智能數據分析平台，由數據採集代理程式、分析代理程式和報告生成代理程式組成。

## 3. Messaging (消息傳遞)

在 ADK 中，消息傳遞是實現代理程式之間以及代理程式與外部系統之間通信的關鍵。主要機制包括基於事件的通信和代理程式間通信 (A2A Protocol)。

### 3.1. Events (事件)

Events 是 ADK 中最基本的通信單元，代表在會話期間發生的所有事情。這包括用戶發送的消息、代理程式的回覆、工具的調用結果、狀態的變化等。所有這些事件都形成了一個連續的事件流，構成了會話的完整歷史記錄。

**關鍵特性：**
*   **統一的通信模型：** 所有交互都抽象為事件，簡化了處理邏輯。
*   **可追溯性：** 事件流提供了完整的執行軌跡，便於調試和審計。
*   **實時可見性：** 開發者可以通過事件監聽器或開發者 UI 實時查看代理程式的內部運作。

**典型用例：**
*   記錄用戶輸入和代理程式輸出。
*   追蹤工具調用及其結果。
*   監控代理程式的內部狀態變化。
*   觸發回調函數以執行自定義邏輯。

### 3.2. Agent-to-Agent (A2A) Protocol (代理程式間通信協議)

A2A Protocol 是一種標準化的通信方式，允許分佈式代理程式 (可能運行在不同的機器或服務上) 之間可靠地進行交互。這對於構建協作式多代理程式系統至關重要，其中不同的代理程式需要相互協調以完成複雜的任務。

**關鍵特性：**
*   **標準化接口：** 提供統一的通信接口，簡化代理程式間的集成。
*   **分佈式協作：** 支持代理程式跨越不同部署環境進行通信和協作。
*   **任務委派：** 允許代理程式將子任務委派給其他專業代理程式。
*   **可靠性：** 旨在確保消息傳遞的可靠性和一致性。

**典型用例：**
*   一個主代理程式將特定領域的問題轉發給專業代理程式處理。
*   多個代理程式協同完成一個複雜的業務流程，例如訂單處理或客戶支持。
*   在微服務架構中，不同的代理程式作為獨立的服務運行並通過 A2A 協議進行通信。

### 3.3. Streaming Support (流式支持)

ADK 原生支持雙向流式傳輸 (文本和音頻)，這對於構建實時、交互式體驗至關重要。這與底層功能 (如 Gemini Developer API 的多模態實時 API) 無縫集成，通常只需簡單的配置更改即可啟用。

**關鍵特性：**
*   **實時交互：** 支持實時文本和音頻流，提供更流暢的用戶體驗。
*   **低延遲：** 減少了等待完整響應的時間，提高了交互效率。
*   **多模態支持：** 能夠處理不同類型的數據流，例如文本、音頻和潛在的視頻。

**典型用例：**
*   實時語音助手和聊天機器人。
*   實時翻譯和轉錄服務。
*   需要即時反饋的交互式應用。

## 4. Deployment & Runtime Environment (部署與運行環境)

ADK 旨在實現部署環境的獨立性，這意味著相同的 `agent.py` 文件可以在本地運行進行測試，通過 API 提供服務，或部署到雲端。ADK 提供了一套工具和最佳實踐，以確保代理程式能夠高效、可擴展地運行。

### 4.1. Canonical Project Structure (標準專案結構)

為了與 ADK 工具兼容，專案應遵循以下標準結構：

```
my_adk_project/
└── src/
    └── my_app/
        ├── agents/
        │   ├── my_agent/
        │   │   ├── __init__.py   # Must contain: from . import agent
        │   │   └── agent.py      # Must contain: root_agent = Agent(...)
        │   └── another_agent/
        │       ├── __init__.py
        │       └── agent.py
```

*   `agent.py`：必須定義代理程式並將其分配給名為 `root_agent` 的變量。這是 ADK 工具查找代理程式的方式。
*   `__init__.py`：在每個代理程式目錄中，它必須包含 `from . import agent` 以使代理程式可被發現。

### 4.2. The API Layer (API 層)

ADK 使用 FastAPI 將代理程式公開為生產 API。`google.adk.cli.fast_api` 中的 `get_fast_api_app` 輔助函數可以從代理程式目錄創建一個 FastAPI 應用程式。

**關鍵特性：**
*   **標準端點：** 生成的應用程式包含 `/list-apps` 和 `/run_sse` 等標準路由，用於流式響應。線路格式為 camelCase。
*   **自定義端點：** 可以向輔助函數返回的應用程式對象添加自定義路由 (例如 `/health`)。

**範例：**
```python
from google.adk.cli.fast_api import get_fast_api_app

app = get_fast_api_app(agent_dir="./agents")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

### 4.3. Deployment to Production (生產部署)

ADK CLI 提供了 `adk deploy` 命令，用於將代理程式部署到 Google Vertex Agent Engine、Google Cloud Run 或 Google GKE。這使得代理程式能夠在 Google Cloud 生態系統中實現可擴展和可靠的部署。

**部署選項：**
*   **Google Vertex Agent Engine：** 專為 AI 代理程式設計的託管服務。
*   **Google Cloud Run：** 無服務器平台，用於部署容器化應用程式，自動擴展。
*   **Google GKE (Google Kubernetes Engine)：** 託管的 Kubernetes 服務，提供高度靈活性和控制力。

### 4.4. Observability & Monitoring (可觀測性與監控)

雖然 ADK 官方文檔中沒有詳細說明具體的監控工具，但作為一個生產級的代理程式框架，可觀測性是至關重要的。通常會集成以下類型的工具：

*   **日誌 (Logging)：** 收集代理程式的運行日誌，用於故障排除和行為分析。
*   **指標 (Metrics)：** 收集關鍵性能指標 (KPIs)，例如請求延遲、錯誤率、工具調用次數等。
*   **追蹤 (Tracing)：** 追蹤代理程式的決策鏈路和工具調用，以便理解複雜的交互流程。

Agent Starter Pack 提供了生產就緒的基礎設施，包括監控和可觀測性，以及在 Cloud Run 或 Agent Engine 上的 CI/CD。

## 5. Testing & Evaluation Strategy (測試與評估策略)

ADK 採用分層測試方法，類似於測試金字塔，以確保代理程式的質量和性能。

### 5.1. Layer 1: Unit Tests (單元測試)

*   **內容：** 測試單個工具函數的獨立功能。
*   **方法：** 使用 `pytest` 在 `tests/test_tools.py` 中進行測試。驗證確定性邏輯。

### 5.2. Layer 2: Integration Tests (集成測試)

*   **內容：** 測試代理程式的內部邏輯以及與工具的交互。
*   **方法：** 使用 `pytest` 在 `tests/test_agent.py` 中進行測試，通常會模擬 LLM 或服務。

### 5.3. Layer 3: Evaluation Tests (評估測試)

*   **內容：** 評估與實時 LLM 的端到端性能。這關乎質量，而不僅僅是通過/失敗。
*   **方法：** 使用 ADK 評估框架。
    *   **測試用例：** 創建包含輸入和參考 (預期的工具調用和最終響應) 的 JSON 文件。
    *   **指標：** `tool_trajectory_avg_score` (是否正確使用工具？) 和 `response_match_score` (最終答案是否良好？)。
*   **運行方式：** 通過 `adk web` (UI)、`pytest` (用於 CI/CD) 或 `adk eval` (CLI) 運行。

### 5.4. Built-in Agent Evaluation (內置代理程式評估)

ADK 框架包含用於系統評估代理程式性能的工具。它允許創建多輪評估數據集，並在本地 (通過 CLI 或開發者 UI) 運行評估，以衡量質量並指導改進。

## 6. Local Development & Debugging (本地開發與調試)

ADK 提供了一套集成的開發者工具，以便於本地開發和迭代。

### 6.1. Interactive UI (adk web)

這是 ADK 的主要調試工具，它是一個解耦的系統：

*   **後端：** 通過 `adk api_server` 啟動的 FastAPI 服務器。
*   **前端：** 連接到後端的 Angular 應用程式。

使用「Events」選項卡可以檢查完整的執行追蹤 (提示、工具調用、響應)。

### 6.2. CLI (adk run)

用於在終端中進行快速、無狀態的功能檢查。

### 6.3. Programmatic (pytest)

用於編寫自動化單元測試和集成測試。

## 7. Conclusion (結論)

Google Agent Development Kit (ADK) 提供了一個全面且強大的框架，用於設計、開發、部署和管理智能 AI 代理程式。其「程式碼優先」的理念、模塊化和可組合的架構，以及對多代理程式系統的內置支持，使其成為構建複雜、可擴展和可維護的 AI 應用程式的理想選擇。

通過對核心概念 (Agent, Tool, Runner, Session, Memory, Artifact Management, Events) 的清晰定義，ADK 為開發者提供了一套標準化的詞彙和抽象層，簡化了代理程式的開發過程。多樣化的代理程式層次結構 (LlmAgent, SequentialAgent, ParallelAgent, LoopAgent, Custom Agents) 允許開發者根據不同的任務需求選擇最合適的代理程式類型，並通過 Agent-to-Agent (A2A) 協議實現代理程式之間的無縫協作。

ADK 在部署方面也提供了極大的靈活性，支持將代理程式部署到 Google Cloud 的多種環境中，包括 Vertex Agent Engine、Cloud Run 和 GKE，確保了生產級應用的可擴展性和可靠性。同時，其分層的測試和評估策略，以及豐富的本地開發和調試工具，為開發者提供了從原型到生產的全生命週期支持。

總體而言，ADK 不僅是一個開發工具包，更是一個完整的生態系統，旨在幫助開發者克服構建和部署智能 AI 代理程式所面臨的挑戰，加速 AI 應用的創新和落地。本文件旨在作為開發 ADK Agent 的標準模板，為團隊提供清晰的技術棧、運作流程、整體生命週期和完整閉環的指導，確保 AI Coding 能夠明確方向，完整構建整個 Multi Agentic System。

## 8. References (參考文獻)

[1] Google. (n.d.). *About ADK - Agent Development Kit*. Retrieved from [https://google.github.io/adk-docs/get-started/about/#key-capabilities](https://google.github.io/adk-docs/get-started/about/#key-capabilities)

[2] Google. (n.d.). *Google's Agent Stack in Action: ADK, A2A, MCP on Google Cloud*. Retrieved from [https://codelabs.developers.google.com/instavibe-adk-multi-agents/instructions](https://codelabs.developers.google.com/instavibe-adk-multi-agents/instructions)

[3] Google. (n.d.). *adk-python/contributing/adk_project_overview_and_architecture.md at main · google/adk-python · GitHub*. Retrieved from [https://github.com/google/adk-python/blob/main/contributing/adk_project_overview_and_architecture.md](https://github.com/google/adk-python/blob/main/contributing/adk_project_overview_and_architecture.md)

[4] GoogleCloudPlatform. (n.d.). *GitHub - GoogleCloudPlatform/agent-starter-pack: A collection of production-ready Generative AI Agent templates built for Google Cloud*. Retrieved from [https://github.com/GoogleCloudPlatform/agent-starter-pack](https://github.com/GoogleCloudPlatform/agent-starter-pack)

[5] Kumar, P. (2025, June 5). *Google’s Agent Development Kit (ADK): A Comprehensive Guide to Building Intelligent AI Agents*. GoPenAI. Retrieved from [https://blog.gopenai.com/googles-agent-development-kit-adk-a-comprehensive-guide-to-building-intelligent-ai-agents-6ef8762e391e](https://blog.gopenai.com/googles-agent-development-kit-adk-a-comprehensive-guide-to-building-intelligent-ai-agents-6ef8762e391e)


