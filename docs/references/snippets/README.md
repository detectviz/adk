# ADK 程式碼片段

此資料夾包含 [Python 代理開發套件 (ADK)](https://github.com/google/adk-python) 的程式碼片段，展示了特定的功能和使用案例。

## 範例索引列表

### 代理 (Agents)

*   [`agents/custom-agent/storyflow_agent.py`](agents/custom-agent/storyflow_agent.py): 展示如何建立一個自訂的協調器代理 (`StoryFlowAgent`)，該代理按順序和迴圈方式組合多個 `LlmAgent`，以建立、評論和修訂一個故事。
*   [`agents/llm-agent/capital_agent.py`](agents/llm-agent/capital_agent.py): 比較了使用工具 (`FunctionTool`) 和使用 `output_schema` 進行結構化輸出的 `LlmAgent` 之間的差異。
*   [`agents/workflow-agents/loop_agent_doc_improv_agent.py`](agents/workflow-agents/loop_agent_doc_improv_agent.py): 實作了一個迭代式的文件改進工作流程，其中一個 `LoopAgent` 反覆執行「評論」和「修訂」代理，直到評論代理發出一個特殊的「完成」訊號，該訊號由一個工具 (`exit_loop`) 捕捉以終止迴圈。
*   [`agents/workflow-agents/parallel_agent_web_research.py`](agents/workflow-agents/parallel_agent_web_research.py): 展示了一個兩階段的工作流程，首先使用 `ParallelAgent` 同時執行多個研究代理，然後一個 `SequentialAgent` 中的後續代理將並行結果合併成一份摘要報告。
*   [`agents/workflow-agents/sequential_agent_code_development_agent.py`](agents/workflow-agents/sequential_agent_code_development_agent.py): 示範瞭如何使用 `SequentialAgent` 建立一個三階段的程式碼開發流程，包括撰寫、審查和重構程式碼。

### 回呼 (Callbacks)

*   [`callbacks/after_agent_callback.py`](callbacks/after_agent_callback.py): 示範如何使用 `after_agent_callback`，根據會話狀態中的條件，有條件地覆寫代理的最終輸出。
*   [`callbacks/after_model_callback.py`](callbacks/after_model_callback.py): 展示如何使用 `after_model_callback` 在從大型語言模型（LLM）收到回應後，檢查並修改該回應。
*   [`callbacks/after_tool_callback.py`](callbacks/after_tool_callback.py): 示範如何使用 `after_tool_callback` 在工具執行後，有條件地修改工具的回應。
*   [`callbacks/before_agent_callback.py`](callbacks/before_agent_callback.py): 展示如何使用 `before_agent_callback`，根據會話狀態中的條件，完全跳過代理的執行。
*   [`callbacks/before_model_callback.py`](callbacks/before_model_callback.py): 示範如何使用 `before_model_callback` 在將請求傳送給大型語言模型（LLM）之前，修改請求內容或完全跳過 LLM 呼叫。
*   [`callbacks/before_tool_callback.py`](callbacks/before_tool_callback.py): 展示如何使用 `before_tool_callback` 在工具執行前，修改傳遞給工具的參數或完全跳過工具呼叫。
*   [`callbacks/callback_basic.py`](callbacks/callback_basic.py): 提供了一個註冊和使用回呼函式的基本範例。

### 入門指南 (Get Started)

*   [`get-started/google_search_agent/agent.py`](get-started/google_search_agent/agent.py): 一個基本的代理，展示如何使用內建的 `google_search` 工具。
*   [`get-started/multi_tool_agent/agent.py`](get-started/multi_tool_agent/agent.py): 一個展示如何讓代理同時使用多個自訂工具（`get_weather` 和 `get_current_time`）的範例。

### 串流 (Streaming)

*   [`streaming/adk-streaming/`](streaming/adk-streaming/): 一個完整的範例，展示如何使用 FastAPI 和伺服器發送事件 (SSE) 來建立一個與代理進行即時雙向通訊的前端應用程式。
*   [`streaming/adk-streaming-ws/`](streaming/adk-streaming-ws/): 一個完整的範例，展示如何使用 FastAPI 和 WebSockets 來建立一個與代理進行即時雙向通訊的前端應用程式。

### 工具 (Tools)

*   [`tools/auth/`](tools/auth/): 一個完整的範例，展示了代理如何使用 `OpenAPIToolset` 和 OAuth 2.0 (透過 OpenID Connect) 來與需要驗證的外部 API 互動。
*   [`tools/built-in-tools/bigquery.py`](tools/built-in-tools/bigquery.py): 示範如何使用內建的 `BigQueryToolset` 來查詢 BigQuery 資料集。
*   [`tools/built-in-tools/code_execution.py`](tools/built-in-tools/code_execution.py): 展示如何為代理啟用內建的程式碼執行器 (`BuiltInCodeExecutor`)，使其能夠撰寫和執行 Python 程式碼來回答問題。
*   [`tools/built-in-tools/google_search.py`](tools/built-in-tools/google_search.py): 一個基本的代理，展示如何使用內建的 `google_search` 工具。
*   [`tools/built-in-tools/vertexai_search.py`](tools/built-in-tools/vertexai_search.py): 展示如何使用 `VertexAiSearchTool` 從特定的 Vertex AI Search 資料儲存庫中檢索資訊。
*   [`tools/function-tools/func_tool.py`](tools/function-tools/func_tool.py): 一個簡單的範例，展示如何將一個普通的 Python 函式 (`get_stock_price`) 直接作為工具提供給代理。
*   [`tools/function-tools/human_in_the_loop.py`](tools/function-tools/human_in_the_loop.py): 示範如何使用 `LongRunningFunctionTool` 來處理需要人工介入或長時間執行的非同步任務，例如核准流程。
*   [`tools/function-tools/summarizer.py`](tools/function-tools/summarizer.py): 展示如何使用 `AgentTool` 將一個代理（摘要代理）包裝成另一個代理（根代理）可以呼叫的工具。
*   [`tools/openapi_tool.py`](tools/openapi_tool.py): 示範如何使用 `OpenAPIToolset` 從 OpenAPI (Swagger) 規格檔案中自動生成工具。
*   [`tools/overview/customer_support_agent.py`](tools/overview/customer_support_agent.py): 展示工具如何使用 `tool_context.actions.transfer_to_agent` 將對話轉接給另一個子代理。
*   [`tools/overview/doc_analysis.py`](tools/overview/doc_analysis.py): 展示工具如何使用 `tool_context` 來存取和操作產物 (`load_artifact`, `save_artifact`) 和記憶體 (`search_memory`)。
*   [`tools/overview/toolset_example.py`](tools/overview/toolset_example.py): 展示如何將多個相關的 `FunctionTool` 組合成一個可重複使用的 `BaseToolset`。
*   [`tools/overview/user_preference.py`](tools/overview/user_preference.py): 示範工具如何使用 `tool_context.state` 來讀取和寫入會話狀態，以管理使用者偏好設定。
*   [`tools/overview/weather_sentiment.py`](tools/overview/weather_sentiment.py): 一個結合了多個工具（天氣查詢和情緒分析）的代理範例，以執行更複雜的任務。
*   [`tools/third-party/crewai_serper_search.py`](tools/third-party/crewai_serper_search.py): 展示如何使用 `CrewaiTool` 將 CrewAI 的 `SerperDevTool` 包裝成 ADK 工具。
*   [`tools/third-party/langchain_tavily_search.py`](tools/third-party/langchain_tavily_search.py): 展示如何使用 `LangchainTool` 將 LangChain 的 `TavilySearchResults` 工具整合到 ADK 中。
