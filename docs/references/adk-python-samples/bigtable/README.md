# Bigtable 工具範例

## 簡介

本範例代理 (Agent) 展示了 ADK 中的 Bigtable 第一方工具，這些工具透過 `google.adk.tools.bigtable` 模組分發。這些工具包括：

1.  `bigtable_list_instances`

    擷取 Google Cloud 專案中的 Bigtable 實例 ID。

2.  `bigtable_get_instance_info`

    擷取有關 Bigtable 實例的元數據資訊。

3.  `bigtable_list_tables`

    擷取 Bigtable 實例中的資料表 ID。

4.  `bigtable_get_table_info`

    擷取有關 Bigtable 資料表的元數據資訊。

5.  `bigtable_execute_sql`

    在 Bigtable 資料庫中執行 DQL SQL 查詢。

## 如何使用

在您的 `.env` 檔案中設定環境變數，以便為您的代理 (Agent) 使用 [Google AI Studio](https://google.github.io/adk-docs/get-started/quickstart/#gemini---google-ai-studio) 或 [Google Cloud Vertex AI](https://google.github.io/adk-docs/get-started/quickstart/#gemini---google-cloud-vertex-ai) 作為大型語言模型 (LLM) 服務。例如，若要使用 Google AI Studio，您需要設定：

*   `GOOGLE_GENAI_USE_VERTEXAI=FALSE`
*   `GOOGLE_API_KEY={您的 API 金鑰}`

### 使用應用程式預設憑證 (Application Default Credentials)

當代理 (Agent) 的建構者是與代理 (Agent) 互動的唯一使用者時，此模式對於快速開發非常有用。工具會使用這些憑證執行。

1.  遵循 https://cloud.google.com/docs/authentication/provide-credentials-adc，在將要執行代理 (Agent) 的機器上建立應用程式預設憑證。

2.  在 `agent.py` 中設定 `CREDENTIALS_TYPE=None`。

3.  執行代理 (Agent)。

### 使用服務帳戶金鑰 (Service Account Keys)

當代理 (Agent) 的建構者希望使用服務帳戶憑證執行代理 (Agent) 時，此模式對於快速開發非常有用。工具會使用這些憑證執行。

1.  遵循 https://cloud.google.com/iam/docs/service-account-creds#user-managed-keys 建立服務帳戶金鑰。

2.  在 `agent.py` 中設定 `CREDENTIALS_TYPE=AuthCredentialTypes.SERVICE_ACCOUNT`。

3.  下載金鑰檔案，並將 `"service_account_key.json"` 替換為該檔案的路徑。

4.  執行代理 (Agent)。

### 使用互動式 OAuth

1.  遵循 https://developers.google.com/identity/protocols/oauth2#1.-obtain-oauth-2.0-credentials-from-the-dynamic_data.setvar.console_name. 以取得您的用戶端 ID 和用戶端密鑰。請務必選擇 "Web" 作為您的用戶端類型。

2.  遵循 https://developers.google.com/workspace/guides/configure-oauth-consent 以新增 "https://www.googleapis.com/auth/bigtable.admin" 和 "https://www.googleapis.com/auth/bigtable.data" 作為宣告，這將用於審查目的。

3.  遵循 https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred 以將 http://localhost/dev-ui/ 新增至「已授權的重新導向 URI」。

    注意：此處的 localhost 只是您用來存取開發 UI 的主機名稱，請將其替換為您實際用來存取開發 UI 的主機名稱。

4.  首次執行時，請在 Chrome 中允許 localhost 的彈出式視窗。

5.  在執行代理 (Agent) 之前，設定您的 `.env` 檔案以新增兩個變數：

    *   `OAUTH_CLIENT_ID={您的用戶端 ID}`
    *   `OAUTH_CLIENT_SECRET={您的用戶端密鑰}`

    注意：請勿建立單獨的 .env 檔案，而是將其放入儲存您的 Vertex AI 或 Dev ML 憑證的同一個 .env 檔案中。

6.  在 `agent.py` 中設定 `CREDENTIALS_TYPE=AuthCredentialTypes.OAUTH2` 並執行代理 (Agent)。

## 範例提示

*   `顯示 my-project 中的所有實例。`
*   `顯示 my-project 中 my-instance 實例的所有資料表。`
*   `描述 my-project 中 my-instance 實例的 my-table 資料表的結構。`
*   `顯示 my-project 中 my-instance 實例的 my-table 資料表的前 10 行資料。`
