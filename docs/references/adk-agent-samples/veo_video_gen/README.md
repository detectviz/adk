## ADK 影片生成代理 (VEO) 範例

此範例使用代理開發套件 (ADK) 建立一個作為 A2A 伺服器託管的「影片生成」代理。此代理利用 Google 的 VEO 模型（透過 `google-generativeai` 函式庫）從文字提示生成影片。

代理接受來自客戶端的文字提示，使用 VEO 啟動影片生成，提供串流進度更新，最後傳回一個指向生成影片的已簽署 Google Cloud Storage (GCS) URL。

## 先決條件

- Python 3.9 或更高版本
- [UV](https://docs.astral.sh/uv/)
- Google Cloud 專案，且具備：
    - 已啟用並可供使用的 VEO API。
    - 用於儲存生成影片的 GCS 儲存貯體。
    - 已設定適當的驗證：
        - **對於 VEO API：** 已設定 Vertex AI (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`)。
        - **對於 GCS 存取：** 已設定應用程式預設憑證 (ADC)（例如，透過執行 `gcloud auth application-default login`）或 `GOOGLE_APPLICATION_CREDENTIALS` 環境變數指向服務帳戶金鑰 JSON 檔案。該身分識別需要具有寫入指定 GCS 儲存貯體和產生已簽署 URL 的權限。

## 設定與依賴項

1.  **複製儲存庫（如果您尚未這樣做）並導覽至此範例的目錄：**
    ```bash
    # 假設您位於 google/a2a 專案的根目錄
    cd samples/python/agents/google_adk_video_generation # 或此範例所在的任何位置
    ```
2.  **使用您的設定建立一個環境檔案 (`.env`)：**
    ```bash
    # .env
    GOOGLE_GENAI_USE_VERTEXAI="TRUE"
    GOOGLE_CLOUD_PROJECT="your_GCP_Project_name"
    GOOGLE_CLOUD_LOCATION="your_project_location" e.g. us-central1
    VIDEO_GEN_GCS_BUCKET="your-gcs-bucket-name-for-videos" # 以您的儲存貯體名稱取代
    # 對於 GCS 已簽署 URL，請使用一個在其自身上具有「服務帳戶權杖建立者」IAM 角色的特定服務帳戶。
    # 如果未設定，執行代理的身分識別（來自 ADC）需要在其自身上具有「服務帳戶權杖建立者」角色才能簽署 URL，或者如果未使用模擬進行簽署，則需要適當的權限。
    SIGNER_SERVICE_ACCOUNT_EMAIL="your-service-account@your-project.iam.gserviceaccount.com"

    ```


## 執行範例代理

1.  **執行影片生成代理伺服器：**
    uv run .

## 執行 A2A 客戶端（範例）

1.  **在另一個終端機中，執行 A2A CLI 客戶端：**
    （導覽至 A2A CLI 客戶端目錄，例如 A2A 專案中的 `samples/python/hosts/cli`）
    ```bash
    uv run . --agent http://localhost:10003
    ```

2.  **與代理互動：**
    連線後，CLI 將提示輸入。輸入用於影片生成的文字提示：
    ```
    >> 建立一段蜂鳥在花朵附近慢動作飛行的短片。
    ```
    代理將提供模擬的進度更新，並最終提供一個指向生成影片的連結。

## 免責聲明
重要提示：所提供的範例程式碼僅供示範之用，並說明代理對代理 (A2A) 協定的機制。在建置生產應用程式時，將任何在您直接控制之外運作的代理視為潛在不受信任的實體至關重要。

從外部代理接收的所有資料——包括但不限於其代理卡 (AgentCard)、訊息、成品和任務狀態——都應作為不受信任的輸入處理。例如，惡意代理可能會提供一個在其欄位（例如，描述、名稱、技能描述）中包含精心設計資料的代理卡。如果在使用此類資料時未經清理就用於建構大型語言模型 (LLM) 的提示，可能會使您的應用程式面臨提示注入攻擊的風險。未能在使用前正確驗證和清理此類資料可能會給您的應用程式帶來安全漏洞。

開發人員有責任實施適當的安全措施，例如輸入驗證和安全處理憑證，以保護其系統和使用者。