# 使用 Google ADK 的即時語音助理

本專案使用 Google 助理「鑽石」套件 (ADK) 實作了一個即時、多模態的語音助理。它包含一個處理音訊和視訊串流的 Python 伺服器，以及一個用於使用者互動的網頁用戶端。

## 功能

- **即時音訊串流**：擷取麥克風輸入並將其串流至伺服器進行處理。
- **多模態能力**：支援音訊和視訊資料流。
- **Google ADK 整合**：利用 Google ADK 進行對話式 AI，包括語音轉文字和文字轉語音。
- **函式呼叫**：與 Google 地圖整合，用於基於位置的查詢。
- **網頁用戶端**：用於與助理互動的簡單 HTML 和 JavaScript 用戶端。

## 專案結構

```
.
├── client/
│   ├── interface.html       # 用戶端 UI 的主要 HTML 檔案
│   ├── sound_handler.js     # 管理音訊播放
│   └── stream_manager.js    # 處理 WebSocket 連線和資料串流
├── server/
│   ├── streaming_service.py # 使用 WebSockets 和 Google ADK 的主要 Python 伺服器
│   ├── core_utils.py        # 核心公用程式和設定
│   ├── requirements.txt     # Python 依賴套件
│   └── start_servers.sh     # 啟動伺服器的腳本
└── README.md                # 此檔案
```

## 設定與安裝

### 先決條件

- Python 3.8+
- 用於套件管理的 `pip`
- 一個已啟用所需 API 的有效 Google Cloud 專案。

### 1. 設定環境變數

在 `server/` 目錄中建立一個 `.env` 檔案，並新增您的 Google 地圖 API 金鑰：

```
GOOGLE_MAPS_API_KEY="您的_API_金鑰_放這裡"
```

### 2. 安裝依賴套件

建議使用虛擬環境來管理專案的依賴套件。

```bash
# 前往伺服器目錄
cd server

# 建立虛擬環境
python3 -m venv .venv

# 啟用虛擬環境
# 在 macOS 和 Linux 上：
source .venv/bin/activate
# 在 Windows 上：
# .\.venv\Scripts\activate

# 安裝必要的 Python 套件
pip install -r requirements.txt
```

## 執行應用程式

1.  **啟動伺服器**：
    開啟一個終端機，前往 `server/` 目錄，然後執行啟動腳本：

    ```bash
    cd server
    ./start_servers.sh
    ```

    伺服器將在 `http://localhost:8080` 上啟動。

2.  **開啟用戶端**：
    在您的網頁瀏覽器中開啟 [`client/interface.html`](client/interface.html) 檔案。用戶端將自動連接到 WebSocket 伺服器。

3.  **與助理互動**：
    - 點擊「開始串流」按鈕以開始擷取音訊。
    - 助理將以文字和音訊兩種方式回應。

## 設定

- **伺服器連接埠**：WebSocket 伺服器連接埠可在 [`server/streaming_service.py`](server/streaming_service.py) 中設定。預設為 `8080`。
- **Google ADK 模型**：模型和語音設定可在 [`server/core_utils.py`](server/core_utils.py) 中調整。
