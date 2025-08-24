# 會話：追蹤個別對話

在我們的簡介之後，讓我們深入探討 `Session`。回想一下「對話線程」的概念。就像您不會從頭開始每一則簡訊一樣，代理程式也需要有關正在進行的互動的上下文。**`Session`** 是 ADK 專門為追蹤和管理這些個別對話線程而設計的物件。

## `Session` 物件

當使用者開始與您的代理程式互動時，`SessionService` 會建立一個 `Session` 物件 (`google.adk.sessions.Session`)。此物件充當一個容器，保存與*該特定聊天線程*相關的所有內容。以下是其主要屬性：

*   **識別 (`id`, `appName`, `userId`)：** 對話的唯一標籤。
    * `id`：*此特定*對話線程的唯一識別碼，對於稍後檢索它至關重要。一個 SessionService 物件可以處理多個 `Session`。此欄位識別我們指的是哪個特定的會話物件。例如，「test_id_modification」。
    * `app_name`：識別此對話屬於哪個代理程式應用程式。例如，「id_modifier_workflow」。
    *   `userId`：將對話連結到特定使用者。
*   **歷史記錄 (`events`)：** 在此特定線程中發生的所有互動（`Event` 物件——使用者訊息、代理程式回應、工具動作）的按時間順序排列的序列。
*   **會話狀態 (`state`)：** 一個儲存*僅*與此特定、正在進行的對話相關的臨時資料的地方。這在互動期間充當代理程式的草稿紙。我們將在下一節中詳細介紹如何使用和管理 `state`。
*   **活動追蹤 (`lastUpdateTime`)：** 一個時間戳，指示此對話線程中最後一次發生事件的時間。

### 範例：檢查會話屬性


=== "Python"

       ```python
        from google.adk.sessions import InMemorySessionService, Session
    
        # 建立一個簡單的會話以檢查其屬性
        temp_service = InMemorySessionService()
        example_session = await temp_service.create_session(
            app_name="my_app",
            user_id="example_user",
            state={"initial_key": "initial_value"} # 狀態可以被初始化
        )

        print(f"--- 檢查會話屬性 ---")
        print(f"ID (`id`):                {example_session.id}")
        print(f"應用程式名稱 (`app_name`): {example_session.app_name}")
        print(f"使用者 ID (`user_id`):         {example_session.user_id}")
        print(f"狀態 (`state`):           {example_session.state}") # 注意：此處僅顯示初始狀態
        print(f"事件 (`events`):         {example_session.events}") # 最初為空
        print(f"最後更新 (`last_update_time`): {example_session.last_update_time:.2f}")
        print(f"---------------------------------")

        # 清理 (此範例中為可選)
        temp_service = await temp_service.delete_session(app_name=example_session.app_name,
                                    user_id=example_session.user_id, session_id=example_session.id)
        print("temp_service 的最終狀態 - ", temp_service)
       ```

=== "Java"

       ```java
        import com.google.adk.sessions.InMemorySessionService;
        import com.google.adk.sessions.Session;
        import java.util.concurrent.ConcurrentMap;
        import java.util.concurrent.ConcurrentHashMap;
    
        String sessionId = "123";
        String appName = "example-app"; // 範例應用程式名稱
        String userId = "example-user"; // 範例使用者 ID
        ConcurrentMap<String, Object> initialState = new ConcurrentHashMap<>(Map.of("newKey", "newValue"));
        InMemorySessionService exampleSessionService = new InMemorySessionService();
    
        // 建立會話
        Session exampleSession = exampleSessionService.createSession(
            appName, userId, initialState, Optional.of(sessionId)).blockingGet();
        System.out.println("會話建立成功。");
    
        System.out.println("--- 檢查會話屬性 ---");
        System.out.printf("ID (`id`): %s%n", exampleSession.id());
        System.out.printf("應用程式名稱 (`appName`): %s%n", exampleSession.appName());
        System.out.printf("使用者 ID (`userId`): %s%n", exampleSession.userId());
        System.out.printf("狀態 (`state`): %s%n", exampleSession.state());
        System.out.println("------------------------------------");
    
    
        # 清理 (此範例中為可選)
        var unused = exampleSessionService.deleteSession(appName, userId, sessionId);
       ```

*（**注意：** 上面顯示的狀態僅為初始狀態。狀態更新是透過事件發生的，如「狀態」一節所述。）*

## 使用 `SessionService` 管理會話

如上所示，您通常不直接建立或管理 `Session` 物件。相反，您使用 **`SessionService`**。此服務充當負責您對話會話整個生命週期的中央管理器。

其核心職責包括：

*   **開始新對話：** 當使用者開始互動時建立新的 `Session` 物件。
*   **恢復現有對話：** 檢索特定的 `Session`（使用其 ID），以便代理程式可以從上次中斷的地方繼續。
*   **儲存進度：** 將新的互動（`Event` 物件）附加到會話的歷史記錄中。這也是會話 `state` 更新的機制（更多內容在 `State` 一節中）。
*   **列出對話：** 尋找特定使用者和應用程式的活動會話線程。
*   **清理：** 當對話結束或不再需要時，刪除 `Session` 物件及其相關資料。

## `SessionService` 實作

ADK 提供了不同的 `SessionService` 實作，讓您可以選擇最適合您需求的儲存後端：

1.  **`InMemorySessionService`**

    *   **運作方式：** 將所有會話資料直接儲存在應用程式的記憶體中。
    *   **持久性：** 無。**如果應用程式重新啟動，所有對話資料都會遺失。**
    *   **要求：** 無額外要求。
    *   **最適合：** 快速開發、本地測試、範例以及不需要長期持久性的場景。

    === "Python"
    
           ```python
            from google.adk.sessions import InMemorySessionService
            session_service = InMemorySessionService()
           ```
    === "Java"
    
           ```java
            import com.google.adk.sessions.InMemorySessionService;
            InMemorySessionService exampleSessionService = new InMemorySessionService();
           ```

2.  **`VertexAiSessionService`**

    *   **運作方式：** 透過 API 呼叫使用 Google Cloud 的 Vertex AI 基礎設施進行會話管理。
    *   **持久性：** 是。資料透過 [Vertex AI 代理程式引擎](https://google.github.io/adk-docs/deploy/agent-engine/)可靠且可擴展地進行管理。
    *   **要求：**
        *   一個 Google Cloud 專案 (`pip install vertexai`)
        *   一個可以透過此[步驟](https://cloud.google.com/vertex-ai/docs/pipelines/configure-project#storage)設定的 Google Cloud 儲存空間值區。
        *   一個可以按照此[教學](https://google.github.io/adk-docs/deploy/agent-engine/)設定的 Reasoning Engine 資源名稱/ID。
        *   如果您沒有 Google Cloud 專案，並且想免費試用 VertexAiSessionService，請參閱[免費試用會話和記憶體](sessions-express-mode.md)。
    *   **最適合：** 部署在 Google Cloud 上的可擴展生產應用程式，尤其是在與其他 Vertex AI 功能整合時。

    === "Python"
    
           ```python
           # 要求：pip install google-adk[vertexai]
           # 加上 GCP 設定和驗證
           from google.adk.sessions import VertexAiSessionService

           PROJECT_ID = "your-gcp-project-id"
           LOCATION = "us-central1"
           # 與此服務一起使用的 app_name 應為 Reasoning Engine ID 或名稱
           REASONING_ENGINE_APP_NAME = "projects/your-gcp-project-id/locations/us-central1/reasoningEngines/your-engine-id"

           session_service = VertexAiSessionService(project=PROJECT_ID, location=LOCATION)
           # 呼叫服務方法時使用 REASONING_ENGINE_APP_NAME，例如：
           # session_service = await session_service.create_session(app_name=REASONING_ENGINE_APP_NAME, ...)
           ```
       
    === "Java"
    
           ```java
           // 請查看上面的要求集，因此在您的 bashrc 檔案中匯出以下內容：
           // export GOOGLE_CLOUD_PROJECT=my_gcp_project
           // export GOOGLE_CLOUD_LOCATION=us-central1
           // export GOOGLE_API_KEY=my_api_key

           import com.google.adk.sessions.VertexAiSessionService;
           import java.util.UUID;

           String sessionId = UUID.randomUUID().toString();
           String reasoningEngineAppName = "123456789";
           String userId = "u_123"; // 範例使用者 ID
           ConcurrentMap<String, Object> initialState = new
               ConcurrentHashMap<>(); // 此範例不需要初始狀態

           VertexAiSessionService sessionService = new VertexAiSessionService();
           Session mySession =
               sessionService
                   .createSession(reasoningEngineAppName, userId, initialState, Optional.of(sessionId))
                   .blockingGet();
           ```

3.  **`DatabaseSessionService`**

    ![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前適用於 Python。Java 支援正在計劃/即將推出。"}

    *   **運作方式：** 連接到關聯式資料庫（例如 PostgreSQL、MySQL、SQLite）以將會話資料持久地儲存在資料表中。
    *   **持久性：** 是。資料在應用程式重新啟動後仍然存在。
    *   **要求：** 一個已設定的資料庫。
    *   **最適合：** 需要您自己管理的可靠、持久性儲存的應用程式。

    ```python
    from google.adk.sessions import DatabaseSessionService
    # 使用本地 SQLite 檔案的範例：
    db_url = "sqlite:///./my_agent_data.db"
    session_service = DatabaseSessionService(db_url=db_url)
    ```

選擇正確的 `SessionService` 是定義您的代理程式對話歷史和臨時資料如何儲存和持久化的關鍵。

## 會話生命週期

<img src="../../assets/session_lifecycle.png" alt="會話生命週期">

以下是 `Session` 和 `SessionService` 在一次對話輪次中如何協同運作的簡化流程：

1.  **開始或恢復：** 您的應用程式需要使用 `SessionService` 來 `create_session`（用於新聊天）或使用現有的會話 ID。
2.  **提供上下文：** `Runner` 從適當的服務方法中取得適當的 `Session` 物件，從而為代理程式提供對相應會話的 `state` 和 `events` 的存取權限。
3.  **代理程式處理：** 使用者向代理程式提示一個查詢。代理程式分析查詢以及可能的會話 `state` 和 `events` 歷史記錄以確定回應。
4.  **回應與狀態更新：** 代理程式產生一個回應（並可能標記要在 `state` 中更新的資料）。`Runner` 將此包裝為一個 `Event`。
5.  **儲存互動：** `Runner` 使用 `session` 和新的 `event` 作為參數呼叫 `sessionService.append_event(session, event)`。服務將 `Event` 新增到歷史記錄中，並根據事件中的資訊更新會話在儲存中的 `state`。會話的 `last_update_time` 也會更新。
6.  **準備下一步：** 代理程式的回應傳送給使用者。更新後的 `Session` 現在由 `SessionService` 儲存，準備好進行下一輪（通常在目前會話中繼續對話，從步驟 1 重新開始循環）。
7.  **結束對話：** 當對話結束時，如果不再需要儲存的會話資料，您的應用程式會呼叫 `sessionService.delete_session(...)` 來清理它。

此循環突顯了 `SessionService` 如何透過管理與每個 `Session` 物件相關的歷史和狀態來確保對話的連續性。
