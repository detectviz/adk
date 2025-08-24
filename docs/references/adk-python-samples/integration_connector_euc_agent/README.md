# 具有使用者憑證的應用程式整合代理 (Agent) 範例

## 簡介

此範例示範如何在 ADK 代理 (agent) 中使用 `ApplicationIntegrationToolset`，以**使用者 OAuth 2.0 憑證**與外部應用程式互動。具體來說，此代理 (agent) (`agent.py`) 設定為使用預先設定的應用程式整合連線與 Google 日曆互動，並以使用者身分進行驗證。

## 先決條件

1. **設定整合連線：**
    * 您需要一個現有的[整合連線](https://cloud.google.com/integration-connectors/docs/overview)，設定為與 Google 日曆 API 互動。請遵循[文件](https://google.github.io/adk-docs/tools/google-cloud-tools/#use-integration-connectors)在 Google Cloud 中佈建整合連接器。您將需要連線的`連線名稱`、`專案 ID` 和 `位置`。
    * 確保連線已設定為使用 Google 日曆（例如，啟用 `google-calendar-connector` 或類似的連接器）。

2. **設定 OAuth 2.0 用戶端：**
    * 您需要一個 OAuth 2.0 用戶端 ID 和用戶端密鑰，該 ID 和密鑰已獲授權存取所需的 Google 日曆範圍（例如 `https://www.googleapis.com/auth/calendar.readonly`）。您可以在 Google Cloud Console 的「API 和服務」->「憑證」下建立 OAuth 憑證。

3. **設定環境變數：**
    * 在與 `agent.py` 相同的目錄中建立一個 `.env` 檔案（或新增至您現有的檔案中）。
    * 將以下變數新增至 `.env` 檔案中，並將預留位置值取代為您的實際連線詳細資料：

      ```dotenv
      CONNECTION_NAME=<您的日曆連線名稱>
      CONNECTION_PROJECT=<您的 GOOGLE CLOUD 專案 ID>
      CONNECTION_LOCATION=<您的連線位置>
      CLIENT_ID=<您的 OAUTH 用戶端 ID>
      CLIENT_SECRET=<您的 OAUTH 用戶端密鑰>
      ```

## 使用者驗證 (OAuth 2.0)

此代理 (agent) 利用 ADK 的 `AuthCredential` 和 `OAuth2Auth` 類別來處理驗證。
* 它會根據 Google Cloud 的 OAuth 端點和必要的範圍定義一個 OAuth 2.0 配置 (`oauth2_scheme`)。
* 它會使用環境變數中的 `CLIENT_ID` 和 `CLIENT_SECRET`（或範例中的硬式編碼值）來設定 `OAuth2Auth`。
* 此 `AuthCredential` 會傳遞至 `ApplicationIntegrationToolset`，讓工具能夠代表執行代理 (agent) 的使用者對 Google 日曆進行已驗證的 API 呼叫。ADK 框架通常會在首次叫用工具時處理 OAuth 流程（例如，提示使用者同意）。

## 如何使用

1. **安裝相依套件：** 確保您已安裝必要的程式庫（例如 `google-adk`、`python-dotenv`）。
2. **執行代理 (Agent)：** 從您的終端機執行代理 (agent) 指令碼：
    ```bash
    python agent.py
    ```
3. **互動：** 代理 (agent) 啟動後，您就可以與其互動。如果是第一次使用需要 OAuth 的工具，系統可能會提示您在瀏覽器中完成 OAuth 同意流程。成功驗證後，您可以要求代理 (agent) 執行工作。

## 範例提示

以下是一些您可以如何與代理 (agent) 互動的範例：

* `你可以列出我主要日曆中的活動嗎？`