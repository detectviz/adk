# 自訂音訊串流應用程式 (WebSocket) {#custom-streaming-websocket}

本文概述了使用 ADK 串流和 [FastAPI](https://fastapi.tiangolo.com/) 建構的自訂非同步 Web 應用程式的伺服器和客戶端程式碼，該應用程式可透過 WebSockets 實現即時、雙向的音訊和文字通訊。

**注意：** 本指南假設您具有 JavaScript 和 Python `asyncio` 程式設計的經驗。

## 支援語音/視訊串流的模型 {#supported-models}

為了在 ADK 中使用語音/視訊串流，您需要使用支援 Live API 的 Gemini 模型。您可以在文件中找到支援 Gemini Live API 的**模型 ID**：

- [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
- [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

此外，還提供了此範例的 [SSE](streaming-custom-streaming.md) 版本。

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
git sparse-checkout set examples/python/snippets/streaming/adk-streaming-ws
git checkout main
cd examples/python/snippets/streaming/adk-streaming-ws/app
```

此範例程式碼包含以下檔案和資料夾：

```console
adk-streaming-ws/
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


### agent.py

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

**注意：** 若要同時啟用文字和音訊/視訊輸入，模型必須支援 generateContent (用於文字) 和 bidiGenerateContent 方法。請參考[列出模型文件](https://ai.google.dev/api/models#method:-models.list)來驗證這些功能。本快速入門使用 gemini-2.0-flash-exp 模型進行示範。

請注意您多麼輕易地整合了[使用 Google 搜尋的 grounding](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search) 功能。`Agent` 類別和 `google_search` 工具處理了與 LLM 和搜尋 API 的 grounding 的複雜互動，讓您可以專注於代理程式的*目的*和*行為*。

![intro_components.png](../assets/quickstart-streaming-tool.png)

## 3\. 與您的串流應用程式互動 {#3.-interact-with-your-streaming-app}

1\. **導覽至正確的目錄：**

   為了有效地執行您的代理程式，請確保您位於 **app 資料夾 (`adk-streaming-ws/app`)**

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
INFO:     ('127.0.0.1', 50068) - "WebSocket /ws/70070018?is_audio=true" [accepted]
Client #70070018 connected, audio mode: true
INFO:     connection open
INFO:     127.0.0.1:50061 - "GET /static/js/pcm-player-processor.js HTTP/1.1" 200 OK
INFO:     127.0.0.1:50060 - "GET /static/js/pcm-recorder-processor.js HTTP/1.1" 200 OK
[AGENT TO CLIENT]: audio/pcm: 9600 bytes.
INFO:     127.0.0.1:50082 - "GET /favicon.ico HTTP/1.1" 404 Not Found
[AGENT TO CLIENT]: audio/pcm: 11520 bytes.
[AGENT TO CLIENT]: audio/pcm: 11520 bytes.
```

如果您開發自己的串流應用程式，這些主控台日誌非常重要。在許多情況下，瀏覽器和伺服器之間的通訊失敗是串流應用程式錯誤的主要原因。

6\. **疑難排解提示**

- **當 `ws://` 無法運作時：** 如果您在 Chrome 開發人員工具中看到任何關於 `ws://` 連線的錯誤，請嘗試在 `app/static/js/app.js` 的第 28 行將 `ws://` 替換為 `wss://`。當您在雲端環境中執行範例並使用代理連線從瀏覽器連線時，可能會發生這種情況。
- **當 `gemini-2.0-flash-exp` 模型無法運作時：** 如果您在應用程式伺服器主控台中看到任何關於 `gemini-2.0-flash-exp` 模型可用性的錯誤，請嘗試在 `app/google_search_agent/agent.py` 的第 6 行將其替換為 `gemini-2.0-flash-live-001`。

## 4. 伺服器端程式碼概觀 {#4.-server-side-code-overview}

此伺服器應用程式可透過 WebSockets 與 ADK 代理程式進行即時、串流的互動。客戶端向 ADK 代理程式傳送文字/音訊，並接收串流的文字/音訊回應。

核心功能：
1.  初始化/管理 ADK 代理程式會話。
2.  處理客戶端 WebSocket 連線。
3.  將客戶端訊息轉發給 ADK 代理程式。
4.  將 ADK 代理程式的回應 (文字/音訊) 串流至客戶端。

### ADK 串流設定

```python
import os
import json
import asyncio
import base64

from pathlib import Path
from dotenv import load_dotenv

from google.genai.types import (
    Part,
    Content,
    Blob,
)

from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.in_memory_session_service import InMemorySessionService

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from google_search_agent.agent import root_agent
```

*   **匯入：** 包含標準 Python 函式庫、用於環境變數的 `dotenv`、Google ADK 和 FastAPI。
*   **`load_dotenv()`：** 載入環境變數。
*   **`APP_NAME`**：ADK 的應用程式識別碼。
*   **`session_service = InMemorySessionService()`**：初始化一個記憶體內的 ADK 會話服務，適用於單一實例或開發用途。生產環境可能會使用持久性儲存。

### `start_agent_session(session_id, is_audio=False)`

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

此函式會初始化 ADK 代理程式的即時會話。

| 參數    | 類型    | 說明                                             |
|--------------|---------|---------------------------------------------------------|
| `user_id` | `str`   | 唯一的客戶端識別碼。                       |
| `is_audio`   | `bool`  | `True` 表示音訊回應，`False` 表示文字 (預設)。 |

**主要步驟：**
1\.  **建立 Runner：** 實例化 `root_agent` 的 ADK 執行器。
2\.  **建立會話：** 建立一個 ADK 會話。
3\.  **設定回應模式：** 將代理程式回應設定為「AUDIO」或「TEXT」。
4\.  **建立 LiveRequestQueue：** 為客戶端輸入到代理程式的內容建立一個佇列。
5\.  **啟動代理程式會話：** `runner.run_live(...)` 啟動代理程式，傳回：
    *   `live_events`：代理程式事件 (文字、音訊、完成) 的非同步可迭代物件。
    *   `live_request_queue`：向代理程式傳送資料的佇列。

**傳回：** `(live_events, live_request_queue)`。

### `agent_to_client_messaging(websocket, live_events)`

```python

async def agent_to_client_messaging(websocket, live_events):
    """代理程式到客戶端的通訊"""
    while True:
        async for event in live_events:

            # 如果輪次完成或中斷，則傳送
            if event.turn_complete or event.interrupted:
                message = {
                    "turn_complete": event.turn_complete,
                    "interrupted": event.interrupted,
                }
                await websocket.send_text(json.dumps(message))
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
                    await websocket.send_text(json.dumps(message))
                    print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                    continue

            # 如果是文字且是部分文字，則傳送
            if part.text and event.partial:
                message = {
                    "mime_type": "text/plain",
                    "data": part.text
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: text/plain: {message}")
```

此非同步函式將 ADK 代理程式事件串流至 WebSocket 客戶端。

**邏輯：**
1.  迭代來自代理程式的 `live_events`。
2.  **輪次完成/中斷：** 向客戶端傳送狀態旗標。
3.  **內容處理：**
    *   從事件內容中提取第一部分 `Part`。
    *   **音訊資料：** 如果是音訊 (PCM)，則進行 Base64 編碼並以 JSON 格式傳送：`{ "mime_type": "audio/pcm", "data": "<base64_audio>" }`。
    *   **文字資料：** 如果是部分文字，則以 JSON 格式傳送：`{ "mime_type": "text/plain", "data": "<partial_text>" }`。
4.  記錄訊息。

### `client_to_agent_messaging(websocket, live_request_queue)`

```python

async def client_to_agent_messaging(websocket, live_request_queue):
    """客戶端到代理程式的通訊"""
    while True:
        # 解碼 JSON 訊息
        message_json = await websocket.receive_text()
        message = json.loads(message_json)
        mime_type = message["mime_type"]
        data = message["data"]

        # 將訊息傳送給代理程式
        if mime_type == "text/plain":
            # 傳送文字訊息
            content = Content(role="user", parts=[Part.from_text(text=data)])
            live_request_queue.send_content(content=content)
            print(f"[CLIENT TO AGENT]: {data}")
        elif mime_type == "audio/pcm":
            # 傳送音訊資料
            decoded_data = base64.b64decode(data)
            live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
        else:
            raise ValueError(f"不支援的 Mime 類型：{mime_type}")
```

此非同步函式將來自 WebSocket 客戶端的訊息轉發給 ADK 代理程式。

**邏輯：**
1.  接收並解析來自 WebSocket 的 JSON 訊息，預期格式為：`{ "mime_type": "text/plain" | "audio/pcm", "data": "<data>" }`。
2.  **文字輸入：** 對於 "text/plain"，透過 `live_request_queue.send_content()` 將 `Content` 傳送給代理程式。
3.  **音訊輸入：** 對於 "audio/pcm"，解碼 Base64 資料，包裝在 `Blob` 中，並透過 `live_request_queue.send_realtime()` 傳送。
4.  對於不支援的 MIME 類型，引發 `ValueError`。
5.  記錄訊息。

### FastAPI Web 應用程式

```python

app = FastAPI()

STATIC_DIR = Path("static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """提供 index.html"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, is_audio: str):
    """客戶端 websocket 端點"""

    # 等待客戶端連線
    await websocket.accept()
    print(f"客戶端 #{user_id} 已連線，音訊模式：{is_audio}")

    # 啟動代理程式會話
    user_id_str = str(user_id)
    live_events, live_request_queue = await start_agent_session(user_id_str, is_audio == "true")

    # 啟動任務
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )

    # 等待直到 websocket 中斷連線或發生錯誤
    tasks = [agent_to_client_task, client_to_agent_task]
    await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    # 關閉 LiveRequestQueue
    live_request_queue.close()

    # 中斷連線
    print(f"客戶端 #{user_id} 已中斷連線")

```

*   **`app = FastAPI()`**：初始化應用程式。
*   **靜態檔案：** 在 `/static` 下提供 `static` 目錄中的檔案。
*   **`@app.get("/")` (根端點)：** 提供 `index.html`。
*   **`@app.websocket("/ws/{user_id}")` (WebSocket 端點)：**
    *   **路徑參數：** `user_id` (int) 和 `is_audio` (str: "true"/"false")。
    *   **連線處理：**
        1.  接受 WebSocket 連線。
        2.  使用 `user_id` 和 `is_audio` 呼叫 `start_agent_session()`。
        3.  **並行訊息傳遞任務：** 使用 `asyncio.gather` 同時建立並執行 `agent_to_client_messaging` 和 `client_to_agent_messaging`。這些任務處理雙向訊息流。
        4.  記錄客戶端連線和中斷連線。

### 運作方式 (整體流程)

1.  客戶端連線至 `ws://<server>/ws/<user_id>?is_audio=<true_or_false>`。
2.  伺服器的 `websocket_endpoint` 接受連線，啟動 ADK 會話 (`start_agent_session`)。
3.  兩個 `asyncio` 任務管理通訊：
    *   `client_to_agent_messaging`：客戶端 WebSocket 訊息 -> ADK `live_request_queue`。
    *   `agent_to_client_messaging`：ADK `live_events` -> 客戶端 WebSocket。
4.  雙向串流持續進行，直到中斷連線或發生錯誤。

## 5. 客戶端程式碼概觀 {#5.-client-side-code-overview}

JavaScript `app.js` (位於 `app/static/js`) 管理與 ADK 串流 WebSocket 後端的客戶端互動。它處理傳送文字/音訊以及接收/顯示串流回應。

主要功能：
1.  管理 WebSocket 連線。
2.  處理文字輸入。
3.  擷取麥克風音訊 (Web Audio API、AudioWorklets)。
4.  向後端傳送文字/音訊。
5.  接收並渲染文字/音訊代理程式回應。
6.  管理 UI。

### 先決條件

*   **HTML 結構：** 需要特定的元素 ID (例如 `messageForm`, `message`, `messages`, `sendButton`, `startAudioButton`)。
*   **後端伺服器：** Python FastAPI 伺服器必須正在執行。
*   **音訊 Worklet 檔案：** 用於音訊處理的 `audio-player.js` 和 `audio-recorder.js`。

### WebSocket 處理

```JavaScript

// 使用 WebSocket 連線伺服器
const sessionId = Math.random().toString().substring(10);
const ws_url =
  "ws://" + window.location.host + "/ws/" + sessionId;
let websocket = null;
let is_audio = false;

// 取得 DOM 元素
const messageForm = document.getElementById("messageForm");
const messageInput = document.getElementById("message");
const messagesDiv = document.getElementById("messages");
let currentMessageId = null;

// WebSocket 處理常式
function connectWebsocket() {
  // 連線 websocket
  websocket = new WebSocket(ws_url + "?is_audio=" + is_audio);

  // 處理連線開啟
  websocket.onopen = function () {
    // 連線開啟訊息
    console.log("WebSocket connection opened.");
    document.getElementById("messages").textContent = "Connection opened";

    // 啟用傳送按鈕
    document.getElementById("sendButton").disabled = false;
    addSubmitHandler();
  };

  // 處理傳入訊息
  websocket.onmessage = function (event) {
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
  };

  // 處理連線關閉
  websocket.onclose = function () {
    console.log("WebSocket connection closed.");
    document.getElementById("sendButton").disabled = true;
    document.getElementById("messages").textContent = "Connection closed";
    setTimeout(function () {
      console.log("Reconnecting...");
      connectWebsocket();
    }, 5000);
  };

  websocket.onerror = function (e) {
    console.log("WebSocket error: ", e);
  };
}
connectWebsocket();

// 將提交處理常式新增到表單
function addSubmitHandler() {
  messageForm.onsubmit = function (e) {
    e.preventDefault();
    const message = messageInput.value;
    if (message) {
      const p = document.createElement("p");
      p.textContent = "> " + message;
      messagesDiv.appendChild(p);
      messageInput.value = "";
      sendMessage({
        mime_type: "text/plain",
        data: message,
      });
      console.log("[CLIENT TO AGENT] " + message);
    }
    return false;
  };
}

// 以 JSON 字串形式向伺服器傳送訊息
function sendMessage(message) {
  if (websocket && websocket.readyState == WebSocket.OPEN) {
    const messageJson = JSON.stringify(message);
    websocket.send(messageJson);
  }
}

// 將 Base64 資料解碼為陣列
function base64ToArray(base64) {
  const binaryString = window.atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}
```

*   **連線設定：** 產生 `sessionId`，建構 `ws_url`。`is_audio` 旗標 (初始為 `false`) 在啟用時將 `?is_audio=true` 附加到 URL。`connectWebsocket()` 初始化連線。
*   **`websocket.onopen`**：啟用傳送按鈕，更新 UI，呼叫 `addSubmitHandler()`。
*   **`websocket.onmessage`**：解析來自伺服器的傳入 JSON。
    *   **輪次完成：** 如果代理程式輪次完成，則重設 `currentMessageId`。
    *   **音訊資料 (`audio/pcm`)：** 解碼 Base64 音訊 (`base64ToArray()`) 並傳送至 `audioPlayerNode` 進行播放。
    *   **文字資料 (`text/plain`)：** 如果是新輪次 (`currentMessageId` 為 null)，則建立新的 `<p>`。將接收到的文字附加到目前的訊息段落以產生串流效果。捲動 `messagesDiv`。
*   **`websocket.onclose`**：停用傳送按鈕，更新 UI，並在 5 秒後嘗試自動重新連線。
*   **`websocket.onerror`**：記錄錯誤。
*   **初始連線：** 在腳本載入時呼叫 `connectWebsocket()`。

#### DOM 互動與訊息提交

*   **元素檢索：** 擷取所需的 DOM 元素。
*   **`addSubmitHandler()`**：附加到 `messageForm` 的提交事件。防止預設提交，從 `messageInput` 取得文字，顯示使用者訊息，清除輸入，並使用 `{ mime_type: "text/plain", data: messageText }` 呼叫 `sendMessage()`。
*   **`sendMessage(messagePayload)`**：如果 WebSocket 已開啟，則傳送 JSON 字串化的 `messagePayload`。

### 音訊處理

```JavaScript

let audioPlayerNode;
let audioPlayerContext;
let audioRecorderNode;
let audioRecorderContext;
let micStream;

// 匯入音訊 worklet
import { startAudioPlayerWorklet } from "./audio-player.js";
import { startAudioRecorderWorklet } from "./audio-recorder.js";

// 啟動音訊
function startAudio() {
  // 啟動音訊輸出
  startAudioPlayerWorklet().then(([node, ctx]) => {
    audioPlayerNode = node;
    audioPlayerContext = ctx;
  });
  // 啟動音訊輸入
  startAudioRecorderWorklet(audioRecorderHandler).then(
    ([node, ctx, stream]) => {
      audioRecorderNode = node;
      audioRecorderContext = ctx;
      micStream = stream;
    }
  );
}

// 僅在使用者點擊按鈕時才啟動音訊
// (由於 Web Audio API 的手勢要求)
const startAudioButton = document.getElementById("startAudioButton");
startAudioButton.addEventListener("click", () => {
  startAudioButton.disabled = true;
  startAudio();
  is_audio = true;
  connectWebsocket(); // 以音訊模式重新連線
});

// 音訊錄製器處理常式
function audioRecorderHandler(pcmData) {
  // 以 base64 格式傳送 pcm 資料
  sendMessage({
    mime_type: "audio/pcm",
    data: arrayBufferToBase64(pcmData),
  });
  console.log("[CLIENT TO AGENT] sent %s bytes", pcmData.byteLength);
}

// 將陣列緩衝區編碼為 Base64
function arrayBufferToBase64(buffer) {
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}
```

*   **音訊 Worklet：** 透過 `audio-player.js` (用於播放) 和 `audio-recorder.js` (用於擷取) 使用 `AudioWorkletNode`。
*   **狀態變數：** 儲存 AudioContext 和 WorkletNode (例如 `audioPlayerNode`)。
*   **`startAudio()`**：初始化播放器和錄製器 worklet。將 `audioRecorderHandler` 作為回呼傳遞給錄製器。
*   **「啟動音訊」按鈕 (`startAudioButton`)：**
    *   需要使用者手勢才能使用 Web Audio API。
    *   點擊時：停用按鈕，呼叫 `startAudio()`，設定 `is_audio = true`，然後呼叫 `connectWebsocket()` 以音訊模式重新連線 (URL 包含 `?is_audio=true`)。
*   **`audioRecorderHandler(pcmData)`**：來自錄製器 worklet 的回呼，包含 PCM 音訊區塊。將 `pcmData` 編碼為 Base64 (`arrayBufferToBase64()`) 並透過 `sendMessage()` 以 `mime_type: "audio/pcm"` 傳送至伺服器。
*   **輔助函式：** `base64ToArray()` (伺服器音訊 -> 客戶端播放器) 和 `arrayBufferToBase64()` (客戶端麥克風音訊 -> 伺服器)。

### 運作方式 (客戶端流程)

1.  **頁面載入：** 以文字模式建立 WebSocket 連線。
2.  **文字互動：** 使用者輸入/提交文字；傳送至伺服器。伺服器文字回應以串流方式顯示。
3.  **切換至音訊模式：** 點擊「啟動音訊」按鈕會初始化音訊 worklet，設定 `is_audio=true`，並以音訊模式重新連線 WebSocket。
4.  **音訊互動：** 錄製器將麥克風音訊 (Base64 PCM) 傳送至伺服器。伺服器的音訊/文字回應由 `websocket.onmessage` 處理以進行播放/顯示。
5.  **連線管理：** WebSocket 關閉時自動重新連線。


## 摘要

本文概述了使用 ADK 串流和 FastAPI 建構的自訂非同步 Web 應用程式的伺服器和客戶端程式碼，該應用程式可透過 WebSockets 實現即時、雙向的語音和文字通訊。

Python FastAPI 伺服器程式碼會初始化 ADK 代理程式會話，並設定為文字或音訊回應。它使用 WebSocket 端點來處理客戶端連線。非同步任務管理雙向訊息傳遞：將客戶端文字或 Base64 編碼的 PCM 音訊轉發給 ADK 代理程式，並將來自代理程式的文字或 Base64 編碼的 PCM 音訊回應串流回客戶端。

客戶端 JavaScript 程式碼管理 WebSocket 連線，該連線可以重新建立以在文字和音訊模式之間切換。它將使用者輸入 (透過 Web Audio API 和 AudioWorklet 擷取的文字或麥克風音訊) 傳送至伺服器。來自伺服器的傳入訊息會被處理：文字會被顯示 (串流)，而 Base64 編碼的 PCM 音訊會被解碼並使用 AudioWorklet 播放。

### 生產環境的後續步驟

當您在生產應用程式中使用 ADK 的串流功能時，您可能需要考慮以下幾點：

*   **部署多個實例：** 執行多個 FastAPI 應用程式實例，而不是單一一個。
*   **實作負載平衡：** 在您的應用程式實例前放置一個負載平衡器，以分配傳入的 WebSocket 連線。
    *   **為 WebSocket 設定：** 確保負載平衡器支援長效的 WebSocket 連線，並考慮「黏性會話」(會話親和性) 將客戶端路由到同一個後端實例，*或者*設計為無狀態實例 (請參閱下一個要點)。
*   **外部化會話狀態：** 將 ADK 的 `InMemorySessionService` 替換為分散式、持久性的會話儲存。這允許任何伺服器實例處理任何使用者的會話，從而在應用程式伺服器層級實現真正的無狀態，並提高容錯能力。
*   **實作健康檢查：** 為您的 WebSocket 伺服器實例設定健全的健康檢查，以便負載平衡器可以自動從輪替中移除不健康的實例。
*   **利用協同運作平台：** 考慮使用像 Kubernetes 這樣的協同運作平台來自動化部署、擴展、自我修復和管理您的 WebSocket 伺服器實例。
```
The file is already translated. I will overwrite it to be sure.我會將 `adk-docs/streaming/custom-streaming-ws.md` 的內容翻譯成繁體中文。此檔案似乎已翻譯，但我會用以下內容覆寫以確保一致性。
