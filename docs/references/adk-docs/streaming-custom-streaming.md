# 自訂音訊串流應用程式 (SSE) {#custom-streaming}

本文概述了使用 ADK 串流和 [FastAPI](https://fastapi.tiangolo.com/) 建構的自訂非同步 Web 應用程式的伺服器和客戶端程式碼，該應用程式可透過伺服器發送事件 (Server-Sent Events, SSE) 實現即時、雙向的音訊和文字通訊。主要功能如下：

**伺服器端 (Python/FastAPI)**：
- FastAPI + ADK 整合
- 用於即時串流的伺服器發送事件
- 具有隔離使用者上下文的會話管理
- 支援文字和音訊通訊模式
- Google 搜尋工具整合以提供有根據的回應

**客戶端 (JavaScript/Web Audio API)**：
- 透過 SSE 和 HTTP POST 進行即時雙向通訊
- 使用 AudioWorklet 處理器進行專業音訊處理
- 在文字和音訊模式之間無縫切換
- 自動重新連線和錯誤處理
- 用於音訊資料傳輸的 Base64 編碼

此外，還提供了此範例的 [WebSocket](streaming-custom-streaming-ws.md) 版本。

## 1. 安裝 ADK {#1.-setup-installation}

建立並啟用虛擬環境 (建議)：

```bash
# 建立
python -m venv .venv
# 啟用 (每個新終端機)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

安裝 ADK：

```bash
pip install --upgrade google-adk==1.2.1
```

使用以下指令設定 `SSL_CERT_FILE` 變數。

```shell
export SSL_CERT_FILE=$(python -m certifi)
```

下載範例程式碼：

```bash
git clone --no-checkout https://github.com/google/adk-docs.git
cd adk-docs
git sparse-checkout init --cone
git sparse-checkout set examples/python/snippets/streaming/adk-streaming
git checkout main
cd examples/python/snippets/streaming/adk-streaming/app
```

此範例程式碼包含以下檔案和資料夾：

```console
adk-streaming/
└── app/ # web 應用程式資料夾
    ├── .env # Gemini API 金鑰 / Google Cloud 專案 ID
    ├── main.py # FastAPI web 應用程式
    ├── static/ # 靜態內容資料夾
    |   ├── js # JavaScript 檔案資料夾 (包含 app.js)
    |   └── index.html # Web 客戶端頁面
    └── google_search_agent/ # 代理程式資料夾
        ├── __init__.py # Python 套件
        └── agent.py # 代理程式定義
```

## 2\. 設定平台 {#2.-set-up-the-platform}

若要執行範例應用程式，請從 Google AI Studio 或 Google Cloud Vertex AI 中選擇一個平台：

=== "Gemini - Google AI Studio"
    1. 從 [Google AI Studio](https://aistudio.google.com/apikey) 取得 API 金鑰。
    2. 開啟位於 (`app/`) 內的 **`.env`** 檔案，並複製貼上以下程式碼。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=在此貼上您的實際API金鑰
        ```

    3. 將 `在此貼上您的實際API金鑰` 替換為您實際的 `API 金鑰`。

=== "Gemini - Google Cloud Vertex AI"
    1. 您需要一個現有的
       [Google Cloud](https://cloud.google.com/?e=48754805&hl=en) 帳戶和一個
       專案。
        * 設定一個
          [Google Cloud 專案](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
        * 設定
          [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
        * 從終端機執行
          `gcloud auth login` 來驗證 Google Cloud。
        * [啟用 Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)。
    2. 開啟位於 (`app/`) 內的 **`.env`** 檔案。複製貼上
       以下程式碼並更新專案 ID 和位置。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=在此貼上您的實際專案ID
        GOOGLE_CLOUD_LOCATION=us-central1
        ```


## 3\. 與您的串流應用程式互動 {#3.-interact-with-your-streaming-app}

1\. **導覽至正確的目錄：**

   為了有效地執行您的代理程式，請確保您位於 **app 資料夾 (`adk-streaming/app`)**

2\. **啟動 Fast API**：執行以下指令以啟動 CLI 介面

```console
uvicorn main:app --reload
```

3\. **以文字模式存取應用程式：** 應用程式啟動後，終端機將顯示一個本地 URL (例如，[http://localhost:8000](http://localhost:8000))。點擊此連結以在瀏覽器中開啟 UI。

現在您應該會看到如下的 UI：

![ADK 串流應用程式](../assets/adk-streaming-text.png)

試著問一個問題 `現在幾點了？`。代理程式將使用 Google 搜尋來回應您的查詢。您會注意到 UI 以串流文字的方式顯示代理程式的回應。您也可以隨時傳送訊息給代理程式，即使代理程式仍在回應中。這展示了 ADK 串流的雙向通訊能力。

4\. **以音訊模式存取應用程式：** 現在點擊 `Start Audio` 按鈕。應用程式會以音訊模式重新連接伺服器，UI 會首次顯示以下對話方塊：

![ADK 串流應用程式](../assets/adk-streaming-audio-dialog.png)

點擊 `允許在瀏覽網站時`，然後您會看到麥克風圖示顯示在瀏覽器頂部：

![ADK 串流應用程式](../assets/adk-streaming-mic.png)

現在您可以用語音與代理程式交談。用聲音問 `現在幾點了？` 之類的問題，您也會聽到代理程式用聲音回應。由於 ADK 的串流支援[多種語言](https://ai.google.dev/gemini-api/docs/live#supported-languages)，它也可以用支援的語言回答問題。

5\. **檢查主控台日誌**

如果您使用的是 Chrome 瀏覽器，請按右鍵並選擇 `檢查` 以開啟開發人員工具。在 `主控台` 中，您可以看到傳入和傳出的音訊資料，例如 `[CLIENT TO AGENT]` 和 `[AGENT TO CLIENT]`，代表在瀏覽器和伺服器之間串流傳入和傳出的音訊資料。

同時，在應用程式伺服器主控台中，您應該會看到如下內容：

```
Client #90766266 connected via SSE, audio mode: false
INFO:     127.0.0.1:52692 - "GET /events/90766266?is_audio=false HTTP/1.1" 200 OK
[CLIENT TO AGENT]: hi
INFO:     127.0.0.1:52696 - "POST /send/90766266 HTTP/1.1" 200 OK
[AGENT TO CLIENT]: text/plain: {'mime_type': 'text/plain', 'data': 'Hi'}
[AGENT TO CLIENT]: text/plain: {'mime_type': 'text/plain', 'data': ' there! How can I help you today?\n'}
[AGENT TO CLIENT]: {'turn_complete': True, 'interrupted': None}
```

如果您開發自己的串流應用程式，這些主控台日誌非常重要。在許多情況下，瀏覽器和伺服器之間的通訊失敗是串流應用程式錯誤的主要原因。

6\. **疑難排解提示**

- **當您的瀏覽器無法透過 SSH 代理連線到伺服器時：** 各種雲端服務中使用的 SSH 代理可能無法與 SSE 一起使用。請嘗試不使用 SSH 代理，例如使用本地筆記型電腦，或嘗試 [WebSocket](streaming-custom-streaming-ws.md) 版本。
- **當 `gemini-2.0-flash-exp` 模型無法運作時：** 如果您在應用程式伺服器主控台中看到任何關於 `gemini-2.0-flash-exp` 模型可用性的錯誤，請嘗試在 `app/google_search_agent/agent.py` 的第 6 行將其替換為 `gemini-2.0-flash-live-001`。

## 4. 代理程式定義

`google_search_agent` 資料夾中的代理程式定義程式碼 `agent.py` 是撰寫代理程式邏輯的地方：


```python
from google.adk.agents import Agent
from google.adk.tools import google_search  # 匯入工具

root_agent = Agent(
   name="google_search_agent",
   model="gemini-2.0-flash-exp", # 如果此模型無效，請嘗試以下模型
   #model="gemini-2.0-flash-live-001",
   description="使用 Google 搜尋回答問題的代理程式。",
   instruction="使用 Google 搜尋工具回答問題。",
   tools=[google_search],
)
```

請注意您多麼輕易地整合了[使用 Google 搜尋的 grounding](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search) 功能。`Agent` 類別和 `google_search` 工具處理了與 LLM 和搜尋 API 的 grounding 的複雜互動，讓您可以專注於代理程式的*目的*和*行為*。

![intro_components.png](../assets/quickstart-streaming-tool.png)


伺服器和客戶端架構可實現 Web 客戶端和 AI 代理程式之間的即時、雙向通訊，並具有適當的會話隔離和資源管理。

## 5. 伺服器端程式碼概觀 {#5.-server-side-code-overview}

FastAPI 伺服器提供 Web 客戶端和 AI 代理程式之間的即時通訊。

### 雙向通訊概觀 {#4.-bidi-comm-overview}

#### 客戶端到代理程式流程：
1. **建立連線** - 客戶端開啟到 `/events/{user_id}` 的 SSE 連線，觸發會話建立並將請求佇列儲存在 `active_sessions` 中
2. **訊息傳輸** - 客戶端向 `/send/{user_id}` 傳送 POST，其中包含包含 `mime_type` 和 `data` 的 JSON 負載
3. **佇列處理** - 伺服器檢索會話的 `live_request_queue` 並透過 `send_content()` 或 `send_realtime()` 將訊息轉發給代理程式

#### 代理程式到客戶端流程：
1. **事件產生** - 代理程式處理請求並透過 `live_events` 非同步產生器產生事件
2. **串流處理** - `agent_to_client_sse()` 過濾事件並將其格式化為與 SSE 相容的 JSON
3. **即時傳遞** - 事件透過具有適當 SSE 標頭的持久性 HTTP 連線串流至客戶端

#### 會話管理：
- **每個使用者隔離** - 每個使用者都會獲得儲存在 `active_sessions` 字典中的唯一會話
- **生命週期管理** - 會話在中斷連線時會自動清理，並妥善處理資源
- **並行支援** - 多個使用者可以同時擁有活動會話

#### 錯誤處理：
- **會話驗證** - POST 請求在處理前會驗證會話是否存在
- **串流彈性** - SSE 串流會處理例外狀況並自動執行清理
- **連線復原** - 客戶端可以透過重新建立 SSE 連線來重新連線


### 代理程式會話管理

`start_agent_session()` 函式會建立隔離的 AI 代理程式會話：

```python
async def start_agent_session(user_id, is_audio=False):
    """啟動代理程式會話"""

    # 建立一個 Runner
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=root_agent,
    )

    # 建立一個會話
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,  # 替換為實際的使用者 ID
    )

    # 設定回應模式
    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(response_modalities=[modality])

    # 為此會話建立一個 LiveRequestQueue
    live_request_queue = LiveRequestQueue()

    # 啟動代理程式會話
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue
```

- **InMemoryRunner 設定** - 建立一個在記憶體中管理代理程式生命週期的執行器實例，應用程式名稱為「ADK 串流範例」，並使用 Google 搜尋代理程式。

- **會話建立** - 使用 `runner.session_service.create_session()` 為每個使用者 ID 建立一個唯一的會話，從而允許多個並行使用者。

- **回應模式設定** - 根據 `is_audio` 參數，將 `RunConfig` 設定為「AUDIO」或「TEXT」模式，以決定輸出格式。

- **LiveRequestQueue** - 建立一個雙向通訊通道，用於對傳入的請求進行排隊，並在客戶端和代理程式之間實現即時訊息傳遞。

- **即時事件串流** - `runner.run_live()` 傳回一個非同步產生器，該產生器會產生來自代理程式的即時事件，包括部分回應、輪次完成和中斷。

### 伺服器發送事件 (SSE) 串流

`agent_to_client_sse()` 函式處理從代理程式到客戶端的即時串流：

```python
async def agent_to_client_sse(live_events):
    """透過 SSE 進行代理程式到客戶端的通訊"""
    async for event in live_events:
        # 如果輪次完成或中斷，則傳送
        if event.turn_complete or event.interrupted:
            message = {
                "turn_complete": event.turn_complete,
                "interrupted": event.interrupted,
            }
            yield f"data: {json.dumps(message)}\n\n"
            print(f"[AGENT TO CLIENT]: {message}")
            continue

        # 讀取內容及其第一部分
        part: Part = (
            event.content and event.content.parts and event.content.parts[0]
        )
        if not part:
            continue

        # 如果是音訊，則傳送 Base64 編碼的音訊資料
        is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/pcm")
        if is_audio:
            audio_data = part.inline_data and part.inline_data.data
            if audio_data:
                message = {
                    "mime_type": "audio/pcm",
                    "data": base64.b64encode(audio_data).decode("ascii")
                }
                yield f"data: {json.dumps(message)}\n\n"
                print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                continue

        # 如果是文字且是部分文字，則傳送
        if part.text and event.partial:
            message = {
                "mime_type": "text/plain",
                "data": part.text
            }
            yield f"data: {json.dumps(message)}\n\n"
            print(f"[AGENT TO CLIENT]: text/plain: {message}")
```

- **事件處理迴圈** - 迭代 `live_events` 非同步產生器，在每個事件從代理程式到達時進行處理。

- **輪次管理**  - 偵測對話輪次完成或中斷事件，並傳送帶有 `turn_complete` 和 `interrupted` 旗標的 JSON 訊息，以指示對話狀態變更。

- **內容部分提取** - 從事件內容中提取第一部分 `Part`，其中包含文字或音訊資料。

- **音訊串流**  - 透過以下方式處理 PCM 音訊資料：
  - 在 `inline_data` 中偵測 `audio/pcm` MIME 類型
  - 對原始音訊位元組進行 Base64 編碼以進行 JSON 傳輸
  - 使用 `mime_type` 和 `data` 欄位傳送

- **文字串流**  - 透過在產生漸進式文字更新時傳送它們來處理部分文字回應，從而實現即時打字效果。

- **SSE 格式** - 所有資料都格式化為 `data: {json}\n\n`，遵循瀏覽器 EventSource API 相容性的 SSE 規範。

### HTTP 端點和路由

#### 根端點
**GET /** - 使用 FastAPI 的 `FileResponse` 提供 `static/index.html` 作為主應用程式介面。

#### SSE 事件端點

```python
@app.get("/events/{user_id}")
async def sse_endpoint(user_id: int, is_audio: str = "false"):
    """用於代理程式到客戶端通訊的 SSE 端點"""

    # 啟動代理程式會話
    user_id_str = str(user_id)
    live_events, live_request_queue = await start_agent_session(user_id_str, is_audio == "true")

    # 儲存此使用者的請求佇列
    active_sessions[user_id_str] = live_request_queue

    print(f"客戶端 #{user_id} 透過 SSE 連線，音訊模式：{is_audio}")

    def cleanup():
        live_request_queue.close()
        if user_id_str in active_sessions:
            del active_sessions[user_id_str]
        print(f"客戶端 #{user_id} 已從 SSE 中斷連線")

    async def event_generator():
        try:
            async for data in agent_to_client_sse(live_events):
                yield data
        except Exception as e:
            print(f"SSE 串流中發生錯誤：{e}")
        finally:
            cleanup()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )
```

**GET /events/{user_id}** - 建立持久性 SSE 連線：

- **參數** - 接受 `user_id` (int) 和可選的 `is_audio` 查詢參數 (預設為 "false")

- **會話初始化** - 呼叫 `start_agent_session()` 並使用 `user_id` 作為鍵將 `live_request_queue` 儲存在 `active_sessions` 字典中

- **StreamingResponse** - 傳回帶有以下內容的 `StreamingResponse`：
  - `event_generator()` 非同步函式，該函式包裝了 `agent_to_client_sse()`
  - MIME 類型：`text/event-stream`
  - 用於跨來源存取的 CORS 標頭
  - 用於防止快取的快取控制標頭

- **清理邏輯** - 透過關閉請求佇列並從活動會話中移除來處理連線終止，並處理串流中斷的錯誤。

#### 訊息傳送端點

```python
@app.post("/send/{user_id}")
async def send_message_endpoint(user_id: int, request: Request):
    """用於客戶端到代理程式通訊的 HTTP 端點"""

    user_id_str = str(user_id)

    # 取得此使用者的即時請求佇列
    live_request_queue = active_sessions.get(user_id_str)
    if not live_request_queue:
        return {"error": "找不到會話"}

    # 解析訊息
    message = await request.json()
    mime_type = message["mime_type"]
    data = message["data"]

    # 將訊息傳送給代理程式
    if mime_type == "text/plain":
        content = Content(role="user", parts=[Part.from_text(text=data)])
        live_request_queue.send_content(content=content)
        print(f"[CLIENT TO AGENT]: {data}")
    elif mime_type == "audio/pcm":
        decoded_data = base64.b64decode(data)
        live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
        print(f"[CLIENT TO AGENT]: audio/pcm: {len(decoded_data)} bytes")
    else:
        return {"error": f"不支援的 Mime 類型：{mime_type}"}

    return {"status": "sent"}
```

**POST /send/{user_id}** - 接收客戶端訊息：

- **會話查詢** - 從 `active_sessions` 中檢索 `live_request_queue`，如果會話不存在則傳回錯誤

- **訊息處理** - 解析帶有 `mime_type` 和 `data` 欄位的 JSON：
  - **文字訊息** - 使用 `Part.from_text()` 建立 `Content` 並透過 `send_content()` 傳送
  - **音訊訊息** - Base64 解碼 PCM 資料並透過 `send_realtime()` 以 `Blob` 傳送

- **錯誤處理** - 對於不支援的 MIME 類型或遺失的會話，傳回適當的錯誤回應。


## 6. 客戶端程式碼概觀 {#6.-client-side-code-overview}

客戶端由一個具有即時通訊和音訊功能的 Web 介面組成：

### HTML 介面 (`static/index.html`)

```html
<!doctype html>
<html>
  <head>
    <title>ADK 串流測試 (音訊)</title>
    <script src="/static/js/app.js" type="module"></script>
  </head>

  <body>
    <h1>ADK 串流測試</h1>
    <div
      id="messages"
      style="height: 300px; overflow-y: auto; border: 1px solid black"></div>
    <br />

    <form id="messageForm">
      <label for="message">訊息：</label>
      <input type="text" id="message" name="message" />
      <button type="submit" id="sendButton" disabled>傳送</button>
      <button type="button" id="startAudioButton">啟動音訊</button>
    </form>
  </body>

</html>
```

簡單的 Web 介面，包含：
- **訊息顯示** - 用於對話歷史記錄的可捲動 div
- **文字輸入表單** - 用於文字訊息的輸入欄位和傳送按鈕
- **音訊控制** - 用於啟用音訊模式和麥克風存取權限的按鈕

### 主要應用程式邏輯 (`static/js/app.js`)

#### 會話管理 (`app.js`)

```js
const sessionId = Math.random().toString().substring(10);
const sse_url =
  "http://" + window.location.host + "/events/" + sessionId;
const send_url =
  "http://" + window.location.host + "/send/" + sessionId;
let is_audio = false;
```

- **隨機會話 ID** - 為每個瀏覽器實例產生唯一的會話 ID
- **URL 建構** - 使用會話 ID 建構 SSE 和傳送端點
- **音訊模式旗標** - 追蹤是否啟用音訊模式

#### 伺服器發送事件連線 (`app.js`)
**connectSSE()** 函式處理即時伺服器通訊：

```js
// SSE 處理常式
function connectSSE() {
  // 連線到 SSE 端點
  eventSource = new EventSource(sse_url + "?is_audio=" + is_audio);

  // 處理連線開啟
  eventSource.onopen = function () {
    // 連線開啟訊息
    console.log("SSE connection opened.");
    document.getElementById("messages").textContent = "Connection opened";

    // 啟用傳送按鈕
    document.getElementById("sendButton").disabled = false;
    addSubmitHandler();
  };

  // 處理傳入訊息
  eventSource.onmessage = function (event) {
    ...
  };

  // 處理連線關閉
  eventSource.onerror = function (event) {
    console.log("SSE connection error or closed.");
    document.getElementById("sendButton").disabled = true;
    document.getElementById("messages").textContent = "Connection closed";
    eventSource.close();
    setTimeout(function () {
      console.log("Reconnecting...");
      connectSSE();
    }, 5000);
  };
}
```

- **EventSource 設定** - 使用音訊模式參數建立 SSE 連線
- **連線處理常式**：
  - **onopen** - 連線時啟用傳送按鈕和表單提交
  - **onmessage** - 處理來自代理程式的傳入訊息
  - **onerror** - 處理中斷連線，並在 5 秒後自動重新連線

#### 訊息處理 (`app.js`)
處理來自伺服器的不同訊息類型：

```js
  // 處理傳入訊息
  eventSource.onmessage = function (event) {
    // 解析傳入訊息
    const message_from_server = JSON.parse(event.data);
    console.log("[AGENT TO CLIENT] ", message_from_server);

    // 檢查輪次是否完成
    // 如果輪次完成，新增新訊息
    if (
      message_from_server.turn_complete &&
      message_from_server.turn_complete == true
    ) {
      currentMessageId = null;
      return;
    }

    // 如果是音訊，則播放
    if (message_from_server.mime_type == "audio/pcm" && audioPlayerNode) {
      audioPlayerNode.port.postMessage(base64ToArray(message_from_server.data));
    }

    // 如果是文字，則列印
    if (message_from_server.mime_type == "text/plain") {
      // 為新輪次新增新訊息
      if (currentMessageId == null) {
        currentMessageId = Math.random().toString(36).substring(7);
        const message = document.createElement("p");
        message.id = currentMessageId;
        // 將訊息元素附加到 messagesDiv
        messagesDiv.appendChild(message);
      }

      // 將訊息文字新增到現有的訊息元素
      const message = document.getElementById(currentMessageId);
      message.textContent += message_from_server.data;

      // 捲動到 messagesDiv 的底部
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
```

- **輪次管理** - 偵測 `turn_complete` 以重設訊息狀態
- **音訊播放** - 解碼 Base64 PCM 資料並傳送至音訊 worklet
- **文字顯示** - 建立新的訊息元素並附加部分文字更新以實現即時打字效果

#### 訊息傳送 (`app.js`)
**sendMessage()** 函式向伺服器傳送資料：

```js
async function sendMessage(message) {
  try {
    const response = await fetch(send_url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(message)
    });
    
    if (!response.ok) {
      console.error('Failed to send message:', response.statusText);
    }
  } catch (error) {
    console.error('Error sending message:', error);
  }
}
```

- **HTTP POST** - 向 `/send/{session_id}` 端點傳送 JSON 負載
- **錯誤處理** - 記錄失敗的請求和網路錯誤
- **訊息格式** - 標準化的 `{mime_type, data}` 結構

### 音訊播放器 (`static/js/audio-player.js`)

**startAudioPlayerWorklet()** 函式：

- **AudioContext 設定** - 建立具有 24kHz 取樣率的上下文以進行播放
- **Worklet 載入** - 載入 PCM 播放器處理器以進行音訊處理
- **音訊管線** - 將 worklet 節點連接到音訊目標 (喇叭)

### 音訊錄製器 (`static/js/audio-recorder.js`)

**startAudioRecorderWorklet()** 函式：

- **AudioContext 設定** - 建立具有 16kHz 取樣率的上下文以進行錄製
- **麥克風存取** - 請求使用者媒體權限以進行音訊輸入
- **音訊處理** - 將麥克風連接到錄製器 worklet
- **資料轉換** - 將 Float32 樣本轉換為 16 位元 PCM 格式

### 音訊 Worklet 處理器

#### PCM 播放器處理器 (`static/js/pcm-player-processor.js`)
**PCMPlayerProcessor** 類別處理音訊播放：

- **環形緩衝區** - 用於 180 秒 24kHz 音訊的循環緩衝區
- **資料擷取** - 將 Int16 轉換為 Float32 並儲存在緩衝區中
- **播放迴圈** - 持續從緩衝區讀取到輸出通道
- **溢位處理** - 當緩衝區已滿時覆寫最舊的樣本

#### PCM 錄製器處理器 (`static/js/pcm-recorder-processor.js`)
**PCMProcessor** 類別擷取麥克風輸入：

- **音訊輸入** - 處理傳入的音訊幀
- **資料傳輸** - 複製 Float32 樣本並透過訊息埠發佈到主執行緒

#### 模式切換：
- **音訊啟用** - 「啟動音訊」按鈕啟用麥克風並使用音訊旗標重新連線 SSE
- **無縫轉換** - 關閉現有連線並建立新的啟用音訊的會話

客戶端架構可實現具有文字和音訊模式的無縫即時通訊，並使用現代 Web API 進行專業級音訊處理。

## 摘要

此應用程式展示了一個完整的即時 AI 代理程式系統，具有以下主要功能：

**架構亮點**：
- **即時**：具有部分文字更新和連續音訊的串流回應
- **穩健**：全面的錯誤處理和自動復原機制
- **現代**：使用最新的 Web 標準 (AudioWorklet、SSE、ES6 模組)

該系統為需要即時互動、Web 搜尋功能和多媒體通訊的複雜 AI 應用程式的建構提供了基礎。

### 生產環境的後續步驟

若要在生產環境中部署此系統，請考慮實作以下改進：

#### 安全性
- **驗證**：將隨機會話 ID 替換為適當的使用者驗證
- **API 金鑰安全性**：使用環境變數或密鑰管理服務
- **HTTPS**：對所有通訊強制執行 TLS 加密
- **速率限制**：防止濫用並控制 API 成本

#### 可擴展性
- **持久性儲存**：將記憶體內會話替換為持久性會話
- **負載平衡**：支援具有共享會話狀態的多個伺服器實例
- **音訊優化**：實作壓縮以減少頻寬使用

#### 監控
- **錯誤追蹤**：監控並警示系統故障
- **API 成本監控**：追蹤 Google 搜尋和 Gemini 的使用情況以防止預算超支
- **效能指標**：監控回應時間和音訊延遲

#### 基礎設施
- **容器化**：使用 Docker 進行封裝，以實現與 Cloud Run 或 Agent Engine 的一致部署
- **健康檢查**：實作端點監控以進行執行時間追蹤
