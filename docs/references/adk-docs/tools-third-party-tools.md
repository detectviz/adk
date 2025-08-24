# 第三方工具

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前適用於 Python。Java 支援正在計劃/即將推出。"}

ADK 的設計具有**高度可擴展性，讓您可以無縫整合來自其他 AI 代理框架 (如 CrewAI 和 LangChain) 的工具**。這種互通性至關重要，因為它能加快開發時間，並讓您重複使用現有的工具。

## 1. 使用 LangChain 工具

ADK 提供了 `LangchainTool` 包裝器，可將 LangChain 生態系統中的工具整合到您的代理程式中。

### 範例：使用 LangChain 的 Tavily 工具進行網路搜尋

[Tavily](https://tavily.com/) 提供了一個搜尋 API，可傳回衍生自即時搜尋結果的答案，專為 AI 代理程式等應用程式使用。

1. 遵循 [ADK 安裝與設定](get-started-installation.md) 指南。

2. **安裝相依套件：** 確保您已安裝必要的 LangChain 套件。例如，若要使用 Tavily 搜尋工具，請安裝其特定的相依套件：

    ```bash
    pip install langchain_community tavily-python
    ```

3. 取得 [Tavily](https://tavily.com/) API 金鑰並將其匯出為環境變數。

    ```bash
    export TAVILY_API_KEY=<請替換為您的API金鑰>
    ```

4. **匯入：** 從 ADK 匯入 `LangchainTool` 包裝器，以及您希望使用的特定 `LangChain` 工具 (例如 `TavilySearchResults`)。

    ```python
    from google.adk.tools.langchain_tool import LangchainTool
    from langchain_community.tools import TavilySearchResults
    ```

5. **實例化與包裝：** 建立您的 LangChain 工具的實例，並將其傳遞給 `LangchainTool` 的建構函式。

    ```python
    # 實例化 LangChain 工具
    tavily_tool_instance = TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True,
        include_images=True,
    )

    # 使用 LangchainTool 為 ADK 進行包裝
    adk_tavily_tool = LangchainTool(tool=tavily_tool_instance)
    ```

6. **新增至代理程式：** 在定義時，將包裝好的 `LangchainTool` 實例包含在您的代理程式的 `tools` 清單中。

    ```python
    from google.adk import Agent

    # 定義 ADK 代理程式，包含包裝好的工具
    my_agent = Agent(
        name="langchain_tool_agent",
        model="gemini-2.0-flash",
        description="使用 TavilySearch 回答問題的代理程式。",
        instruction="我可以用網路搜尋來回答您的問題。儘管問我任何事！",
        tools=[adk_tavily_tool] # 在此處新增包裝好的工具
    )
    ```

### 完整範例：Tavily 搜尋

以下是結合上述步驟的完整程式碼，用於建立和執行一個使用 LangChain Tavily 搜尋工具的代理程式。

```python
--8<-- "examples/python/snippets/tools/third-party/langchain_tavily_search.py"
```

## 2. 使用 CrewAI 工具

ADK 提供了 `CrewaiTool` 包裝器，可將 CrewAI 函式庫中的工具整合進來。

### 範例：使用 CrewAI 的 Serper API 進行網路搜尋

[Serper API](https://serper.dev/) 以程式化的方式提供對 Google 搜尋結果的存取。它允許像 AI 代理程式這樣的應用程式執行即時的 Google 搜尋 (包括新聞、圖片等)，並取回結構化的資料，而無需直接爬取網頁。

1. 遵循 [ADK 安裝與設定](get-started-installation.md) 指南。

2. **安裝相依套件：** 安裝必要的 CrewAI 工具套件。例如，若要使用 SerperDevTool：

    ```bash
    pip install crewai-tools
    ```

3. 取得 [Serper API 金鑰](https://serper.dev/)並將其匯出為環境變數。

    ```bash
    export SERPER_API_KEY=<請替換為您的API金鑰>
    ```

4. **匯入：** 從 ADK 匯入 `CrewaiTool`，以及所需的 CrewAI 工具 (例如 `SerperDevTool`)。

    ```python
    from google.adk.tools.crewai_tool import CrewaiTool
    from crewai_tools import SerperDevTool
    ```

5. **實例化與包裝：** 建立 CrewAI 工具的實例。將其傳遞給 `CrewaiTool` 的建構函式。**至關重要的是，您必須向 ADK 包裝器提供名稱和描述**，因為 ADK 的底層模型會使用這些資訊來了解何時使用該工具。

    ```python
    # 實例化 CrewAI 工具
    serper_tool_instance = SerperDevTool(
        n_results=10,
        save_file=False,
        search_type="news",
    )

    # 使用 CrewaiTool 為 ADK 進行包裝，並提供名稱和描述
    adk_serper_tool = CrewaiTool(
        name="InternetNewsSearch",
        description="使用 Serper 專門搜尋最近的新聞文章。",
        tool=serper_tool_instance
    )
    ```

6. **新增至代理程式：** 將包裝好的 `CrewaiTool` 實例包含在您的代理程式的 `tools` 清單中。

    ```python
    from google.adk import Agent
 
    # 定義 ADK 代理程式
    my_agent = Agent(
        name="crewai_search_agent",
        model="gemini-2.0-flash",
        description="使用 Serper 搜尋工具尋找最新新聞的代理程式。",
        instruction="我可以為您找到最新的新聞。您對哪個主題感興趣？",
        tools=[adk_serper_tool] # 在此處新增包裝好的工具
    )
    ```

### 完整範例：Serper API

以下是結合上述步驟的完整程式碼，用於建立和執行一個使用 CrewAI Serper API 搜尋工具的代理程式。

```python
--8<-- "examples/python/snippets/tools/third-party/crewai_serper_search.py"
```
