# 使用多代理 (Multi-Agent) 進行資料科學

## 總覽

本專案展示了一個專為複雜資料分析設計的多代理 (Multi-Agent) 系統。它整合了數個專門的代理，以處理資料流程的不同環節，從資料擷取到進階分析與機器學習。此系統設計用於與 BigQuery 互動，執行複雜的資料操作、產生資料視覺化圖表，並使用 BigQuery ML (BQML) 執行機器學習任務。此代理不僅能產生文字回應，還能生成用於資料分析與探索的視覺化圖表，包括各式圖形。

▶️ **觀看影片教學：** [如何使用 ADK 建立資料科學代理](https://www.youtube.com/watch?v=efcUXoMX818)

## 代理詳細資訊
資料科學多代理 (Multi-Agent) 的主要功能包括：

| 功能 | 描述 |
| --- | --- |
| **互動類型：** | 對話式 |
| **複雜度：** | 進階 |
| **代理類型：** | 多代理 (Multi Agent) |
| **元件：** | 工具 (Tools)、代理工具 (AgentTools)、會話記憶體 (Session Memory)、RAG |
| **垂直領域：** | 所有 (適用於需要進階資料分析的各行各業) |


### 架構
![資料科學架構](data-science-architecture.png)

### 主要功能

*   **多代理架構 (Multi-Agent Architecture)：** 利用一個頂層代理來協調多個子代理，每個子代理專精於特定任務。
*   **資料庫互動 (NL2SQL)：** 使用一個資料庫代理，透過自然語言查詢與 BigQuery 互動，並將其翻譯成 SQL。
*   **資料科學分析 (NL2Py)：** 包含一個資料科學代理，能根據自然語言指令，使用 Python 進行資料分析與視覺化。
*   **機器學習 (BQML)：** 配備一個 BQML 代理，利用 BigQuery ML 進行機器學習模型的訓練與評估。
*   **程式碼直譯器整合 (Code Interpreter Integration)：** 支援在 Vertex AI 中使用程式碼直譯器擴充功能來執行 Python 程式碼，從而實現複雜的資料分析與操作。
*   **ADK Web GUI：** 提供一個使用者友善的圖形化介面 (GUI)，方便與代理互動。
*   **可測試性：** 包含一套完整的測試組，以確保代理的可靠性。



## 設定與安裝

### 先決條件

*   **Google Cloud 帳號：** 您需要一個已啟用 BigQuery 的 Google Cloud 帳號。
*   **Python 3.12+：** 請確保您已安裝 Python 3.12 或更新版本。
*   **Poetry：** 請依照 [Poetry 官方網站](https://python-poetry.org/docs/) 的說明安裝 Poetry。
*   **Git：** 請確保您已安裝 Git。如果尚未安裝，您可以從 [https://git-scm.com/](https://git-scm.com/) 下載並依照[安裝指南](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)進行安裝。



### 使用 Poetry 進行專案設定

1.  **複製儲存庫：**

    ```bash
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/python/agents/data-science
    ```

2.  **使用 Poetry 安裝相依套件：**

    ```bash
    poetry install
    ```

    此指令會讀取 `pyproject.toml` 檔案，並將所有必要的相依套件安裝到由 Poetry 管理的虛擬環境中。

3.  **啟動 Poetry Shell：**

    ```bash
    poetry env activate
    ```

    這會啟動虛擬環境，讓您可以在專案的環境中執行指令。為確保環境已啟動，可使用例如：

    ```bash
    $> poetry env list
       data-science-FAlhSuLn-py3.13 (Activated)
    ```

    如果上述指令未為您啟動環境，您也可以透過以下方式啟動：

     ```bash
    source $(poetry env info --path)/bin/activate
    ```

4.  **設定環境變數：**
    將檔案 `.env.example` 重新命名為 `.env`
    填寫以下值：

    ```bash
    # 選擇模型後端：0 -> ML Dev, 1 -> Vertex
    GOOGLE_GENAI_USE_VERTEXAI=1

    # ML Dev 後端設定。若使用 ML Dev 後端請填寫。
    GOOGLE_API_KEY='您的數值'

    # Vertex 後端設定
    GOOGLE_CLOUD_PROJECT='您的數值'
    GOOGLE_CLOUD_LOCATION='您的數值'
    ```

    請依照下列步驟設定其餘的環境變數。

5.  **BigQuery 設定：**
    這些步驟會將本儲存庫中提供的範例資料載入到 BigQuery。
    在我們的範例使用案例中，我們處理的是來自 Kaggle 的預測貼紙銷售資料：

    _Walter Reade and Elizabeth Park. Forecasting Sticker Sales. https://kaggle.com/competitions/playground-series-s5e1, 2025. Kaggle._

    *   首先，在 `.env` 檔案中設定 BigQuery 的專案 ID。這可以與您用於 `GOOGLE_CLOUD_PROJECT` 的 GCP 專案相同，但您也可以使用其他 BigQuery 專案，只要您有權限存取該專案即可。
        *   在某些情況下，您可能會想將 BigQuery 的運算耗用與資料儲存分開。您可以將 `BQ_DATA_PROJECT_ID` 設定為您用於資料儲存的專案，並將 `BQ_COMPUTE_PROJECT_ID` 設定為您想用於運算的專案。
        *   否則，您可以將 `BQ_DATA_PROJECT_ID` 和 `BQ_COMPUTE_PROJECT_ID` 設定為相同的專案 ID。

        如果您有現有的 BigQuery 資料表想要連接，也請在 `.env` 檔案中指定 `BQ_DATASET_ID`。
        如果您想使用範例資料，請確保保留 `BQ_DATASET_ID='forecasting_sticker_sales'`。

        或者，您也可以從終端機設定變數：

        ```bash
        export BQ_DATA_PROJECT_ID='您的-BQ-資料-專案-ID'
        export BQ_COMPUTE_PROJECT_ID='您的-BQ-運算-專案-ID'
        export BQ_DATASET_ID='您的-資料集-ID' # 如果使用範例資料，請保留 'forecasting_sticker_sales'
        ```

        如果您使用自己的資料，可以跳過上傳步驟。我們建議不要將任何生產關鍵資料集加入此範例代理。
        如果您想使用範例資料，請繼續下一步。

    *   您會在 `data-science/data_science/utils/data/` 中找到資料集。
        請確保您仍在工作目錄 (`agents/data-science`) 中。若要將測試和訓練資料表載入 BigQuery，請執行以下指令：
        ```bash
        python3 data_science/utils/create_bq_table.py
        ```


6.  **BQML 設定：**
    BQML 代理使用 Vertex AI RAG 引擎來查詢完整的 BigQuery ML 參考指南。

    在執行設定之前，請確保您的專案 ID 已新增至 `.env` 檔案中：`"GOOGLE_CLOUD_PROJECT"`。
    請將 `.env` 檔案中的語料庫名稱留空：`BQML_RAG_CORPUS_NAME = ''`。語料庫名稱將在建立後自動新增。

    若要為您的專案設定 RAG 語料庫，請在 `data-science/data_science/utils/reference_guide_RAG.py` 中執行 `create_RAG_corpus()` 和 `ingest_files()` 方法，方法是從工作目錄執行以下指令：

    ```bash
    python3 data_science/utils/reference_guide_RAG.py
    ```


7.  **其他環境變數：**

    *   `NL2SQL_METHOD`：（可選）`BASELINE` 或 `CHASE`。設定 SQL 生成的方法。Baseline 直接使用 Gemini，而 CHASE 使用 [CHASE-SQL](https://arxiv.org/abs/2410.01943)。
    *   `CODE_INTERPRETER_EXTENSION_NAME`：（可選）Vertex AI 中預先存在的程式碼直譯器擴充功能的完整資源名稱。如果未提供，將會建立一個新的擴充功能。（例如：`projects/<您的_專案_ID>/locations/<您的_位置>/extensions/<您的_擴充功能_ID>`）。
        請檢查日誌/終端機以取得新建立的程式碼直譯器擴充功能的 ID，並在您的環境變數中提供該值，以避免建立多個擴充功能。

    從終端機：

    ```bash
    export CODE_INTERPRETER_EXTENSION_NAME='projects/<您的_專案_ID>/locations/us-central1/extensions/<您的_擴充功能_ID>'
    ```

## 執行代理

您可以使用終端機中的 ADK 指令來執行代理。
從工作目錄：

1.  在 CLI 中執行代理：

    ```bash
    poetry run adk run data_science
    ```

2.  使用 ADK Web UI 執行代理：
    ```bash
    poetry run adk web
    ```
    從下拉式選單中選取 data_science



### 代理互動範例

以下是一個使用者如何與資料科學多代理系統互動的快速範例：

> ´**使用者：** 你好，你有哪些資料的存取權限？

> **代理：** 我可以存取 `train` 和 `test` 這兩個資料表。兩個資料表都包含貼紙銷售資料，欄位如下：`id`、`date`、`country`、`store`、`product` 和 `num_sold`。

> **使用者：** 我需要 train 資料表的更多詳細資訊。有哪些國家？有多少家商店？

> **代理：** 結果：train 資料表包含來自加拿大、芬蘭、義大利、肯亞、挪威和新加坡的資料。這些國家各有 3 家不同的商店。

>說明：資料庫代理對 train 資料表執行了一條 SQL 查詢，以找出不同的國家以及每個國家內不同商店的數量。該查詢按國家分組結果，並計算了不同商店值的數量。

> **使用者：** 請產生一個各國總銷售額的圖表。

> **代理：** 結果：已產生一個顯示各國總銷售額的長條圖。x 軸代表國家，y 軸代表總銷售額。

> 說明：
> 1. 首先呼叫資料庫代理，從 train 資料表中擷取各國的總銷售額。
> 2. 然後呼叫資料科學代理，產生一個將結果視覺化的長條圖。該圖表在 x 軸上顯示每個國家，在 y 軸上顯示其對應的總銷售額。

> **使用者：** 我可以在 BQML 中訓練哪些類型的預測模型？

> **代理：** 您可以在 BQML 中訓練多種類型的預測模型，包括 ARIMA、指數平滑法 (Exponential Smoothing) 和時序融合轉換器 (Temporal Fusion Transformer, TFT) 模型。您想繼續訓練預測模型嗎？

> **使用者：** 是的

> **代理：** 好的，在繼續之前，讓我們確認一下 BQML 的專案和資料集 ID。我們將使用 `PROJECT_ID` 專案和 `forecasting_sticker_sales` 資料集。這樣對嗎？

> **使用者：** 是的

> **代理：** BQML 支援 `ARIMA_PLUS`、`ARIMA_PLUS_XREG`。

>若要繼續，我需要知道您想使用哪種模型。我還需要知道以下資訊：

>*   提供時間點的欄位名稱（例如：'date'）。
>*   包含要預測資料的欄位名稱（例如：'num_sold'）。
>*   您是否想使用單一查詢來擬合和預測多個時間序列？如果是，ID 欄位是什麼？（例如：`country`、`store`、`product`）


## 測試與評估

若要執行測試與評估程式碼，您需要一些額外的相依套件。請從 `agents/data-science` 目錄執行以下 Poetry 指令來安裝它們：
```bash
poetry install --with=dev
```

### 執行評估


評估測試以整體的方式評量代理的整體效能與能力。

**執行評估測試：**

    ```bash
    poetry run pytest eval
    ```


- 此指令會執行 `eval/` 目錄中的所有測試檔案。
- `poetry run` 確保 pytest 在專案的虛擬環境中執行。



### 執行測試

測試評量代理的整體可執行性。

**測試類別：**

*   **整合測試 (Integration Tests)：** 這些測試驗證代理之間以及與 BigQuery 等外部服務之間是否能正確互動。它們確保根代理可以將任務委派給適當的子代理，且子代理可以執行其預期任務。
*   **子代理功能測試 (Sub-Agent Functionality Tests)：** 這些測試專注於每個子代理（例如資料庫代理、BQML 代理）的特定能力。它們確保每個子代理都能執行其預期任務，例如執行 SQL 查詢或訓練 BQML 模型。
*   **環境查詢測試 (Environment Query Tests)：** 這些測試驗證代理是否能處理基於環境的查詢。

**執行測試：**

    ```bash
    poetry run pytest tests
    ```

- 此指令會執行 `tests/` 目錄中的所有測試檔案。
- `poetry run` 確保 pytest 在專案的虛擬環境中執行。



## 在 Vertex AI Agent Engine 上部署

若要將代理部署到 Google Agent Engine，請先依照
[這些步驟](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/set-up)
設定您的 Google Cloud 專案以使用 Agent Engine。

您還需要授予 BigQuery 使用者、BigQuery 資料檢視者和 Vertex AI 使用者
權限給 Reasoning Engine 服務代理。請執行以下指令以授予所需權限：

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
gcloud projects add-iam-policy-binding ${GOOGLE_CLOUD_PROJECT} \
    --member="serviceAccount:${RE_SA}" \
    --condition=None \
    --role="roles/aiplatform.user"
```

接下來，您需要為您的代理建立一個 `.whl` 檔案。從 `data-science`
目錄執行此指令：

```bash
poetry build --format=wheel --output=deployment
```

這會在 `deployment` 目錄中建立一個名為 `data_science-0.1-py3-none-any.whl` 的檔案。

然後執行以下指令。這會在您的 GCP 專案中建立一個暫存儲存桶，並將代理部署到 Vertex AI Agent Engine：

```bash
cd deployment/
python3 deploy.py --create
```

當此指令傳回時，如果成功，它將印出一個 AgentEngine 資源
名稱，如下所示：
```
projects/************/locations/us-central1/reasoningEngines/7737333693403889664
```
最後一串數字是 AgentEngine 資源 ID。

成功部署您的代理後，您可以使用 `deployment` 目錄中的
`test_deployment.py` 指令碼與其互動。將代理的資源 ID 儲存在環境變數中，然後執行以下指令：

```bash
export RESOURCE_ID=...
export USER_ID=<任何字串>
python test_deployment.py --resource_id=$RESOURCE_ID --user_id=$USER_ID
```

會話將如下所示：
```
找到資源 ID 為 ... 的代理
為使用者 ID ... 建立會話
輸入 'quit' 離開。
輸入：你好。你有什麼資料？
回應：我可以存取 forecasting_sticker_sales 資料集中的 train 和 test 資料表。
...
```

請注意，這*不是*一個功能齊全、可用於生產的 CLI；它僅用於
展示如何使用 Agent Engine API 與已部署的代理互動。

`test_deployment.py` 指令碼的主要部分大致如下：

```python
from vertexai import agent_engines
remote_agent = vertexai.agent_engines.get(RESOURCE_ID)
session = remote_agent.create_session(user_id=USER_ID)
while True:
    user_input = input("輸入：")
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
                print(f"回應：{text_part}")
```

若要刪除代理，請執行以下指令（使用先前傳回的資源 ID）：
```bash
python3 deployment/deploy.py --delete --resource_id=RESOURCE_ID
```



## 最佳化與調整提示

*   **提示詞工程 (Prompt Engineering)：** 為 `root_agent`、`bqml_agent`、`db_agent`
    和 `ds_agent` 優化提示詞，以提高準確性並更有效地引導代理。
    嘗試使用不同的措辭和詳細程度。
*   **擴充 (Extension)：** 使用您自己的 AgentTools 或 sub_agents 來擴充多代理系統。
    您可以透過在 `agents/data-science/data_science/agent.py` 中將額外的工具和子代理新增至根代理來實現。
*   **部分匯入 (Partial imports)：** 如果您只需要多代理系統中的某些功能，
    例如只需要資料代理，您可以將 data_agent 作為 AgentTool 匯入到您自己的根代理中。
*   **模型選擇 (Model Selection)：** 為頂層
    代理和子代理嘗試不同的語言模型，以找到最適合您的資料和
    查詢的效能。


## 疑難排解

*   如果您在執行代理時遇到 `500 內部伺服器錯誤 (Internal Server Errors)`，只需重新執行您最後的指令即可。
    這應該可以解決問題。
*   如果您遇到程式碼直譯器的問題，請檢視日誌以
    了解錯誤。如果您直接與程式碼直譯器擴充功能互動
    而不是透過代理的輔助函式，請確保您對
    檔案/圖片使用 base-64 編碼。
*   如果您在產生的 SQL 中看到錯誤，請嘗試以下方法：
    - 在您的資料表和欄位中包含清楚的描述有助於提高效能
    - 如果您的資料庫很大，請嘗試為結構化連結設定 RAG 管道，方法是將您的資料表結構詳細資訊儲存在向量儲存中


## 免責聲明

此代理範例僅供說明之用，不適用於生產環境。它作為代理的基本範例和個人或團隊開發自己代理的基礎起點。

此範例未經嚴格測試，可能包含錯誤或限制，且不包含生產環境通常所需的功能或最佳化（例如，穩健的錯誤處理、安全措施、可擴展性、效能考量、全面的日誌記錄或進階組態選項）。

使用者對基於此範例的代理的任何進一步開發、測試、安全強化和部署負全部責任。我們建議在使用任何衍生代理於即時或關鍵系統之前，進行徹底的審查、測試並實施適當的保護措施。
