# 上下文 (Context)

## 什麼是上下文 (Context)

在代理開發套件 (Agent Development Kit, ADK) 中，「上下文 (context)」指的是在特定操作期間可供您的代理 (agent) 及其工具 (tools) 使用的關鍵資訊組合。您可以把它想像成有效處理當前任務或對話回合所需的背景知識和資源。

代理 (agent) 通常不僅需要最新的使用者訊息才能表現良好。上下文 (Context) 至關重要，因為它能夠：

1.  **維持狀態 (Maintaining State)**：記住對話中多個步驟的細節（例如，使用者偏好、先前的計算、購物車中的商品）。這主要透過**會話狀態 (session state)** 來管理。
2.  **傳遞資料 (Passing Data)**：將某個步驟中發現或產生的資訊（如大型語言模型 (LLM) 呼叫或工具執行）分享給後續步驟。會話狀態 (Session state) 在這裡也是關鍵。
3.  **存取服務 (Accessing Services)**：與框架功能互動，例如：
    *   **產物儲存 (Artifact Storage)**：儲存或載入與會話 (session) 相關的檔案或資料塊（如 PDF、圖片、設定檔）。
    *   **記憶體 (Memory)**：從過去的互動或與使用者相關的外部知識來源中搜尋相關資訊。
    *   **驗證 (Authentication)**：請求和擷取工具 (tools) 安全存取外部 API 所需的憑證。
4.  **身份與追蹤 (Identity and Tracking)**：了解哪個代理 (agent) 目前正在執行 (`agent.name`)，並唯一識別當前的請求-回應週期 (`invocation_id`)，以便於記錄和偵錯。
5.  **工具特定操作 (Tool-Specific Actions)**：在工具 (tools) 中啟用專門的操作，例如請求驗證或搜尋記憶體，這些操作需要存取當前互動的詳細資訊。


將所有這些資訊整合在一起，用於單一、完整的使用者請求到最終回應週期（一次**調用 (invocation)**）的核心部分是 `InvocationContext`。然而，您通常不會直接建立或管理此物件。ADK 框架在調用 (invocation) 開始時（例如，透過 `runner.run_async`）建立它，並將相關的上下文資訊隱含地傳遞給您的代理 (agent) 程式碼、回呼 (callbacks) 和工具 (tools)。

=== "Python"

    ```python
    # 概念性虛擬碼：框架如何提供上下文 (內部邏輯)
    
    # runner = Runner(agent=my_root_agent, session_service=..., artifact_service=...)
    # user_message = types.Content(...)
    # session = session_service.get_session(...) # 或建立新的
    
    # --- 在 runner.run_async(...) 內部 ---
    # 1. 框架為此次特定執行建立主要上下文
    # invocation_context = InvocationContext(
    #     invocation_id="unique-id-for-this-run",
    #     session=session,
    #     user_content=user_message,
    #     agent=my_root_agent, # 起始代理
    #     session_service=session_service,
    #     artifact_service=artifact_service,
    #     memory_service=memory_service,
    #     # ... 其他必要欄位 ...
    # )
    #
    # 2. 框架呼叫代理的 run 方法，隱含地傳遞上下文
    #    (代理的方法簽章將接收它，例如 runAsyncImpl(InvocationContext invocationContext))
    # await my_root_agent.run_async(invocation_context)
    #   --- 結束內部邏輯 ---
    #
    # 作為開發者，您將使用方法參數中提供的上下文物件。
    ```

=== "Java"

    ```java
    /* 概念性虛擬碼：框架如何提供上下文 (內部邏輯) */
    InMemoryRunner runner = new InMemoryRunner(agent);
    Session session = runner
        .sessionService()
        .createSession(runner.appName(), USER_ID, initialState, SESSION_ID )
        .blockingGet();

    try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
      while (true) {
        System.out.print("\nYou > ");
      }
      String userInput = scanner.nextLine();
      if ("quit".equalsIgnoreCase(userInput)) {
        break;
      }
      Content userMsg = Content.fromParts(Part.fromText(userInput));
      Flowable<Event> events = runner.runAsync(session.userId(), session.id(), userMsg);
      System.out.print("\nAgent > ");
      events.blockingForEach(event -> System.out.print(event.stringifyContent()));
    }
    ```

## 不同類型的上下文 (Context)

雖然 `InvocationContext` 作為全面的內部容器，但 ADK 提供了針對特定情況量身訂製的專門上下文物件。這確保您在處理手邊任務時擁有正確的工具和權限，而無需在各處處理內部上下文的全部複雜性。以下是您會遇到的不同「版本」：

1.  **`InvocationContext`**
    *   **使用位置：** 在代理 (agent) 的核心實作方法 (`_run_async_impl`, `_run_live_impl`) 中作為 `ctx` 參數直接接收。
    *   **目的：** 提供對當前調用 (invocation) *整個* 狀態的存取。這是最全面的上下文物件。
    *   **主要內容：** 直接存取 `session`（包括 `state` 和 `events`）、當前的 `agent` 實例、`invocation_id`、初始的 `user_content`、對已設定服務（`artifact_service`, `memory_service`, `session_service`）的引用，以及與即時/串流模式相關的欄位。
    *   **使用案例：** 主要用於代理 (agent) 的核心邏輯需要直接存取整體會話 (session) 或服務時，儘管狀態和產物 (artifact) 的互動通常會委派給使用其自身上下文的回呼 (callbacks)/工具 (tools)。也用於控制調用 (invocation) 本身（例如，設定 `ctx.end_invocation = True`）。

    === "Python"
    
        ```python
        # 虛擬碼：代理實作接收 InvocationContext
        from google.adk.agents import BaseAgent
        from google.adk.agents.invocation_context import InvocationContext
        from google.adk.events import Event
        from typing import AsyncGenerator
    
        class MyAgent(BaseAgent):
            async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
                # 直接存取範例
                agent_name = ctx.agent.name
                session_id = ctx.session.id
                print(f"代理 {agent_name} 正在會話 {session_id} 中為調用 {ctx.invocation_id} 執行")
                # ... 使用 ctx 的代理邏輯 ...
                yield # ... event ...
        ```
    
    === "Java"
    
        ```java
        // 虛擬碼：代理實作接收 InvocationContext
        import com.google.adk.agents.BaseAgent;
        import com.google.adk.agents.InvocationContext;
        
            LlmAgent root_agent =
                LlmAgent.builder()
                    .model("gemini-***")
                    .name("sample_agent")
                    .description("回答使用者問題。")
                    .instruction(
                        """
                        在此提供代理的指令。
                        """
                    )
                    .tools(sampleTool)
                    .outputKey("YOUR_KEY")
                    .build();
    
            ConcurrentMap<String, Object> initialState = new ConcurrentHashMap<>();
            initialState.put("YOUR_KEY", "");
          
            InMemoryRunner runner = new InMemoryRunner(agent);
            Session session =
                  runner
                      .sessionService()
                      .createSession(runner.appName(), USER_ID, initialState, SESSION_ID )
                      .blockingGet();
    
           try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
                while (true) {
                  System.out.print("\nYou > ");
                  String userInput = scanner.nextLine();
        
                  if ("quit".equalsIgnoreCase(userInput)) {
                    break;
                  }
                  
                  Content userMsg = Content.fromParts(Part.fromText(userInput));
                  Flowable<Event> events = 
                          runner.runAsync(session.userId(), session.id(), userMsg);
        
                  System.out.print("\nAgent > ");
                  events.blockingForEach(event -> 
                          System.out.print(event.stringifyContent()));
              }
        
            protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
                // 直接存取範例
                String agentName = invocationContext.agent.name;
                String sessionId = invocationContext.session.id;
                String invocationId = invocationContext.invocationId;
                System.out.println("代理 " + agentName + " 正在會話 " + sessionId + " 中為調用 " + invocationId + " 執行");
                // ... 使用 ctx 的代理邏輯 ...
            }
        ```

2.  **`ReadonlyContext`**
    *   **使用位置：** 在僅需對基本資訊進行唯讀存取且不允許變動的情境中提供（例如 `InstructionProvider` 函式）。它也是其他上下文的基底類別。
    *   **目的：** 提供對基本上下文詳細資訊的安全、唯讀檢視。
    *   **主要內容：** `invocation_id`、`agent_name`，以及對當前 `state` 的唯讀*檢視*。

    === "Python"
    
        ```python
        # 虛擬碼：指令提供者接收 ReadonlyContext
        from google.adk.agents.readonly_context import ReadonlyContext
    
        def my_instruction_provider(context: ReadonlyContext) -> str:
            # 唯讀存取範例
            user_tier = context.state().get("user_tier", "standard") # 可以讀取狀態
            # context.state['new_key'] = 'value' # 這通常會導致錯誤或無效
            return f"處理 {user_tier} 使用者的請求。"
        ```
    
    === "Java"
    
        ```java
        // 虛擬碼：指令提供者接收 ReadonlyContext
        import com.google.adk.agents.ReadonlyContext;
    
        public String myInstructionProvider(ReadonlyContext context){
            // 唯讀存取範例
            String userTier = (String) context.state().get("user_tier");
            context.state().put("new_key", "value"); //這通常會導致錯誤
            return "處理 " + userTier + " 使用者的請求。";
        }
        ```
    
3.  **`CallbackContext`**
    *   **使用位置：** 作為 `callback_context` 傳遞給代理生命週期回呼 (`before_agent_callback`, `after_agent_callback`) 和模型互動回呼 (`before_model_callback`, `after_model_callback`)。
    *   **目的：** 便於在回呼 (callbacks) 中*專門*檢查和修改狀態、與產物 (artifacts) 互動，以及存取調用 (invocation) 詳細資訊。
    *   **主要功能 (新增於 `ReadonlyContext` 之上)：**
        *   **可變的 `state` 屬性：** 允許讀取*和寫入*會話狀態 (session state)。此處所做的變更 (`callback_context.state['key'] = value`) 會被追蹤，並與框架在回呼後產生的事件相關聯。
        *   **產物 (Artifact) 方法：** `load_artifact(filename)` 和 `save_artifact(filename, part)` 方法，用於與已設定的 `artifact_service` 互動。
        *   直接存取 `user_content`。

    === "Python"
    
        ```python
        # 虛擬碼：回呼接收 CallbackContext
        from google.adk.agents.callback_context import CallbackContext
        from google.adk.models import LlmRequest
        from google.genai import types
        from typing import Optional
    
        def my_before_model_cb(callback_context: CallbackContext, request: LlmRequest) -> Optional[types.Content]:
            # 讀/寫狀態範例
            call_count = callback_context.state.get("model_calls", 0)
            callback_context.state["model_calls"] = call_count + 1 # 修改狀態
    
            # 選擇性地載入產物
            # config_part = callback_context.load_artifact("model_config.json")
            print(f"正在為調用 {callback_context.invocation_id} 準備第 {call_count + 1} 次模型呼叫")
            return None # 允許模型呼叫繼續
        ```
    
    === "Java"
    
        ```java
        // 虛擬碼：回呼接收 CallbackContext
        import com.google.adk.agents.CallbackContext;
        import com.google.adk.models.LlmRequest;
        import com.google.genai.types.Content;
        import java.util.Optional;
    
        public Maybe<LlmResponse> myBeforeModelCb(CallbackContext callbackContext, LlmRequest request){
            // 讀/寫狀態範例
            int callCount = (int) callbackContext.state().get("model_calls");
            callbackContext.state().put("model_calls", callCount + 1); // 修改狀態
    
            // 選擇性地載入產物
            // Maybe<Part> configPart = callbackContext.loadArtifact("model_config.json");
            System.out.println("正在準備模型呼叫 " + (callCount + 1));
            return Maybe.empty(); // 允許模型呼叫繼續
        }
        ```

4.  **`ToolContext`**
    *   **使用位置：** 作為 `tool_context` 傳遞給支援 `FunctionTool` 的函式，以及工具執行回呼 (`before_tool_callback`, `after_tool_callback`)。
    *   **目的：** 提供 `CallbackContext` 的所有功能，外加對工具執行至關重要的專門方法，如處理驗證、搜尋記憶體和列出產物 (artifacts)。
    *   **主要功能 (新增於 `CallbackContext` 之上)：**
        *   **驗證 (Authentication) 方法：** `request_credential(auth_config)` 觸發驗證流程，`get_auth_response(auth_config)` 擷取使用者/系統提供的憑證。
        *   **產物 (Artifact) 列表：** `list_artifacts()` 發現會話 (session) 中可用的產物。
        *   **記憶體搜尋 (Memory Search)：** `search_memory(query)` 查詢已設定的 `memory_service`。
        *   **`function_call_id` 屬性：** 識別觸發此工具執行的特定大型語言模型 (LLM) 函式呼叫，這對於正確連結驗證請求或回應至關重要。
        *   **`actions` 屬性：** 直接存取此步驟的 `EventActions` 物件，允許工具發出狀態變更、驗證請求等信號。

    === "Python"
    
        ```python
        # 虛擬碼：工具函式接收 ToolContext
        from google.adk.tools import ToolContext
        from typing import Dict, Any
    
        # 假設此函式由 FunctionTool 包裝
        def search_external_api(query: str, tool_context: ToolContext) -> Dict[str, Any]:
            api_key = tool_context.state.get("api_key")
            if not api_key:
                # 定義所需的驗證設定
                # auth_config = AuthConfig(...)
                # tool_context.request_credential(auth_config) # 請求憑證
                # 使用 'actions' 屬性來表示已發出驗證請求
                # tool_context.actions.requested_auth_configs[tool_context.function_call_id] = auth_config
                return {"status": "需要驗證"}
    
            # 使用 API 金鑰...
            print(f"工具正在為查詢 '{query}' 使用 API 金鑰執行。調用：{tool_context.invocation_id}")
    
            # 選擇性地搜尋記憶體或列出產物
            # relevant_docs = tool_context.search_memory(f"與 {query} 相關的資訊")
            # available_files = tool_context.list_artifacts()
    
            return {"result": f"已擷取 {query} 的資料。"}
        ```
    
    === "Java"
    
        ```java
        // 虛擬碼：工具函式接收 ToolContext
        import com.google.adk.tools.ToolContext;
        import java.util.HashMap;
        import java.util.Map;
    
        // 假設此函式由 FunctionTool 包裝
        public Map<String, Object> searchExternalApi(String query, ToolContext toolContext){
            String apiKey = (String) toolContext.state().get("api_key");
            if(apiKey.isEmpty()){
                // 定義所需的驗證設定
                // authConfig = AuthConfig(...);
                // toolContext.requestCredential(authConfig); # 請求憑證
                // 使用 'actions' 屬性來表示已發出驗證請求
                ...
                return Map.of("status", "需要驗證");
            }
    
            // 使用 API 金鑰...
            System.out.println("工具正在為查詢 " + query + " 使用 API 金鑰執行。");
    
            // 選擇性地列出產物
            // Single<List<String>> availableFiles = toolContext.listArtifacts();
    
            return Map.of("result", "已擷取 " + query + " 的資料");
        }
        ```

了解這些不同的上下文物件以及何時使用它們，是有效管理狀態、存取服務和控制 ADK 應用程式流程的關鍵。下一節將詳細介紹您可以使用這些上下文執行的常見任務。


## 使用上下文 (Context) 的常見任務

現在您已了解不同的上下文物件，讓我們專注於如何在建立您的代理 (agents) 和工具 (tools) 時使用它們來執行常見任務。

### 存取資訊

您會經常需要讀取儲存在上下文中的資訊。

*   **讀取會話狀態 (Session State)：** 存取先前步驟中儲存的資料或使用者/應用程式層級的設定。在 `state` 屬性上使用類似字典的存取方式。

    === "Python"
    
        ```python
        # 虛擬碼：在工具函式中
        from google.adk.tools import ToolContext
    
        def my_tool(tool_context: ToolContext, **kwargs):
            user_pref = tool_context.state.get("user_display_preference", "default_mode")
            api_endpoint = tool_context.state.get("app:api_endpoint") # 讀取應用程式層級的狀態
    
            if user_pref == "dark_mode":
                # ... 應用暗黑模式邏輯 ...
                pass
            print(f"正在使用 API 端點：{api_endpoint}")
            # ... 其餘的工具邏輯 ...
    
        # 虛擬碼：在回呼函式中
        from google.adk.agents.callback_context import CallbackContext
    
        def my_callback(callback_context: CallbackContext, **kwargs):
            last_tool_result = callback_context.state.get("temp:last_api_result") # 讀取暫時狀態
            if last_tool_result:
                print(f"從上一個工具找到暫時結果：{last_tool_result}")
            # ... 回呼邏輯 ...
        ```
    
    === "Java"
    
        ```java
        // 虛擬碼：在工具函式中
        import com.google.adk.tools.ToolContext;
    
        public void myTool(ToolContext toolContext){
           String userPref = (String) toolContext.state().get("user_display_preference");
           String apiEndpoint = (String) toolContext.state().get("app:api_endpoint"); // 讀取應用程式層級的狀態
           if(userPref.equals("dark_mode")){
                // ... 應用暗黑模式邏輯 ...
                pass;
            }
           System.out.println("正在使用 API 端點：" + apiEndpoint);
           // ... 其餘的工具邏輯 ...
        }
    
    
        // 虛擬碼：在回呼函式中
        import com.google.adk.agents.CallbackContext;
    
            public void myCallback(CallbackContext callbackContext){
                String lastToolResult = (String) callbackContext.state().get("temp:last_api_result"); // 讀取暫時狀態
                if(!(lastToolResult.isEmpty())){
                    System.out.println("從上一個工具找到暫時結果：" + lastToolResult);
                }
                // ... 回呼邏輯 ...
            }
        ```

*   **取得目前識別碼：** 對於記錄或基於當前操作的自訂邏輯很有用。

    === "Python"
    
        ```python
        # 虛擬碼：在任何上下文中 (以 ToolContext 為例)
        from google.adk.tools import ToolContext
    
        def log_tool_usage(tool_context: ToolContext, **kwargs):
            agent_name = tool_context.agent_name
            inv_id = tool_context.invocation_id
            func_call_id = getattr(tool_context, 'function_call_id', 'N/A') # ToolContext 特有
    
            print(f"日誌：調用={inv_id}, 代理={agent_name}, 函式呼叫ID={func_call_id} - 工具已執行。")
        ```
    
    === "Java"
    
        ```java
        // 虛擬碼：在任何上下文中 (以 ToolContext 為例)
         import com.google.adk.tools.ToolContext;
    
         public void logToolUsage(ToolContext toolContext){
                    String agentName = toolContext.agentName();
                    String invId = toolContext.invocationId();
                    String functionCallId = toolContext.functionCallId().get(); // ToolContext 特有
                    System.out.println("日誌：調用= " + invId + " 代理= " + agentName);
                }
        ```

*   **存取初始使用者輸入：** 回頭參考啟動當前調用 (invocation) 的訊息。

    === "Python"
    
        ```python
        # 虛擬碼：在回呼中
        from google.adk.agents.callback_context import CallbackContext
    
        def check_initial_intent(callback_context: CallbackContext, **kwargs):
            initial_text = "N/A"
            if callback_context.user_content and callback_context.user_content.parts:
                initial_text = callback_context.user_content.parts[0].text or "非文字輸入"
    
            print(f"此次調用始於使用者輸入：'{initial_text}'")
    
        # 虛擬碼：在代理的 _run_async_impl 中
        # async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        #     if ctx.user_content and ctx.user_content.parts:
        #         initial_text = ctx.user_content.parts[0].text
        #         print(f"代理邏輯記住初始查詢：{initial_text}")
        #     ...
        ```
    
    === "Java"
    
        ```java
        // 虛擬碼：在回呼中
        import com.google.adk.agents.CallbackContext;
    
        public void checkInitialIntent(CallbackContext callbackContext){
            String initialText = "N/A";
            if((!(callbackContext.userContent().isEmpty())) && (!(callbackContext.userContent().get().parts().isEmpty()))){
                initialText = callbackContext.userContent().get().parts().get(0).text().get();
                ...
                System.out.println("此次調用始於使用者輸入：" + initialText);
            }
        }
        ```
    
### 管理會話狀態 (Session State)

狀態對於記憶體和資料流至關重要。當您使用 `CallbackContext` 或 `ToolContext` 修改狀態時，變更會由框架自動追蹤和保存。

*   **運作方式：** 寫入 `callback_context.state['my_key'] = my_value` 或 `tool_context.state['my_key'] = my_value` 會將此變更加入與目前步驟事件相關的 `EventActions.state_delta`。然後 `SessionService` 在保存事件時應用這些差異。
*   **在工具之間傳遞資料：**

    === "Python"
    
        ```python
        # 虛擬碼：工具 1 - 擷取使用者 ID
        from google.adk.tools import ToolContext
        import uuid
    
        def get_user_profile(tool_context: ToolContext) -> dict:
            user_id = str(uuid.uuid4()) # 模擬擷取 ID
            # 將 ID 儲存到狀態中，供下一個工具使用
            tool_context.state["temp:current_user_id"] = user_id
            return {"profile_status": "ID 已產生"}
    
        # 虛擬碼：工具 2 - 使用來自狀態的使用者 ID
        def get_user_orders(tool_context: ToolContext) -> dict:
            user_id = tool_context.state.get("temp:current_user_id")
            if not user_id:
                return {"error": "在狀態中找不到使用者 ID"}
    
            print(f"正在為使用者 ID 擷取訂單：{user_id}")
            # ... 使用 user_id 擷取訂單的邏輯 ...
            return {"orders": ["order123", "order456"]}
        ```
    
    === "Java"
    
        ```java
        // 虛擬碼：工具 1 - 擷取使用者 ID
        import com.google.adk.tools.ToolContext;
        import java.util.UUID;
        import java.util.Map;
    
        public Map<String, String> getUserProfile(ToolContext toolContext){
            String userId = UUID.randomUUID().toString();
            // 將 ID 儲存到狀態中，供下一個工具使用
            toolContext.state().put("temp:current_user_id", userId);
            return Map.of("profile_status", "ID 已產生");
        }
    
        // 虛擬碼：工具 2 - 使用來自狀態的使用者 ID
        public  Map<String, Object> getUserOrders(ToolContext toolContext){
            String userId = (String) toolContext.state().get("temp:current_user_id");
            if(userId.isEmpty()){
                return Map.of("error", "在狀態中找不到使用者 ID");
            }
            System.out.println("正在為使用者 ID 擷取訂單：" + userId);
             // ... 使用 user_id 擷取訂單的邏輯 ...
            return Map.of("orders", new String[]{"order123", "order456"});
        }
        ```

*   **更新使用者偏好：**

    === "Python"
    
        ```python
        # 虛擬碼：工具或回呼識別偏好
        from google.adk.tools import ToolContext # 或 CallbackContext
    
        def set_user_preference(tool_context: ToolContext, preference: str, value: str) -> dict:
            # 對於使用者層級的狀態，使用 'user:' 前綴 (如果使用持久性 SessionService)
            state_key = f"user:{preference}"
            tool_context.state[state_key] = value
            print(f"已將使用者偏好 '{preference}' 設定為 '{value}'")
            return {"status": "偏好已更新"}
        ```
    
    === "Java"
    
        ```java
        // 虛擬碼：工具或回呼識別偏好
        import com.google.adk.tools.ToolContext; // 或 CallbackContext
        import java.util.Map;

        public Map<String, String> setUserPreference(ToolContext toolContext, String preference, String value){
            // 對於使用者層級的狀態，使用 'user:' 前綴 (如果使用持久性 SessionService)
            String stateKey = "user:" + preference;
            toolContext.state().put(stateKey, value);
            System.out.println("已將使用者偏好 '" + preference + "' 設定為 '" + value + "'");
            return Map.of("status", "偏好已更新");
        }
        ```

*   **狀態前綴：** 雖然基本狀態是會話 (session) 特有的，但 `app:` 和 `user:` 等前綴可與持久性 `SessionService` 實作（如 `DatabaseSessionService` 或 `VertexAiSessionService`）一起使用，以表示更廣泛的範圍（應用程式範圍或跨會話的使用者範圍）。`temp:` 可表示僅在當前調用 (invocation) 中相關的資料。

### 使用產物 (Artifacts)

使用產物 (artifacts) 來處理與會話 (session) 相關的檔案或大型資料塊。常見使用案例：處理上傳的文件。

*   **文件摘要器範例流程：**

    1.  **擷取參考（例如，在設定工具或回呼中）：** 將文件的*路徑或 URI*（而不是整個內容）儲存為產物 (artifact)。

        === "Python"
    
               ```python
               # 虛擬碼：在回呼或初始工具中
               from google.adk.agents.callback_context import CallbackContext # 或 ToolContext
               from google.genai import types
                
               def save_document_reference(context: CallbackContext, file_path: str) -> None:
                   # 假設 file_path 是像 "gs://my-bucket/docs/report.pdf" 或 "/local/path/to/report.pdf"
                   try:
                       # 建立一個包含路徑/URI 文字的 Part
                       artifact_part = types.Part(text=file_path)
                       version = context.save_artifact("document_to_summarize.txt", artifact_part)
                       print(f"已將文件參考 '{file_path}' 儲存為產物版本 {version}")
                       # 如果其他工具需要，將檔名儲存在狀態中
                       context.state["temp:doc_artifact_name"] = "document_to_summarize.txt"
                   except ValueError as e:
                       print(f"儲存產物時發生錯誤：{e}") # 例如，未設定產物服務
                   except Exception as e:
                       print(f"儲存產物參考時發生意外錯誤：{e}")
                
               # 使用範例：
               # save_document_reference(callback_context, "gs://my-bucket/docs/report.pdf")
               ```
    
        === "Java"
    
               ```java
               // 虛擬碼：在回呼或初始工具中
               import com.google.adk.agents.CallbackContext;
               import com.google.genai.types.Part;
               import java.util.Optional;
                
               public void saveDocumentReference(CallbackContext context, String filePath){
                   // 假設 file_path 是像 "gs://my-bucket/docs/report.pdf" 或 "/local/path/to/report.pdf"
                   try{
                       // 建立一個包含路徑/URI 文字的 Part
                       Part artifactPart = Part.fromText(filePath);
                       Optional<Integer> version = context.saveArtifact("document_to_summarize.txt", artifactPart);
                       System.out.println("已將文件參考" + filePath + "儲存為產物版本 " + version);
                       // 如果其他工具需要，將檔名儲存在狀態中
                       context.state().put("temp:doc_artifact_name", "document_to_summarize.txt");
                   } catch(Exception e){
                       System.out.println("儲存產物參考時發生意外錯誤：" + e);
                   }
               }
                    
               // 使用範例：
               // saveDocumentReference(context, "gs://my-bucket/docs/report.pdf")
               ```

    2.  **摘要器工具：** 載入產物 (artifact) 以取得路徑/URI，使用適當的函式庫讀取實際文件內容，進行摘要，然後返回結果。

        === "Python"

            ```python
            # 虛擬碼：在摘要器工具函式中
            from google.adk.tools import ToolContext
            from google.genai import types
            # 假設 google.cloud.storage 或內建的 open 等函式庫可用
            # 假設存在 'summarize_text' 函式
            # from my_summarizer_lib import summarize_text

            def summarize_document_tool(tool_context: ToolContext) -> dict:
                artifact_name = tool_context.state.get("temp:doc_artifact_name")
                if not artifact_name:
                    return {"error": "在狀態中找不到文件產物名稱。"}

                try:
                    # 1. 載入包含路徑/URI 的產物部分
                    artifact_part = tool_context.load_artifact(artifact_name)
                    if not artifact_part or not artifact_part.text:
                        return {"error": f"無法載入產物或產物沒有文字路徑：{artifact_name}"}

                    file_path = artifact_part.text
                    print(f"已載入文件參考：{file_path}")

                    # 2. 讀取實際文件內容 (在 ADK 上下文之外)
                    document_content = ""
                    if file_path.startswith("gs://"):
                        # 範例：使用 GCS 客戶端函式庫下載/讀取
                        # from google.cloud import storage
                        # client = storage.Client()
                        # blob = storage.Blob.from_string(file_path, client=client)
                        # document_content = blob.download_as_text() # 或根據格式使用 bytes
                        pass # 用實際的 GCS 讀取邏輯取代
                    elif file_path.startswith("/"):
                         # 範例：使用本地檔案系統
                         with open(file_path, 'r', encoding='utf-8') as f:
                             document_content = f.read()
                    else:
                        return {"error": f"不支援的檔案路徑配置：{file_path}"}

                    # 3. 摘要內容
                    if not document_content:
                         return {"error": "讀取文件內容失敗。"}

                    # summary = summarize_text(document_content) # 呼叫您的摘要邏輯
                    summary = f"來自 {file_path} 的內容摘要" # 預留位置

                    return {"summary": summary}

                except ValueError as e:
                     return {"error": f"產物服務錯誤：{e}"}
                except FileNotFoundError:
                     return {"error": f"找不到本地檔案：{file_path}"}
                # except Exception as e: # 捕捉 GCS 等的特定例外
                #      return {"error": f"讀取文件 {file_path} 時發生錯誤：{e}"}
            ```

        === "Java"

            ```java
            // 虛擬碼：在摘要器工具函式中
            import com.google.adk.tools.ToolContext;
            import com.google.genai.types.Part;
            import io.reactivex.rxjava3.core.Maybe;
            import java.util.Map;
            import java.io.FileNotFoundException;


            public Map<String, String> summarizeDocumentTool(ToolContext toolContext){
                String artifactName = (String) toolContext.state().get("temp:doc_artifact_name");
                if(artifactName.isEmpty()){
                    return Map.of("error", "在狀態中找不到文件產物名稱。");
                }
                try{
                    // 1. 載入包含路徑/URI 的產物部分
                    Maybe<Part> artifactPart = toolContext.loadArtifact(artifactName);
                    if((artifactPart.isEmpty()) || (artifactPart.get().text().isEmpty())){
                        return Map.of("error", "無法載入產物或產物沒有文字路徑：" + artifactName);
                    }
                    String filePath = artifactPart.get().text().get();
                    System.out.println("已載入文件參考：" + filePath);

                    // 2. 讀取實際文件內容 (在 ADK 上下文之外)
                    String documentContent = "";
                    if(filePath.startsWith("gs://")){
                        // 範例：使用 GCS 客戶端函式庫下載/讀取到 documentContent
                        pass; // 用實際的 GCS 讀取邏輯取代
                    } else if(filePath.startsWith("/")){
                        // 範例：使用本地檔案系統下載/讀取到 documentContent
                    } else{
                        return Map.of("error", "不支援的檔案路徑配置：" + filePath);
                    }

                    // 3. 摘要內容
                    if(documentContent.isEmpty()){
                        return Map.of("error", "讀取文件內容失敗。");
                    }

                    // String summary = summarizeText(documentContent) // 呼叫您的摘要邏輯
                    String summary = "來自 " + filePath + " 的內容摘要"; // 預留位置

                    return Map.of("summary", summary);
                } catch(IllegalArgumentException e){
                    return Map.of("error", "產物服務錯誤 " + e);
                } catch(FileNotFoundException e){
                    return Map.of("error", "找不到本地檔案 " + e);
                } catch(Exception e){
                    return Map.of("error", "讀取文件時發生錯誤 " + e);
                }
            }
            ```
    
*   **列出產物 (Artifacts)：** 發現可用的檔案。
    
    === "Python"
        
        ```python
        # 虛擬碼：在工具函式中
        from google.adk.tools import ToolContext
        
        def check_available_docs(tool_context: ToolContext) -> dict:
            try:
                artifact_keys = tool_context.list_artifacts()
                print(f"可用的產物：{artifact_keys}")
                return {"available_docs": artifact_keys}
            except ValueError as e:
                return {"error": f"產物服務錯誤：{e}"}
        ```
        
    === "Java"
        
        ```java
        // 虛擬碼：在工具函式中
        import com.google.adk.tools.ToolContext;
        import java.util.List;
        import java.util.Map;
        import io.reactivex.rxjava3.core.Single;

        public Map<String, List<String>> checkAvailableDocs(ToolContext toolContext){
            try{
                Single<List<String>> artifactKeys = toolContext.listArtifacts();
                System.out.println("可用的產物" + artifactKeys.toString());
                return Map.of("availableDocs", artifactKeys.blockingGet());
            } catch(IllegalArgumentException e){
                return Map.of("error", List.of("產物服務錯誤：" + e.toString()));
            }
        }
        ```

### 處理工具驗證 (Tool Authentication)

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前僅支援 Python。Java 支援計畫中/即將推出。" }

安全地管理工具所需的 API 金鑰或其他憑證。

```python
# 虛擬碼：需要驗證的工具
from google.adk.tools import ToolContext
from google.adk.auth import AuthConfig # 假設已定義適當的 AuthConfig

# 定義您所需的驗證設定 (例如，OAuth, API 金鑰)
MY_API_AUTH_CONFIG = AuthConfig(...)
AUTH_STATE_KEY = "user:my_api_credential" # 用於儲存擷取到的憑證的金鑰

def call_secure_api(tool_context: ToolContext, request_data: str) -> dict:
    # 1. 檢查憑證是否已存在於狀態中
    credential = tool_context.state.get(AUTH_STATE_KEY)

    if not credential:
        # 2. 如果不存在，則請求它
        print("找不到憑證，正在請求...")
        try:
            tool_context.request_credential(MY_API_AUTH_CONFIG)
            # 框架會處理產生事件。此回合的工具執行到此為止。
            return {"status": "需要驗證。請提供憑證。"}
        except ValueError as e:
            return {"error": f"驗證錯誤：{e}"} # 例如，缺少 function_call_id
        except Exception as e:
            return {"error": f"請求憑證失敗：{e}"}

    # 3. 如果憑證存在 (可能來自請求後的上一個回合)
    #    或者如果這是在外部驗證流程完成後的後續呼叫
    try:
        # 選擇性地重新驗證/擷取 (如果需要)，或直接使用
        # 如果外部流程剛完成，這可能會擷取到憑證
        auth_credential_obj = tool_context.get_auth_response(MY_API_AUTH_CONFIG)
        api_key = auth_credential_obj.api_key # 或 access_token 等。

        # 將其存回狀態中，供會話中的未來呼叫使用
        tool_context.state[AUTH_STATE_KEY] = auth_credential_obj.model_dump() # 保存擷取到的憑證

        print(f"正在使用擷取的憑證呼叫 API，資料為：{request_data}")
        # ... 使用 api_key 進行實際的 API 呼叫 ...
        api_result = f"用於 {request_data} 的 API 結果"

        return {"result": api_result}
    except Exception as e:
        # 處理擷取/使用憑證時的錯誤
        print(f"使用憑證時發生錯誤：{e}")
        # 如果憑證無效，也許可以清除狀態金鑰？
        # tool_context.state[AUTH_STATE_KEY] = None
        return {"error": "使用憑證失敗"}

```
*請記住：`request_credential` 會暫停工具並發出需要驗證的信號。使用者/系統提供憑證後，在後續的呼叫中，`get_auth_response`（或再次檢查狀態）允許工具繼續執行。* 框架會隱含地使用 `tool_context.function_call_id` 來連結請求和回應。

### 利用記憶體 (Memory)

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前僅支援 Python。Java 支援計畫中/即將推出。" }

存取過去或外部來源的相關資訊。

```python
# 虛擬碼：使用記憶體搜尋的工具
from google.adk.tools import ToolContext

def find_related_info(tool_context: ToolContext, topic: str) -> dict:
    try:
        search_results = tool_context.search_memory(f"關於 {topic} 的資訊")
        if search_results.results:
            print(f"找到 {len(search_results.results)} 個關於 '{topic}' 的記憶體結果")
            # 處理 search_results.results (它們是 SearchMemoryResponseEntry)
            top_result_text = search_results.results[0].text
            return {"memory_snippet": top_result_text}
        else:
            return {"message": "找不到相關的記憶。"}
    except ValueError as e:
        return {"error": f"記憶體服務錯誤：{e}"} # 例如，服務未設定
    except Exception as e:
        return {"error": f"搜尋記憶體時發生意外錯誤：{e}"}
```

### 進階：直接使用 `InvocationContext`

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前僅支援 Python。Java 支援計畫中/即將推出。" }

雖然大多數互動是透過 `CallbackContext` 或 `ToolContext` 進行的，但有時代理 (agent) 的核心邏輯 (`_run_async_impl`/`_run_live_impl`) 需要直接存取。

```python
# 虛擬碼：在代理的 _run_async_impl 內部
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator

class MyControllingAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 範例：檢查特定服務是否可用
        if not ctx.memory_service:
            print("此調用無法使用記憶體服務。")
            # 可能會改變代理行為

        # 範例：基於某個條件提前終止
        if ctx.session.state.get("critical_error_flag"):
            print("偵測到嚴重錯誤，正在結束調用。")
            ctx.end_invocation = True # 通知框架停止處理
            yield Event(author=self.name, invocation_id=ctx.invocation_id, content="因嚴重錯誤而停止。")
            return # 停止此代理的執行

        # ... 正常的代理處理 ...
        yield # ... event ...
```

設定 `ctx.end_invocation = True` 是從代理 (agent) 或其回呼 (callbacks)/工具 (tools)（透過它們各自也可以存取和修改底層 `InvocationContext` 旗標的上下文物件）內部優雅地停止整個請求-回應週期的方法。

## 重點摘要與最佳實踐

*   **使用正確的上下文：** 始終使用提供的最具體的上下文物件（在工具/工具回呼中使用 `ToolContext`，在代理/模型回呼中使用 `CallbackContext`，在適用情況下使用 `ReadonlyContext`）。僅在必要時直接在 `_run_async_impl` / `_run_live_impl` 中使用完整的 `InvocationContext` (`ctx`)。
*   **狀態用於資料流：** `context.state` 是在一次調用 (invocation) *內部* 分享資料、記住偏好和管理對話記憶體的主要方式。使用持久性儲存時，請謹慎使用前綴（`app:`、`user:`、`temp:`）。
*   **產物用於檔案：** 使用 `context.save_artifact` 和 `context.load_artifact` 來管理檔案參考（如路徑或 URI）或較大的資料塊。儲存參考，隨需載入內容。
*   **追蹤變更：** 透過上下文方法對狀態或產物所做的修改會自動連結到目前步驟的 `EventActions`，並由 `SessionService` 處理。
*   **從簡單開始：** 首先專注於 `state` 和基本的產物 (artifact) 使用。隨著您的需求變得更加複雜，再探索驗證、記憶體和進階的 `InvocationContext` 欄位（例如用於即時串流的欄位）。

透過了解並有效使用這些上下文物件，您可以使用 ADK 建立更複雜、有狀態且功能強大的代理 (agents)。
