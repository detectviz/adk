/**
 * 用於雙向音訊 AI 通訊的音訊處理用戶端
 */

class SoundHandler {
    constructor(serverUrl = 'ws://localhost:8765') {
        this.serverUrl = serverUrl;
        this.ws = null;
        this.recorder = null;
        this.audioContext = null;
        this.isConnected = false;
        this.isRecording = false;
        this.isModelSpeaking = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 3;
        this.sessionId = null;

        // 回呼函式
        this.onReady = () => { };
        this.onAudioReceived = () => { };
        this.onTextReceived = () => { };
        this.onUserTranscript = () => { };
        this.onTurnComplete = () => { };
        this.onError = () => { };
        this.onInterrupted = () => { };
        this.onSessionIdReceived = (sessionId) => { };

        // 音訊播放
        this.audioQueue = [];
        this.isPlaying = false;
        this.currentSource = null;

        // 清理任何現有的 audioContexts
        if (window.existingAudioContexts) {
            window.existingAudioContexts.forEach(ctx => {
                try {
                    ctx.close();
                } catch (e) {
                    console.error("關閉現有音訊內容時出錯：", e);
                }
            });
        }

        // 追蹤已建立的音訊內容
        window.existingAudioContexts = window.existingAudioContexts || [];
    }

    // 連接到 WebSocket 伺服器
    async openConnection() {
        // 如有現有連線，則關閉
        if (this.ws) {
            try {
                this.ws.close();
            } catch (e) {
                console.error("關閉 WebSocket 時出錯：", e);
            }
        }

        // 如果是新連線，則重設重新連線嘗試次數
        if (this.reconnectAttempts > this.maxReconnectAttempts) {
            this.reconnectAttempts = 0;
        }

        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(this.serverUrl);

                const connectionTimeout = setTimeout(() => {
                    if (!this.isConnected) {
                        console.error('連線逾時');
                        this.attemptReconnect();
                        reject(new Error('連線逾時'));
                    }
                }, 5000);

                this.ws.onopen = () => {
                    console.log('連線已建立');
                    clearTimeout(connectionTimeout);
                    this.reconnectAttempts = 0; // 連線成功後重設
                };

                this.ws.onclose = (event) => {
                    console.log('連線已關閉：', event.code, event.reason);
                    this.isConnected = false;

                    // 如果不是正常關閉，請嘗試重新連線
                    if (event.code !== 1000 && event.code !== 1001) {
                        this.attemptReconnect();
                    }
                };

                this.ws.onerror = (error) => {
                    console.error('連線錯誤：', error);
                    clearTimeout(connectionTimeout);
                    this.onError(error);
                    reject(error);
                };

                this.ws.onmessage = async (event) => {
                    try {
                        // 記錄原始訊息資料以協助偵錯
                        console.log('收到原始訊息：', event.data);

                        const message = JSON.parse(event.data);

                        if (message.type === 'ready') {
                            this.isConnected = true;
                            this.onReady();
                            resolve();
                        }
                        else if (message.type === 'audio') {
                            // 處理從伺服器接收音訊資料
                            const audioData = message.data;
                            this.onAudioReceived(audioData);
                            await this.playSound(audioData);
                        }
                        else if (message.type === 'text') {
                            // 處理從伺服器接收文字
                            this.onTextReceived(message.data);
                        }
                        else if (message.type === 'user_transcript') {
                            // 處理從伺服器接收使用者轉錄
                            this.onUserTranscript(message.data);
                        }
                        else if (message.type === 'turn_complete') {
                            // 模型已說完
                            this.isModelSpeaking = false;
                            this.onTurnComplete();
                        }
                        else if (message.type === 'interrupted') {
                            // 回應已中斷
                            this.isModelSpeaking = false;
                            this.onInterrupted(message.data);
                        }
                        else if (message.type === 'error') {
                            // 處理伺服器錯誤
                            this.onError(message.data);
                        }
                        else if (message.type === 'session_id') {
                            // 處理會話 ID
                            console.log('收到會話 ID：', message);
                            this.sessionId = message.data;
                            this.onSessionIdReceived(message.data);
                        }
                    } catch (error) {
                        console.error('處理訊息時出錯：', error);
                    }
                };
            } catch (error) {
                console.error('建立連線時出錯：', error);
                reject(error);
            }
        });
    }

    // 嘗試以指數退避方式重新連線
    async attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('已達最大重新連線嘗試次數');
            return;
        }

        this.reconnectAttempts++;
        const backoffTime = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);

        console.log(`在 ${backoffTime} 毫秒後重新連線 (嘗試次數 ${this.reconnectAttempts})`);

        setTimeout(async () => {
            try {
                await this.openConnection();
                console.log('重新連線成功');
            } catch (error) {
                console.error('重新連線失敗：', error);
            }
        }, backoffTime);
    }

    // 初始化音訊內容和錄音機
    async setupAudio() {
        try {
            // 請求麥克風存取權限
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // 如果可用，重複使用現有音訊內容，或建立新的音訊內容
            if (!this.audioContext || this.audioContext.state === 'closed') {
                console.log("正在建立新的音訊內容");
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                    sampleRate: 16000 // 符合伺服器預期的取樣率
                });

                // 追蹤此內容以進行清理
                window.existingAudioContexts = window.existingAudioContexts || [];
                window.existingAudioContexts.push(this.audioContext);
            }

            // 建立 MediaStreamSource
            const source = this.audioContext.createMediaStreamSource(stream);

            // 建立 ScriptProcessor 以進行音訊處理
            const processor = this.audioContext.createScriptProcessor(4096, 1, 1);

            processor.onaudioprocess = (e) => {
                if (!this.isRecording) return;

                // 取得音訊資料
                const inputData = e.inputBuffer.getChannelData(0);

                // 將 float32 轉換為 int16
                const int16Data = new Int16Array(inputData.length);
                for (let i = 0; i < inputData.length; i++) {
                    int16Data[i] = Math.max(-32768, Math.min(32767, Math.floor(inputData[i] * 32768)));
                }

                // 如果已連線，則傳送至伺服器
                if (this.isConnected && this.isRecording) {
                    const audioBuffer = new Uint8Array(int16Data.buffer);
                    const base64Audio = this._arrayBufferToBase64(audioBuffer);

                    this.ws.send(JSON.stringify({
                        type: 'audio',
                        data: base64Audio
                    }));
                }
            };

            // 連接音訊節點
            source.connect(processor);
            processor.connect(this.audioContext.destination);

            this.recorder = {
                source: source,
                processor: processor,
                stream: stream
            };

            return true;
        } catch (error) {
            console.error('設定音訊時出錯：', error);
            this.onError(error);
            return false;
        }
    }

    // 開始錄製音訊
    async start() {
        if (!this.recorder) {
            const initialized = await this.setupAudio();
            if (!initialized) return false;
        }

        if (!this.isConnected) {
            try {
                await this.openConnection();
            } catch (error) {
                console.error('開啟連線失敗：', error);
                return false;
            }
        }

        this.isRecording = true;
        return true;
    }

    // 停止錄製音訊
    stop() {
        this.isRecording = false;

        // 將結束訊息傳送至伺服器
        if (this.isConnected) {
            this.ws.send(JSON.stringify({
                type: 'end'
            }));
        }
    }

    // 解碼並播放收到的音訊
    async playSound(base64Audio) {
        try {
            // 解碼 base64 音訊資料
            const audioData = this._base64ToArrayBuffer(base64Audio);

            // 如有需要，建立音訊內容
            if (!this.audioContext || this.audioContext.state === 'closed') {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                    sampleRate: 24000 // 符合從伺服器收到的取樣率
                });

                // 追蹤此內容以進行清理
                window.existingAudioContexts.push(this.audioContext);

                // 限制我們追蹤的內容數量以避免記憶體問題
                if (window.existingAudioContexts.length > 5) {
                    const oldContext = window.existingAudioContexts.shift();
                    try {
                        if (oldContext && oldContext !== this.audioContext && oldContext.state !== 'closed') {
                            oldContext.close();
                        }
                    } catch (e) {
                        console.error("關閉舊音訊內容時出錯：", e);
                    }
                }
            }

            // 如果音訊內容已暫停，則繼續
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }

            // 新增至音訊佇列
            this.audioQueue.push(audioData);

            // 如果目前未播放，則開始播放
            if (!this.isPlaying) {
                this.playNext();
            }

            // 設定旗標以表示模型正在說話
            this.isModelSpeaking = true;
        } catch (error) {
            console.error('播放聲音時出錯：', error);
        }
    }

    // 從佇列播放下一個音訊區塊
    playNext() {
        if (this.audioQueue.length === 0) {
            this.isPlaying = false;
            return;
        }

        this.isPlaying = true;

        try {
            // 如果仍在使用中，則停止任何先前的來源
            if (this.currentSource) {
                try {
                    this.currentSource.onended = null; // 移除事件監聽器
                    this.currentSource.stop();
                    this.currentSource.disconnect();
                } catch (e) {
                    // 如果已停止，則忽略錯誤
                }
                this.currentSource = null;
            }

            // 從佇列取得下一個音訊資料
            const audioData = this.audioQueue.shift();

            // 將 Int16Array 轉換為 Float32Array 以用於 AudioBuffer
            const int16Array = new Int16Array(audioData);
            const float32Array = new Float32Array(int16Array.length);
            for (let i = 0; i < int16Array.length; i++) {
                float32Array[i] = int16Array[i] / 32768.0;
            }

            // 建立 AudioBuffer
            const audioBuffer = this.audioContext.createBuffer(1, float32Array.length, 24000);
            audioBuffer.getChannelData(0).set(float32Array);

            // 建立來源節點
            const source = this.audioContext.createBufferSource();
            source.buffer = audioBuffer;

            // 儲存目前來源的參考
            this.currentSource = source;

            // 連接到目的地
            source.connect(this.audioContext.destination);

            // 當此緩衝區結束時，播放下一個
            source.onended = () => {
                this.currentSource = null;
                this.playNext();
            };

            // 開始播放
            source.start(0);
        } catch (error) {
            console.error('聲音播放期間發生錯誤：', error);
            this.currentSource = null;
            // 發生錯誤時嘗試下一個緩衝區
            setTimeout(() => this.playNext(), 100);
        }
    }

    // 中斷目前播放
    interrupt() {
        this.isModelSpeaking = false;

        // 如果目前音訊來源正在使用中，則停止
        if (this.currentSource) {
            try {
                this.currentSource.onended = null; // 移除事件監聽器
                this.currentSource.stop();
                this.currentSource.disconnect();
            } catch (e) {
                // 如果已停止，則忽略錯誤
            }
            this.currentSource = null;
        }

        // 清除佇列並重設播放狀態
        this.audioQueue = [];
        this.isPlaying = false;
    }

    // 清理資源
    close() {
        this.stop();

        // 重設會話 ID
        this.sessionId = null;

        // 停止任何音訊播放
        this.interrupt();
        this.isModelSpeaking = false;

        // 清理錄音機
        if (this.recorder) {
            try {
                this.recorder.stream.getTracks().forEach(track => track.stop());
                this.recorder.source.disconnect();
                this.recorder.processor.disconnect();
                this.recorder = null;
            } catch (e) {
                console.error("清理錄音機時出錯：", e);
            }
        }

        // 關閉音訊內容
        if (this.audioContext && this.audioContext.state !== 'closed') {
            try {
                this.audioContext.close().catch(e => console.error("關閉音訊內容時出錯：", e));
            } catch (e) {
                console.error("關閉音訊內容時出錯：", e);
            }
        }

        // 關閉 WebSocket
        if (this.ws) {
            try {
                if (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING) {
                    this.ws.close();
                }
                this.ws = null;
            } catch (e) {
                console.error("關閉 WebSocket 時出錯：", e);
            }
        }

        this.isConnected = false;
    }

    // 公用程式：將 ArrayBuffer 轉換為 Base64
    _arrayBufferToBase64(buffer) {
        let binary = '';
        const bytes = new Uint8Array(buffer);
        const len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }

    // 公用程式：將 Base64 轉換為 ArrayBuffer
    _base64ToArrayBuffer(base64) {
        const binaryString = atob(base64);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        return bytes.buffer;
    }
}