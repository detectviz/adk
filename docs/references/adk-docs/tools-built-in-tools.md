# 內建工具

這些內建工具提供了現成的功能，例如 Google 搜尋或程式碼執行器，為代理程式提供常見的功能。例如，需要從網路擷取資訊的代理程式可以直接使用 **google_search** 工具，無需任何額外設定。

## 如何使用

1. **匯入：** 從工具模組匯入所需的工具。在 Python 中是 `agents.tools`，在 Java 中是 `com.google.adk.tools`。
2. **設定：** 初始化工具，並提供任何必要的參數。
3. **註冊：** 將初始化後的工具新增到您的代理程式的 **tools** 清單中。

一旦新增到代理程式中，代理程式就可以根據**使用者提示**及其**指令**決定是否使用該工具。當代理程式呼叫工具時，框架會處理工具的執行。重要提示：請查看本頁的***限制***部分。

## 可用的內建工具

注意：Java 目前僅支援 Google 搜尋和程式碼執行工具。

### Google 搜尋

`google_search` 工具允許代理程式使用 Google 搜尋執行網路搜尋。`google_search` 工具僅與 Gemini 2 模型相容。有關該工具的更多詳細資訊，請參閱[了解 Google 搜尋 grounding](grounding-google_search_grounding.md)。

!!! warning "使用 `google_search` 工具時的額外要求"
    當您使用 grounding with Google Search，並在回應中收到搜尋建議時，您必須在生產環境和您的應用程式中顯示這些搜尋建議。
    有關使用 grounding with Google Search 的更多資訊，請參閱 [Google AI Studio](https://ai.google.dev/gemini-api/docs/grounding/search-suggestions) 或 [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions) 的 Google 搜尋 grounding 文件。UI 程式碼 (HTML) 會在 Gemini 回應中以 `renderedContent` 的形式傳回，您需要根據政策在您的應用程式中顯示該 HTML。

=== "Python"

    ```python
    --8<-- "examples/python/snippets/tools/built-in-tools/google_search.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/GoogleSearchAgentApp.java:full_code"
    ```

### 程式碼執行

`built_in_code_execution` 工具使代理程式能夠執行程式碼，特別是在使用 Gemini 2 模型時。這允許模型執行計算、資料操作或執行小型腳本等任務。

=== "Python"

    ```python
    --8<-- "examples/python/snippets/tools/built-in-tools/code_execution.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CodeExecutionAgentApp.java:full_code"
    ```


### Vertex AI Search

`vertex_ai_search_tool` 使用 Google Cloud 的 Vertex AI Search，使代理程式能夠在您私有的、已設定的資料儲存區（例如，內部文件、公司政策、知識庫）中進行搜尋。此內建工具要求您在設定期間提供特定的資料儲存區 ID。有關該工具的更多詳細資訊，請參閱[了解 Vertex AI Search grounding](grounding-vertex_ai_search_grounding.md)。


```python
--8<-- "examples/python/snippets/tools/built-in-tools/vertexai_search.py"
```


### BigQuery

這是一組旨在提供與 BigQuery 整合的工具，即：

* **`list_dataset_ids`**：擷取 GCP 專案中存在的 BigQuery 資料集 ID。
* **`get_dataset_info`**：擷取有關 BigQuery 資料集的元數據。
* **`list_table_ids`**：擷取 BigQuery 資料集中存在的資料表 ID。
* **`get_table_info`**：擷取有關 BigQuery 資料表的元數據。
* **`execute_sql`**：在 BigQuery 中執行 SQL 查詢並擷取結果。

它們被打包在 `BigQueryToolset` 工具集中。



```python
--8<-- "examples/python/snippets/tools/built-in-tools/bigquery.py"
```

## 將內建工具與其他工具一起使用

以下程式碼範例示範如何使用多個內建工具，或如何透過使用多個代理程式將內建工具與其他工具一起使用：

=== "Python"

    ```python
    from google.adk.tools import agent_tool
    from google.adk.agents import Agent
    from google.adk.tools import google_search
    from google.adk.code_executors import BuiltInCodeExecutor
    

    search_agent = Agent(
        model='gemini-2.0-flash',
        name='SearchAgent',
        instruction="""
        您是 Google 搜尋的專家
        """,
        tools=[google_search],
    )
    coding_agent = Agent(
        model='gemini-2.0-flash',
        name='CodeAgent',
        instruction="""
        您是程式碼執行的專家
        """,
        tools=[BuiltInCodeExecutor],
    )
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="根代理程式",
        tools=[agent_tool.AgentTool(agent=search_agent), agent_tool.AgentTool(agent=coding_agent)],
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;
    import com.google.adk.tools.BuiltInCodeExecutionTool;
    import com.google.adk.tools.GoogleSearchTool;
    import com.google.common.collect.ImmutableList;
    
    public class NestedAgentApp {
    
      private static final String MODEL_ID = "gemini-2.0-flash";
    
      public static void main(String[] args) {

        // 定義 SearchAgent
        LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("您是 Google 搜尋的專家")
                .tools(new GoogleSearchTool()) // 實例化 GoogleSearchTool
                .build();
    

        // 定義 CodingAgent
        LlmAgent codingAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("CodeAgent")
                .instruction("您是程式碼執行的專家")
                .tools(new BuiltInCodeExecutionTool()) // 實例化 BuiltInCodeExecutionTool
                .build();

        // 定義 RootAgent，它使用 AgentTool.create() 來包裝 SearchAgent 和 CodingAgent
        BaseAgent rootAgent =
            LlmAgent.builder()
                .name("RootAgent")
                .model(MODEL_ID)
                .description("根代理程式")
                .tools(
                    AgentTool.create(searchAgent), // 使用 create 方法
                    AgentTool.create(codingAgent)   // 使用 create 方法
                 )
                .build();

        // 注意：此範例僅示範代理程式定義。
        // 若要執行這些代理程式，您需要將它們與 Runner 和 SessionService 整合，
        // 類似於先前的範例。
        System.out.println("代理程式定義成功：");
        System.out.println("  根代理程式：" + rootAgent.name());
        System.out.println("  搜尋代理程式 (巢狀)：" + searchAgent.name());
        System.out.println("  程式碼代理程式 (巢狀)：" + codingAgent.name());
      }
    }
    ```


### 限制

!!! warning

    目前，對於每個根代理程式或單一代理程式，僅支援一個內建工具。同一代理程式中不能使用任何其他類型的工具。

 例如，以下在單一代理程式中使用***內建工具和其他工具***的方法目前**不**受支援：

=== "Python"

    ```python
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="根代理程式",
        tools=[custom_function, BuiltInCodeExecutor], # <-- 與工具一起使用時不支援 BuiltInCodeExecutor
    )
    ```

=== "Java"

    ```java
     LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("您是 Google 搜尋的專家")
                .tools(new GoogleSearchTool(), new YourCustomTool()) // <-- 不支援
                .build();
    ```

!!! warning

    內建工具不能在子代理程式中使用。

例如，以下在子代理程式中使用內建工具的方法目前**不**受支援：

=== "Python"

    ```python
    search_agent = Agent(
        model='gemini-2.0-flash',
        name='SearchAgent',
        instruction="""
        您是 Google 搜尋的專家
        """,
        tools=[google_search],
    )
    coding_agent = Agent(
        model='gemini-2.0-flash',
        name='CodeAgent',
        instruction="""
        您是程式碼執行的專家
        """,
        tools=[BuiltInCodeExecutor],
    )
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="根代理程式",
        sub_agents=[
            search_agent,
            coding_agent
        ],
    )
    ```

=== "Java"

    ```java
    LlmAgent searchAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("SearchAgent")
            .instruction("您是 Google 搜尋的專家")
            .tools(new GoogleSearchTool())
            .build();

    LlmAgent codingAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("CodeAgent")
            .instruction("您是程式碼執行的專家")
            .tools(new BuiltInCodeExecutionTool())
            .build();
    

    LlmAgent rootAgent =
        LlmAgent.builder()
            .name("RootAgent")
            .model("gemini-2.0-flash")
            .description("根代理程式")
            .subAgents(searchAgent, codingAgent) // 不支援，因為子代理程式使用內建工具。
            .build();
    ```
