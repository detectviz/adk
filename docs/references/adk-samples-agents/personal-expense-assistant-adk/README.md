# 使用 Google ADK、Gemini 2.5 Flash 和 Firestore 的個人開銷助理代理

> **⚠️ 免責聲明：這不是 Google 官方支援的產品。此專案僅供示範之用，不適用於生產環境。**

此專案包含用於部署個人助理 (personal assistant) 的範例程式碼，該助理能夠擷取和儲存個人發票和收據，將其儲存在資料庫 (database) 中，並提供搜尋功能。它建置為兩項服務：使用 Gradio 的前端 (frontend) 和使用 FastAPI 的後端服務 (backend services)。它利用 Google ADK 作為代理 (Agent) 框架，Gemini 2.5 Flash 作為語言模型 (language model)，Firestore 作為資料庫 (database)，Google Cloud Storage 作為儲存 (storage)。它還展示了我們如何在 UI 中利用 Gemini 2.5 Flash 的思維過程 (thinking process)。

想要關於這個的詳細教學嗎？請造訪此 Codelab：[https://codelabs.developers.google.com/personal-expense-assistant-multimodal-adk](https://codelabs.developers.google.com/personal-expense-assistant-multimodal-adk?utm_campaign=CDR_0x6a71b73a_default_b404145037&utm_medium=external&utm_source=blog)

## 先決條件

- 如果您是從個人 IDE 執行此專案，請使用以下指令透過 CLI 登入 Gcloud：

    ```shell
    gcloud auth application-default login
    ```

- 準備一個 Google Cloud Storage 儲存貯體 (bucket)

    ```shell
    gsutil mb -l us-central1 gs://personal-expense-assistant-receipts
    ```

- 建立 Firestore 資料庫 (database) `(default)`，其安全規則為開啟（30 天內）且區域為 us-central1

- 啟用以下 API

    ```shell
    gcloud services enable aiplatform.googleapis.com \
                           firestore.googleapis.com \
                           run.googleapis.com \
                           cloudbuild.googleapis.com \
                           cloudresourcemanager.googleapis.com
    ```

- 安裝 [uv](https://docs.astral.sh/uv/getting-started/installation/) 相依性並準備 python 環境

    ```shell
    curl -LsSf https://astral.sh/uv/install.sh | sh
    uv python install 3.12
    uv sync --frozen
    ```

- 建立 Firestore 向量索引 (Vector Index)

    ```shell
    gcloud firestore indexes composite create \
        --collection-group="personal-expense-assistant-receipts" \
        --query-scope=COLLECTION \
        --field-config field-path="embedding",vector-config='{"dimension":"768", "flat": "{}"}' \
        --database="(default)"
    ```

- 為交易時間和總金額的複合搜尋 (Composite Search) 建立 Firestore 索引

    ```shell
    gcloud firestore indexes composite create \
        --collection-group=personal-expense-assistant-receipts \
        --field-config field-path=total_amount,order=ASCENDING \
        --field-config field-path=transaction_time,order=ASCENDING \
        --field-config field-path=__name__,order=ASCENDING \
        --database="(default)"
    ```

- 將 `settings.yaml.example` 複製到 `settings.yaml` 並相應地更新值。僅強制更新以下值：
  - `GCLOUD_PROJECT_ID`：您的 GCP 專案 ID

## 在本機執行

- 執行後端服務

    ```shell
    uv run backend.py
    ```

    如果成功，您應該會看到以下輸出（後端服務將在 8081 連接埠上執行）：

    ```shell
    INFO:     Started server process [4572]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://0.0.0.0:8081 (Press CTRL+C to quit)
    ```

- 執行前端服務

    ```shell
    uv run frontend.py
    ```

    如果成功，您應該會看到以下輸出（前端服務將在 8080 連接埠上執行）：

    ```shell
    * Running on local URL:  http://0.0.0.0:8080

    To create a public link, set `share=True` in `launch()`.
    ```

現在您可以在瀏覽器中存取 Web 應用程式

## 部署到 Cloud Run

若要部署到 Cloud Run

```shell
gcloud run deploy personal-expense-assistant \
--source . \
--port=8080 \
--allow-unauthenticated \
--env-vars-file=settings.yaml \
--memory 1024Mi
```

如果成功，您應該會看到以下輸出：

```shell
Deployed revision: personal-expense-assistant-00001
```
