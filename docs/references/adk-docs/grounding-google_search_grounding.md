# 了解 Google 搜尋的資料基模 (Google Search Grounding)

[Google 搜尋資料基模工具 (Google Search Grounding tool)](../tools/built-in-tools.md#google-search) 是代理開發套件 (Agent Development Kit, ADK) 中的一項強大功能，能讓 AI 代理程式存取來自網路的即時、權威資訊。透過將您的代理程式與 Google 搜尋連結，您可以為使用者提供由可靠來源支援的最新答案。

此功能對於需要當前資訊的查詢特別有價值，例如天氣更新、新聞事件、股票價格，或任何自模型訓練資料截止日期後可能已變更的事實。當您的代理程式確定需要外部資訊時，它會自動執行網路搜尋，並將結果整合到其回應中，並附上適當的來源標註。

## 您將學到什麼

在本指南中，您將了解：

- **快速設定**：如何從頭開始建立並執行一個啟用 Google 搜尋的代理程式
- **資料基模架構**：網路資料基模背後的資料流和技術流程
- **回應結構**：如何解讀資料基模回應及其元數據
- **最佳實踐**：向使用者顯示搜尋結果和引用的指南

### 額外資源

作為額外資源，[Gemini Fullstack 代理開發套件 (ADK) 快速入門](https://github.com/google/adk-samples/tree/main/python/agents/gemini-fullstack) 提供了一個[Google 搜尋資料基模的絕佳實際應用](https://github.com/google/adk-samples/blob/main/python/agents/gemini-fullstack/app/agent.py)，做為一個全端應用程式的範例。

## Google 搜尋資料基模快速入門

本快速入門將引導您建立一個具有 Google 搜尋資料基模功能的 ADK 代理程式。本快速入門假設您擁有一個本地 IDE（VS Code 或 PyCharm 等）、Python 3.9+ 以及終端機存取權限。

### 1. 設定環境並安裝 ADK {#venv-install}

建立並啟用虛擬環境：

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
pip install google-adk==1.4.2
```

### 2. 建立代理程式專案 {#create-agent-project}

在專案目錄下，執行以下指令：

```bash
# 步驟 1：為您的代理程式建立一個新目錄
mkdir google_search_agent

# 步驟 2：為代理程式建立 __init__.py
echo "from . import agent" > google_search_agent/__init__.py

# 步驟 3：建立 agent.py (代理程式定義) 和 .env (Gemini 驗證設定)
touch google_search_agent/agent.py .env
```

#### 編輯 `agent.py`

將以下程式碼複製並貼到 `agent.py` 中：

```python title="google_search_agent/agent.py"
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="google_search_agent",
    model="gemini-2.5-flash",
    instruction="在需要時使用 Google 搜尋回答問題。務必引用來源。",
    description="具備 Google 搜尋能力的專業搜尋助理",
    tools=[google_search]
)
```

現在您應該有以下的目錄結構：

```console
my_project/
    google_search_agent/
        __init__.py
        agent.py
    .env
```

### 3. 選擇一個平台 {#choose-a-platform}

要執行代理程式，您需要選擇一個平台，代理程式將使用該平台來呼叫 Gemini 模型。請從 Google AI Studio 或 Vertex AI 中選擇一個：

=== "Gemini - Google AI Studio"
    1. 從 [Google AI Studio](https://aistudio.google.com/apikey) 取得 API 金鑰。
    2. 使用 Python 時，請開啟 **`.env`** 檔案並複製貼上以下程式碼。

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
        * 從終端機執行 `gcloud auth login` 來驗證 Google Cloud。
        * [啟用 Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)。
    2. 使用 Python 時，請開啟 **`.env`** 檔案並複製貼上以下程式碼，並更新專案 ID 和位置。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=您的專案ID
        GOOGLE_CLOUD_LOCATION=您的位置
        ```

### 4. 執行您的代理程式 {#run-your-agent}

有多種方式可以與您的代理程式互動：

=== "開發者介面 (adk web)"
    執行以下指令以啟動**開發者介面**。

    ```shell
    adk web
    ```
    
    !!!info "給 Windows 使用者的提示"

        如果遇到 `_make_subprocess_transport NotImplementedError` 錯誤，請考慮改用 `adk web --no-reload`。


    **步驟 1：** 在瀏覽器中直接開啟提供的 URL（通常是 `http://localhost:8000` 或 `http://127.0.0.1:8000`）。

    **步驟 2：** 在介面的左上角，您可以在下拉式選單中選擇您的代理程式。選擇 "google_search_agent"。

    !!!note "疑難排解"

        如果您在下拉式選單中沒有看到 "google_search_agent"，請確保您是在代理程式資料夾的**父資料夾**（即 google_search_agent 的父資料夾）中執行 `adk web`。

    **步驟 3：** 現在您可以使用文字框與您的代理程式聊天。

=== "終端機 (adk run)"

    執行以下指令，與您的天氣代理程式聊天。

    ```
    adk run google_search_agent
    ```
    若要結束，請使用 Cmd/Ctrl+C。

### 📝 嘗試的範例提示

透過這些問題，您可以確認代理程式確實正在呼叫 Google 搜尋以取得最新的天氣和時間。

* 紐約現在天氣如何？
* 紐約現在幾點？
* 巴黎現在天氣如何？
* 巴黎現在幾點？

![使用 adk web 試用代理程式](../assets/google_search_grd_adk_web.png)

您已成功使用 ADK 建立並與您的 Google 搜尋代理程式互動！

## Google 搜尋的資料基模如何運作

資料基模 (Grounding) 是將您的代理程式與來自網路的即時資訊連接起來的過程，使其能夠產生更準確、更即時的回應。當使用者的提示需要模型未經訓練或具時效性的資訊時，代理程式底層的大型語言模型會智慧地決定調用 `google_search` 工具來尋找相關事實。

### **資料流圖**

此圖說明了使用者查詢如何產生資料基模回應的逐步過程。

![](../assets/google_search_grd_dataflow.png)

### **詳細說明**

資料基模代理程式使用圖中描述的資料流來檢索、處理外部資訊，並將其整合到呈現給使用者的最終答案中。

1.  **使用者查詢**：終端使用者透過提問或下指令與您的代理程式互動。
2.  **ADK 協調**：代理開發套件 (Agent Development Kit) 協調代理程式的行為，並將使用者的訊息傳遞給代理程式的核心。
3.  **大型語言模型 (LLM) 分析與工具呼叫**：代理程式的 LLM（例如 Gemini 模型）會分析提示。如果它確定需要外部的最新資訊，它會透過呼叫 `google_search` 工具來觸發資料基模機制。這對於回答有關最新新聞、天氣或模型訓練資料中不存在的事實的查詢非常理想。
4.  **資料基模服務互動**：`google_search` 工具與內部資料基模服務互動，該服務會制定並向 Google 搜尋索引發送一個或多個查詢。
5.  **內容注入**：資料基模服務檢索相關的網頁和摘要。然後，在產生最終回應之前，它會將這些搜尋結果整合到模型的內容中。這個關鍵步驟讓模型能夠基於事實、即時的資料進行「推理」。
6.  **產生資料基模回應**：現在，LLM 在新的搜尋結果的幫助下，會產生一個包含檢索到的資訊的回應。
7.  **帶有來源的回應呈現**：ADK 接收最終的資料基模回應，其中包含必要的來源 URL 和 `groundingMetadata`，並將其連同來源標註呈現給使用者。這讓終端使用者可以驗證資訊，並建立對代理程式答案的信任。

### 了解 Google 搜尋的資料基模回應

當代理程式使用 Google 搜尋來為回應提供資料基模時，它會返回一組詳細資訊，不僅包括最終的文字答案，還包括用於產生該答案的來源。此元數據對於驗證回應和提供原始來源的歸屬至關重要。

#### **資料基模回應範例**

以下是模型在經過資料基模查詢後返回的內容物件範例。

**最終答案文字：**

```
"是的，國際邁阿密在他們最近一場 FIFA 世界俱樂部盃比賽中獲勝。他們在第二場小組賽中以 2-1 擊敗了波爾圖足球俱樂部。他們在錦標賽中的第一場比賽是與阿赫利足球俱樂部以 0-0 戰平。國際邁阿密預計將於 2025 年 6 月 23 日星期一對陣帕梅拉斯進行第三場小組賽。"
```

**資料基模元數據摘要：**

```json
"groundingMetadata": {
  "groundingChunks": [
    { "web": { "title": "mlssoccer.com", "uri": "..." } },
    { "web": { "title": "intermiamicf.com", "uri": "..." } },
    { "web": { "title": "mlssoccer.com", "uri": "..." } }
  ],
  "groundingSupports": [
    {
      "groundingChunkIndices": [0, 1],
      "segment": {
        "startIndex": 65,
        "endIndex": 126,
        "text": "他們在第二場小組賽中以 2-1 擊敗了波爾圖足球俱樂部。"
      }
    },
    {
      "groundingChunkIndices": [1],
      "segment": {
        "startIndex": 127,
        "endIndex": 196,
        "text": "他們在錦標賽中的第一場比賽是與阿赫利足球俱樂部以 0-0 戰平。"
      }
    },
    {
      "groundingChunkIndices": [0, 2],
      "segment": {
        "startIndex": 197,
        "endIndex": 303,
        "text": "國際邁阿密預計將於 2025 年 6 月 23 日星期一對陣帕梅拉斯進行第三場小組賽。"
      }
    }
  ],
  "searchEntryPoint": { ... }
}

```

#### **如何解讀回應**

元數據提供了模型產生的文字與支援它的來源之間的連結。以下是逐步分解：

1.  **groundingChunks**：這是模型參考的網頁列表。每個區塊都包含網頁的標題和連結到來源的 `uri`。
2.  **groundingSupports**：此列表將最終答案中的特定句子連結回 `groundingChunks`。
    *   **segment**：此物件識別最終文字答案的特定部分，由其 `startIndex`、`endIndex` 和文字本身定義。
    *   **groundingChunkIndices**：此陣列包含對應於 `groundingChunks` 中所列來源的索引號碼。例如，「他們以 2-1 擊敗了波爾圖足球俱樂部...」這句話的資訊來源於 `groundingChunks` 的索引 0 和 1（來自 mlssoccer.com 和 intermiamicf.com）。

### 如何顯示 Google 搜尋的資料基模回應

使用資料基模的一個關鍵部分是正確顯示資訊，包括引文和搜尋建議，給終端使用者。這能建立信任，並讓使用者驗證資訊。

![來自 Google 搜尋的回應](../assets/google_search_grd_resp.png)

#### **顯示搜尋建議**

`groundingMetadata` 中的 `searchEntryPoint` 物件包含用於顯示搜尋查詢建議的預格式化 HTML。如範例圖片所示，這些通常呈現為可點擊的晶片，讓使用者可以探索相關主題。

**來自 searchEntryPoint 的渲染 HTML：** 元數據提供了必要的 HTML 和 CSS 來渲染搜尋建議列，其中包括 Google 標誌和相關查詢的晶片，例如「下一屆 FIFA 世界俱樂部盃是什麼時候」和「國際邁阿密 FIFA 世界俱樂部盃歷史」。將此 HTML 直接整合到您的應用程式前端將會如預期地顯示建議。

更多資訊，請參閱 Vertex AI 文件中的[使用 Google 搜尋建議](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions)。

## 總結

Google 搜尋資料基模 (Google Search Grounding) 將 AI 代理程式從靜態的知識庫轉變為動態的、與網路連接的助理，能夠提供即時、準確的資訊。透過將此功能整合到您的 ADK 代理程式中，您可以讓它們：

- 存取超出其訓練資料的當前資訊
- 提供來源歸屬以實現透明度和信任
- 提供具有可驗證事實的全面答案
- 透過相關的搜尋建議增強使用者體驗

資料基模過程無縫地將使用者查詢與 Google 龐大的搜尋索引連接起來，用最新的內容豐富回應，同時保持對話的流暢性。透過正確實作和顯示資料基模回應，您的代理程式將成為資訊發現和決策的強大工具。
