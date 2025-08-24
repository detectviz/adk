# 狀態：會話的草稿紙

在每個 `Session`（我們的對話線程）中，**`state`** 屬性充當代理程式在該特定互動中的專用草稿紙。雖然 `session.events` 保存了完整的歷史記錄，但 `session.state` 是代理程式儲存和更新*在*對話期間所需的動態詳細資訊的地方，以使其有效運作。

## 什麼是 `session.state`？

從概念上講，`session.state` 是一個包含鍵值對的集合（一個字典或 Map）。它旨在儲存代理程式需要回憶或追蹤以使當前對話有效的資訊：

*   **個人化互動：** 記住使用者先前提到的偏好（例如，`'user_preference_theme': 'dark'`）。
*   **追蹤任務進度：** 記錄多輪次流程中的步驟（例如，`'booking_step': 'confirm_payment'`）。
*   **累積資訊：** 建立清單或摘要（例如，`'shopping_cart_items': ['book', 'pen']`）。
*   **做出明智的決定：** 儲存影響下一個回應的旗標或值（例如，`'user_is_authenticated': True`）。

### `State` 的主要特性

1.  **結構：可序列化的鍵值對**

    *   資料以 `key: value` 的形式儲存。
    *   **鍵 (Keys)：** 始終是字串 (`str`)。使用清晰的名稱（例如，`'departure_city'`、`'user:language_preference'`）。
    *   **值 (Values)：** 必須是**可序列化的 (serializable)**。這意味著它們可以被 `SessionService` 輕鬆地儲存和載入。請使用特定語言（Python/Java）中的基本類型，如字串、數字、布林值，以及*僅*包含這些基本類型的簡單列表或字典。（有關精確詳細資訊，請參閱 API 文件）。
    *   **⚠️ 避免複雜物件：** **不要直接在狀態中儲存不可序列化的物件**（自訂類別實例、函式、連線等）。如果需要，請儲存簡單的識別碼，並在其他地方檢索複雜的物件。

2.  **可變性：它會改變**

    *   隨著對話的進行，`state` 的內容預期會發生變化。

3.  **持久性：取決於 `SessionService`**

    *   狀態是否能在應用程式重新啟動後存留，取決於您選擇的服務：
        *   `InMemorySessionService`：**非持久性。** 狀態在重新啟動時會遺失。
        *   `DatabaseSessionService` / `VertexAiSessionService`：**持久性。** 狀態會被可靠地儲存。

!!! Note
    原始類型的特定參數或方法名稱可能會因 SDK 語言而略有不同（例如，Python 中的 `session.state['current_intent'] = 'book_flight'`，Java 中的 `session.state().put("current_intent", "book_flight")`）。有關詳細資訊，請參閱特定語言的 API 文件。

### 使用前綴組織狀態：範圍很重要

狀態鍵上的前綴定義了它們的範圍和持久性行為，尤其是在使用持久性服務時：

*   **無前綴（會話狀態）：**

    *   **範圍：** 特定於*目前*會話 (`id`)。
    *   **持久性：** 僅當 `SessionService` 是持久性的（`Database`、`VertexAI`）時才持久。
    *   **使用案例：** 追蹤目前任務中的進度（例如，`'current_booking_step'`），此互動的臨時旗標（例如，`'needs_clarification'`）。
    *   **範例：** `session.state['current_intent'] = 'book_flight'`

*   **`user:` 前綴（使用者狀態）：**

    *   **範圍：** 與 `user_id` 綁定，在該使用者（在相同的 `app_name` 中）的*所有*會話中共享。
    *   **持久性：** 使用 `Database` 或 `VertexAI` 時是持久性的。（由 `InMemory` 儲存，但在重新啟動時會遺失）。
    *   **使用案例：** 使用者偏好（例如，`'user:theme'`），個人資料詳細資訊（例如，`'user:name'`）。
    *   **範例：** `session.state['user:preferred_language'] = 'fr'`

*   **`app:` 前綴（應用程式狀態）：**

    *   **範圍：** 與 `app_name` 綁定，在該應用程式的所有使用者和會話中共享。
    *   **持久性：** 使用 `Database` 或 `VertexAI` 時是持久性的。（由 `InMemory` 儲存，但在重新啟動時會遺失）。
    *   **使用案例：** 全域設定（例如，`'app:api_endpoint'`），共享範本。
    *   **範例：** `session.state['app:global_discount_code'] = 'SAVE10'`

*   **`temp:` 前綴（臨時會話狀態）：**

    *   **範圍：** 特定於*目前*會話處理輪次。
    *   **持久性：** **絕不持久。** 保證會被丟棄，即使使用持久性服務也是如此。
    *   **使用案例：** 僅立即需要的中間結果，您明確不希望儲存的資料。
    *   **範例：** `session.state['temp:raw_api_response'] = {...}`

**代理程式如何看待它：** 您的代理程式程式碼透過單一的 `session.state` 集合（字典/Map）與*組合*的狀態互動。`SessionService` 根據前綴處理從正確的底層儲存體中擷取/合併狀態。

### 在代理程式指令中存取會話狀態

在使用 `LlmAgent` 實例時，您可以使用簡單的範本語法將會話狀態值直接注入代理程式的指令字串中。這使您可以建立動態且具有上下文感知的指令，而無需僅僅依賴自然語言指令。

#### 使用 `{key}` 範本

若要從會話狀態中注入一個值，請將所需狀態變數的鍵包含在大括號中：`{key}`。在將指令傳遞給 LLM 之前，框架會自動將此預留位置替換為 `session.state` 中的相應值。

**範例：**

```python
from google.adk.agents import LlmAgent

story_generator = LlmAgent(
    name="StoryGenerator",
    model="gemini-2.0-flash",
    instruction="""寫一個關於貓的短篇故事，主題是：{topic}。"""
)

# 假設 session.state['topic'] 被設定為 "friendship"，LLM
# 將會收到以下指令：
# "寫一個關於貓的短篇故事，主題是：friendship。"
```

#### 重要考量

* 鍵的存在性：確保您在指令字串中引用的鍵存在於 session.state 中。如果鍵遺失，代理程式可能會行為不當或引發錯誤。
* 資料類型：與鍵關聯的值應該是字串或可以輕鬆轉換為字串的類型。
* 逸出：如果您需要在指令中使用字面上的大括號（例如，用於 JSON 格式），您需要將它們逸出。

#### 使用 `InstructionProvider` 繞過狀態注入

在某些情況下，您可能希望在指令中按字面意思使用 `{{` 和 `}}`，而不觸發狀態注入機制。例如，您可能正在為一個幫助處理使用相同語法的範本語言的代理程式編寫指令。

為此，您可以向 `instruction` 參數提供一個函式，而不是一個字串。此函式稱為 `InstructionProvider`。當您使用 `InstructionProvider` 時，ADK 將不會嘗試注入狀態，您的指令字串將按原樣傳遞給模型。

`InstructionProvider` 函式會收到一個 `ReadonlyContext` 物件，如果您需要動態地建立指令，可以使用它來存取會話狀態或其他上下文資訊。

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.agents.readonly_context import ReadonlyContext

    # 這是一個 InstructionProvider
    def my_instruction_provider(context: ReadonlyContext) -> str:
        # 您可以選擇性地使用上下文來建立指令
        # 在這個範例中，我們將傳回一個帶有字面大括號的靜態字串。
        return "這是一個帶有 {{literal_braces}} 且不會被替換的指令。"

    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="template_helper_agent",
        instruction=my_instruction_provider
    )
    ```

如果您想同時使用 `InstructionProvider` *和* 將狀態注入您的指令中，您可以使用 `inject_session_state` 公用程式函式。

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.agents.readonly_context import ReadonlyContext
    from google.adk.utils import instructions_utils

    async def my_dynamic_instruction_provider(context: ReadonlyContext) -> str:
        template = "這是一個 {adjective} 的指令，帶有 {{literal_braces}}。"
        # 這將注入 'adjective' 狀態變數，但會保留字面大括號。
        return await instructions_utils.inject_session_state(template, context)

    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="dynamic_template_helper_agent",
        instruction=my_dynamic_instruction_provider
    )
    ```

**直接注入的好處**

* 清晰度：明確指出指令的哪些部分是動態的且基於會話狀態。
* 可靠性：避免依賴 LLM 正確解釋自然語言指令來存取狀態。
* 可維護性：簡化指令字串並減少更新狀態變數名稱時出錯的風險。

**與其他狀態存取方法的關係**

這種直接注入方法特定於 LlmAgent 指令。有關其他狀態存取方法的更多資訊，請參閱以下部分。

### 如何更新狀態：建議的方法

!!! note "修改狀態的正確方法"
    當您需要變更會話狀態時，正確且最安全的方法是**直接修改提供給您函式的 `Context` 上的 `state` 物件**（例如，`callback_context.state['my_key'] = 'new_value'`）。這被認為是以正確的方式進行「直接狀態操作」，因為框架會自動追蹤這些變更。

    這與直接修改您從 `SessionService` 檢索到的 `Session` 物件上的 `state`（例如，`my_session.state['my_key'] = 'new_value'`）有著根本的不同。**您應該避免這樣做**，因為它會繞過 ADK 的事件追蹤並可能導致資料遺失。本頁末尾的「警告」部分對此重要區別有更多詳細資訊。

狀態應**始終**作為使用 `session_service.append_event()` 將 `Event` 新增到會話歷史記錄的一部分進行更新。這可確保變更被追蹤，持久性正常運作，並且更新是執行緒安全的。

**1\. 簡單方法：`output_key`（用於代理程式文字回應）**

這是將代理程式的最終文字回應直接儲存到狀態中的最簡單方法。在定義您的 `LlmAgent` 時，指定 `output_key`：

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.runners import Runner
    from google.genai.types import Content, Part

    # 使用 output_key 定義代理程式
    greeting_agent = LlmAgent(
        name="Greeter",
        model="gemini-2.0-flash", # 使用一個有效的模型
        instruction="產生一個簡短、友好的問候語。",
        output_key="last_greeting" # 將回應儲存到 state['last_greeting']
    )

    # --- 設定 Runner 和 Session ---
    app_name, user_id, session_id = "state_app", "user1", "session1"
    session_service = InMemorySessionService()
    runner = Runner(
        agent=greeting_agent,
        app_name=app_name,
        session_service=session_service
    )
    session = await session_service.create_session(app_name=app_name,
                                        user_id=user_id,
                                        session_id=session_id)
    print(f"初始狀態：{session.state}")

    # --- 執行代理程式 ---
    # Runner 處理呼叫 append_event，它使用 output_key
    # 來自動建立 state_delta。
    user_message = Content(parts=[Part(text="你好")])
    for event in runner.run(user_id=user_id,
                            session_id=session_id,
                            new_message=user_message):
        if event.is_final_response():
          print(f"代理程式已回應。") # 回應文字也在 event.content 中

    # --- 檢查更新後的狀態 ---
    updated_session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    print(f"代理程式執行後的狀態：{updated_session.state}")
    # 預期輸出可能包括：{'last_greeting': '你好！今天我能為您做些什麼？'}
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/state/GreetingAgentExample.java:full_code"
    ```

在幕後，`Runner` 使用 `output_key` 來建立必要的 `EventActions`，其中包含一個 `state_delta`，並呼叫 `append_event`。

**2\. 標準方法：`EventActions.state_delta`（用於複雜更新）**

對於更複雜的場景（更新多個鍵、非字串值、特定範圍如 `user:` 或 `app:`，或與代理程式的最終文字不直接相關的更新），您可以在 `EventActions` 中手動建構 `state_delta`。

=== "Python"

    ```python
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.events import Event, EventActions
    from google.genai.types import Part, Content
    import time

    # --- 設定 ---
    session_service = InMemorySessionService()
    app_name, user_id, session_id = "state_app_manual", "user2", "session2"
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state={"user:login_count": 0, "task_status": "idle"}
    )
    print(f"初始狀態：{session.state}")

    # --- 定義狀態變更 ---
    current_time = time.time()
    state_changes = {
        "task_status": "active",              # 更新會話狀態
        "user:login_count": session.state.get("user:login_count", 0) + 1, # 更新使用者狀態
        "user:last_login_ts": current_time,   # 新增使用者狀態
        "temp:validation_needed": True        # 新增臨時狀態 (將被丟棄)
    }

    # --- 建立帶有動作的事件 ---
    actions_with_update = EventActions(state_delta=state_changes)
    # 此事件可能代表一個內部系統動作，而不僅僅是代理程式的回應
    system_event = Event(
        invocation_id="inv_login_update",
        author="system", # 或 'agent'、'tool' 等。
        actions=actions_with_update,
        timestamp=current_time
        # content 可能為 None 或代表所採取的動作
    )

    # --- 附加事件 (這會更新狀態) ---
    await session_service.append_event(session, system_event)
    print("已使用明確的狀態差異呼叫 `append_event`。")

    # --- 檢查更新後的狀態 ---
    updated_session = await session_service.get_session(app_name=app_name,
                                                user_id=user_id,
                                                session_id=session_id)
    print(f"事件後的狀態：{updated_session.state}")
    # 預期：{'user:login_count': 1, 'task_status': 'active', 'user:last_login_ts': <timestamp>}
    # 注意：'temp:validation_needed' 不存在。
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/state/ManualStateUpdateExample.java:full_code"
    ```

**3. 透過 `CallbackContext` 或 `ToolContext`（建議用於回呼和工具）**

在代理程式回呼（例如 `on_before_agent_call`、`on_after_agent_call`）或工具函式中修改狀態，最好是使用提供給您函式的 `CallbackContext` 或 `ToolContext` 的 `state` 屬性。

*   `callback_context.state['my_key'] = my_value`
*   `tool_context.state['my_key'] = my_value`

這些上下文物件專門設計用於管理其各自執行範圍內的狀態變更。當您修改 `context.state` 時，ADK 框架會確保這些變更被自動捕獲並正確地路由到由回呼或工具產生的事件的 `EventActions.state_delta` 中。然後，當事件被附加時，此差異會由 `SessionService` 處理，確保正確的持久性和追蹤。

對於回呼和工具中最常見的狀態更新場景，此方法抽象化了手動建立 `EventActions` 和 `state_delta` 的過程，使您的程式碼更乾淨且不易出錯。

有關上下文物件的更全面詳細資訊，請參閱[上下文文件](context.md)。

=== "Python"

    ```python
    # 在代理程式回呼或工具函式中
    from google.adk.agents import CallbackContext # 或 ToolContext

    def my_callback_or_tool_function(context: CallbackContext, # 或 ToolContext
                                     # ... 其他參數 ...
                                    ):
        # 更新現有狀態
        count = context.state.get("user_action_count", 0)
        context.state["user_action_count"] = count + 1

        # 新增新狀態
        context.state["temp:last_operation_status"] = "success"

        # 狀態變更會自動成為事件的 state_delta 的一部分
        # ... 其餘的回呼/工具邏輯 ...
    ```

=== "Java"

    ```java
    // 在代理程式回呼或工具方法中
    import com.google.adk.agents.CallbackContext; // 或 ToolContext
    // ... 其他匯入 ...

    public class MyAgentCallbacks {
        public void onAfterAgent(CallbackContext callbackContext) {
            // 更新現有狀態
            Integer count = (Integer) callbackContext.state().getOrDefault("user_action_count", 0);
            callbackContext.state().put("user_action_count", count + 1);

            // 新增新狀態
            callbackContext.state().put("temp:last_operation_status", "success");

            // 狀態變更會自動成為事件的 state_delta 的一部分
            // ... 其餘的回呼邏輯 ...
        }
    }
    ```

**`append_event` 的作用：**

* 將 `Event` 新增到 `session.events`。
* 從事件的 `actions` 中讀取 `state_delta`。
* 將這些變更應用於由 `SessionService` 管理的狀態，根據服務類型正確處理前綴和持久性。
* 更新會話的 `last_update_time`。
* 確保並行更新的執行緒安全。

### ⚠️ 關於直接狀態修改的警告

避免直接修改從 `SessionService` 直接取得的 `Session` 物件上的 `session.state` 集合（字典/Map）（例如，透過 `session_service.get_session()` 或 `session_service.create_session()`）*在*代理程式調用的託管生命週期*之外*。例如，像 `retrieved_session = await session_service.get_session(...); retrieved_session.state['key'] = value` 這樣的程式碼是有問題的。

*在*回呼或工具中使用 `CallbackContext.state` 或 `ToolContext.state` 進行的狀態修改是確保變更被追蹤的正確方法，因為這些上下文物件會處理與事件系統的必要整合。

**為什麼強烈不建議直接修改（在上下文之外）：**

1. **繞過事件歷史記錄：** 變更未被記錄為 `Event`，失去了可稽核性。
2. **破壞持久性：** 以這種方式進行的變更**很可能不會被** `DatabaseSessionService` 或 `VertexAiSessionService` 儲存。它們依賴 `append_event` 來觸發儲存。
3. **非執行緒安全：** 可能導致競爭條件和更新遺失。
4. **忽略時間戳/邏輯：** 不會更新 `last_update_time` 或觸發相關的事件邏輯。

**建議：** 堅持透過 `output_key`、`EventActions.state_delta`（手動建立事件時）或在各自範圍內修改 `CallbackContext` 或 `ToolContext` 物件的 `state` 屬性來更新狀態。這些方法確保了可靠、可追蹤和持久的狀態管理。僅在*讀取*狀態時才直接存取 `session.state`（從 `SessionService` 檢索的會話中）。

### 狀態設計最佳實踐回顧

* **極簡主義：** 僅儲存必要的動態資料。
* **序列化：** 使用基本的、可序列化的類型。
* **描述性鍵和前綴：** 使用清晰的名稱和適當的前綴（`user:`、`app:`、`temp:` 或無）。
* **淺層結構：** 盡可能避免深度巢狀。
* **標準更新流程：** 依賴 `append_event`。
