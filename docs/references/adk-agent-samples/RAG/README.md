# 文件檢索代理

## 總覽

此代理旨在回答與您上傳至 Vertex AI RAG 引擎的文件相關的問題。它利用檢索增強生成 (Retrieval-Augmented Generation, RAG) 搭配 Vertex AI RAG 引擎來擷取相關的文件片段和程式碼參考，然後由大型語言模型 (LLM, Gemini) 綜合這些資訊，以提供附有引文的資訊性答案。


![RAG 架構](RAG_architecture.png)

此圖表概述了代理的工作流程，旨在提供有根據且具上下文感知的回應。使用者查詢由代理開發套件處理。LLM 決定是否需要外部知識（RAG 語料庫）。如果需要，`VertexAiRagRetrieval` 工具會從設定的 Vertex RAG 引擎語料庫中擷取相關資訊。然後，LLM 會將此擷取的資訊與其內部知識綜合，以產生準確的答案，包括指回來源文件 URL 的引文。

## 代理詳細資訊
| 屬性         | 詳細資訊                                                                                                                                                                                             |
| :---------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **互動類型** | 對話式                                                                                                                                                                                      |
| **複雜度**    | 中等
| **代理類型**    | 單一代理                                                                                                                                                                                        |
| **元件**    | 工具、RAG、評估                                                                                                                                                                               |
| **垂直領域**      | 水平                                                                                                                                                                               |
### 代理架構

![RAG](RAG_workflow.png)


### 主要功能

*   **檢索增強生成 (RAG):** 利用 [Vertex AI RAG 引擎](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview)來擷取相關文件。
*   **引文支援：** 為擷取的內容提供準確的引文，格式為 URL。
*   **清晰的指示：** 遵守提供事實性答案和適當引文的嚴格指南。

## 設定與安裝說明
### 先決條件

*   **Google Cloud 帳戶：** 您需要一個 Google Cloud 帳戶。
*   **Python 3.9+：** 確保您已安裝 Python 3.9 或更新版本。
*   **Poetry：** 按照官方 Poetry 網站上的說明安裝 Poetry：[https://python-poetry.org/docs/](https://python-poetry.org/docs/)
*   **Git：** 確保您已安裝 git。

### 使用 Poetry 進行專案設定

1.  **複製儲存庫：**

    ```bash
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/python/agents/RAG
    ```

2.  **使用 Poetry 安裝依賴項：**

    ```bash
    poetry install
    ```

    此指令會讀取 `pyproject.toml` 檔案，並將所有必要的依賴項安裝到由 Poetry 管理的虛擬環境中。

3.  **啟動 Poetry Shell：**

    ```bash
    poetry env activate
    ```

    這會啟動虛擬環境，讓您可以在專案的環境中執行指令。
    請確保環境已啟動。如果沒有，您也可以透過以下方式啟動它

     ```bash
    source .venv/bin/activate 
    ```   
4.  **設定環境變數：**
    將檔案 ".env.example" 重新命名為 ".env"
    按照檔案中的步驟設定環境變數。

5. **設定語料庫：**
    如果您在 Vertex AI RAG 引擎中已有現有的語料庫，請在您的 .env 檔案中設定語料庫資訊。例如：RAG_CORPUS='projects/123/locations/us-central1/ragCorpora/456'。

    如果您尚未設定語料庫，請按照「如何將我的檔案上傳到我的 RAG 語料庫」一節的說明操作。`prepare_corpus_and_data.py` 腳本將自動建立一個語料庫（如果需要），並使用建立或擷取的語料庫的資源名稱更新您 `.env` 檔案中的 `RAG_CORPUS` 變數。

#### 如何將我的檔案上傳到我的 RAG 語料庫

`rag/shared_libraries/prepare_corpus_and_data.py` 腳本可協助您設定 RAG 語料庫並上傳初始文件。預設情況下，它會下載 Alphabet 的 2024 年 10-K PDF 並將其上傳到一個新的語料庫中。

1.  **使用您的 Google Cloud 帳戶進行驗證：**
    ```bash
    gcloud auth application-default login
    ```

2.  **在您的 `.env` 檔案中設定環境變數：**
    確保您的 `.env` 檔案（從 `.env.example` 複製）已設定以下變數：
    ```
    GOOGLE_CLOUD_PROJECT=your-project-id
    GOOGLE_CLOUD_LOCATION=your-location  # 例如 us-central1
    ```

3.  **設定並執行準備腳本：**
    *   **若要使用預設行為（上傳 Alphabet 的 10K PDF）：**
        只需執行腳本：
        ```bash
        python rag/shared_libraries/prepare_corpus_and_data.py
        ```
        這將建立一個名為 `Alphabet_10K_2024_corpus` 的語料庫（如果它不存在），並上傳從腳本中指定的 URL 下載的 PDF `goog-10-k-2024.pdf`。

    *   **若要從 URL 上傳不同的 PDF：**
        a. 開啟 `rag/shared_libraries/prepare_corpus_and_data.py` 檔案。
        b. 修改腳本頂部的以下變數：
           ```python
           # --- 請填寫您的設定 ---
           # ... 專案和位置從 .env 讀取 ...
           CORPUS_DISPLAY_NAME = "Your_Corpus_Name"  # 依需求變更
           CORPUS_DESCRIPTION = "Description of your corpus" # 依需求變更
           PDF_URL = "https://path/to/your/document.pdf"  # 您的 PDF 文件的 URL
           PDF_FILENAME = "your_document.pdf"  # 語料庫中檔案的名稱
           # --- 腳本開始 ---
           ```
        c. 執行腳本：
           ```bash
           python rag/shared_libraries/prepare_corpus_and_data.py
           ```

    *   **若要上傳本地 PDF 檔案：**
        a. 開啟 `rag/shared_libraries/prepare_corpus_and_data.py` 檔案。
        b. 依需求修改 `CORPUS_DISPLAY_NAME` 和 `CORPUS_DESCRIPTION` 變數（見上文）。
        c. 修改腳本底部的 `main()` 函式，以直接使用您的本地檔案詳細資訊呼叫 `upload_pdf_to_corpus`：
           ```python
           def main():
             initialize_vertex_ai()
             corpus = create_or_get_corpus() # 使用 CORPUS_DISPLAY_NAME 和 CORPUS_DESCRIPTION

             # 將您的本地 PDF 上傳到語料庫
             local_file_path = "/path/to/your/local/file.pdf" # 設定正確的路徑
             display_name = "Your_File_Name.pdf" # 設定所需的顯示名稱
             description = "Description of your file" # 設定描述

             # 上傳前確保檔案存在
             if os.path.exists(local_file_path):
                 upload_pdf_to_corpus(
                     corpus_name=corpus.name,
                     pdf_path=local_file_path,
                     display_name=display_name,
                     description=description
                 )
             else:
                 print(f"錯誤：在 {local_file_path} 找不到本地檔案")

             # 列出語料庫中的所有檔案
             list_corpus_files(corpus_name=corpus.name)
           ```
        d. 執行腳本：
           ```bash
           python rag/shared_libraries/prepare_corpus_and_data.py
           ```

有關在 Vertex RAG 引擎中管理資料的更多詳細資訊，請參閱
[官方文件頁面](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-quickstart)。

## 執行代理
您可以在終端機中使用 ADK 指令來執行代理。
從專案根目錄：

1.  在 CLI 中執行代理：

    ```bash
    adk run rag
    ```

2.  使用 ADK Web UI 執行代理：
    ```bash
    adk web
    ```
    從下拉式選單中選擇 RAG


### 範例互動
以下是使用者可能如何與代理互動的快速範例：

**範例 1：文件資訊檢索**

使用者：Alphabet 的 2024 年 10-K 報告中提到的主要業務部門是什麼？

代理：根據 Alphabet 的 2024 年 10-K 報告，主要業務部門是：
1. Google 服務（包括 Google 搜尋、YouTube、Google 地圖、Play 商店）
2. Google Cloud（提供雲端運算服務、資料分析和 AI 解決方案）
3. 其他賭注（包括 Waymo 的自動駕駛技術）
[來源：goog-10-k-2024.pdf]

## 評估代理

評估可以從 `RAG` 目錄使用
`pytest` 模組執行：

```
poetry run pytest eval
```

### 評估流程

評估框架由三個關鍵元件組成：

1. **test_eval.py**：協調評估流程的主要測試腳本。它使用 Google ADK 的 `AgentEvaluator` 針對測試資料集執行代理，並根據預先定義的標準評估其表現。

2. **conversation.test.json**：包含一系列結構為對話的測試案例。每個測試案例包括：
   - 使用者查詢（例如，關於 Alphabet 的 10-K 報告的問題）
   - 預期的工具使用（代理應呼叫哪些工具以及使用哪些參數）
   - 參考答案（代理應提供的理想回應）

3. **test_config.json**：定義評估標準和閾值：
   - `tool_trajectory_avg_score`：衡量代理使用適當工具的程度
   - `response_match_score`：衡量代理的回應與參考答案的匹配程度

當您執行評估時，系統會：
1. 從 conversation.test.json 載入測試案例
2. 將每個查詢傳送給代理
3. 將代理的工具使用與預期的工具使用進行比較
4. 將代理的回應與參考答案進行比較
5. 根據 test_config.json 中的標準計算分數

此評估有助於確保代理正確利用 RAG 功能來擷取相關資訊，並產生附有適當引文的準確回應。

## 部署代理

代理可以使用以下
指令部署到 Vertex AI Agent Engine：

```
python deployment/deploy.py
```

部署代理後，您將能夠讀取以下 INFO 記錄訊息：

```
成功將代理部署到 Vertex AI Agent Engine，資源名稱：projects/<PROJECT_NUMBER>/locations/us-central1/reasoningEngines/<AGENT_ENGINE_ID>
```

請記下您的 Agent Engine 資源名稱並相應地更新 `.env` 檔案，因為這對於測試遠端代理至關重要。

您也可以為您的使用案例修改部署腳本。

## 測試已部署的代理

部署代理後，請按照以下步驟進行測試：

1. **更新環境變數：**
   - 開啟您的 `.env` 檔案。
   - 當您部署代理時，`AGENT_ENGINE_ID` 應已由 `deployment/deploy.py` 腳本自動更新。請確認其設定正確：
     ```
     AGENT_ENGINE_ID=projects/<PROJECT_NUMBER>/locations/us-central1/reasoningEngines/<AGENT_ENGINE_ID>
     ```

2. **授予 RAG 語料庫存取權限：**
   - 確保您的 `.env` 檔案已正確設定以下變數：
     ```
     GOOGLE_CLOUD_PROJECT=your-project-id
     RAG_CORPUS=projects/<project-number>/locations/us-central1/ragCorpora/<corpus-id>
     ```
   - 執行權限腳本：
     ```bash
     chmod +x deployment/grant_permissions.sh
     ./deployment/grant_permissions.sh
     ```
   此腳本將：
   - 從您的 `.env` 檔案讀取環境變數
   - 建立一個具有 RAG 語料庫查詢權限的自訂角色
   - 將必要的權限授予 AI Platform Reasoning Engine 服務代理

3. **測試遠端代理：**
   - 執行測試腳本：
     ```bash
     python deployment/run.py
     ```
   此腳本將：
   - 連接到您已部署的代理
   - 傳送一系列測試查詢
   - 以適當的格式顯示代理的回應

測試腳本包含有關 Alphabet 的 10-K 報告的範例查詢。您可以修改 `deployment/run.py` 中的查詢以測試已部署代理的不同方面。

## 客製化

### 客製化代理
您可以為代理客製化系統指令，並新增更多工具以滿足您的需求，例如 Google 搜尋。

### 客製化 Vertex RAG 引擎
您可以閱讀更多關於[官方 Vertex RAG 引擎文件](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-quickstart)的內容，以了解有關客製化語料庫和資料的更多詳細資訊。


### 插入其他檢索來源
您還可以整合您偏好的檢索來源，以增強代理的
功能。例如，您可以無縫地取代或增強現有的
`VertexAiRagRetrieval` 工具，使用一個利用 Vertex AI Search 或任何
其他檢索機制的工具。這種靈活性讓您可以根據
您的特定資料來源和檢索需求量身訂製代理。


## 免責聲明

此代理範例僅供說明之用，不適用於生產環境。它作為一個代理的基本範例，以及個人或團隊開發自己代理的基礎起點。

此範例未經嚴格測試，可能包含錯誤或限制，且不包含生產環境通常所需的功能或優化（例如，穩健的錯誤處理、安全措施、可擴展性、效能考量、全面的日誌記錄或進階設定選項）。

使用者對基於此範例的任何進一步開發、測試、安全強化和部署負全部責任。我們建議在使用任何衍生的代理於即時或關鍵系統之前，進行徹底的審查、測試並實施適當的保護措施。