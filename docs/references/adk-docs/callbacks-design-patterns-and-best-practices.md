# 回呼的設計模式與最佳實務

回呼提供了強大的掛鉤來介入代理生命週期。以下是說明如何在 ADK 中有效利用它們的常見設計模式，以及實作的最佳實務。

## 設計模式

這些模式示範了使用回呼來增強或控制代理行為的典型方法：

### 1. 護欄與政策強制執行

* **模式：** 在請求到達 LLM 或工具之前攔截它們以強制執行規則。
* **方法：** 使用 `before_model_callback` 檢查 `LlmRequest` 提示，或使用 `before_tool_callback` 檢查工具引數。如果偵測到違反政策 (例如，禁止的主題、不雅用語)，則傳回預先定義的回應 (`LlmResponse` 或 `dict`/ `Map`) 以阻止操作，並可選擇性地更新 `context.state` 以記錄違規行為。
* **範例：** `before_model_callback` 檢查 `llm_request.contents` 中是否有敏感關鍵字，如果找到，則傳回標準的「無法處理此請求」`LlmResponse`，從而阻止 LLM 呼叫。

### 2. 動態狀態管理

* **模式：** 在回呼中讀取和寫入工作階段狀態，以使代理行為具有上下文感知能力，並在步驟之間傳遞資料。
* **方法：** 存取 `callback_context.state` 或 `tool_context.state`。修改 (`state['key'] = value`) 會在後續的 `Event.actions.state_delta` 中自動追蹤，以供 `SessionService` 持續化。
* **範例：** `after_tool_callback` 將工具結果中的 `transaction_id` 儲存到 `tool_context.state['last_transaction_id']`。稍後的 `before_agent_callback` 可能會讀取 `state['user_tier']` 以自訂代理的問候語。

### 3. 記錄與監控

* **模式：** 在特定的生命週期點新增詳細的記錄，以進行可觀測性和除錯。
* **方法：** 實作回呼 (例如 `before_agent_callback`、`after_tool_callback`、`after_model_callback`) 來列印或傳送包含代理名稱、工具名稱、調用 ID 以及來自上下文或引數的相關資料的結構化記錄。
* **範例：** 記錄訊息，例如 `INFO: [Invocation: e-123] Before Tool: search_api - Args: {'query': 'ADK'}`。

### 4. 快取

* **模式：** 透過快取結果來避免多餘的 LLM 呼叫或工具執行。
* **方法：** 在 `before_model_callback` 或 `before_tool_callback` 中，根據請求/引數產生一個快取鍵。檢查 `context.state` (或外部快取) 中是否有此鍵。如果找到，則直接傳回快取的 `LlmResponse` 或結果，略過實際操作。如果找不到，則允許操作繼續，並使用對應的 `after_` 回呼 (`after_model_callback`、`after_tool_callback`) 將新結果使用該鍵儲存到快取中。
*   **範例：** `get_stock_price(symbol)` 的 `before_tool_callback` 檢查 `state[f"cache:stock:{symbol}"]`。如果存在，則傳回快取的價格；否則，允許 API 呼叫，`after_tool_callback` 會將結果儲存到狀態鍵中。

### 5. 請求/回應修改

* **模式：** 在將資料傳送給 LLM/工具之前或收到資料之後修改資料。
* **方法：**
    * `before_model_callback`：修改 `llm_request` (例如，根據 `state` 新增系統指令)。
    * `after_model_callback`：修改傳回的 `LlmResponse` (例如，格式化文字、過濾內容)。
    *  `before_tool_callback`：修改工具 `args` 字典 (或 Java 中的 Map)。
    *  `after_tool_callback`：修改 `tool_response` 字典 (或 Java 中的 Map)。
* **範例：** 如果 `context.state['lang'] == 'es'`，`before_model_callback` 會將「使用者語言偏好：西班牙語」附加到 `llm_request.config.system_instruction`。

### 6. 條件式略過步驟

* **模式：** 根據某些條件阻止標準操作 (代理執行、LLM 呼叫、工具執行)。
* **方法：** 從 `before_` 回呼傳回一個值 (`before_agent_callback` 的 `Content`、`before_model_callback` 的 `LlmResponse`、`before_tool_callback` 的 `dict`)。框架會將此傳回值解譯為該步驟的結果，從而略過正常執行。
* **範例：** `before_tool_callback` 檢查 `tool_context.state['api_quota_exceeded']`。如果為 `True`，它會傳回 `{'error': 'API 配額已超出'}`，從而阻止實際的工具函式執行。

### 7. 特定於工具的動作 (身份驗證和摘要控制)

* **模式：** 處理特定於工具生命週期的動作，主要是身份驗證和控制工具結果的 LLM 摘要。
* **方法：** 在工具回呼 (`before_tool_callback`、`after_tool_callback`) 中使用 `ToolContext`。
    * **身份驗證：** 如果需要但找不到憑證 (例如，透過 `tool_context.get_auth_response` 或狀態檢查)，請在 `before_tool_callback` 中呼叫 `tool_context.request_credential(auth_config)`。這會啟動身份驗證流程。
    * **摘要：** 如果工具的原始字典輸出應直接傳回給 LLM 或可能直接顯示，繞過預設的 LLM 摘要步驟，請設定 `tool_context.actions.skip_summarization = True`。
* **範例：** 一個安全 API 的 `before_tool_callback` 會在狀態中檢查身份驗證權杖；如果遺失，它會呼叫 `request_credential`。一個傳回結構化 JSON 的工具的 `after_tool_callback` 可能會設定 `skip_summarization = True`。

### 8. 產物處理

* **模式：** 在代理生命週期中儲存或載入與工作階段相關的檔案或大型資料 blob。
* **方法：** 使用 `callback_context.save_artifact` / `await tool_context.save_artifact` 儲存資料 (例如，產生的報告、記錄、中間資料)。使用 `load_artifact` 擷取先前儲存的產物。變更是透過 `Event.actions.artifact_delta` 追蹤的。
* **範例：** 一個「generate_report」工具的 `after_tool_callback` 使用 `await tool_context.save_artifact("report.pdf", report_part)` 儲存輸出檔案。`before_agent_callback` 可能會使用 `callback_context.load_artifact("agent_config.json")` 載入組態產物。

## 回呼的最佳實務

* **保持專注：** 為每個回呼設計一個單一、明確定義的目的 (例如，僅記錄、僅驗證)。避免單體式回呼。
* **注意效能：** 回呼在代理的處理循環中同步執行。避免長時間執行或阻塞操作 (網路呼叫、大量計算)。如有必要，請將其卸載，但請注意這會增加複雜性。
* **優雅地處理錯誤：** 在您的回呼函式中使用 `try...except/ catch` 區塊。適當地記錄錯誤，並決定代理調用應停止還是嘗試復原。不要讓回呼錯誤導致整個流程崩潰。
* **仔細管理狀態：**
    * 謹慎地從 `context.state` 讀取和寫入。變更在*目前*調用中立即可見，並在事件處理結束時持續化。
    * 使用特定的狀態鍵，而不是修改廣泛的結構，以避免意外的副作用。
    *  考慮使用狀態前置詞 (`State.APP_PREFIX`、`State.USER_PREFIX`、`State.TEMP_PREFIX`) 以求清晰，特別是對於持續性的 `SessionService` 實作。
* **考慮冪等性：** 如果回呼執行具有外部副作用的動作 (例如，遞增外部計數器)，請盡可能將其設計為冪等的 (可以安全地使用相同的輸入執行多次)，以處理框架或您的應用程式中可能的重試。
* **徹底測試：** 使用模擬上下文物件對您的回呼函式進行單元測試。執行整合測試以確保回呼在完整的代理流程中正常運作。
* **確保清晰度：** 為您的回呼函式使用描述性名稱。新增清晰的說明文件，解釋其目的、執行時間以及任何副作用 (特別是狀態修改)。
* **使用正確的上下文類型：** 始終使用提供的特定上下文類型 (`CallbackContext` 用於代理/模型，`ToolContext` 用於工具)，以確保可以存取適當的方法和屬性。

透過應用這些模式和最佳實務，您可以有效地使用回呼來在 ADK 中建立更穩健、可觀測和自訂的代理行為。