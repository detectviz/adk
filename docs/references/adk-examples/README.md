# Google Agent Development Kit (ADK) 的 Python 範例

以下是所有可用範例的索引，並附有簡短說明。

## 範例索引列表

*   [`a2a_auth/`](a2a_auth/): 展示了代理對代理 (A2A) 架構與 OAuth 驗證的整合，其中一個遠端代理需要透過本地代理進行使用者驗證，以存取受保護的資源 (例如 BigQuery)。
*   [`a2a_basic/`](a2a_basic/): 一個基本的代理對代理 (A2A) 範例，展示了本地代理 (擲骰子) 和遠端代理 (檢查質數) 如何協同工作。
*   [`a2a_human_in_loop/`](a2a_human_in_loop/): 展示了代理對代理 (A2A) 架構中的人工介入流程，其中一個遠端代理需要人工批准才能完成一項任務 (例如，批准大額報銷)。
*   [`a2a_root/`](a2a_root/): 展示了如何將一個遠端代理對代理 (A2A) 服務作為根代理，並使用 uvicorn 伺服器來部署遠端代理。
*   [`adk_answering_agent/`](adk_answering_agent/): 一個使用大型語言模型和 Vertex AI Search 來回答 `google/adk-python` 儲存庫中 GitHub 討論區問題的代理。
*   [`adk_issue_formatting_agent/`](adk_issue_formatting_agent/): 一個檢查 GitHub 問題是否遵循範本格式的代理，如果問題格式不正確，它會自動留言要求作者提供更多資訊。
*   [`adk_pr_agent/`](adk_pr_agent/): 一個能為 GitHub 拉取請求 (PR) 產生符合慣例的描述的代理。
*   [`adk_pr_triaging_agent/`](adk_pr_triaging_agent/): 一個能自動為 GitHub 拉取請求 (PR) 進行分類、推薦標籤和指派審核者的代理。
*   [`adk_triaging_agent/`](adk_triaging_agent/): 一個能自動為 GitHub 問題進行分類並應用標籤的代理。
*   [`application_integration_agent/`](application_integration_agent/): 展示如何使用應用程式整合工具集 (ApplicationIntegrationToolset) 來與外部應用程式 (例如 Jira) 互動。
*   [`artifact_save_text/`](artifact_save_text/): 展示如何使用 `tool_context.save_artifact` 將文字產物儲存到工具上下文 (Tool Context) 中。
*   [`bigquery/`](bigquery/): 展示如何使用 ADK 提供的 BigQuery 工具，包括列出資料集和資料表、取得元數據以及執行 SQL 查詢。
*   [`bigtable/`](bigtable/): 展示如何使用 ADK 提供的 Bigtable 工具，包括列出實例和資料表、取得元數據以及執行 SQL 查詢。
*   [`callbacks/`](callbacks/): 展示如何在代理 (Agent) 的生命週期中註冊和使用各種回呼函式，例如在代理或模型執行前後觸發的函式。
*   [`code_execution/`](code_execution/): 一個資料科學代理，能夠在類似 Colab 的環境中執行 Python 程式碼來進行資料分析。
*   [`core_basic_config/`](core_basic_config/): 一個最基本的代理設定範例，僅包含 `name`、`description` 和 `model` 三個欄位。
*   [`core_callback_config/`](core_callback_config/): 展示如何在 YAML 設定檔中為代理 (Agent) 設定各種回呼函式。
*   [`core_custom_agent_config/`](core_custom_agent_config/): 展示如何透過 `agent_class` 欄位來使用自訂的代理 (Agent) 類別，並傳入自訂的欄位 (`my_field`)。
*   [`core_generate_content_config_config/`](core_generate_content_config_config/): 展示如何使用 `generate_content_config` 來設定模型的生成參數，例如溫度 (temperature) 和最大輸出 token 數。
*   [`fields_output_schema/`](fields_output_schema/): 展示如何使用 `output_schema` 和 `output_key` 來定義代理 (Agent) 的輸出結構。
*   [`fields_planner/`](fields_planner/): 展示如何為代理 (Agent) 設定一個規劃器 (Planner)，例如 `BuiltInPlanner` 或 `PlanReActPlanner`。
*   [`generate_image/`](generate_image/): 展示如何使用圖片生成模型 (Imagen) 來根據文字提示生成圖片，並將圖片儲存為產物。
*   [`google_api/`](google_api/): 展示如何使用 `GoogleApiTool` 來呼叫任何 Google API，此範例以 BigQuery API 為例。
*   [`google_search_agent/`](google_search_agent/): 一個使用內建的 `google_search` 工具來執行 Google 搜尋的代理。
*   [`hello_world/`](hello_world/): 一個基本的 'Hello World' 範例，展示了如何建立一個具有簡單工具 (擲骰子、檢查質數) 的代理。
*   [`hello_world_anthropic/`](hello_world_anthropic/): 一個 'Hello World' 範例，展示如何使用 Anthropic 的 Claude 模型作為代理的 LLM。
*   [`hello_world_litellm/`](hello_world_litellm/): 一個 'Hello World' 範例，展示如何使用 LiteLLM 來與多種不同的 LLM (例如 OpenAI 的 GPT-4o) 進行互動。
*   [`hello_world_litellm_add_function_to_prompt/`](hello_world_litellm_add_function_to_prompt/): 展示如何在使用 LiteLLM 時，將函式定義動態加入到提示中，以啟用那些原生不支援函式呼叫的模型的工具使用能力。
*   [`hello_world_ma/`](hello_world_ma/): 一個多代理 (Multi-Agent) 的 'Hello World' 範例，其中一個根代理 (Root Agent) 將任務 (擲骰子、檢查質數) 委派給不同的子代理 (Sub-Agent)。
*   [`hello_world_ollama/`](hello_world_ollama/): 展示如何透過 LiteLLM 將 ADK 與本地執行的 Ollama 模型整合，並提供了詳細的設定和偵錯指南。
*   [`history_management/`](history_management/): 展示如何使用 `before_model_callback` 來管理對話歷史，例如只保留最近的 N 輪對話。
*   [`human_in_loop/`](human_in_loop/): 展示如何實作一個需要人工介入的長時間執行工具，例如一個需要等待外部批准才能繼續執行的報銷流程。
*   [`integration_connector_euc_agent/`](integration_connector_euc_agent/): 展示如何使用應用程式整合工具集 (ApplicationIntegrationToolset) 和使用者 OAuth 2.0 憑證來與 Google 日曆等外部應用程式互動。
*   [`jira_agent/`](jira_agent/): 展示如何使用 Google Application Integration 和 Integration Connectors 將代理 (Agent) 連接到 Jira Cloud。
*   [`langchain_structured_tool_agent/`](langchain_structured_tool_agent/): 展示如何使用 `LangchainTool` 將 LangChain 的 `StructuredTool` 整合到 ADK 代理中。
*   [`langchain_youtube_search_agent/`](langchain_youtube_search_agent/): 一個使用 LangChain 的 `YoutubeSearchTool` 來搜尋 YouTube 影片的代理。
*   [`live_bidi_streaming_multi_agent/`](live_bidi_streaming_multi_agent/): 一個用於測試和實驗的即時、雙向串流多代理 (Multi-Agent) 範例。
*   [`live_bidi_streaming_single_agent/`](live_bidi_streaming_single_agent/): 一個用於測試和實驗的基本的即時、雙向串流單一代理 (Single-Agent) 範例。
*   [`live_bidi_streaming_tools_agent/`](live_bidi_streaming_tools_agent/): 展示如何在即時串流代理中使用串流工具，允許工具將中繼結果串流回代理，例如監控股票價格或視訊串流。
*   [`live_tool_callbacks_agent/`](live_tool_callbacks_agent/): 展示了在即時串流模式下，工具回呼函式 (Tool Callbacks) 如何運作，包括在工具執行前後觸發同步和非同步的回呼。
*   [`mcp_sse_agent/`](mcp_sse_agent/): 展示如何透過伺服器發送事件 (Server-Sent Events, SSE) 將代理 (Agent) 連接到一個本地的多通道對話 (Multi-Channel Protocol, MCP) 伺服器。
*   [`mcp_stdio_notion_agent/`](mcp_stdio_notion_agent/): 一個使用 Notion MCP 工具來呼叫 Notion API 的代理，並展示如何傳入 Notion API 金鑰。
*   [`mcp_stdio_server_agent/`](mcp_stdio_server_agent/): 展示如何使用 `MCPToolset` 和 `StdioConnectionParams` 來與一個透過標準輸入/輸出 (stdio) 執行的本地檔案系統伺服器進行互動。
*   [`mcp_streamablehttp_agent/`](mcp_streamablehttp_agent/): 展示如何透過可串流的 HTTP 將代理 (Agent) 連接到一個本地的多通道對話 (Multi-Channel Protocol, MCP) 伺服器。
*   [`memory/`](memory/): 展示如何使用 `load_memory_tool` 和 `preload_memory_tool` 來讓代理 (Agent) 存取和預載記憶體中的資料。
*   [`multi_agent_basic_config/`](multi_agent_basic_config/): 一個基本的多代理 (Multi-Agent) 設定範例，其中一個根代理會根據問題類型 (程式設計或數學) 將任務委派給不同的子代理。
*   [`multi_agent_llm_config/`](multi_agent_llm_config/): 一個多代理 (Multi-Agent) 設定範例，其中根代理和子代理都是透過 YAML 設定檔來定義的。
*   [`multi_agent_loop_config/`](multi_agent_loop_config/): 一個多代理 (Multi-Agent) 範例，展示了如何透過循序和迴圈工作流程來實現一個迭代式的寫作過程，其中包含寫作、評論和精煉等步驟。
*   [`multi_agent_seq_config/`](multi_agent_seq_config/): 一個多代理 (Multi-Agent) 範例，展示了如何透過循序工作流程來實現一個多階段的程式碼撰寫過程，其中每個階段使用不同能力和成本的模型。
*   [`non_llm_sequential/`](non_llm_sequential/): 一個展示循序代理 (SequentialAgent) 的範例，其中兩個子代理會依序執行。
*   [`oauth_calendar_agent/`](oauth_calendar_agent/): 一個展示 ADK 中 OAuth 支援的範例，透過自訂工具和內建的 Google Calendar ToolSet 來與 Google 日曆 API 互動。
*   [`output_schema_with_tools/`](output_schema_with_tools/): 展示如何在同一個代理中同時使用 `output_schema` (結構化輸出) 和 `tools` (工具)，ADK 會自動處理這種組合。
*   [`parallel_functions/`](parallel_functions/): 展示了 ADK 中的平行函式呼叫功能，並說明如何透過非同步工具來實現真正的平行化，以提高效能。
*   [`plugin_basic/`](plugin_basic/): 展示如何使用外掛程式 (Plugin) 將回呼函式打包，以實作日誌記錄、策略強制執行和快取等橫跨整個應用的功能。
*   [`quickstart/`](quickstart/): 一個快速入門範例，展示如何建立一個具有簡單工具 (取得天氣、取得時間) 的代理。
*   [`rag_agent/`](rag_agent/): 展示如何使用 `VertexAiRagRetrieval` 工具從 Vertex AI RAG 語料庫中檢索文件，以回答問題。
*   [`session_state_agent/`](session_state_agent/): 展示了會話狀態 (Session State) 的生命週期，以及如何在不同的回呼函式中存取和修改狀態。
*   [`simple_sequential_agent/`](simple_sequential_agent/): 一個簡單的循序代理 (SequentialAgent) 範例，其中 `roll_agent` 和 `prime_agent` 會依序執行。
*   [`spanner/`](spanner/): 展示如何使用 ADK 提供的 Spanner 工具，包括列出資料表和索引、取得結構以及執行 SQL 查詢。
*   [`sub_agents_config/`](sub_agents_config/): 展示如何透過 `config_path` (YAML 檔案) 和 `code` (Python 模組) 兩種方式來設定子代理。
*   [`telemetry/`](telemetry/): 這個範例本身不包含遙測 (Telemetry) 功能，但它是一個可以用來測試和觀察 ADK 遙測功能的代理。
*   [`token_usage/`](token_usage/): 一個循序代理，其中包含多個使用不同大型語言模型 (OpenAI, Claude, Gemini) 的子代理，可以用來比較不同模型的 token 使用情況。
*   [`tool_agent_tool_config/`](tool_agent_tool_config/): 展示如何使用 `AgentTool` 將其他代理 (Agent) 作為工具來使用，此範例中使用了一個網路搜尋代理和一個總結代理。
*   [`tool_builtin_config/`](tool_builtin_config/): 展示如何在 YAML 設定檔中直接使用內建的工具，例如 `google_search`。
*   [`tool_functions_config/`](tool_functions_config/): 展示如何在 YAML 設定檔中透過指定函式路徑的方式來設定工具。
*   [`tool_human_in_the_loop_config/`](tool_human_in_the_loop_config/): 展示如何在 YAML 設定檔中設定一個需要人工介入的長時間執行工具 (`LongRunningFunctionTool`)。
*   [`tool_mcp_stdio_notion_config/`](tool_mcp_stdio_notion_config/): 展示如何在 YAML 設定檔中使用 `MCPToolset` 和 `stdio_server_params` 來與 Notion MCP 伺服器互動。
*   [`toolbox_agent/`](toolbox_agent/): 展示如何使用 `ToolboxToolset` 來與一個本地的 MCP 工具箱伺服器互動，此範例以 SQLite 資料庫為例。
*   [`workflow_agent_seq/`](workflow_agent_seq/): 一個展示循序代理 (SequentialAgent) 如何用於多階段工作流程的範例，例如先寫程式碼，然後審查，最後再重構。
*   [`workflow_triage/`](workflow_triage/): 一個多代理 (Multi-Agent) 範例，展示如何建置一個可智慧地分流傳入請求，並將其委派給適當的專門代理 (例如程式碼代理或數學代理) 的工作流程。


## 範例

範例資料夾中存放了用於測試不同功能的範例。這些範例通常是最小化且簡單的，旨在測試一個或幾個特定的情境。

**注意**：這與 [google/adk-samples](https://github.com/google/adk-samples) Repo 不同，後者存放了更複雜的端到端範例，可供客戶直接使用或修改。

## ADK 專案總覽與架構

Google Agent Development Kit (ADK) for Python

### 核心理念與架構

- **程式碼優先 (Code-First)**：所有內容都在 Python 程式碼中定義，以便於版本控制、測試和 IDE 支援。避免使用圖形化介面 (GUI) 進行邏輯開發。

- **模組化與組合 (Modularity & Composition)**：我們透過組合多個較小的、專業化的代理 (Agent) 來建構複雜的多代理 (Multi Agent) 系統。

- **部署無關性 (Deployment-Agnostic)**：代理 (Agent) 的核心邏輯與其部署環境分離。同一個 `agent.py` 可以在本地運行以進行測試，可以透過 API 提供服務，也可以部署到雲端。

### 基礎抽象 (我們的詞彙)

- **代理 (Agent)**：藍圖。它定義了代理 (Agent) 的身份、指令和工具。它是一個宣告式的設定物件。

- **工具 (Tool)**：一種能力。一個代理 (Agent) 可以呼叫來與世界互動的 Python 函式（例如，搜尋、API 呼叫）。

- **執行器 (Runner)**：引擎。它協調「推理-行動 (Reason-Act)」循環，管理大型語言模型 (LLM) 的呼叫，並執行工具。

- **會話 (Session)**：對話狀態。它保存單一、連續對話的歷史記錄。

- **記憶體 (Memory)**：跨不同會話的長期記憶。

- **產物服務 (Artifact Service)**：管理非文字資料，如檔案。

### 標準專案結構

請遵守此結構，以確保與 ADK 工具的相容性。

```bash
my_adk_project/
└── src/
    └── my_app/
        ├── agents/
        │   ├── my_agent/
        │   │   ├── __init__.py   # 必須包含: from. import agent \
        │   │   └── agent.py      # 必須包含: root_agent = Agent(...) \
        │   └── another_agent/
        │       ├── __init__.py
        │       └── agent.py\
```

`agent.py`: 必須定義代理 (Agent) 並將其分配給名為 `root_agent` 的變數。這是 ADK 工具找到它的方式。

`__init__.py`: 在每個代理 (Agent) 目錄中，它必須包含 `from. import agent`，以使代理 (Agent) 可被發現。

### 本地開發與偵錯

- **互動式介面 (adk web)**：這是我們主要的偵錯工具。它是一個解耦的系統：
    - **後端**：一個用 `adk api_server` 啟動的 FastAPI 伺服器。
    - **前端**：一個連接到後端的 Angular 應用程式。
    - 使用「Events」分頁來檢查完整的執行追蹤（提示、工具呼叫、回應）。

- **命令列介面 (adk run)**：用於在終端機中進行快速、無狀態的功能檢查。

- **程式化 (pytest)**：用於撰寫自動化的單元和整合測試。

### API 層 (FastAPI)

我們使用 FastAPI 將代理 (Agent) 公開為生產級 API。

- `get_fast_api_app`：這是 `google.adk.cli.fast_api` 中的關鍵輔助函式，可從我們的代理 (Agent) 目錄創建一個 FastAPI 應用程式。

- **標準端點**：生成的應用程式包含標準路由，如 `/list-apps` 和 `/run_sse` 用於串流回應。傳輸格式為駝峰式 (camelCase)。

- **自訂端點**：我們可以將自己的路由（例如 `/health`）添加到輔助函式返回的應用程式物件中。

```python
from google.adk.cli.fast_api import get_fast_api_app
app = get_fast_api_app(agent_dir="./agents")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

## 部署到生產環境

`adk` 命令列介面提供 `adk deploy` 指令，可部署到 Google Vertex Agent Engine、Google Cloud Run、Google GKE。

### 測試與評估策略

測試是分層的，就像金字塔一樣。

#### 第一層：單元測試 (基礎)

- **內容**：獨立測試單個工具 (Tool) 函式。
- **方法**：在 `tests/test_tools.py` 中使用 `pytest`。驗證確定性邏輯。

#### 第二層：整合測試 (中層)

- **內容**：測試代理 (Agent) 的內部邏輯以及與工具的互動。
- **方法**：在 `tests/test_agent.py` 中使用 `pytest`，通常會模擬大型語言模型 (LLM) 或服務。

#### 第三層：評估測試 (頂層)

- **內容**：使用即時的大型語言模型 (LLM) 評估端到端的性能。這關乎品質，而不僅僅是通過/失敗。
- **方法**：使用 ADK 評估框架。
    - **測試案例**：創建包含輸入和參考（預期的工具呼叫和最終回應）的 JSON 檔案。
    - **指標**：`tool_trajectory_avg_score`（它是否正確使用工具？）和 `response_match_score`（最終答案是否良好？）。
- **執行方式**：透過 `adk web`（使用者介面）、`pytest`（用於 CI/CD）或 `adk eval`（命令列介面）運行。
