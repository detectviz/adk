# 測試您的代理

在部署您的代理之前，您應該對其進行測試，以確保其按預期運作。在您的開發環境中測試代理最簡單的方法是使用 ADK API 伺服器。

=== "Python"

    ```py
    adk api_server
    ```

=== "Java"

    請務必更新埠號。

    ```java
    mvn compile exec:java \
         -Dexec.args="--adk.agents.source-dir=src/main/java/agents --server.port=8080"
    ```
    在 Java 中，開發者介面和 API 伺服器是捆綁在一起的。

此指令將啟動一個本地 Web 伺服器，您可以在其中執行 cURL 指令或傳送 API 請求來測試您的代理。

!!! tip "進階用法與除錯"

    有關所有可用端點、請求/回應格式以及除錯提示 (包括如何使用互動式 API 文件) 的完整參考，請參閱下方的 **ADK API 伺服器指南**。

## 本地測試

本地測試涉及啟動本地 Web 伺服器、建立會話以及向您的代理傳送查詢。首先，請確保您位於正確的工作目錄中：

```console
parent_folder/
└── my_sample_agent/
    └── agent.py (or Agent.java)
```

**啟動本地伺服器**

接下來，使用上面列出的指令啟動本地伺服器。

輸出應類似於：

=== "Python"

    ```shell
    INFO:     Started server process [12345]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
    ```

=== "Java"

    ```shell
    2025-05-13T23:32:08.972-06:00  INFO 37864 --- [ebServer.main()] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 8080 (http) with context path '/'
    2025-05-13T23:32:08.980-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : Started AdkWebServer in 1.15 seconds (process running for 2.877)
    2025-05-13T23:32:08.981-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : AdkWebServer application started successfully.
    ```

您的伺服器現在正在本地執行。請確保在所有後續指令中使用正確的 **_埠號_**。

**建立新會話**

在 API 伺服器仍在執行的情況下，開啟一個新的終端機視窗或標籤，並使用以下指令與代理建立新會話：

```shell
curl -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"state": {"key1": "value1", "key2": 42}}'
```

讓我們來分解一下發生了什麼：

* `http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123`：這會為您的代理 `my_sample_agent` (代理資料夾的名稱) 建立一個新會話，使用者 ID 為 (`u_123`)，會話 ID 為 (`s_123`)。您可以將 `my_sample_agent` 替換為您的代理資料夾名稱。您可以將 `u_123` 替換為特定的使用者 ID，並將 `s_123` 替換為特定的會話 ID。
* `{"state": {"key1": "value1", "key2": 42}}`：這是可選的。您可以在建立會話時使用它來自訂代理的預先存在狀態 (字典)。

如果建立成功，這應該會傳回會話資訊。輸出應類似於：

```json
{"id":"s_123","appName":"my_sample_agent","userId":"u_123","state":{"key1":"value1","key2":42},"events":[],"lastUpdateTime":1743711430.022186}
```

!!! info

    您無法使用完全相同的使用者 ID 和會話 ID 建立多個會話。如果您嘗試這樣做，您可能會看到類似以下的回應：
    `{"detail":"Session already exists: s_123"}`。要解決此問題，您可以刪除該會話 (例如 `s_123`)，或選擇不同的會話 ID。

**傳送查詢**

有兩種方法可以透過 POST 向您的代理傳送查詢，即透過 `/run` 或 `/run_sse` 路由。

* `POST http://localhost:8000/run`：將所有事件收集為一個列表並一次性傳回。適用於大多數使用者 (如果您不確定，我們建議使用此方法)。
* `POST http://localhost:8000/run_sse`：以伺服器傳送事件 (Server-Sent-Events) 的形式傳回，這是一個事件物件的串流。適用於希望在事件可用時立即收到通知的使用者。使用 `/run_sse`，您還可以將 `streaming` 設定為 `true` 以啟用權杖級串流。

**使用 `/run`**

```shell
curl -X POST http://localhost:8000/run \
-H "Content-Type: application/json" \
-d '{
"app_name": "my_sample_agent",
"user_id": "u_123",
"session_id": "s_123",
"new_message": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
}
}'
```

如果使用 `/run`，您將同時看到事件的完整輸出，以列表形式顯示，應類似於：

```json
[{"content":{"parts":[{"functionCall":{"id":"af-e75e946d-c02a-4aad-931e-49e4ab859838","args":{"city":"new york"},"name":"get_weather"}}],"role":"model"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"longRunningToolIds":[],"id":"2Btee6zW","timestamp":1743712220.385936},{"content":{"parts":[{"functionResponse":{"id":"af-e75e946d-c02a-4aad-931e-49e4ab859838","name":"get_weather","response":{"status":"success","report":"The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}}}],"role":"user"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"PmWibL2m","timestamp":1743712221.895042},{"content":{"parts":[{"text":"OK. The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).\n"}],"role":"model"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"sYT42eVC","timestamp":1743712221.899018}]
```

**使用 `/run_sse`**

```shell
curl -X POST http://localhost:8000/run_sse \
-H "Content-Type: application/json" \
-d '{
"app_name": "my_sample_agent",
"user_id": "u_123",
"session_id": "s_123",
"new_message": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
},
"streaming": false
}'
```

您可以將 `streaming` 設定為 `true` 以啟用權杖級串流，這意味著回應將以多個區塊的形式傳回給您，輸出應類似於：


```shell
data: {"content":{"parts":[{"functionCall":{"id":"af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d","args":{"city":"new york"},"name":"get_weather"}}],"role":"model"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"longRunningToolIds":[],"id":"ptcjaZBa","timestamp":1743712255.313043}

data: {"content":{"parts":[{"functionResponse":{"id":"af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d","name":"get_weather","response":{"status":"success","report":"The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}}}],"role":"user"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"5aocxjaq","timestamp":1743712257.387306}

data: {"content":{"parts":[{"text":"OK. The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).\n"}],"role":"model"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"rAnWGSiV","timestamp":1743712257.391317}
```

!!! info

    如果您使用 `/run_sse`，您應該會在每個事件可用時立即看到它。

## 整合

ADK 使用 [回呼](callbacks.md) 與第三方可觀測性工具整合。這些整合會擷取代理呼叫和互動的詳細追蹤，這對於理解行為、除錯問題和評估效能至關重要。

* [Comet Opik](https://github.com/comet-ml/opik) 是一個開源的 LLM 可觀測性和評估平台，[原生支援 ADK](https://www.comet.com/docs/opik/tracing/integrations/adk)。

## 部署您的代理

既然您已經驗證了代理的本地操作，您就可以繼續部署您的代理了！以下是部署代理的一些方法：

* 部署到 [代理引擎 (Agent Engine)](deploy-agent-engine.md)，這是將您的 ADK 代理部署到 Google Cloud 上 Vertex AI 中託管服務的最簡單方法。
* 部署到 [Cloud Run](deploy-cloud-run.md)，並使用 Google Cloud 上的無伺服器架構完全控制您如何擴展和管理您的代理。


## ADK API 伺服器

ADK API 伺服器是一個預先封裝的 [FastAPI](https://fastapi.tiangolo.com/) Web 伺服器，可透過 RESTful API 公開您的代理。它是本地測試和開發的主要工具，可讓您在部署代理之前以程式設計方式與其互動。

## 執行伺服器

要啟動伺服器，請從專案的根目錄執行以下指令：

```shell
adk api_server
```

預設情況下，伺服器在 `http://localhost:8000` 上執行。您將看到確認伺服器已啟動的輸出：

```shell
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

## 使用互動式 API 文件進行除錯

API 伺服器會使用 Swagger UI 自動產生互動式 API 文件。這是一個非常寶貴的工具，可用於探索端點、了解請求格式以及直接從瀏覽器測試您的代理。

要存取互動式文件，請啟動 API 伺服器並在您的網頁瀏覽器中導覽至 [http://localhost:8000/docs](http://localhost:8000/docs)。

您將看到所有可用 API 端點的完整互動式清單，您可以展開以查看有關參數、請求主體和回應結構的詳細資訊。您甚至可以點擊「試用」以向您正在執行的代理傳送即時請求。

## API 端點

以下各節詳細介紹了與您的代理互動的主要端點。

!!! note "JSON 命名慣例"
    - **請求主體**必須對欄位名稱使用 `snake_case` (例如 `"app_name"`)。
    - **回應主體**將對欄位名稱使用 `camelCase` (例如 `"appName"`)。

### 公用程式端點

#### 列出可用代理

傳回伺服器發現的所有代理應用程式的清單。

*   **方法：** `GET`
*   **路徑：** `/list-apps`

**請求範例**
```shell
curl -X GET http://localhost:8000/list-apps
```

**回應範例**
```json
["my_sample_agent", "another_agent"]
```

---

### 會話管理

會話儲存特定使用者與代理互動的狀態和事件歷史記錄。

#### 建立或更新會話

建立新會話或更新現有會話。如果具有給定 ID 的會話已存在，其狀態將被提供的新狀態覆寫。

*   **方法：** `POST`
*   **路徑：** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**請求主體**
```json
{
  "state": {
    "key1": "value1",
    "key2": 42
  }
}
```

**請求範例**
```shell
curl -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc \
  -H "Content-Type: application/json" \
  -d '{"state": {"visit_count": 5}}'
```

**回應範例**
```json
{"id":"s_abc","appName":"my_sample_agent","userId":"u_123","state":{"visit_count":5},"events":[],"lastUpdateTime":1743711430.022186}
```

#### 取得會話

擷取特定會話的詳細資訊，包括其目前狀態和所有相關事件。

*   **方法：** `GET`
*   **路徑：** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**請求範例**
```shell
curl -X GET http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc
```

**回應範例**
```json
{"id":"s_abc","appName":"my_sample_agent","userId":"u_123","state":{"visit_count":5},"events":[...],"lastUpdateTime":1743711430.022186}
```

#### 刪除會話

刪除一個會話及其所有相關資料。

*   **方法：** `DELETE`
*   **路徑：** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**請求範例**
```shell
curl -X DELETE http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc
```

**回應範例**
成功的刪除會傳回一個空的回應和 `204 No Content` 狀態碼。

---

### 代理執行

這些端點用於向代理傳送新訊息並取得回應。

#### 執行代理 (單一回應)

執行代理並在執行完成後在單一 JSON 陣列中傳回所有產生的事件。

*   **方法：** `POST`
*   **路徑：** `/run`

**請求主體**
```json
{
  "app_name": "my_sample_agent",
  "user_id": "u_123",
  "session_id": "s_abc",
  "new_message": {
    "role": "user",
    "parts": [
      { "text": "What is the capital of France?" }
    ]
  }
}
```

**請求範例**
```shell
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my_sample_agent",
    "user_id": "u_123",
    "session_id": "s_abc",
    "new_message": {
      "role": "user",
      "parts": [{"text": "What is the capital of France?"}]
    }
  }'
```

#### 執行代理 (串流)

執行代理並在使用 [伺服器傳送事件 (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) 產生事件時將其串流回用戶端。

*   **方法：** `POST`
*   **路徑：** `/run_sse`

**請求主體**
請求主體與 `/run` 相同，但有一個額外的可選 `streaming` 旗標。
```json
{
  "app_name": "my_sample_agent",
  "user_id": "u_123",
  "session_id": "s_abc",
  "new_message": {
    "role": "user",
    "parts": [
      { "text": "What is the weather in New York?" }
    ]
  },
  "streaming": true
}
```
- `streaming`：(可選) 設定為 `true` 以啟用模型回應的權杖級串流。預設為 `false`。

**請求範例**
```shell
curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my_sample_agent",
    "user_id": "u_123",
    "session_id": "s_abc",
    "new_message": {
      "role": "user",
      "parts": [{"text": "What is the weather in New York?"}]
    },
    "streaming": false
  }'
```