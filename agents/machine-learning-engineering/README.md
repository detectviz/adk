# 透過多代理 (Multi-Agent) 實現機器學習工程 (MLE-STAR)

## 總覽

機器學習工程代理 (Machine Learning Engineering Agent) 是一種建構機器學習工程 (MLE) 代理的方法，能夠透過利用網路搜尋和針對性程式碼區塊優化的創新方法，在各種任務（包括分類和回歸任務）上訓練出最先進的機器學習模型。以預測加州房價為例，我們展示了 MLE-STAR 如何根據人口、收入等因素建立一個回歸模型，其表現優於傳統的機器學習模型訓練方法。實驗結果顯示，MLE-STAR 在 MLE-bench-Lite 的 Kaggle 競賽中獲得了 63.6% 的獎牌，顯著優於其他最佳替代方案。此實作基於 Google Cloud AI 研究論文《MLE-STAR: Machine Learning Engineering Agent via Search and Targeted Refinement》(https://www.arxiv.org/abs/2506.15692)。

#### MLE 代理在 [MLE-Bench-Lite](https://github.com/openai/mle-bench/tree/main) 資料集上的表現。

| MLE 代理 | 基礎 LLM | 任何獎牌 | 金牌 | 銀牌 | 銅牌 |
| --- | --- | --- | --- | --- | --- |
| [ **MLE-STAR** ](https://www.arxiv.org/pdf/2506.15692) | **Gemini-2.5-Pro** | **63.6%** | **36.4%** | **21.2%** | 6.1% |
| [ **MLE-STAR** ](https://www.arxiv.org/pdf/2506.15692) | **Gemini-2.5-Flash** | 43.9% | 30.3% | 4.5% | **9.1%** |
---

<br>

## 代理詳細資訊

機器學習代理的主要功能包括：

| 功能 | 描述 |
| --- | --- |
| **互動類型** | 對話式 |
| **複雜度**  | 進階 |
| **代理類型**  | 多代理 (Multi Agent) |
| **元件**  | 工具：程式碼執行、檢索 |
| **垂直領域**  | 所有 |

### 代理架構

此圖表顯示了用於實作此工作流程的代理和工具的詳細架構。
<img src="machine-learning-engineering-architecture.svg" alt="Machine-Learning-Engineering" width="800"/>

### 主要功能

1.  **初始解決方案生成：** 使用搜尋引擎檢索最先進的模型及其範例程式碼，然後將表現最佳的候選方案合併成一個統一的初始解決方案。

2.  **程式碼區塊優化：** 透過消融研究 (ablation studies) 確定對性能影響最顯著的特定程式碼區塊（機器學習管線元件），並對其進行迭代改進。內部迴圈會使用各種策略來優化目標區塊。

3.  **集成策略 (Ensemble Strategies)：** 引入一種新穎的集成方法，代理會提出並優化集成策略，以結合多個解決方案，目標是取得比單一最佳解決方案更優越的性能。

4.  **穩健性模組：** 包括一個用於錯誤修正的除錯代理、一個用於防止在預處理過程中不當存取資料的資料洩漏檢查器，以及一個確保所有提供的資料來源都得到利用的資料使用檢查器。

## 設定與安裝

1.  **先決條件**

    *   Python 3.12+
    *   Poetry
        *   用於依賴管理和封裝。請遵循官方
            [Poetry 網站](https://python-poetry.org/docs/) 上的說明進行安裝。

        ```bash
        pip install poetry
        ```
    *  Git
        *   可從 https://git-scm.com/ 下載 Git。然後遵循[安裝指南](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)。


    * Google Cloud 帳戶
        *   您需要一個 Google Cloud 帳戶
    * 一個 Google Cloud Platform 上的專案
    * Google Cloud CLI
        *   安裝請遵循官方
            [Google Cloud 網站](https://cloud.google.com/sdk/docs/install) 上的說明。

2.  **安裝與設定**

    *   克隆儲存庫
        ```bash
        # 克隆此儲存庫。
        git clone https://github.com/google/adk-samples.git
        cd adk-samples/python/agents/machine-learning-engineering
        ```

    *   安裝 Poetry
        ```bash
        # 安裝 Poetry 套件和依賴項。
        # Linux 使用者請注意：如果在安裝過程中遇到與 `keyring` 相關的錯誤，可以執行以下命令來禁用它：
        # poetry config keyring.enabled false
        # 這是一次性設定。
        poetry install
        ```

        此命令會讀取 `pyproject.toml` 檔案，並將所有必要的依賴項安裝到由 Poetry 管理的虛擬環境中。

        如果上述命令返回 `command not found` 錯誤，請使用：

        ```bash
        python -m poetry install
        ```

    *   啟動 shell

        ```bash
        poetry env activate
        ```

        這會啟動虛擬環境，讓您可以在專案的環境中執行命令。為確保環境已啟動，可使用例如

        ```bash
        $> poetry env list
        machine-learning-engineering-Gb54hHID-py3.12 (Activated)
        ```

        如果上述命令未能為您啟動環境，您也可以透過以下方式啟動：

        ```bash
        source $(poetry env info --path)/bin/activate
        ```

<a name="configuration"></a>

3.  **設定**

    *   設定 Google Cloud 憑證。

        *   您可以在您的 shell 中設定以下環境變數，或
            在一個 `.env` 檔案中設定。

        ```bash
        export GOOGLE_GENAI_USE_VERTEXAI=true
        export GOOGLE_CLOUD_PROJECT=<your-project-id>
        export GOOGLE_CLOUD_LOCATION=<your-project-location>
        export ROOT_AGENT_MODEL=<要使用的 Google LLM>
        export GOOGLE_CLOUD_STORAGE_BUCKET=<your-storage-bucket>  # 僅在 Agent Engine 上部署時需要
        ```

    *   驗證您的 GCloud 帳戶。

        ```bash
        gcloud auth application-default login
        gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
        ```

## 執行代理

**準備您的任務**

您應該以下列方式準備任務的輸入：

1. 在 `tasks` 下建立一個以您的任務命名的資料夾。
2. 在該資料夾中，建立一個包含任務描述的檔案。
3. 將資料檔案放在此資料夾中。

**使用 `adk`**

ADK 提供了在本機啟動代理並與之互動的便利方法。
您可以使用 CLI 與代理對話：

```bash
adk run machine_learning_engineering
```

或透過 Poetry shell：
```bash
poetry run adk run machine_learning_engineering
```

或在網頁介面上：

```bash
 adk web
```

`adk web` 命令將在您的機器上啟動一個網頁伺服器並印出 URL。

### 互動範例

您可以打開該 URL，在左上角的下拉式選單中選擇 "machine_learning_engineering"，
右側將出現一個聊天機器人介面。對話最初是
空白的。以下是您可以向機器學習代理詢問以識別其身分的一些範例請求：

> **[使用者]:** 你是誰？

> **[mle_frontdoor_agent]:** 我是一個機器學習工程師代理。

> **[使用者]:** 你能做什麼？

> **[mle_frontdoor_agent]:** 我是一名機器學習工程師。我的主要職責是為機器學習任務（例如加州房價任務）設計解決方案。如果您願意，我也可以描述這個任務。我透過執行一系列子代理來解決機器學習工程任務。

> **[使用者]:** 描述一下你有的任務

> **[mle_frontdoor_agent]:** 我手上的任務是加州房價任務。此任務涉及根據加州各區的各種特徵來預測其中位數房價。這是一個回歸問題，目標是建立一個能夠根據人口、中位數收入和區內房屋年齡等因素準確估計房價的模型。

> **[使用者]:** 執行任務

> **[mle_frontdoor_agent]:** *\<中間輸出已省略\>*.
<br>
\# 將提交檔案儲存為 CSV，不含索引
print(f"提交檔案已成功儲存至 {submission_file_path}")

## 執行測試

若要執行測試和評估，請安裝額外的依賴項：

```bash
poetry install --with dev
```

然後可以從 `machine-learning-engineering` 目錄使用
`pytest` 模組執行測試和評估：

```bash
python3 -m pytest tests
python3 -m pytest eval
```

`tests` 會在一個範例請求上執行代理，並確保每個元件
都能正常運作。`eval` 則示範如何評估代理，它使用了
ADK 中的 `AgentEvaluator`。它會向代理發送幾個請求，並期望
代理的回應與預先定義的回應相當吻合。


## 部署

您需要在環境變數 `GOOGLE_CLOUD_BUCKET` 中指定一個 GCS 儲存貯體，如[設定](#configuration)部分所述。

如果儲存貯體不存在，ADK 將為您建立一個。這是最簡單的選項。如果儲存貯體已存在，則您必須按照[此](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/troubleshooting/deploy#permission_errors)疑難排解文章中的說明為服務帳戶提供權限。

機器學習工程代理可以使用以下
命令部署到 Vertex AI Agent Engine：

```bash
poetry install --with deployment
python3 deployment/deploy.py --create
```

部署完成後，它將印出如下一行：

```
Created remote agent: projects/<PROJECT_NUMBER>/locations/<PROJECT_LOCATION>/reasoningEngines/<AGENT_ENGINE_ID>
```

如果您忘記了 AGENT_ENGINE_ID，可以使用以下命令列出現有的代理：

```bash
python3 deployment/deploy.py --list
```

輸出將如下所示：

```
All remote agents:

123456789 ("machine_learning_engineering")
- Create time: 2025-07-11 09:46:07+00:00
- Update time: 2025-05-10 09:46:09+00:00
```

您可以使用 `test_deployment.py` 指令碼與已部署的代理互動
```bash
$ export USER_ID=<任何字串>
$ python3 deployment/test_deployment.py --resource_id=${AGENT_ENGINE_ID} --user_id=${USER_ID}
Found agent with resource ID: ...
Created session for user ID: ...
輸入 'quit' 離開。
Input: 你好。你能為我做什麼？
Response: 你好！我是一個機器學習工程師助理。我可以幫助您在解決機器學習任務時達到競賽級別的品質。

若要開始，請提供競賽的任務描述。
```

若要刪除已部署的代理，您可以執行以下命令：

```bash
python3 deployment/deploy.py --delete --resource_id=${AGENT_ENGINE_ID}
```


## 附錄

### 必要設定參數

本文件描述了 `DefaultConfig` dataclass 中必要的設定參數。

---

#### `data_dir`
-   **描述：** 指定儲存機器學習任務及其資料的目錄路徑。
-   **類型：** `str`
-   **預設值：** `"./machine_learning_engineering/tasks/"`

---

#### `task_name`
-   **描述：** 要載入和處理的特定任務的名稱。
-   **類型：** `str`
-   **預設值：** `"california-housing-prices"`

---

#### `task_type`
-   **描述：** 定義機器學習問題的類型。
-   **類型：** `str`
-   **預設值：** `"Tabular Regression"`

---

#### `lower`
-   **描述：** 一個布林標誌，指出指標值越低是否越好。
-   **類型：** `bool`
-   **預設值：** `True`

---

#### `workspace_dir`
-   **描述：** 用於儲存任務執行期間生成的中繼輸出、結果、日誌或任何其他產物的目錄路徑。
-   **類型：** `str`
-   **預設值：** `"./machine_learning_engineering/workspace/"`

---

#### `agent_model`
-   **描述：** 指定代理要使用的 LLM 模型的識別碼。它預設為環境變數 `ROOT_AGENT_MODEL` 的值，如果該變數未設定，則為 `"gemini-2.0-flash-001"`。
-   **類型：** `str`
-   **預設值：** `os.environ.get("ROOT_AGENT_MODEL", "gemini-2.0-flash-001")`
