# Vertex AI Express 模式：免費使用 Vertex AI 會話和記憶體

如果您有興趣使用 `VertexAiSessionService` 或 `VertexAiMemoryBankService`，但沒有 Google Cloud 專案，您可以註冊 Vertex AI Express 模式並免費取得存取權限，試用這些服務！您可以使用符合資格的 ***gmail*** 帳戶[在此](https://console.cloud.google.com/expressmode)註冊。有關 Vertex AI Express 模式的更多詳細資訊，請參閱[總覽頁面](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)。
註冊後，取得[API 金鑰](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview#api-keys)，您就可以開始使用您的本地 ADK 代理程式搭配 Vertex AI 會話和記憶體服務了！

!!! info Vertex AI Express 模式限制

    Vertex AI Express 模式在免費方案中有某些限制。免費的 Express 模式專案僅有效期 90 天，且只有部分服務可用，並有配額限制。例如，代理程式引擎的數量限制為 10 個，且部署到代理程式引擎僅保留給付費方案。若要移除配額限制並使用所有 Vertex AI 的服務，請將帳單帳戶新增至您的 Express 模式專案。

## 建立一個代理程式引擎

`Session` 物件是 `AgentEngine` 的子物件。使用 Vertex AI Express 模式時，我們可以建立一個空的 `AgentEngine` 父物件來管理我們所有的 `Session` 和 `Memory` 物件。
首先，請確保您的環境變數設定正確。例如，在 Python 中：

      ```env title="weather_agent/.env"
      GOOGLE_GENAI_USE_VERTEXAI=TRUE
      GOOGLE_API_KEY=在此貼上您實際的EXPRESS模式API金鑰
      ```

接下來，我們可以建立我們的代理程式引擎實例。您可以使用 Gen AI SDK。

=== "GenAI SDK"
    1. 匯入 Gen AI SDK。

        ```
        from google import genai
        ```

    2. 將 Vertex AI 設定為 True，然後使用 POST 請求建立代理程式引擎。
        
        ```
        # 使用 GenAI SDK 建立代理程式引擎
        client = genai.Client(vertexai = True)._api_client

        response = client.request(
                http_method='POST',
                path=f'reasoningEngines',
                request_dict={"displayName": "您的代理程式引擎顯示名稱", "description": "您的代理程式引擎描述"},
            )
        response
        ```

    3. 將 `您的代理程式引擎顯示名稱` 和 `您的代理程式引擎描述` 替換為您的使用案例。
    4. 從回應中取得代理程式引擎名稱和 ID。

        ```
        APP_NAME="/".join(response['name'].split("/")[:6])
        APP_ID=APP_NAME.split('/')[-1]
        ```

## 使用 `VertexAiSessionService` 管理會話

[VertexAiSessionService](session.md###sessionservice-implementations) 與 Vertex AI Express 模式 API 金鑰相容。我們可以改為在沒有任何專案或位置的情況下初始化會話物件。

       ```py
       # 需要：pip install google-adk[vertexai]
       # 加上環境變數設定：
       # GOOGLE_GENAI_USE_VERTEXAI=TRUE
       # GOOGLE_API_KEY=在此貼上您實際的EXPRESS模式API金鑰
       from google.adk.sessions import VertexAiSessionService

       # 與此服務一起使用的 app_name 應為 Reasoning Engine ID 或名稱
       APP_ID = "your-reasoning-engine-id"

       # 使用 Vertex Express 模式初始化時不需要專案和位置
       session_service = VertexAiSessionService(agent_engine_id=APP_ID)
       # 呼叫服務方法時使用 REASONING_ENGINE_APP_ID，例如：
       # session = await session_service.create_session(app_name=REASONING_ENGINE_APP_ID, user_id= ...)
       ```
!!! info 會話服務配額

    對於免費的 Express 模式專案，`VertexAiSessionService` 有以下配額：

    - 100 個會話實體
    - 10,000 個事件實體

## 使用 `VertexAiMemoryBankService` 管理記憶體

[VertexAiMemoryBankService](memory.md###memoryservice-implementations) 與 Vertex AI Express 模式 API 金鑰相容。我們可以改為在沒有任何專案或位置的情況下初始化記憶體物件。

       ```py
       # 需要：pip install google-adk[vertexai]
       # 加上環境變數設定：
       # GOOGLE_GENAI_USE_VERTEXAI=TRUE
       # GOOGLE_API_KEY=在此貼上您實際的EXPRESS模式API金鑰
       from google.adk.sessions import VertexAiMemoryBankService

       # 與此服務一起使用的 app_name 應為 Reasoning Engine ID 或名稱
       APP_ID = "your-reasoning-engine-id"

       # 使用 Vertex Express 模式初始化時不需要專案和位置
       memory_service = VertexAiMemoryBankService(agent_engine_id=APP_ID)
       # 從該會話產生記憶體，以便代理程式可以記住有關使用者的相關詳細資訊
       # memory = await memory_service.add_session_to_memory(session)
       ```
!!! info 記憶體服務配額

    對於免費的 Express 模式專案，`VertexAiMemoryBankService` 有以下配額：

    - 200 個記憶體實體

## 程式碼範例：使用 Vertex AI Express 模式的天氣代理程式與會話和記憶體

在此範例中，我們建立一個天氣代理程式，它利用 `VertexAiSessionService` 和 `VertexAiMemoryBankService` 進行上下文管理，讓我們的代理程式能夠記住使用者的偏好和對話！

**[使用 Vertex AI Express 模式的天氣代理程式與會話和記憶體](https://github.com/google/adk-docs/blob/main/examples/python/notebooks/express-mode-weather-agent.ipynb)**
