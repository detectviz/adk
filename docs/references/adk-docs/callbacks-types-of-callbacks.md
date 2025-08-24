# 回呼的類型

框架提供了不同類型的回呼，它們在代理程式執行的不同階段觸發。了解每個回呼何時觸發以及它接收到什麼上下文，是有效使用它們的關鍵。

## 代理程式生命週期回呼

這些回呼適用於*任何*繼承自 `BaseAgent` 的代理程式 (包括 `LlmAgent`、`SequentialAgent`、`ParallelAgent`、`LoopAgent` 等)。

!!! Note
    具體的方法名稱或傳回類型可能會因 SDK 語言而略有不同 (例如，在 Python 中傳回 `None`，在 Java 中傳回 `Optional.empty()` 或 `Maybe.empty()`)。有關特定語言的指導，請參閱 API 文件。

### 代理程式前回呼

**時機：** 在代理程式的 `_run_async_impl` (或 `_run_live_impl`) 方法執行*之前立即*呼叫。它在代理程式的 `InvocationContext` 建立之後，但在其核心邏輯開始*之前*執行。

**目的：** 非常適合設定僅在此特定代理程式執行期間所需的資源或狀態，在執行開始前對會話狀態 (`callback_context.state`) 進行驗證檢查，記錄代理程式活動的進入點，或可能在核心邏輯使用它之前修改調用上下文。


??? "程式碼"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_agent_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeAgentCallbackExample.java:init"
        ```


**關於 `before_agent_callback` 範例的注意事項：**

* **展示內容：** 此範例示範了 `before_agent_callback`。此回呼在代理程式針對給定請求的主要處理邏輯開始*之前*執行。
* **運作方式：** 回呼函式 (`check_if_agent_should_run`) 會查看會話狀態中的一個旗標 (`skip_llm_agent`)。
    * 如果旗標為 `True`，回呼會傳回一個 `types.Content` 物件。這會告訴 ADK 框架完全**跳過**代理程式的主要執行，並使用回呼傳回的內容作為最終回應。
    * 如果旗標為 `False` (或未設定)，回呼會傳回 `None` 或一個空物件。這會告訴 ADK 框架**繼續**代理程式的正常執行 (在此情況下是呼叫 LLM)。
* **預期結果：** 您會看到兩種情況：
    1. 在具有 `skip_llm_agent: True` 狀態的會話中，代理程式的 LLM 呼叫會被繞過，輸出直接來自回呼 (「代理程式...已跳過...」)。
    2. 在沒有該狀態旗標的會話中，回呼允許代理程式執行，您會看到來自 LLM 的實際回應 (例如，「你好！」)。
* **了解回呼：** 這突顯了 `before_` 回呼如何充當**守門員**，讓您能夠在主要步驟*之前*攔截執行，並可能根據檢查 (如狀態、輸入驗證、權限) 來阻止它。


### 代理程式後回呼

**時機：** 在代理程式的 `_run_async_impl` (或 `_run_live_impl`) 方法成功完成*之後立即*呼叫。如果代理程式因 `before_agent_callback` 傳回內容而被跳過，或者在代理程式執行期間設定了 `end_invocation`，則*不會*執行。

**目的：** 用於清理任務、執行後驗證、記錄代理程式活動的完成、修改最終狀態，或增強/取代代理程式的最終輸出。

??? "程式碼"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/after_agent_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AfterAgentCallbackExample.java:init"
        ```


**關於 `after_agent_callback` 範例的注意事項：**

* **展示內容：** 此範例示範了 `after_agent_callback`。此回呼在代理程式的主要處理邏輯完成並產生其結果*之後*，但在該結果最終確定並傳回*之前*執行。
* **運作方式：** 回呼函式 (`modify_output_after_agent`) 會檢查會話狀態中的一個旗標 (`add_concluding_note`)。
    * 如果旗標為 `True`，回呼會傳回一個*新的* `types.Content` 物件。這會告訴 ADK 框架用回呼傳回的內容**取代**代理程式的原始輸出。
    * 如果旗標為 `False` (或未設定)，回呼會傳回 `None` 或一個空物件。這會告訴 ADK 框架**使用**代理程式產生的原始輸出。
*   **預期結果：** 您會看到兩種情況：
    1. 在沒有 `add_concluding_note: True` 狀態的會話中，回呼允許使用代理程式的原始輸出 (「處理完成！」)。
    2. 在具有該狀態旗標的會話中，回呼會攔截代理程式的原始輸出，並用其自己的訊息 (「已新增結論性說明...」) 取代它。
* **了解回呼：** 這突顯了 `after_` 回呼如何允許**後處理**或**修改**。您可以檢查一個步驟的結果 (代理程式的執行)，並根據您的邏輯決定是讓它通過、變更它，還是完全取代它。

## LLM 互動回呼

這些回呼特定於 `LlmAgent`，並在與大型語言模型互動的周圍提供掛鉤。

### 模型前回呼

**時機：** 在 `generate_content_async` (或等效) 請求在 `LlmAgent` 流程中傳送給 LLM 之前呼叫。

**目的：** 允許檢查和修改傳送給 LLM 的請求。使用案例包括新增動態指令、根據狀態注入少樣本範例、修改模型設定、實作護欄 (如不雅用語過濾器) 或實作請求層級的快取。

**傳回值效果：**
如果回呼傳回 `None` (或在 Java 中為 `Maybe.empty()` 物件)，則 LLM 會繼續其正常工作流程。如果回呼傳回一個 `LlmResponse` 物件，則對 LLM 的呼叫會被**跳過**。傳回的 `LlmResponse` 會被直接使用，就好像它來自模型一樣。這對於實作護欄或快取非常強大。

??? "程式碼"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_model_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeModelCallbackExample.java:init"
        ```

### 模型後回呼

**時機：** 在從 LLM 收到回應 (`LlmResponse`) 之後，在由調用代理程式進一步處理之前呼叫。

**目的：** 允許檢查或修改原始 LLM 回應。使用案例包括

* 記錄模型輸出，
* 重新格式化回應，
* 審查模型產生的敏感資訊，
* 從 LLM 回應中解析結構化資料並將其儲存在 `callback_context.state` 中
* 或處理特定的錯誤代碼。

??? "程式碼"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/after_model_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AfterModelCallbackExample.java:init"
        ```

## 工具執行回呼

這些回呼也特定於 `LlmAgent`，並在 LLM 可能請求的工具 (包括 `FunctionTool`、`AgentTool` 等) 執行周圍觸發。

### 工具前回呼

**時機：** 在特定工具的 `run_async` 方法被調用之前，在 LLM 為其產生函式呼叫之後呼叫。

**目的：** 允許檢查和修改工具引數、在執行前執行授權檢查、記錄工具使用嘗試或實作工具層級的快取。

**傳回值效果：**

1. 如果回呼傳回 `None` (或在 Java 中為 `Maybe.empty()` 物件)，則會使用 (可能已修改的) `args` 執行工具的 `run_async` 方法。
2. 如果傳回一個字典 (或在 Java 中為 `Map`)，則會**跳過**工具的 `run_async` 方法。傳回的字典會被直接用作工具呼叫的結果。這對於快取或覆寫工具行為很有用。


??? "程式碼"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_tool_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeToolCallbackExample.java:init"
        ```



### 工具後回呼

**時機：** 在工具的 `run_async` 方法成功完成之後呼叫。

**目的：** 允許在將工具的結果傳回給 LLM (可能在摘要之後) 之前檢查和修改它。用於記錄工具結果、後處理或格式化結果，或將結果的特定部分儲存到會話狀態。

**傳回值效果：**

1. 如果回呼傳回 `None` (或在 Java 中為 `Maybe.empty()` 物件)，則使用原始的 `tool_response`。
2. 如果傳回一個新的字典，它會**取代**原始的 `tool_response`。這允許修改或過濾 LLM 看到的結果。