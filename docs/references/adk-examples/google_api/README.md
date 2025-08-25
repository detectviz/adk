# Google API 工具範例

## 簡介

本範例測試並展示 `google.adk.tools.google_api_tool` 模組中可用的 Google API 工具。我們為此範例代理 (Agent) 挑選了以下 BigQuery API 工具：

1.  `bigquery_datasets_list`：列出使用者的資料集。

2.  `bigquery_datasets_get`：取得資料集的詳細資訊。

3.  `bigquery_datasets_insert`：建立一個新的資料集。

4.  `bigquery_tables_list`：列出資料集中的所有資料表。

5.  `bigquery_tables_get`：取得資料表的詳細資訊。

6.  `bigquery_tables_insert`：在資料集中插入一個新的資料表。

## 如何使用

1.  遵循 https://developers.google.com/identity/protocols/oauth2#1.-obtain-oauth-2.0-credentials-from-the-dynamic_data.setvar.console_name. 以取得您的用戶端 ID 和用戶端密鑰。
    請務必選擇 "Web" 作為您的用戶端類型。

2.  設定您的 `.env` 檔案以新增兩個變數：

    *   `OAUTH_CLIENT_ID={您的用戶端 ID}`
    *   `OAUTH_CLIENT_SECRET={您的用戶端密鑰}`

    注意：請勿建立單獨的 .env 檔案，而是將其放入儲存您的 Vertex AI 或 Dev ML 憑證的同一個 .env 檔案中。

3.  遵循 https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred 以將 http://localhost/dev-ui/ 新增至「已授權的重新導向 URI」。

    注意：此處的 localhost 只是您用來存取開發 UI 的主機名稱，請將其替換為您實際用來存取開發 UI 的主機名稱。

4.  首次執行時，請在 Chrome 中允許 localhost 的彈出式視窗。

## 範例提示

*   `我在 sean-dev-agent 專案中有任何資料集嗎？`
*   `它下面有任何資料表嗎？`
*   `可以告訴我這個資料表的詳細資訊嗎？`
*   `您能幫我在同一個專案中建立一個新的資料集嗎？ id：sean_test，location：us`
*   `可以向我顯示這個新資料集的詳細資訊嗎？`
*   `您可以在此資料集下建立一個新資料表嗎？ 資料表名稱：sean_test_table。 欄位1：名稱為 id，類型為整數，必要。 欄位2：名稱為 info，類型為字串，必要。 欄位3：名稱為 backup，類型為字串，選用。`
