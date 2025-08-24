# 函式工具

## 什麼是函式工具？

當現成的工具無法完全滿足特定需求時，開發人員可以建立自訂的函式工具。這允許實現 **量身訂製的功能**，例如連接到專有資料庫或實現獨特的演算法。

*例如*，一個名為 "myfinancetool" 的函式工具可能是一個計算特定財務指標的函式。ADK 也支援長時間運行的函式，因此如果該計算需要一段時間，代理 (agent) 可以繼續處理其他任務。

ADK 提供了多種建立函式工具的方法，每種方法都適用於不同程度的複雜性和控制需求：

1. 函式工具 (Function Tool)
2. 長時間運行函式工具 (Long Running Function Tool)
3. 代理即工具 (Agents-as-a-Tool)

## 1. 函式工具 (Function Tool)

將 Python 函式轉換為工具是將自訂邏輯整合到您的代理 (agent) 中的一種直接方法。當您將一個函式分配給代理 (agent) 的 `tools` 列表時，框架會自動將其包裝為 `FunctionTool`。

### 運作方式

ADK 框架會自動檢查您的 Python 函式簽章——包括其名稱、文件字串 (docstring)、參數、類型提示和預設值——以生成一個結構 (schema)。大型語言模型 (LLM) 使用此結構來理解工具的用途、何時使用它以及它需要哪些參數。

### 定義函式簽章

一個定義良好的函式簽章對於大型語言模型 (LLM) 正確使用您的工具至關重要。

#### 參數

您可以定義具有必需參數、可選參數和可變參數的函式。以下是每種參數的處理方式：

##### 必需參數
如果一個參數有類型提示但 **沒有預設值**，則該參數被視為 **必需**。大型語言模型 (LLM) 在呼叫該工具時必須為此參數提供一個值。

???+ "範例：必需參數"
    === "Python"
        ```python
        def get_weather(city: str, unit: str):
            """
            以指定的單位檢索一個城市的天氣。

            Args:
                city (str): 城市名稱。
                unit (str): 溫度單位，'Celsius' 或 'Fahrenheit'。
            """
            # ... 函式邏輯 ...
            return {"status": "success", "report": f"Weather for {city} is sunny."}
        ```
    在此範例中，`city` 和 `unit` 都是強制性的。如果大型語言模型 (LLM) 嘗試在沒有其中一個參數的情況下呼叫 `get_weather`，ADK 將向大型語言模型 (LLM) 返回一個錯誤，提示其更正呼叫。

##### 帶有預設值的可選參數
如果您為參數提供 **預設值**，則該參數被視為 **可選**。這是定義可選參數的標準 Python 方法。ADK 會正確解釋這些參數，並且不會在發送給大型語言模型 (LLM) 的工具結構 (schema) 的 `required` 欄位中列出它們。

???+ "範例：帶有預設值的可選參數"
    === "Python"
        ```python
        def search_flights(destination: str, departure_date: str, flexible_days: int = 0):
            """
            搜尋航班。

            Args:
                destination (str): 目的地城市。
                departure_date (str): 期望的出發日期。
                flexible_days (int, optional): 搜尋的彈性天數。預設為 0。
            """
            # ... 函式邏輯 ...
            if flexible_days > 0:
                return {"status": "success", "report": f"Found flexible flights to {destination}."}
            return {"status": "success", "report": f"Found flights to {destination} on {departure_date}."}
        ```
    在這裡，`flexible_days` 是可選的。大型語言模型 (LLM) 可以選擇提供它，但不是必需的。

##### 使用 `typing.Optional` 的可選參數
您也可以使用 `typing.Optional[SomeType]` 或 `| None` 語法 (Python 3.10+) 將參數標記為可選。這表示該參數可以為 `None`。當與 `None` 的預設值結合使用時，它的行為與標準的可選參數相同。

???+ "範例：`typing.Optional`"
    === "Python"
        ```python
        from typing import Optional

        def create_user_profile(username: str, bio: Optional[str] = None):
            """
            建立新的使用者個人資料。

            Args:
                username (str): 使用者的唯一使用者名稱。
                bio (str, optional): 使用者的簡短個人簡介。預設為 None。
            """
            # ... 函式邏輯 ...
            if bio:
                return {"status": "success", "message": f"Profile for {username} created with a bio."}
            return {"status": "success", "message": f"Profile for {username} created."}
        ```

##### 可變參數 (`*args` 和 `**kwargs`)
雖然您可以在函式簽章中包含 `*args` (可變位置參數) 和 `**kwargs` (可變關鍵字參數) 用於其他目的，但在為大型語言模型 (LLM) 生成工具結構 (schema) 時，它們會被 **ADK 框架忽略**。大型語言模型 (LLM) 不會意識到它們的存在，也無法向它們傳遞參數。最好依賴明確定義的參數來獲取您期望從大型語言模型 (LLM) 獲得的所有資料。

#### 返回類型

函式工具 (Function Tool) 的首選返回類型在 Python 中是 **字典 (dictionary)**，在 Java 中是 **Map**。這使您可以使用鍵值對來結構化回應，為大型語言模型 (LLM) 提供上下文和清晰度。如果您的函式返回的類型不是字典，框架會自動將其包裝成一個名為 **"result"** 的單一鍵的字典。

努力使您的返回值盡可能具有描述性。*例如*，不要返回一個數字錯誤代碼，而是返回一個帶有 "error_message" 鍵的字典，其中包含人類可讀的解釋。**請記住，是大型語言模型 (LLM)**，而不是一段程式碼，需要理解結果。作為最佳實踐，在您的返回字典中包含一個 "status" 鍵，以指示整體結果 (例如，"success"、"error"、"pending")，為大型語言模型 (LLM) 提供有關操作狀態的清晰信號。

#### 文件字串 (Docstrings)

您函式的文件字串 (docstring) 作為工具的 **描述** 發送給大型語言模型 (LLM)。因此，一個編寫良好且全面的文件字串 (docstring) 對於大型語言模型 (LLM) 有效地理解如何使用該工具至關重要。清楚地解釋函式的目的、其參數的含義以及預期的返回值。

### 範例

??? "範例"

    === "Python"
    
        此工具是一個 Python 函式，用於獲取給定股票代碼/符號的股價。
    
        <u>注意</u>：在使用此工具之前，您需要 `pip install yfinance` 函式庫。
    
        ```py
        --8<-- "examples/python/snippets/tools/function-tools/func_tool.py"
        ```
    
        此工具的返回值將被包裝到一個字典中。
    
        ```json
        {"result": "$123"}
        ```
    
    === "Java"
    
        此工具檢索模擬的股價。
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/tools/StockPriceAgent.java:full_code"
        ```
    
        此工具的返回值將被包裝到一個 Map<String, Object> 中。
    
        ```json
        對於輸入 `GOOG`：{"symbol": "GOOG", "price": "1.0"}
        ```

### 最佳實踐

雖然您在定義函式時有相當大的靈活性，但請記住，簡單性可以增強大型語言模型 (LLM) 的可用性。請考慮以下準則：

* **參數越少越好：** 盡量減少參數數量以降低複雜性。
* **簡單的資料類型：** 盡可能使用 `str` 和 `int` 等基本資料類型，而不是自訂類別。
* **有意義的名稱：** 函式的名稱和參數名稱會顯著影響大型語言模型 (LLM) 如何解釋和使用該工具。選擇能清楚反映函式目的及其輸入含義的名稱。避免使用像 `do_stuff()` 或 `beAgent()` 這樣的通用名稱。

## 2. 長時間運行函式工具 (Long Running Function Tool)

專為需要大量處理時間而不會阻塞代理 (agent) 執行的任務而設計。此工具是 `FunctionTool` 的子類別。

使用 `LongRunningFunctionTool` 時，您的函式可以啟動長時間運行的操作，並可選擇性地返回一個 **初始結果** (例如，長時間運行操作的 ID)。一旦長時間運行的函式工具被調用，代理 (agent) 運行器將暫停代理 (agent) 的運行，並讓代理 (agent) 客戶端決定是繼續還是等待長時間運行的操作完成。代理 (agent) 客戶端可以查詢長時間運行操作的進度，並發回中間或最終的回應。然後，代理 (agent) 可以繼續處理其他任務。一個例子是人機迴圈 (human-in-the-loop) 的場景，其中代理 (agent) 在繼續執行任務之前需要人類的批准。

### 運作方式

在 Python 中，您使用 `LongRunningFunctionTool` 包裝一個函式。在 Java 中，您將一個方法名稱傳遞給 `LongRunningFunctionTool.create()`。


1. **啟動：** 當大型語言模型 (LLM) 呼叫該工具時，您的函式會啟動長時間運行的操作。

2. **初始更新：** 您的函式應可選擇性地返回一個初始結果 (例如，長時間運行操作的 ID)。ADK 框架會獲取該結果，並將其包裝在 `FunctionResponse` 中發送回大型語言模型 (LLM)。這使得大型語言模型 (LLM) 可以通知使用者 (例如，狀態、完成百分比、訊息)。然後代理 (agent) 的運行結束/暫停。

3. **繼續或等待：** 在每個代理 (agent) 運行完成後。代理 (agent) 客戶端可以查詢長時間運行操作的進度，並決定是使用中間回應繼續代理 (agent) 運行 (以更新進度)，還是等待檢索到最終回應。代理 (agent) 客戶端應將中間或最終回應發送回代理 (agent) 以進行下一次運行。

4. **框架處理：** ADK 框架管理執行。它將代理 (agent) 客戶端發送的中間或最終 `FunctionResponse` 發送給大型語言模型 (LLM)，以生成使用者友好的訊息。

### 建立工具

定義您的工具函式並使用 `LongRunningFunctionTool` 類別將其包裝：

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py:define_long_running_function"
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.LongRunningFunctionTool;
    import java.util.HashMap;
    import java.util.Map;
    
    public class ExampleLongRunningFunction {
    
      // 定義您的長時間運行函式。
      // 請求批准報銷。
      public static Map<String, Object> askForApproval(String purpose, double amount) {
        // 模擬建立工單並發送通知
        System.out.println(
            "Simulating ticket creation for purpose: " + purpose + ", amount: " + amount);
    
        // 向審批人發送帶有工單連結的通知
        Map<String, Object> result = new HashMap<>();
        result.put("status", "pending");
        result.put("approver", "Sean Zhou");
        result.put("purpose", purpose);
        result.put("amount", amount);
        result.put("ticket-id", "approval-ticket-1");
        return result;
      }
    
      public static void main(String[] args) throws NoSuchMethodException {
        // 將方法傳遞給 LongRunningFunctionTool.create
        LongRunningFunctionTool approveTool =
            LongRunningFunctionTool.create(ExampleLongRunningFunction.class, "askForApproval");
    
        // 將工具包含在代理 (agent) 中
        LlmAgent approverAgent =
            LlmAgent.builder()
                // ...
                .tools(approveTool)
                .build();
      }
    }
    ```

### 中間/最終結果更新

代理 (agent) 客戶端收到帶有長時間運行函式呼叫的事件，並檢查工單的狀態。然後代理 (agent) 客戶端可以發送中間或最終回應以更新進度。框架將此值 (即使為 None) 包裝到發送回大型語言模型 (LLM) 的 `FunctionResponse` 的內容中。

!!! Tip "僅適用於 Java ADK"

    當使用函式工具 (Function Tools) 傳遞 `ToolContext` 時，請確保以下其中一項為真：

    * 結構 (Schema) 是通過函式簽章中的 ToolContext 參數傳遞的，例如：
      ```
      @com.google.adk.tools.Annotations.Schema(name = "toolContext") ToolContext toolContext
      ```
    或

    * 以下 `-parameters` 旗標被設置到 mvn 編譯器外掛程式中

    ```
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.14.0</version> <!-- or newer -->
                <configuration>
                    <compilerArgs>
                        <arg>-parameters</arg>
                    </compilerArgs>
                </configuration>
            </plugin>
        </plugins>
    </build>
    ```
    此限制是暫時的，將會被移除。


=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py:call_reimbursement_tool"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/LongRunningFunctionExample.java:full_code"
    ```


??? "Python 完整範例：檔案處理模擬"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py"
    ```

#### 此範例的關鍵方面

* **`LongRunningFunctionTool`**：包裝所提供的方法/函式；框架處理發送產生的更新和最終返回值作為順序的 FunctionResponses。

* **代理 (agent) 指令**：指示大型語言模型 (LLM) 使用該工具並理解傳入的 FunctionResponse 流 (進度與完成) 以更新使用者。

* **最終返回**：函式返回最終的結果字典，該字典在結束的 FunctionResponse 中發送以表示完成。

## 3. 代理即工具 (Agent-as-a-Tool)

這個強大的功能允許您透過將系統中的其他代理 (agent) 作為工具來呼叫它們，從而利用它們的功能。代理即工具 (Agent-as-a-Tool) 使您能夠調用另一個代理 (agent) 來執行特定任務，從而有效地 **委派責任**。這在概念上類似於建立一個 Python 函式，該函式呼叫另一個代理 (agent) 並使用該代理 (agent) 的回應作為函式的返回值。

### 與子代理 (sub-agents) 的主要區別

區分代理即工具 (Agent-as-a-Tool) 和子代理 (Sub-Agent) 非常重要。

* **代理即工具 (Agent-as-a-Tool)：** 當代理 (agent) A 將代理 (agent) B 作為工具呼叫時 (使用代理即工具)，代理 (agent) B 的答案將 **傳回** 給代理 (agent) A，然後代理 (agent) A 會總結該答案並向使用者生成回應。代理 (agent) A 保留控制權並繼續處理未來的用戶輸入。

* **子代理 (sub-agent)：** 當代理 (agent) A 將代理 (agent) B 作為子代理呼叫時，回答使用者的責任將完全 **轉移給代理 (agent) B**。代理 (agent) A 實際上已經退出了循環。所有後續的用戶輸入都將由代理 (agent) B 回答。

### 用法

要將代理 (agent) 用作工具，請使用 AgentTool 類別包裝該代理 (agent)。

=== "Python"

    ```py
    tools=[AgentTool(agent=agent_b)]
    ```

=== "Java"

    ```java
    AgentTool.create(agent)
    ```

### 自訂

`AgentTool` 類別提供以下屬性來自訂其行為：

* **skip_summarization: bool:** 如果設置為 True，框架將 **繞過基於大型語言模型 (LLM) 的工具代理回應摘要**。當工具的回應已經格式良好且無需進一步處理時，這可能很有用。

??? "範例"

    === "Python"

        ```py
        --8<-- "examples/python/snippets/tools/function-tools/summarizer.py"
        ```
  
    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/tools/AgentToolCustomization.java:full_code"
        ```

### 運作方式

1. 當 `main_agent` 收到長文本時，其指令會告訴它對長文本使用 'summarize' 工具。
2. 框架將 'summarize' 識別為包裝 `summary_agent` 的 `AgentTool`。
3. 在幕後，`main_agent` 將以長文本作為輸入呼叫 `summary_agent`。
4. `summary_agent` 將根據其指令處理文本並生成摘要。
5. **`summary_agent` 的回應然後會傳回給 `main_agent`。**
6. `main_agent` 然後可以獲取摘要並向使用者制定其最終回應 (例如，「這是文本的摘要：...」)