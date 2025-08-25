# 重新思考語音 AI：使用 Gemini 1.5 的原生音訊功能建構助理的實用指南

多年來，語音助理的藍圖始終如一：一個由語音轉文字 (STT)、大型語言模型 (LLM) 處理，最後是文字轉語音 (TTS) 組成的僵化三步驟。這個流程雖然可用，但卻很笨拙。明顯的延遲、機器人般的語調，以及無法掌握情緒細微差別，都是一個只會翻譯而非真正理解的系統所表現出的症狀。

傳統方法會產生瓶頸，增加延遲並剝奪對話的自然流暢性。具備原生音訊處理功能的 Gemini 1.5 Flash 改變了遊戲規則。

透過在單一、統一的模型中進行端到端的音訊處理，Gemini 消除了笨拙的轉換過程，從而實現了流暢、低延遲的互動，感覺更像是一場真正的對話，而不僅僅是命令與回應。

## 原生音訊的優勢（簡介）

*   **自然對話：** 體驗極其流暢、低延遲的互動，並帶有適當的表達能力和節奏感。
*   **強大的工具整合：** 模型可以在即時對話中使用 Google 搜尋或您自己的自訂函式等工具來擷取即時資訊。
*   **影音理解：** 超越語音。透過即時視訊饋送或螢幕分享，與 AI 討論它所看到的一切。
*   **情感與情境感知對話：** AI 會回應您的語氣，並智慧地忽略背景噪音，了解何時該說話、何時該傾聽。

## 建構 NaviGo AI：逐步指南

讓我們來逐步介紹如何使用 Google 代理開發套件 (ADK) 和一個簡單的網頁介面來建構一個名為「NaviGo AI」的語音優先 AI 旅遊代理。

### 第 1 部分：後端代理 (`streaming_service.py`)

Python 後端使用 WebSockets 來管理與瀏覽器的即時對話串流。

#### 步驟 1.1：定義代理及其工具

首先，我們實例化一個 `Agent`，透過系統指令定義其「NaviGo AI」的角色，並為其配備網頁搜尋和 Google 地圖的工具。

```python
# From streaming_service.py

# MCPToolset 需要您的 Google 地圖 API 金鑰
maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

self.agent = Agent(
    name="voice_assistant_agent",
    model=MODEL, # "gemini-1.5-flash-preview-native-audio-dialog"
    instruction=SYSTEM_INSTRUCTION, # 定義 "NaviGo AI" 的角色
    tools=[
        google_search,
        MCPToolset( # Google 地圖工具
            connection_params=StdioServerParameters(
                command='npx',
                args=["-y", "@modelcontextprotocol/server-google-maps"],
                env={"GOOGLE_MAPS_API_KEY": maps_api_key}
            ),
        )
    ],
)
```

** 使用工具為代理增強功能**

定義代理只是第一步。真正的力量來自我們提供的工具。這正是將我們的語音模型從一個健談者轉變為一個能幹的助理的關鍵。透過整合工具，代理可以突破其預先訓練的知識，並與真實世界進行即時互動。

我們的 NaviGo 代理配備了兩種強大的工具：

*   **Google 搜尋 (`google_search`):** 這是代理通往世界的窗口。它讓 NaviGo 能夠在對話中查詢網路上的任何內容。
*   **Google 地圖 (`MCPToolset`):** 對於旅遊代理來說，這個工具是不可或缺的。它將代理直接連接到 Google 地圖強大的 API。

#### 步驟 1.2：設定即時會話

`RunConfig` 物件告訴代理如何處理串流。我們將其設定為雙向 (BIDI) 音訊，指定我們需要音訊回應，並要求對使用者所說和模型所說的內容進行轉錄。

```python
# From streaming_service.py

run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI, # 雙向串流
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name=VOICE_NAME # 例如 "Puck"
            )
        )
    ),
    response_modalities=["AUDIO"], # 我們希望從模型得到音訊回應
    output_audio_transcription=types.AudioTranscriptionConfig(),
    input_audio_transcription=types.AudioTranscriptionConfig(),
)
```

#### 步驟 1.3：處理即時資料流

我們使用 `asyncio.TaskGroup` 來同時執行多個任務，確保我們可以在不阻塞的情況下同時發送和接收資料。這種架構是實現低延遲體驗的關鍵。

```python
# From streaming_service.py

async with asyncio.TaskGroup() as tg:
    # 任務 1：監聽來自瀏覽器用戶端的音訊訊息
    tg.create_task(receive_client_messages(), name="ClientMessageReceiver")
    
    # 任務 2：將來自用戶端的音訊發送到 Gemini 服務
    tg.create_task(send_audio_to_service(), name="AudioSender")
    
    # 任務 3：監聽來自 Gemini 服務的回應
    tg.create_task(receive_service_responses(), name="ServiceResponseReceiver")
```

#### 步驟 1.4：處理串流回應

在 `receive_service_responses` 中，我們迭代來自代理的事件。串流中的一個主要挑戰是處理部分回應，以避免在前端重複文本。我們檢查事件字串中的一個旗標，以僅處理文本的最終串流區塊。

```python
# From streaming_service.py, inside receive_service_responses

async for event in runner.run_live(...):
    event_str = str(event) # 用於檢查部分旗標

    if event.content and event.content.parts:
        for part in event.content.parts:
            # 處理模型的音訊輸出
            if hasattr(part, "inline_data") and part.inline_data:
                b64_audio = base64.b64encode(part.inline_data.data).decode("utf-8")
                await websocket.send(json.dumps({"type": "audio", "data": b64_audio}))

            # 處理文字輸出
            if hasattr(part, "text") and part.text:
                if "partial=True" in event_str: # 檢查串流區塊
                    await websocket.send(json.dumps({"type": "text", "data": part.text}))
    
    # 讓用戶端知道模型何時完成其回合
    if event.turn_complete:
        await websocket.send(json.dumps({"type": "turn_complete"}))
```

### 第 2 部分：前端用戶端 (`interface.html` & `sound_handler.js`)

前端擷取麥克風音訊並播放代理的語音回應。

#### 步驟 2.1：連接到伺服器

用戶端使用提供給 `StreamManager` 建構函式的 URL 連接到 WebSocket 伺服器。

```javascript
// From interface.html

const stream = new StreamManager('ws://localhost:8765');
```

#### 步驟 2.2：擷取並傳送使用者音訊

當使用者點擊麥克風按鈕時，`sound_handler.js` 使用 `ScriptProcessorNode` 來擷取原始音訊。每個區塊都從瀏覽器的 32 位元浮點格式轉換為模型期望的 16 位元 PCM 格式，進行 Base64 編碼，並透過 WebSocket 發送到伺服器。

```javascript
// From sound_handler.js

processor.onaudioprocess = (e) => {
    if (!this.isRecording) return;

    const inputData = e.inputBuffer.getChannelData(0);

    // 將 float32 轉換為 int16
    const int16Data = new Int16Array(inputData.length);
    for (let i = 0; i < inputData.length; i++) {
        int16Data[i] = Math.max(-32768, Math.min(32767, Math.floor(inputData[i] * 32768)));
    }

    const audioBuffer = new Uint8Array(int16Data.buffer);
    const base64Audio = this._arrayBufferToBase64(audioBuffer);

    // 將音訊區塊發送到伺服器
    this.ws.send(JSON.stringify({
        type: 'audio',
        data: base64Audio
    }));
};
```

#### 步驟 2.3：確保流暢的音訊播放

為避免音訊斷斷續續，從伺服器傳來的音訊區塊會被新增到一個佇列中。`playNext` 函式使用 Web Audio API 按順序播放它們，從而產生流暢、不間斷的語音流。

```javascript
// From sound_handler.js

async playSound(base64Audio) {
    // 解碼並將新的音訊資料新增到佇列中
    const audioData = this._base64ToArrayBuffer(base64Audio);
    this.audioQueue.push(audioData);

    // 如果尚未播放，則開始播放過程
    if (!this.isPlaying) {
        this.playNext();
    }
}

playNext() {
    if (this.audioQueue.length === 0) {
        this.isPlaying = false;
        return;
    }

    this.isPlaying = true;
    const audioData = this.audioQueue.shift(); // 從佇列中獲取下一個區塊

    // ... 使用 Web Audio API 解碼和播放 audioData 的程式碼 ...

    source.onended = () => {
        this.playNext(); // 當一個區塊播放完畢時，播放下一個
    };

    source.start(0);
}
```

#### 步驟 2.4：將事件連接到 UI

最後，在 `interface.html` 中，我們在 `stream` 物件上設定事件監聽器。這些監聽器接收從伺服器傳來的資料，並使用 `updateTranscript` 函式在瀏覽器中動態呈現對話，提供完整的互動體驗。

```javascript
// From interface.html

stream.onUserTranscript = (text) => {
    if (text && text.trim()) {
        updateTranscript(text, 'user', true); // 顯示部分使用者轉錄稿
    }
};

stream.onTextReceived = (text) => {
    if (text && text.trim()) {
        currentResponseText += text;
        updateTranscript(currentResponseText, "assistant", true); // 更新助理的部分回應
    }
};

stream.onTurnComplete = () => {
    // 將最後一則訊息標示為已完成
    const lastMessage = transcriptContainer.lastElementChild;
    if (lastMessage && lastMessage.dataset.partial === 'true') {
        delete lastMessage.dataset.partial;
    }
};
```

## 開始使用

本指南提供了使用 Google 代理開發套件 (ADK) 建構即時語音助理的實用演練。本專案的完整原始碼以及官方文件可在以下連結中找到。

*   專案原始碼
*   Google AI 官方文件
*   Google ADK 範例專案
