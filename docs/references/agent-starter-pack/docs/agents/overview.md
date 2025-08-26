# 代理模板

Agent Starter Pack 遵循「帶上你自己的代理 (bring your own agent)」的理念。它提供了幾個可用於生產的代理模板，旨在加速您的開發，同時提供使用您偏好的代理框架或模式的靈活性。

## 可用模板


| 代理名稱 | 描述 | 使用案例 |
|------------|-------------|----------|
| `adk_base` | 使用 Google 的 [Agent Development Kit](https://github.com/google/adk-python) 實現的基礎 ReAct 代理 | 通用對話代理 |
| `agentic_rag` | 用於文件檢索和問答的 RAG 代理 | 文件搜尋與問答 |
| `langgraph_base_react` | 使用 LangGraph 的基礎 ReAct 代理 | 基於圖的對話代理 |
| `crewai_coding_crew` | 使用 CrewAI 實現的多代理系統 | 協作編碼輔助 |
| `live_api` | 即時多模態 RAG 代理 | 帶有知識庫的音訊/視訊/文字聊天 |

## 選擇正確的模板

在選擇模板時，請考慮以下因素：

1.  **主要目標**：您是在建構一個對話機器人、一個基於文件的問答系統、一個任務自動化團隊，還是其他東西？
2.  **核心模式/框架**：您是否偏好 Google 的 ADK、LangChain/LangGraph、CrewAI，或是直接實現像 RAG 這樣的模式？入門套件支援多種方法。
3.  **推理複雜性**：您的代理是否需要複雜的規劃和工具使用 (如 ReAct)，還是更專注於檢索和綜合 (如基本的 RAG)？
4.  **協作需求**：您是否需要多個專業代理協同工作？
5.  **模態**：您的代理是否需要處理或回應音訊、視訊，或僅僅是文字？

## 模板詳情

### ADK 基礎 (`adk_base`)

此模板提供了一個使用 Google 的 [代理開發套件 (Agent Development Kit, ADK)](https://github.com/google/adk-python) 建構的 ReAct 代理的最小範例。它展示了 ADK 的核心概念，如代理建立和工具整合，從而實現推理和工具選擇。適用於：

*   在 Google Cloud 上開始代理開發。
*   建構通用目的的對話代理。
*   學習 ADK 框架和 ReAct 模式。

### Agentic RAG (`agentic_rag`)

此模板建構在 ADK 之上，實現了[檢索增強生成 (Retrieval-Augmented Generation, RAG)](https://cloud.google.com/use-cases/retrieval-augmented-generation?hl=en)，並帶有一個可用於生產的資料擷取管線，用於基於文件的問答。它允許您擷取、處理和嵌入自訂資料，以增強回應的相關性。功能包括：

*   用於自訂資料的自動化資料擷取管線。
*   靈活的資料儲存選項：[Vertex AI Search](https://cloud.google.com/vertex-ai-search-and-conversation) 和 [Vertex AI Vector Search](https://cloud.google.com/vertex-ai/docs/vector-search/overview)。
*   生成自訂嵌入以增強語意搜尋。
*   從檢索到的上下文中綜合答案。
*   透過 Terraform 進行基礎設施部署，並可選擇 CI/CD 執行器 (Google Cloud Build 或 GitHub Actions)。

### LangGraph 基礎 ReAct (`langgraph_base_react`)

此模板提供了一個使用 [LangGraph](https://langchain-ai.github.io/langgraph/) 建構的 ReAct 代理的最小範例。它為開發具有基於圖的結構的代理提供了一個極佳的起點，提供：

*   用於複雜、多步驟推理流程的明確狀態管理。
*   對推理週期的精細控制。
*   穩健的工具整合和錯誤處理能力。
*   使用 Vertex AI 的串流回應支援。
*   包含一個基本的搜尋工具以展示工具用法。

### CrewAI 編碼團隊 (`crewai_coding_crew`)

此模板將 [CrewAI](https://www.crewai.com/) 的多代理協作與 LangGraph 的對話控制相結合，創建了一個互動式編碼助理。它協調專業代理 (例如，資深工程師、QA 工程師) 來理解需求並生成程式碼。主要功能包括：

*   透過自然對話進行互動式需求收集 (LangGraph)。
*   由一組專業 AI 代理協作開發程式碼 (CrewAI)。
*   從需求到實作和 QA 的任務順序處理。
*   適用於需要委派和模擬團隊協作的複雜任務。

### Live API (`live_api`)

此模板由 Google Gemini 提供支援，展示了一個使用 [Vertex AI Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api) 的即時、多模態對話式 RAG 代理。功能包括：

*   處理音訊、視訊和文字互動。
*   利用工具呼叫。
*   透過 WebSockets 進行即時雙向通訊，以實現低延遲聊天。
*   可用於生產的 Python 後端 (FastAPI) 和 React 前端。
*   包含回饋收集功能。

## 客製化模板

所有模板都作為起點提供，並為客製化而設計：

1.  選擇最符合您需求的模板。
2.  基於所選模板建立一個新的代理實例。
3.  熟悉程式碼結構，專注於代理邏輯、工具定義和任何 UI 元件。
4.  修改和擴展程式碼：根據需要調整提示、新增或移除工具、整合不同的資料來源、更改推理邏輯或更新框架版本。

祝您建構代理愉快！