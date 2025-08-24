# OAuth 範例

## 簡介

此範例透過以下兩個工具測試並示範 ADK 中的 OAuth 支援：

* 1. list_calendar_events

  這是一個自訂工具，可呼叫 Google 日曆 API 來列出日曆活動。
  它會將用戶端 ID 和用戶端密鑰傳遞給 ADK，然後從 ADK 取回存取權杖 (access token)。
  然後，它會使用存取權杖 (access token) 呼叫日曆 API。

* 2. get_calendar_events

  這是一個 Google 日曆工具，可呼叫 Google 日曆 API 來取得特定日曆的詳細資訊。
  此工具來自 ADK 內建的 Google Calendar ToolSet。
  所有內容都已封裝，工具使用者只需傳入用戶端 ID 和用戶端密鑰即可。

## 如何使用

* 1. 請遵循 https://developers.google.com/identity/protocols/oauth2#1.-obtain-oauth-2.0-credentials-from-the-dynamic_data.setvar.console_name. 的說明，以取得您的用戶端 ID 和用戶端密鑰。
  請務必選擇「Web」作為您的用戶端類型。

* 2. 設定您的 `.env` 檔案以新增兩個變數：

  * OAUTH_CLIENT_ID={您的用戶端 ID}
  * OAUTH_CLIENT_SECRET={您的用戶端密鑰}

  注意：請勿建立獨立的 `.env` 檔案，而是將其放入儲存 Vertex AI 或 Dev ML 憑證的同一個 `.env` 檔案中。

* 3. 請遵循 https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred 的說明，將 http://localhost/dev-ui/ 新增至「已授權的重新導向 URI」。

  注意：此處的 localhost 只是您用來存取開發 UI 的主機名稱，請將其替換為您用來存取開發 UI 的實際主機名稱。

* 4. 首次執行時，請在 Chrome 中允許 localhost 的彈出式視窗。

## 範例提示詞

* `列出我今天早上 7 點到晚上 7 點的所有會議。`
* `取得第一個活動的詳細資訊。`
