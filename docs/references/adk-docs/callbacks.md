# 回呼：觀察、自訂和控制代理行為

## 簡介：什麼是回呼以及為何使用它們？

回呼是 ADK 的一個基石功能，提供了一個強大的機制來掛鉤到代理的執行流程中。它們允許您在特定的、預先定義的點觀察、自訂甚至控制代理的行為，而無需修改核心 ADK 框架程式碼。

**它們是什麼？** 實質上，回呼是您定義的標準函式。然後，您在建立代理時將這些函式與代理關聯起來。ADK 框架會在關鍵階段自動呼叫您的函式，讓您觀察或介入。可以把它想像成代理流程中的檢查點：

* **在代理開始處理請求的主要工作之前，以及在它完成之後：** 當您要求代理做某事 (例如，回答一個問題) 時，它會執行其內部邏輯來找出回應。
  * `Before Agent` 回呼在該特定請求的主要工作開始*之前*執行。
  * `After Agent` 回呼在代理完成該請求的所有步驟並準備好最終結果之後，但在傳回結果之前*執行*。
  * 這個「主要工作」涵蓋了代理處理該單一請求的*整個*過程。這可能涉及決定呼叫 LLM、實際呼叫 LLM、決定使用工具、使用工具、處理結果，最後組合答案。這些回呼基本上包裝了從接收輸入到為該次互動產生最終輸出的整個序列。
* **在向大型語言模型 (LLM) 傳送請求之前，或在收到其回應之後：** 這些回呼 (`Before Model`、`After Model`) 允許您專門檢查或修改進出 LLM 的資料。
* **在執行工具 (如 Python 函式或其他代理) 之前或之後：** 同樣，`Before Tool` 和 `After Tool` 回呼專門在代理呼叫的工具執行周圍提供控制點。


![intro_components.png](../assets/callback_flow.png)

**為何使用它們？** 回呼釋放了顯著的 flexibility 並啟用了進階的代理功能：

* **觀察與除錯：** 在關鍵步驟記錄詳細資訊，以進行監控和疑難排解。
* **自訂與控制：** 修改流經代理的資料 (如 LLM 請求或工具結果)，甚至根據您的邏輯完全略過某些步驟。
* **實作護欄：** 強制執行安全規則、驗證輸入/輸出或防止不允許的操作。
* **管理狀態：** 在執行期間讀取或動態更新代理的工作階段狀態。
* **整合與增強：** 觸發外部動作 (API 呼叫、通知) 或新增快取等功能。

**如何新增它們：**

??? "程式碼"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/callback_basic.py:callback_basic"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AgentWithBeforeModelCallback.java:init"
        ```

## 回呼機制：攔截與控制

當 ADK 框架遇到可以執行回呼的點時 (例如，在呼叫 LLM 之前)，它會檢查您是否為該代理提供了對應的回呼函式。如果您提供了，框架就會執行您的函式。

**上下文是關鍵：** 您的回呼函式不是孤立呼叫的。框架會提供特殊的**上下文物件** (`CallbackContext` 或 `ToolContext`) 作為引數。這些物件包含有關代理執行的目前狀態的重要資訊，包括調用詳細資訊、會話狀態以及對產物或記憶體等服務的潛在引用。您可以使用這些上下文物件來了解情況並與框架互動。(有關完整詳細資訊，請參閱專門的「上下文物件」部分)。

**控制流程 (核心機制)：** 回呼最強大的方面在於其**傳回值**如何影響代理的後續操作。這就是您攔截和控制執行流程的方式：

1. **`return None` (允許預設行為)：**

    * 特定的傳回類型可能會因語言而異。在 Java 中，等效的傳回類型是 `Optional.empty()`。有關特定語言的指導，請參閱 API 文件。
    * 這是表示您的回呼已完成其工作 (例如，記錄、檢查、對*可變*輸入引數 (如 `llm_request`) 進行微小修改) 並且 ADK 代理應**繼續其正常操作**的標準方式。
    * 對於 `before_*` 回呼 (`before_agent`、`before_model`、`before_tool`)，傳回 `None` 表示序列中的下一步 (執行代理邏輯、呼叫 LLM、執行工具) 將會發生。
    * 對於 `after_*` 回呼 (`after_agent`、`after_model`、`after_tool`)，傳回 `None` 表示剛由前一步驟產生的結果 (代理的輸出、LLM 的回應、工具的結果) 將按原樣使用。

2. **`return <Specific Object>` (覆寫預設行為)：**

    * 傳回一個*特定類型的物件* (而不是 `None`) 是您**覆寫** ADK 代理預設行為的方式。框架將使用您傳回的物件並*略過*通常會執行的下一步驟或*取代*剛產生的結果。
    * **`before_agent_callback` → `types.Content`**：略過代理的主要執行邏輯 (`_run_async_impl` / `_run_live_impl`)。傳回的 `Content` 物件會立即被視為代理在此回合的最終輸出。對於直接處理簡單請求或強制執行存取控制很有用。
    * **`before_model_callback` → `LlmResponse`**：略過對外部大型語言模型的呼叫。傳回的 `LlmResponse` 物件會被處理，就好像它是來自 LLM 的實際回應一樣。非常適合實作輸入護欄、提示驗證或提供快取的回應。
    * **`before_tool_callback` → `dict` 或 `Map`**：略過實際工具函式 (或子代理) 的執行。傳回的 `dict` 會被用作工具呼叫的結果，然後通常會傳回給 LLM。非常適合驗證工具引數、應用程式原則限制或傳回模擬/快取的工具結果。
    * **`after_agent_callback` → `types.Content`**：*取代*代理的執行邏輯剛產生的 `Content`。
    * **`after_model_callback` → `LlmResponse`**：*取代*從 LLM 收到的 `LlmResponse`。對於清理輸出、新增標準免責聲明或修改 LLM 的回應結構很有用。
    * **`after_tool_callback` → `dict` 或 `Map`**：*取代*工具傳回的 `dict` 結果。允許在將工具輸出傳回給 LLM 之前對其進行後處理或標準化。

**概念程式碼範例 (護欄)：**

此範例示範了使用 `before_model_callback` 的護欄的常見模式。

<!-- ```py
--8<-- "examples/python/snippets/callbacks/before_model_callback.py"
``` -->
??? "程式碼"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_model_callback.py"
        ```
    
    === "Java"
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeModelGuardrailExample.java:init"
        ```

透過了解這種傳回 `None` 與傳回特定物件的機制，您可以精確地控制代理的執行路徑，使回呼成為使用 ADK 建構複雜可靠代理的重要工具。
