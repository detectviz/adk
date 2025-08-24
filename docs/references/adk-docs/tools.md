# 工具

## 什麼是工具？

在 ADK 的上下文中，工具代表提供給 AI 代理程式的特定功能，使其能夠執行動作並與其核心文字生成和推理能力之外的世界互動。有能力的代理程式與基本語言模型的區別通常在於它們對工具的有效使用。

從技術上講，工具通常是一個模組化的程式碼元件——**就像一個 Python/Java 函式**、一個類別方法，甚至另一個專門的代理程式——旨在執行一個獨特的、預先定義的任務。這些任務通常涉及與外部系統或資料的互動。

<img src="../assets/agent-tool-call.png" alt="代理程式工具呼叫">

### 主要特性

**以行動為導向：** 工具執行特定的動作，例如：

* 查詢資料庫
* 發出 API 請求（例如，擷取天氣資料、預訂系統）
* 搜尋網路
* 執行程式碼片段
* 從文件中擷取資訊 (RAG)
* 與其他軟體或服務互動

**擴充代理程式能力：** 它們使代理程式能夠存取即時資訊、影響外部系統，並克服其訓練資料中固有的知識限制。

**執行預先定義的邏輯：** 至關重要的是，工具執行特定的、由開發人員定義的邏輯。它們不具備像代理程式核心大型語言模型 (LLM) 那樣的獨立推理能力。LLM 會推理要使用哪個工具、何時使用以及使用什麼輸入，但工具本身只會執行其指定的函式。

## 代理程式如何使用工具

代理程式透過通常涉及函式呼叫的機制動態地利用工具。該過程通常遵循以下步驟：

1. **推理：** 代理程式的 LLM 分析其系統指令、對話歷史和使用者請求。
2. **選擇：** 根據分析，LLM 根據可用的工具和描述每個工具的文件字串，決定要執行哪個工具（如果有的話）。
3. **調用：** LLM 為所選工具產生必要的參數（輸入）並觸發其執行。
4. **觀察：** 代理程式接收工具傳回的輸出（結果）。
5. **定案：** 代理程式將工具的輸出整合到其正在進行的推理過程中，以制定下一個回應、決定後續步驟或確定目標是否已達成。

將工具視為一個專門的工具包，代理程式的智慧核心 (LLM) 可以根據需要存取和利用它來完成複雜的任務。

## ADK 中的工具類型

ADK 透過支援多種類型的工具提供靈活性：

1. **[函式工具](tools-function-tools.md)：** 由您建立的工具，根據您特定應用程式的需求量身訂做。
    * **[函式/方法](../tools/function-tools.md#1-function-tool)：** 在您的程式碼中定義標準的同步函式或方法（例如，Python def）。
    * **[代理程式即工具](../tools/function-tools.md#3-agent-as-a-tool)：** 使用另一個可能更專業的代理程式作為父代理程式的工具。
    * **[長時間執行的函式工具](../tools/function-tools.md#2-long-running-function-tool)：** 支援執行非同步操作或需要大量時間才能完成的工具。
2. **[內建工具](tools-built-in-tools.md)：** 框架為常見任務提供的現成工具。
        範例：Google 搜尋、程式碼執行、檢索增強生成 (RAG)。
3. **[第三方工具](tools-third-party-tools.md)：** 從流行的外部函式庫無縫整合工具。
        範例：LangChain 工具、CrewAI 工具。

導覽至上面連結的各自文件頁面，以取得每種工具類型的詳細資訊和範例。

## 在代理程式的指令中引用工具

在代理程式的指令中，您可以使用其**函式名稱**直接引用工具。如果工具的**函式名稱**和**文件字串**足夠具有描述性，您的指令可以主要專注於**大型語言模型 (LLM) 應何時利用該工具**。這可以提高清晰度，並幫助模型理解每個工具的預期用途。

**清楚地指示代理程式如何處理工具可能產生的不同傳回值至關重要**。例如，如果工具傳回錯誤訊息，您的指令應指定代理程式是應該重試操作、放棄任務，還是向使用者請求更多資訊。

此外，ADK 支援工具的循序使用，其中一個工具的輸出可以作為另一個工具的輸入。在實作此類工作流程時，在代理程式的指令中**描述預期的工具使用順序**以引導模型完成必要的步驟非常重要。

### 範例

以下範例展示了代理程式如何透過**在其指令中引用其函式名稱**來使用工具。它還示範了如何引導代理程式**處理來自工具的不同傳回值**，例如成功或錯誤訊息，以及如何協調**多個工具的循序使用**以完成任務。

=== "Python"

    ```python
    --8<-- "examples/python/snippets/tools/overview/weather_sentiment.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/WeatherSentimentAgentApp.java:full_code"
    ```

## 工具上下文

對於更進階的場景，ADK 允許您透過包含特殊參數 `tool_context: ToolContext` 在您的工具函式中存取額外的上下文資訊。透過在函式簽章中包含此參數，ADK 將在代理程式執行期間呼叫您的工具時**自動**提供 **ToolContext** 類別的實例。

**ToolContext** 提供對幾個關鍵資訊和控制槓桿的存取：

* `state: State`：讀取和修改目前會話的狀態。此處所做的變更會被追蹤並持久化。

* `actions: EventActions`：影響代理程式在工具執行後的後續動作（例如，跳過摘要、轉移到另一個代理程式）。

* `function_call_id: str`：框架指派給此工具特定調用的唯一識別碼。可用於追蹤和與驗證回應關聯。當在單一模型回應中呼叫多個工具時，這也很有用。

* `function_call_event_id: str`：此屬性提供觸發目前工具呼叫的**事件**的唯一識別碼。這對於追蹤和記錄目的很有用。

* `auth_response: Any`：如果在此工具呼叫之前已完成驗證流程，則包含驗證回應/憑證（常見於 RestApiTool 和 OpenAPI 安全方案）。

* 存取服務：與設定的服務（如 Artifacts 和 Memory）互動的方法。

請注意，您不應在工具函式文件字串中包含 `tool_context` 參數。由於 `ToolContext` 是在 LLM 決定呼叫工具函式*之後*由 ADK 框架自動注入的，因此它與 LLM 的決策無關，包含它可能會使 LLM 感到困惑。

### **狀態管理**

`tool_context.state` 屬性提供對與目前會話相關的狀態的直接讀寫存取權。它的行為類似於字典，但可確保任何修改都被追蹤為差異並由會話服務持久化。這使工具能夠在不同的互動和代理程式步驟之間維護和共享資訊。

* **讀取狀態**：使用標準的字典存取 (`tool_context.state['my_key']`) 或 `.get()` 方法 (`tool_context.state.get('my_key', default_value)`)。

* **寫入狀態**：直接指派值 (`tool_context.state['new_key'] = 'new_value'`)。這些變更會記錄在結果事件的 state_delta 中。

* **狀態前綴**：請記住標準的狀態前綴：

    * `app:*`：在應用程式的所有使用者之間共享。

    * `user:*`：特定於目前使用者在其所有會話中。

    * (無前綴)：特定於目前會話。

    * `temp:*`：臨時的，不會在調用之間持久化（可用於在單次執行呼叫中傳遞資料，但在工具上下文中通常較少使用，因為它在 LLM 呼叫之間運作）。

=== "Python"

    ```python
    --8<-- "examples/python/snippets/tools/overview/user_preference.py"
    ```

=== "Java"

    ```java
    import com.google.adk.tools.FunctionTool;
    import com.google.adk.tools.ToolContext;

    // 更新使用者特定的偏好設定。
    public Map<String, String> updateUserThemePreference(String value, ToolContext toolContext) {
      String userPrefsKey = "user:preferences:theme";
  
      // 取得目前的偏好設定，如果不存在則初始化
      String preference = toolContext.state().getOrDefault(userPrefsKey, "").toString();
      if (preference.isEmpty()) {
        preference = value;
      }
  
      // 將更新後的字典寫回狀態
      toolContext.state().put("user:preferences", preference);
      System.out.printf("工具：已將使用者偏好 %s 更新為 %s", userPrefsKey, preference);
  
      return Map.of("status", "success", "updated_preference", toolContext.state().get(userPrefsKey).toString());
      // 當 LLM 呼叫 updateUserThemePreference("dark") 時：
      // toolContext.state 將會更新，且變更將成為
      // 結果工具回應事件的 actions.stateDelta 的一部分。
    }
    ```

### **控制代理程式流程**

`tool_context.actions` 屬性（在 Java 中為 `ToolContext.actions()`）持有一個 **EventActions** 物件。修改此物件上的屬性可讓您的工具影響代理程式或框架在工具完成執行後的行為。

* **`skip_summarization: bool`**：（預設值：False）如果設定為 True，則指示 ADK 繞過通常會摘要工具輸出的 LLM 呼叫。如果您的工具的傳回值已經是使用者可直接使用的訊息，這會很有用。

* **`transfer_to_agent: str`**：將此設定為另一個代理程式的名稱。框架將停止目前代理程式的執行，並將**對話的控制權轉移給指定的代理程式**。這允許工具動態地將任務移交給更專業的代理程式。

* **`escalate: bool`**：（預設值：False）將此設定為 True 表示目前代理程式無法處理請求，應將控制權傳遞給其父代理程式（如果在階層結構中）。在 LoopAgent 中，在子代理程式的工具中設定 **escalate=True** 將終止迴圈。

#### 範例

=== "Python"

    ```python
    --8<-- "examples/python/snippets/tools/overview/customer_support_agent.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CustomerSupportAgentApp.java:full_code"
    ```

##### 說明

*我們定義了兩個代理程式：`main_agent` 和 `support_agent`。`main_agent` 被設計為初始的接觸點。
* 當 `main_agent` 呼叫 `check_and_transfer` 工具時，它會檢查使用者的查詢。
* 如果查詢包含「urgent」一詞，該工具會存取 `tool_context`，特別是 **`tool_context.actions`**，並將 `transfer_to_agent` 屬性設定為 `support_agent`。
* 此動作會向框架發出信號，將**對話的控制權轉移給名為 `support_agent` 的代理程式**。
* 當 `main_agent` 處理緊急查詢時，`check_and_transfer` 工具會觸發轉移。後續的回應理想上會來自 `support_agent`。
* 對於沒有緊急性的正常查詢，該工具只會處理它而不會觸發轉移。

此範例說明了工具如何透過其 ToolContext 中的 EventActions，藉由將控制權轉移給另一個專門的代理程式來動態影響對話的流程。

### **驗證**

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前適用於 Python。Java 支援正在計劃/即將推出。"}

ToolContext 提供了與經過驗證的 API 互動的工具的機制。如果您的工具需要處理驗證，您可能會使用以下方法：

* **`auth_response`**：如果驗證已在您的工具被呼叫之前由框架處理（常見於 RestApiTool 和 OpenAPI 安全方案），則包含憑證（例如，權杖）。

* **`request_credential(auth_config: dict)`**：如果您的工具確定需要驗證但憑證不可用，請呼叫此方法。這會向框架發出信號，根據提供的 auth_config 啟動驗證流程。

* **`get_auth_response()`**：在後續的調用中（在成功處理 request_credential 之後）呼叫此方法，以檢索使用者提供的憑證。

有關驗證流程、設定和範例的詳細說明，請參閱專門的工具驗證文件頁面。

### **上下文感知資料存取方法**

這些方法為您的工具提供了方便的方式，可以與與會話或使用者相關的持久性資料互動，這些資料由已設定的服務管理。

* **`list_artifacts()`** (或 Java 中的 **`listArtifacts()`**)：傳回目前透過 artifact_service 為會話儲存的所有產物的檔案名稱（或鍵）列表。產物通常是使用者上傳或由工具/代理程式產生的檔案（影像、文件等）。

* **`load_artifact(filename: str)`**：透過其檔案名稱從 **artifact_service** 檢索特定的產物。您可以選擇性地指定版本；如果省略，則傳回最新版本。傳回一個包含產物資料和 mime 類型的 `google.genai.types.Part` 物件，如果找不到則傳回 None。

* **`save_artifact(filename: str, artifact: types.Part)`**：將新版本的產物儲存到 artifact_service。傳回新的版本號（從 0 開始）。

* **`search_memory(query: str)`** ![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前適用於 Python。Java 支援正在計劃/即將推出。"}

       使用已設定的 `memory_service` 查詢使用者的長期記憶。這對於從過去的互動或儲存的知識中檢索相關資訊很有用。**SearchMemoryResponse** 的結構取決於特定的記憶體服務實作，但通常包含相關的文字片段或對話摘錄。

#### 範例

=== "Python"

    ```python
    --8<-- "examples/python/snippets/tools/overview/doc_analysis.py"
    ```

=== "Java"

    ```java
    // 使用來自記憶體的上下文來分析文件。
    // 您也可以使用 Callback Context 或 LoadArtifacts 工具來列出、載入和儲存產物。
    public static @NonNull Maybe<ImmutableMap<String, Object>> processDocument(
        @Annotations.Schema(description = "要分析的文件名稱。") String documentName,
        @Annotations.Schema(description = "分析的查詢。") String analysisQuery,
        ToolContext toolContext) {
  
      // 1. 列出所有可用的產物
      System.out.printf(
          "正在列出所有可用的產物 %s：", toolContext.listArtifacts().blockingGet());
  
      // 2. 將產物載入到記憶體
      System.out.println("工具：正在嘗試載入產物：" + documentName);
      Part documentPart = toolContext.loadArtifact(documentName, Optional.empty()).blockingGet();
      if (documentPart == null) {
        System.out.println("工具：找不到文件 '" + documentName + "'。");
        return Maybe.just(
            ImmutableMap.<String, Object>of(
                "status", "error", "message", "找不到文件 '" + documentName + "'。"));
      }
      String documentText = documentPart.text().orElse("");
      System.out.println(
          "工具：已載入文件 '" + documentName + "' (" + documentText.length() + " 個字元)。");
  
      // 3. 執行分析 (預留位置)
      String analysisResult =
          "對 '"
              + documentName
              + "' 關於 '"
              + analysisQuery
              + " [預留位置分析結果]";
      System.out.println("工具：已執行分析。");
  
      // 4. 將分析結果儲存為新的產物
      Part analysisPart = Part.fromText(analysisResult);
      String newArtifactName = "analysis_" + documentName;
  
      toolContext.saveArtifact(newArtifactName, analysisPart);
  
      return Maybe.just(
          ImmutableMap.<String, Object>builder()
              .put("status", "success")
              .put("analysis_artifact", newArtifactName)
              .build());
    }
    // FunctionTool processDocumentTool =
    //      FunctionTool.create(ToolContextArtifactExample.class, "processDocument");
    // 在代理程式中，包含此函式工具。
    // LlmAgent agent = LlmAgent().builder().tools(processDocumentTool).build();
    ```

透過利用 **ToolContext**，開發人員可以建立更複雜且具有上下文感知的自訂工具，這些工具可以無縫地與 ADK 的架構整合，並增強其代理程式的整體功能。

## 定義有效的工具函式

當使用方法或函式作為 ADK 工具時，您定義它的方式會顯著影響代理程式正確使用它的能力。代理程式的大型語言模型 (LLM) 在很大程度上依賴函式的**名稱**、**參數（引數）**、**類型提示**和**文件字串** / **原始碼註解**來了解其目的並產生正確的呼叫。

以下是定義有效工具函式的關鍵準則：

* **函式名稱：**
    * 使用描述性的、基於動詞-名詞的名稱，清楚地表明動作（例如 `get_weather`、`searchDocuments`、`schedule_meeting`）。
    * 避免使用像 `run`、`process`、`handle_data` 這樣的通用名稱，或像 `doStuff` 這樣過於模棱兩可的名稱。即使有很好的描述，像 `do_stuff` 這樣的名稱也可能會讓模型混淆何時使用該工具，而不是例如 `cancelFlight`。
    * LLM 在工具選擇期間使用函式名稱作為主要識別碼。

* **參數（引數）：**
    * 您的函式可以有任意數量的參數。
    * 使用清晰且具描述性的名稱（例如 `city` 而不是 `c`，`search_query` 而不是 `q`）。
    * **在 Python 中為所有參數提供類型提示**（例如 `city: str`、`user_id: int`、`items: list[str]`）。這對於 ADK 為 LLM 產生正確的結構描述至關重要。
    * 確保所有參數類型都是 **JSON 可序列化的**。所有 java 基本類型以及標準 Python 類型，如 `str`、`int`、`float`、`bool`、`list`、`dict` 及其組合通常是安全的。避免將複雜的自訂類別實例作為直接參數，除非它們有清晰的 JSON 表示。
    * **不要為參數設定預設值**。例如 `def my_func(param1: str = "default")`。在函式呼叫產生期間，底層模型不支援或不穩定地使用預設值。所有必要的資訊都應由 LLM 從上下文中推導出來，如果缺少則明確要求。
    * **`self` / `cls` 自動處理：** 像 `self`（用於實例方法）或 `cls`（用於類別方法）這樣的隱含參數會由 ADK 自動處理，並從顯示給 LLM 的結構描述中排除。您只需要為您的工具要求 LLM 提供的邏輯參數定義類型提示和描述。

* **傳回類型：**
    * 函式的傳回值**必須是** Python 中的**字典 (`dict`)** 或 Java 中的 **Map**。
    * 如果您的函式傳回非字典類型（例如，字串、數字、列表），ADK 框架會自動將其包裝成一個像 `{'result': your_original_return_value}` 這樣的字典/Map，然後再將結果傳回給模型。
    * 設計字典/Map 的鍵和值，使其**具描述性且易於 *LLM* 理解**。請記住，模型會讀取此輸出來決定其下一步。
    * 包含有意義的鍵。例如，不要只傳回像 `500` 這樣的錯誤代碼，而是傳回 `{'status': 'error', 'error_message': '資料庫連線失敗'}`。
    * **強烈建議**包含一個 `status` 鍵（例如 `'success'`、`'error'`、`'pending'`、`'ambiguous'`），以清楚地向模型指示工具執行的結果。

* **文件字串/原始碼註解：**
    * **這至關重要。** 文件字串是 LLM 的主要描述性資訊來源。
    * **清楚地說明工具*做什麼*。** 具體說明其目的和限制。
    * **解釋*何時*應該使用該工具。** 提供上下文或範例場景來引導 LLM 的決策。
    * **清楚地描述*每個參數*。** 解釋 LLM 需要為該參數提供什麼資訊。
    * 描述預期 `dict` 傳回值的**結構和含義**，特別是不同的 `status` 值和相關的資料鍵。
    * **不要描述注入的 ToolContext 參數**。避免在文件字串描述中提及可選的 `tool_context: ToolContext` 參數，因為它不是 LLM 需要知道的參數。ToolContext 是在 LLM 決定呼叫它*之後*由 ADK 注入的。

    **良好定義的範例：**

=== "Python"
    
    ```python
    def lookup_order_status(order_id: str) -> dict:
      """使用其 ID 擷取客戶訂單的目前狀態。

      僅當使用者明確詢問特定訂單的狀態並提供訂單 ID 時才使用此工具。請勿用於一般查詢。

      Args:
          order_id: 要查詢的訂單的唯一識別碼。

      Returns:
          一個包含訂單狀態的字典。
          可能的狀態：'shipped'、'processing'、'pending'、'error'。
          成功範例：{'status': 'shipped', 'tracking_number': '1Z9...'}
          錯誤範例：{'status': 'error', 'error_message': '找不到訂單 ID。'}
      """
      # ... 用於擷取狀態的函式實作 ...
      if status := fetch_status_from_backend(order_id):
           return {"status": status.state, "tracking_number": status.tracking} # 範例結構
      else:
           return {"status": "error", "error_message": f"找不到訂單 ID {order_id}。"}

    ```

=== "Java"

    ```java
    /**
     * 擷取指定城市目前的氣象報告。
     *
     * @param city 要擷取氣象報告的城市。
     * @param toolContext 工具的上下文。
     * @return 一個包含天氣資訊的字典。
     */
    public static Map<String, Object> getWeatherReport(String city, ToolContext toolContext) {
        Map<String, Object> response = new HashMap<>();
        if (city.toLowerCase(Locale.ROOT).equals("london")) {
            response.put("status", "success");
            response.put(
                    "report",
                    "倫敦目前的天氣是多雲，溫度為攝氏 18 度，有降雨機率。");
        } else if (city.toLowerCase(Locale.ROOT).equals("paris")) {
            response.put("status", "success");
            response.put("report", "巴黎的天氣是晴天，溫度為攝氏 25 度。");
        } else {
            response.put("status", "error");
            response.put("error_message", String.format("無法取得 '%s' 的天氣資訊。", city));
        }
        return response;
    }
    ```

* **簡單性和專注性：**
    * **保持工具專注：** 每個工具理想上應執行一個定義明確的任務。
    * **參數越少越好：** 模型通常能更可靠地處理參數較少、定義明確的工具，而不是那些有許多可選或複雜參數的工具。
    * **使用簡單的資料類型：** 盡可能優先使用基本類型（Python 中的 `str`、`int`、`bool`、`float`、`List[str]`，或 Java 中的 `int`、`byte`、`short`、`long`、`float`、`double`、`boolean` 和 `char`），而不是複雜的自訂類別或深度巢狀的結構作為參數。
    * **分解複雜任務：** 將執行多個不同邏輯步驟的函式分解為更小、更專注的工具。例如，不要使用單一的 `update_user_profile(profile: ProfileObject)` 工具，而是考慮使用像 `update_user_name(name: str)`、`update_user_address(address: str)`、`update_user_preferences(preferences: list[str])` 等單獨的工具。這使得 LLM 更容易選擇和使用正確的功能。

透過遵守這些準則，您可以為 LLM 提供有效利用您的自訂函式工具所需的清晰度和結構，從而實現更有能力和更可靠的代理程式行為。

## 工具集：分組和動態提供工具 ![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前適用於 Python。Java 支援正在計劃/即將推出。"}

除了個別工具之外，ADK 還透過 `BaseToolset` 介面（定義於 `google.adk.tools.base_toolset`）引入了**工具集**的概念。工具集允許您管理並向代理程式提供 `BaseTool` 實例的集合，通常是動態的。

這種方法有益於：

*   **組織相關工具：** 將用於共同目的的工具分組（例如，所有用於數學運算的工具，或所有與特定 API 互動的工具）。
*   **動態工具可用性：** 使代理程式能夠根據目前的上下文（例如，使用者權限、會話狀態或其他執行階段條件）擁有不同的可用工具。工具集的 `get_tools` 方法可以決定要公開哪些工具。
*   **整合外部工具提供者：** 工具集可以充當來自外部系統（如 OpenAPI 規格或 MCP 伺服器）的工具的適配器，將它們轉換為與 ADK 相容的 `BaseTool` 物件。

### `BaseToolset` 介面

在 ADK 中充當工具集的任何類別都應實作 `BaseToolset` 抽象基礎類別。此介面主要定義了兩種方法：

*   **`async def get_tools(...) -> list[BaseTool]:`**
    這是工具集的核心方法。當 ADK 代理程式需要知道其可用工具時，它將對其 `tools` 列表中提供的每個 `BaseToolset` 實例呼叫 `get_tools()`。
    *   它接收一個可選的 `readonly_context`（`ReadonlyContext` 的實例）。此上下文提供對目前會話狀態 (`readonly_context.state`)、代理程式名稱和調用 ID 等資訊的唯讀存取。工具集可以使用此上下文來動態決定要傳回哪些工具。
    *   它**必須**傳回一個 `BaseTool` 實例的 `list`（例如，`FunctionTool`、`RestApiTool`）。

*   **`async def close(self) -> None:`**
    當不再需要工具集時（例如，當代理程式伺服器正在關閉或 `Runner` 正在關閉時），ADK 框架會呼叫此非同步方法。實作此方法以執行任何必要的清理，例如關閉網路連線、釋放檔案控制代碼或清理工具集管理的其他資源。

### 將工具集與代理程式一起使用

您可以將 `BaseToolset` 實作的實例直接包含在 `LlmAgent` 的 `tools` 列表中，與個別的 `BaseTool` 實例並列。

當代理程式初始化或需要確定其可用功能時，ADK 框架將迭代 `tools` 列表：

*   如果項目是 `BaseTool` 實例，則直接使用。
*   如果項目是 `BaseToolset` 實例，則呼叫其 `get_tools()` 方法（使用目前的 `ReadonlyContext`），並將傳回的 `BaseTool` 列表新增到代理程式的可用工具中。

### 範例：一個簡單的數學工具集

讓我們建立一個提供簡單算術運算的工具集的基本範例。

```python
--8<-- "examples/python/snippets/tools/overview/toolset_example.py:init"
```

在此範例中：

*   `SimpleMathToolset` 實作了 `BaseToolset`，其 `get_tools()` 方法傳回 `add_numbers` 和 `subtract_numbers` 的 `FunctionTool` 實例。它還使用前綴自訂了它們的名稱。
*   `calculator_agent` 設定了單獨的 `greet_tool` 和 `SimpleMathToolset` 的實例。
*   當執行 `calculator_agent` 時，ADK 將呼叫 `math_toolset_instance.get_tools()`。然後，代理程式的 LLM 將可以存取 `greet_user`、`calculator_add_numbers` 和 `calculator_subtract_numbers` 來處理使用者請求。
*   `add_numbers` 工具示範了寫入 `tool_context.state`，代理程式的指令提到了讀取此狀態。
*   呼叫 `close()` 方法以確保釋放工具集持有的任何資源。

工具集提供了一種強大的方式來組織、管理和動態地向您的 ADK 代理程式提供工具集合，從而實現更模組化、可維護和適應性更強的代理程式應用程式。
