# 快速入門 (串流 / Python) {#adk-streaming-quickstart}

透過本快速入門，您將學習如何建立一個簡單的代理，並使用 ADK 串流功能來實現與其低延遲、雙向的語音和視訊通訊。我們將安裝 ADK，設定一個基本的「Google 搜尋」代理，嘗試使用 `adk web` 工具以串流方式執行代理，然後說明如何使用 ADK 串流和 [FastAPI](https://fastapi.tiangolo.com/) 自行建立一個簡單的非同步 Web 應用程式。

**注意：** 本指南假設您在 Windows、Mac 和 Linux 環境中具有使用終端機的經驗。

## 語音/視訊串流支援的模型 {#supported-models}

為了在 ADK 中使用語音/視訊串流，您需要使用支援 Live API 的 Gemini 模型。您可以在文件中找到支援 Gemini Live API 的 **模型 ID**：

- [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
- [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## 1. 設定環境並安裝 ADK {#1.-setup-installation}

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
pip install google-adk
```

## 2. 專案結構 {#2.-project-structure}

使用空檔案建立以下資料夾結構：

```console
adk-streaming/  # 專案資料夾
└── app/ # Web 應用程式資料夾
    ├── .env # Gemini API 金鑰
    └── google_search_agent/ # 代理資料夾
        ├── __init__.py # Python 套件
        └── agent.py # 代理定義
```

### agent.py

將以下程式碼區塊複製並貼到 `agent.py` 檔案中。

對於 `model`，請再次檢查先前在 [模型部分](#supported-models) 中說明的模型 ID。

```py
from google.adk.agents import Agent
from google.adk.tools import google_search  # 匯入工具

root_agent = Agent(
   # 代理的唯一名稱。
   name="basic_search_agent",
   # 代理將使用的大型語言模型 (LLM)。
   # 請填寫支援即時的最新模型 ID
   # https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/#supported-models
   model="...",  # 例如：model="gemini-2.0-flash-live-001" 或 model="gemini-2.0-flash-live-preview-04-09"
   # 代理用途的簡短描述。
   description="使用 Google 搜尋回答問題的代理。",
   # 設定代理行為的說明。
   instruction="你是一位專業的研究員。你總是堅持事實。",
   # 新增 google_search 工具以執行 Google 搜尋的基礎設定。
   tools=[google_search]
)
```

`agent.py` 是儲存所有代理邏輯的地方，您必須定義一個 `root_agent`。

請注意，您是多麼輕易地整合了[使用 Google 搜尋的基礎設定](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search)功能。`Agent` 類別和 `google_search` 工具處理與 LLM 的複雜互動以及與搜尋 API 的基礎設定，讓您能夠專注於代理的*目的*和*行為*。

![intro_components.png](../../assets/quickstart-streaming-tool.png)

將以下程式碼區塊複製並貼到 `__init__.py` 檔案中。

```py title="__init__.py"
from . import agent
```

## 3\. 設定平台 {#3.-set-up-the-platform}

若要執行代理，請從 Google AI Studio 或 Google Cloud Vertex AI 中選擇一個平台：

=== "Gemini - Google AI Studio"
    1. 從 [Google AI Studio](https://aistudio.google.com/apikey) 取得 API 金鑰。
    2. 開啟位於 (`app/`) 內的 **`.env`** 檔案，並複製貼上以下程式碼。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3. 將 `PASTE_YOUR_ACTUAL_API_KEY_HERE` 替換為您實際的 `API KEY`。

=== "Gemini - Google Cloud Vertex AI"
    1. 您需要一個現有的 [Google Cloud](https://cloud.google.com/?e=48754805&hl=en) 帳戶和一個專案。
        * 設定一個 [Google Cloud 專案](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
        * 設定 [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
        * 透過執行 `gcloud auth login` 從終端機向 Google Cloud 進行身份驗證。
        * [啟用 Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)。
    2. 開啟位於 (`app/`) 內的 **`.env`** 檔案。複製貼上以下程式碼並更新專案 ID 和位置。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=PASTE_YOUR_ACTUAL_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=us-central1
        ```

## 4. 使用 `adk web` 試用代理 {#4.-try-it-adk-web}

現在可以試用代理了。執行以下指令以啟動 **開發者介面**。首先，請確保將目前目錄設定為 `app`：

```shell
cd app
```

此外，請使用以下指令設定 `SSL_CERT_FILE` 變數。這對於稍後的語音和視訊測試是必需的。

```shell
export SSL_CERT_FILE=$(python -m certifi)
```

然後，執行開發者介面：

```shell
adk web
```

!!!info "Windows 使用者注意事項"

    當遇到 `_make_subprocess_transport NotImplementedError` 時，請考慮改用 `adk web --no-reload`。


在您的瀏覽器中**直接**開啟提供的 URL (通常是 `http://localhost:8000` 或 `http://127.0.0.1:8000`)。此連線完全保留在您的本機上。選擇 `google_search_agent`。

### 使用文字試用

透過在 UI 中輸入以下提示來試用。

* 紐約的天氣如何？
* 紐約現在幾點？
* 巴黎的天氣如何？
* 巴黎現在幾點？

代理將使用 google_search 工具取得最新資訊來回答這些問題。

### 使用語音和視訊試用

若要使用語音試用，請重新載入網頁瀏覽器，點擊麥克風按鈕以啟用語音輸入，並用語音提出相同的問題。您將即時聽到語音回答。

若要使用視訊試用，請重新載入網頁瀏覽器，點擊攝影機按鈕以啟用視訊輸入，並提出諸如「你看到了什麼？」之類的問題。代理將回答他們在視訊輸入中看到的內容。

(只需點擊一次麥克風或攝影機按鈕即可。您的語音或視訊將被串流傳輸到模型，模型的回應將被持續串流傳輸回來。不支援多次點擊麥克風或攝影機按鈕。)

### 停止工具

在主控台上按 `Ctrl-C` 停止 `adk web`。

### 關於 ADK 串流的注意事項

ADK 串流的未來版本將支援以下功能：回呼、長時間執行工具、範例工具和殼層代理 (例如 SequentialAgent)。

恭喜！您已成功使用 ADK 建立並與您的第一個串流代理互動！

## 後續步驟：建置自訂串流應用程式

在[自訂音訊串流應用程式](streaming-custom-streaming.md)教學中，它概述了使用 ADK 串流和 [FastAPI](https://fastapi.tiangolo.com/) 建置的自訂非同步 Web 應用程式的伺服器和用戶端程式碼，可實現即時、雙向的音訊和文字通訊。
