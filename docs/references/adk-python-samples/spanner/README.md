# Spanner 工具範例

## 簡介

此範例代理程式展示了 ADK 中的 Spanner 第一方工具，這些工具透過 `google.adk.tools.spanner` 模組分發。這些工具包括：

1. `list_table_names`

  擷取 GCP Spanner 資料庫中存在的 Spanner 資料表名稱。

1. `list_table_indexes`

  擷取 GCP Spanner 資料庫中存在的 Spanner 資料表索引。

1. `list_table_index_columns`

  擷取 GCP Spanner 資料庫中存在的 Spanner 資料表索引欄位。

1. `list_named_schemas`

  擷取 Spanner 資料庫的具名結構。

1. `get_table_schema`

  擷取 Spanner 資料庫資料表結構和中繼資料資訊。

1. `execute_sql`

  在 Spanner 資料庫中執行 SQL 查詢。

## 如何使用

在您的 `.env` 檔案中設定環境變數，以便為您的代理程式使用 [Google AI Studio](https://google.github.io/adk-docs/get-started/quickstart/#gemini---google-ai-studio) 或 [Google Cloud Vertex AI](https://google.github.io/adk-docs/get-started/quickstart/#gemini---google-cloud-vertex-ai) 的 LLM 服務。例如，若要使用 Google AI Studio，您需要設定：

* GOOGLE_GENAI_USE_VERTEXAI=FALSE
* GOOGLE_API_KEY={your api key}

### 使用應用程式預設憑證

當代理程式建構者是與代理程式互動的唯一使用者時，此模式對於快速開發很有用。工具會使用這些憑證執行。

1. 按照 https://cloud.google.com/docs/authentication/provide-credentials-adc 的說明，在將執行代理程式的機器上建立應用程式預設憑證。

1. 在 `agent.py` 中設定 `CREDENTIALS_TYPE=None`

1. 執行代理程式

### 使用服務帳戶金鑰

當代理程式建構者想要使用服務帳戶憑證執行代理程式時，此模式對於快速開發很有用。工具會使用這些憑證執行。

1. 按照 https://cloud.google.com/iam/docs/service-account-creds#user-managed-keys 的說明建立服務帳戶金鑰。

1. 在 `agent.py` 中設定 `CREDENTIALS_TYPE=AuthCredentialTypes.SERVICE_ACCOUNT`

1. 下載金鑰檔案並將 `"service_account_key.json"` 替換為路徑

1. 執行代理程式

### 使用互動式 OAuth

1. 按照 https://developers.google.com/identity/protocols/oauth2#1.-obtain-oauth-2.0-credentials-from-the-dynamic_data.setvar.console_name. 的說明取得您的用戶端 ID 和用戶端密碼。請務必選擇「Web」作為您的用戶端類型。

1.  按照 https://developers.google.com/workspace/guides/configure-oauth-consent 的說明，將範圍 "https://www.googleapis.com/auth/spanner.data" 和 "https://www.googleapis.com/auth/spanner.admin" 新增為宣告，這用於審查目的。

1.  按照 https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred 的說明，將 http://localhost/dev-ui/ 新增至「已授權的重新導向 URI」。

    注意：此處的 localhost 只是您用來存取開發 UI 的主機名稱，請將其替換為您用來存取開發 UI 的實際主機名稱。

1.  首次執行時，請在 Chrome 中允許 localhost 的彈出式視窗。

1.  在執行代理程式之前，設定您的 `.env` 檔案以新增兩個變數：

    *   OAUTH_CLIENT_ID={your client id}
    *   OAUTH_CLIENT_SECRET={your client secret}

    注意：請勿建立獨立的 .env，而是將其放入儲存您的 Vertex AI 或 Dev ML 憑證的同一個 .env 檔案中

1.  在 `agent.py` 中設定 `CREDENTIALS_TYPE=AuthCredentialTypes.OAUTH2` 並執行代理程式

## 範例提示

* 顯示 product_db Spanner 資料庫中的所有資料表。
* 描述 product_table 資料表的結構。
* 列出 product_table 資料表上的所有索引。
* 顯示 product_table 資料表中的前 10 列資料。
* 撰寫一個查詢，透過聯結 product_table 和 sales_table 資料表來尋找最受歡迎的產品。
