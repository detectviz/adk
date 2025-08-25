/**
 * 用於處理網路攝影機/螢幕視訊和音訊串流至 Gemini Live API 的多模態用戶端
 */

class StreamManager extends SoundHandler {
    constructor(serverUrl = 'wss://adk-audio-assistant-234439745674.us-central1.run.app') {
        super(serverUrl);

        // 視訊串流屬性
        this.videoStream = null;
        this.videoElement = null;
        this.isVideoActive = false;
        this.videoSendInterval = null;
        this.videoFrameRate = 1; // 預設每秒傳送 1 幀
        this.videoMode = null; // '網路攝影機' 或 '螢幕'
        this.screenTrack = null;

        // 覆寫父類別的重新連線設定
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 0; // 防止自動重新連線
        this.isReconnecting = false;
    }

    // 初始化網路攝影機
    async setupWebcam(videoElement) {
        if (!videoElement) {
            console.error('需要視訊元素');
            return false;
        }

        // 首先，清理任何現有的串流
        this.stopVideo();

        this.videoElement = videoElement;
        this.videoMode = 'webcam';

        try {
            // 請求攝影機存取權限
            this.videoStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                }
            });

            // 設定視訊元素來源
            this.videoElement.srcObject = this.videoStream;
            this.isVideoActive = true;

            return true;
        } catch (error) {
            console.error('設定網路攝影機時出錯：', error);
            return false;
        }
    }

    // 初始化螢幕分享
    async setupScreenShare(videoElement) {
        if (!videoElement) {
            console.error('需要視訊元素');
            return false;
        }

        // 首先，清理任何現有的串流
        this.stopVideo();

        this.videoElement = videoElement;
        this.videoMode = 'screen';

        try {
            // 請求螢幕分享存取權限
            this.videoStream = await navigator.mediaDevices.getDisplayMedia({
                video: {
                    cursor: "always"
                },
                audio: false
            });

            // 保留螢幕軌道的參考以進行清理
            this.screenTrack = this.videoStream.getVideoTracks()[0];

            // 監聽使用者透過瀏覽器 UI 停止分享的事件
            this.screenTrack.onended = () => {
                console.log('使用者已結束螢幕分享');
                this.stopVideo();
                // 觸發自訂事件以更新 UI
                window.dispatchEvent(new CustomEvent('screenshare-ended'));
            };

            // 設定視訊元素來源
            this.videoElement.srcObject = this.videoStream;
            this.isVideoActive = true;

            return true;
        } catch (error) {
            console.error('設定螢幕分享時出錯：', error);
            return false;
        }
    }

    // 開始將視訊幀傳送至伺服器
    startVideo(frameRate = 1) {
        if (!this.isVideoActive || !this.isConnected) {
            console.error('視訊未啟用或未連接到伺服器');
            return false;
        }

        this.videoFrameRate = frameRate;

        // 如有現有間隔，則清除
        if (this.videoSendInterval) {
            clearInterval(this.videoSendInterval);
        }

        // 建立用於幀擷取的畫布元素
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        // 設定畫布大小以符合視訊
        canvas.width = this.videoElement.videoWidth || 640;
        canvas.height = this.videoElement.videoHeight || 480;

        // 以指定速率開始傳送幀
        this.videoSendInterval = setInterval(() => {
            if (!this.isConnected || !this.isVideoActive) {
                clearInterval(this.videoSendInterval);
                this.videoSendInterval = null;
                return;
            }

            try {
                // 將目前視訊幀繪製到畫布上
                context.drawImage(this.videoElement, 0, 0, canvas.width, canvas.height);

                // 將畫布轉換為 JPEG 資料 URL
                const dataURL = canvas.toDataURL('image/jpeg', 0.7);

                // 從資料 URL 中提取 base64 資料
                const base64Data = dataURL.split(',')[1];

                // 將帶有視訊模式元資料的資料傳送至伺服器
                this.ws.send(JSON.stringify({
                    type: 'video',
                    data: base64Data,
                    mode: this.videoMode || 'webcam'
                }));
            } catch (error) {
                console.error('擷取幀時出錯：', error);
            }
        }, 1000 / this.videoFrameRate);

        return true;
    }

    // 停止傳送視訊幀
    stopVideo() {
        if (this.videoSendInterval) {
            clearInterval(this.videoSendInterval);
            this.videoSendInterval = null;
        }
    }

    // 停止所有視訊
    stop() {
        this.stopVideo();

        if (this.videoStream) {
            this.videoStream.getTracks().forEach(track => track.stop());
            this.videoStream = null;
        }

        if (this.videoElement) {
            this.videoElement.srcObject = null;
        }

        this.screenTrack = null;
        this.isVideoActive = false;
        this.videoMode = null;
    }

    // 取得目前視訊模式
    getVideoMode() {
        return this.videoMode;
    }

    // 檢查視訊是否已啟用
    isVideoStreamActive() {
        return this.isVideoActive;
    }

    // 覆寫連線方法以更謹慎地處理連線
    async openConnection() {
        // 如果已連線或正在連線，請勿再次嘗試連線
        if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
            console.log('已連線或正在連線。不建立新連線。');
            if (this.isConnected) return Promise.resolve();

            // 等待連線完成
            return new Promise((resolve, reject) => {
                const checkConnection = () => {
                    if (this.isConnected) {
                        resolve();
                    } else if (this.ws.readyState === WebSocket.CLOSED || this.ws.readyState === WebSocket.CLOSING) {
                        reject(new Error('WebSocket 在連線嘗試期間關閉'));
                    } else {
                        setTimeout(checkConnection, 100);
                    }
                };
                checkConnection();
            });
        }

        // 如果我們尚未嘗試連線，則實際進行連線
        return super.openConnection();
    }

    // 覆寫 tryReconnect 以更受控制地進行重新連線
    async attemptReconnect() {
        if (this.isReconnecting || this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('由於設定或已在嘗試，因此不重新連線');
            return;
        }

        this.isReconnecting = true;
        this.reconnectAttempts++;

        try {
            await this.openConnection();
            console.log('重新連線成功');
        } catch (error) {
            console.error('重新連線失敗：', error);
        } finally {
            this.isReconnecting = false;
        }
    }

    // 覆寫關閉方法以同時清理視訊資源
    closeConnection() {
        this.stopVideo();
        this.stop();
        super.close();
    }
}
