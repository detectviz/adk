# ADK 問答代理

ADK 問答代理是一個基於 Python 的代理，旨在協助回答 `google/adk-python` 儲存庫中 GitHub 討論區的問題。它使用大型語言模型來分析開放的討論、從文件儲存中檢索資訊、產生回應，並在 GitHub 討論中發表評論。

此代理可以三種不同模式運作：

- 用於本機使用的互動模式。
- 用於值班使用的批次腳本模式。
- 一個完全自動化的 GitHub Actions 工作流程（待定）。

---

## 互動模式

此模式允許您在本機執行代理，以便在對儲存庫的問題進行任何變更之前，即時審查其建議。

### 功能
* **Web 介面**：代理的互動模式可以使用 ADK 的 `adk web` 命令在網頁瀏覽器中呈現。
* **使用者批准**：在互動模式下，代理被指示在向 GitHub 問題發表評論之前，請求您的確認。
* **問答**：您可以提出與 ADK 相關的問題，代理將根據其對 ADK 的知識提供答案。

### 在互動模式下執行
若要在互動模式下執行代理，請先設定必要的環境變數。然後，在您的終端機中執行以下命令：

```bash
adk web
```
這將啟動一個本機伺服器，並提供一個 URL，讓您在瀏覽器中存取代理的 Web 介面。

---

## 批次腳本模式

`answer_discussions.py` 是為 ADK 值班團隊建立的，用於批次處理討論。

### 功能
* **批次處理**：無論是輸入最近討論的計數，還是討論編號列表，腳本都將呼叫代理，在一次執行中回答所有指定的討論。

### 在互動模式下執行
若要在批次腳本模式下執行代理，請先設定必要的環境變數。然後，在您的終端機中執行以下命令：

```bash
export PYTHONPATH=contributing/samples
python -m adk_answering_agent.answer_discussions --numbers 27 36 # 回答指定的討論
```

或 `python -m adk_answering_agent.answer_discussions --recent 10` 來回答最近更新的 10 個討論。

---

## GitHub 工作流程模式

`main.py` 保留給 Github 工作流程使用。自動化工作流程的詳細設定待定。

---

## 更新知識庫

`upload_docs_to_vertex_ai_search.py` 是一個將 ADK 相關文件上傳到 Vertex AI Search 資料儲存庫以更新知識庫的腳本。可以在您的終端機中執行以下命令：

```bash
export PYTHONPATH=contributing/samples # 如果尚未匯出
python -m adk_answering_agent.upload_docs_to_vertex_ai_search
```

## 設定與組態

無論是在互動模式還是工作流程模式下執行，代理都需要以下設定。

### 相依性
代理需要以下 Python 函式庫。

```bash
pip install --upgrade pip
pip install google-adk
```

代理還需要 gcloud 登入：

```bash
gcloud auth application-default login
```

上傳腳本需要以下額外的 Python 函式庫。

```bash
pip install google-cloud-storage google-cloud-discoveryengine
```

### 環境變數
代理需要以下環境變數才能連接到必要的服務。

* `GITHUB_TOKEN=YOUR_GITHUB_TOKEN`: **(必要)** 具有 `issues:write` 權限的 GitHub 個人存取權杖。互動和工作流程模式都需要。
* `GOOGLE_GENAI_USE_VERTEXAI=TRUE`: **(必要)** 使用 Google Vertex AI 進行驗證。
* `GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID`: **(必要)** Google Cloud 專案 ID。
* `GOOGLE_CLOUD_LOCATION=LOCATION`: **(必要)** Google Cloud 區域。
* `VERTEXAI_DATASTORE_ID=YOUR_DATASTORE_ID`: **(必要)** 文件儲存（即知識庫）的完整 Vertex AI 資料儲存庫 ID，格式為 `projects/{project_number}/locations/{location}/collections/{collection}/dataStores/{datastore_id}`。
* `OWNER`: 擁有儲存庫的 GitHub 組織或使用者名稱（例如 `google`）。兩種模式都需要。
* `REPO`: GitHub 儲存庫的名稱（例如 `adk-python`）。兩種模式都需要。
* `INTERACTIVE`: 控制代理的互動模式。對於自動化工作流程，此設定為 `0`。對於互動模式，應設定為 `1` 或不設定。

上傳文件以更新知識庫需要以下環境變數。

* `GCS_BUCKET_NAME=YOUR_GCS_BUCKET_NAME`: **(必要)** 用於儲存文件的 GCS 儲存桶名稱。
* `ADK_DOCS_ROOT_PATH=YOUR_ADK_DOCS_ROOT_PATH`: **(必要)** 下載的 adk-docs 儲存庫根目錄的路徑。
* `ADK_PYTHON_ROOT_PATH=YOUR_ADK_PYTHON_ROOT_PATH`: **(必要)** 下載的 adk-python 儲存庫根目錄的路徑。

對於在本機互動模式下執行，您可以將這些變數放在專案根目錄中的 `.env` 檔案中。對於 GitHub 工作流程，應將它們設定為儲存庫密鑰。
