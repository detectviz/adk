# FOMC 研究代理

FOMC 研究代理使用多代理 (multi-agent)、多模態 (multi-modal) 架構，結合工具使用、即時網路存取和外部資料庫整合，針對聯邦公開市場委員會 (Federal Open Market Committee) 的最新會議產生詳細的分析報告。此代理展示了一個多階段、非對話式的代理工作流程，而非傳統的對話式使用者互動。

## 總覽

聯邦公開市場委員會 (FOMC) 是美國政府負責制定利率政策的機構。全球金融市場的參與者都會密切關注並深入分析 FOMC 會議的聲明和新聞稿。

此代理展示了如何使用多代理 (multi-agent) 架構來產生關於聯準會會議等金融市場事件的詳細分析報告。FOMC 研究代理與其他代理略有不同，它在很大程度上是非對話式的——代理的大部分工作是透過各個子代理之間的來回互動完成的。在必要時，它會向使用者詢問關鍵資訊，但通常在沒有人為互動的情況下運作。

這是代理產生分析報告所遵循的高階工作流程 (請注意，步驟 3，「審查記者會影片」，仍在開發中)。
![FOMC Research agent workflow](<FOMC_Research_Agent_Workflow.png>)

## 代理詳情
FOMC 研究代理的主要功能包括：

| 功能 | 描述 |
| --- | --- |
| *互動類型* | 工作流程 (Workflow) |
| *複雜度* | 進階 |
| *代理類型* | 多代理 (Multi Agent) |
| *元件* | 工具 (Tools)、多模態 (Multimodal)、AgentTools |
| *垂直領域* | 金融服務 (Financial Services) |

### 代理架構

此圖表顯示了用於實現此工作流程的代理和工具的詳細架構。
![FOMC Research agent architecture](<fomc-research.svg>)

### 主要功能

##### 代理 (Agents)
* **root_agent:** 代理工作流程的進入點。協調其他代理的活動。
* **research_agent:** 協調各個研究元件的檢索。
* **analysis_agent:** 接收 `research_agent` 的輸出並產生分析報告。
* **retrieve_meeting_data_agent:** 從網路上擷取 FOMC 會議資料。
* **extract_page_data_agent:** 從 HTML 頁面中提取特定資料。
* **summarize_meeting_agent:** 讀取會議記錄並產生摘要。

##### 工具 (Tools)
* **fetch_page_tool**: 封裝用於檢索網頁的 HTTP 請求。
* **store_state_tool**: 在 ToolContext 中儲存特定資訊。
* **analyze_video_tool**: 處理和分析 YouTube 影片。
* **compute_probability_tool**: 根據聯邦基金利率期貨 (Fed Futures) 的定價計算利率變動的機率。
* **compare_statements**: 比較當前和先前的 FOMC 聲明。
* **fetch_transcript**: 檢索 FOMC 會議記錄。

##### 回呼 (Callbacks)
* **rate_limit_callback**: 實作請求速率限制，以最小化 `429: Resource Exhausted` 錯誤。

## 設定與安裝
1.  **先決條件：**

    **Google Cloud SDK 和 GCP 專案：**

    對於 BigQuery 設定和 Agent Engine 部署步驟，您將需要一個 Google Cloud 專案。建立專案後，[安裝 Google Cloud SDK](https://cloud.google.com/sdk/docs/install)。然後執行以下指令來驗證您的專案：
    ```bash
    gcloud auth login
    ```
    您還需要啟用某些 API。執行以下指令以啟用必要的 API：
    ```bash
    gcloud services enable aiplatform.googleapis.com
    gcloud services enable bigquery.googleapis.com
    ```

2.  **安裝：**

    複製此儲存庫並切換到該儲存庫目錄：
    ```
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/python/agents/fomc-research
    ```

    安裝 [Poetry](https://python-poetry.org)

    如果您之前沒有安裝過 poetry，可以透過執行以下指令來安裝：
    ```bash
    pip install poetry
    ```

    安裝 FOMC 研究代理的依賴套件：
    ```bash
    poetry install
    ```

    這也將安裝 `google-adk`（Google Agent Development Kit）的發行版本。

3.  **設定：**

    **環境：**

    儲存庫中包含一個 `.env-example` 檔案。請使用適合您專案的值更新此檔案，並將其另存為 `.env`。此檔案中的值將被讀取到您應用程式的環境中。

    建立 `.env` 檔案後，如果您使用的是 `bash` shell，請執行以下指令將 `.env` 檔案中的變數匯出到您的本機 shell 環境中：
    ```bash
    set -o allexport
    . .env
    set +o allexport
    ```
    如果您不使用 `bash`，您可能需要手動匯出這些變數。

    **BigQuery 設定：**

    您需要建立一個包含聯邦基金利率期貨 (Fed Futures) 定價資料的 BigQuery 表。

    FOMC 研究代理儲存庫包含一個範例資料檔案 (`sample_timeseries_data.csv`)，其中包含 2025 年 1 月 29 日和 3 月 19 日 FOMC 會議的數據。如果您想針對其他 FOMC 會議執行此代理，則需要取得額外的資料。

    要將此資料檔案安裝到您專案的 BigQuery 表中，請在 `fomc-research/deployment` 目錄中執行以下指令：
    ```bash
    python bigquery_setup.py --project_id=$GOOGLE_CLOUD_PROJECT \
        --dataset_id=$GOOGLE_CLOUD_BQ_DATASET \
        --location=$GOOGLE_CLOUD_LOCATION \
        --data_file=sample_timeseries_data.csv
    ```

## 執行代理

**使用 ADK 命令列：**

在 `fomc-research` 目錄下，執行此指令：
```bash
adk run fomc_research
```
初始輸出將包含一個可用於追蹤代理日誌檔案的指令。該指令將類似於：
```bash
tail -F /tmp/agents_log/agent.latest.log
```

**使用 ADK 開發人員 UI：**

在 `fomc-research` 目錄下，執行此指令：
```bash
adk web .
```
它將顯示一個用於示範 UI 的 URL。請將您的瀏覽器指向該 URL。

UI 最初將是空白的。在左上方的下拉式選單中，選擇 `fomc_research` 來載入代理。

代理的日誌將在執行時即時顯示在控制台上。但是，如果您想儲存互動日誌並即時追蹤互動，請使用以下指令：

```bash
adk web . > fomc_research_log.txt 2>&1 &
tail -f fomc_research_log.txt
```

### 範例互動

透過輸入「Hello. What can you do for me?」開始互動。在第一個提示後，給出日期：「2025-01-29」。

互動將如下所示：
```
$ adk run .
Log setup complete: /tmp/agents_log/agent.20250405_140937.log
To access latest log: tail -F /tmp/agents_log/agent.latest.log
Running agent root_agent, type exit to exit.
user: Hello. What can you do for me?
[root_agent]: I can help you analyze past Fed Open Market Committee (FOMC) meetings and provide you with a thorough analysis report. To start, please provide the date of the meeting you would like to analyze. If you have already provided it, please confirm the date. I need the date in ISO format (YYYY-MM-DD).

user: 2025-01-29
[analysis_agent]: Here is a summary and analysis of the January 29, 2025 FOMC meeting, based on the available information:
...
```
如果代理在完成分析前停止，請嘗試要求它繼續。

## 在 Vertex AI Agent Engine 上部署

要將代理部署到 Google Agent Engine，請先按照[這些步驟](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/set-up)設定您的 Google Cloud 專案以使用 Agent Engine。

您還需要將 BigQuery 使用者 (BigQuery User) 和 BigQuery 資料檢視者 (BigQuery Data Viewer) 權限授予 Reasoning Engine 服務代理。執行以下指令以授予所需權限：
```bash
export RE_SA="service-${GOOGLE_CLOUD_PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding ${GOOGLE_CLOUD_PROJECT} \
    --member="serviceAccount:${RE_SA}" \
    --condition=None \
    --role="roles/bigquery.user"
gcloud projects add-iam-policy-binding ${GOOGLE_CLOUD_PROJECT} \
    --member="serviceAccount:${RE_SA}" \
    --condition=None \
    --role="roles/bigquery.dataViewer"
```
接下來，您需要為您的代理建立一個 `.whl` 檔案。在 `fomc-research` 目錄下，執行此指令：
```bash
poetry build --format=wheel --output=deployment
```
這將在 `deployment` 目錄中建立一個名為 `fomc_research-0.1-py3-none-any.whl` 的檔案。

然後執行以下指令：
```bash
cd deployment
python3 deploy.py --create
```
當此指令成功返回時，它將印出一個 AgentEngine 資源名稱，如下所示：
```
projects/************/locations/us-central1/reasoningEngines/7737333693403889664
```
最後一串數字是 AgentEngine 資源 ID。

成功部署代理後，您可以使用 `deployment` 目錄中的 `test_deployment.py` 指令碼與其互動。將代理的資源 ID 儲存到環境變數中，並執行以下指令：
```bash
export RESOURCE_ID=...
export USER_ID=<any string>
python test_deployment.py --resource_id=$RESOURCE_ID --user_id=$USER_ID
```
會話將如下所示：
```
Found agent with resource ID: ...
Created session for user ID: ...
Type 'quit' to exit.
Input: Hello. What can you do for me?
Response: I can create an analysis report on FOMC meetings. To start, please provide the date of the meeting you want to analyze. I need the date in YYYY-MM-DD format.

Input: 2025-01-29
Response: I have stored the date you provided. Now I will retrieve the meeting data.
...
```
請注意，這 *不是* 一個功能齊全、可用於生產環境的命令列介面 (CLI)；它僅用於展示如何使用 Agent Engine API 與已部署的代理進行互動。

`test_deploy.py` 指令碼的主要部分大致如下：

```python
from vertexai import agent_engines
remote_agent = vertexai.agent_engines.get(RESOURCE_ID)
session = remote_agent.create_session(user_id=USER_ID)
while True:
    user_input = input("Input: ")
    if user_input == "quit":
      break

    for event in remote_agent.stream_query(
        user_id=USER_ID,
        session_id=session["id"],
        message=user_input,
    ):
        parts = event["content"]["parts"]
        for part in parts:
            if "text" in part:
                text_part = part["text"]
                print(f"Response: {text_part}")
```

要刪除代理，請執行以下指令 (使用先前返回的資源 ID)：
```bash
python3 deployment/deploy.py --delete --resource_id=$RESOURCE_ID
```

## 疑難排解

### "Malformed function call" (函式呼叫格式錯誤)

代理偶爾會返回「Malformed function call」錯誤。這是 Gemini 模型的一個錯誤，應在未來的模型版本中得到解決。只需重新啟動 UI，代理就會重設。

### 代理在工作流程中停止

有時代理會在完成其中一個中間步驟後，在工作流程中停止。發生這種情況時，通常只需告訴代理繼續，或給予其他指令讓其繼續操作即可。


## 免責聲明

此代理範例僅供說明之用，不適用於生產環境。它作為代理的基本範例和一個基礎起點，供個人或團隊開發自己的代理。

此範例未經嚴格測試，可能包含錯誤或限制，並且不包括生產環境通常所需的功能或優化 (例如，穩健的錯誤處理、安全措施、可擴展性、效能考量、全面的日誌記錄或進階設定選項)。

使用者對基於此範例的代理的任何進一步開發、測試、安全強化和部署負全部責任。我們建議在使用任何衍生代理於即時或關鍵系統之前，進行徹底的審查、測試和實施適當的保護措施。
