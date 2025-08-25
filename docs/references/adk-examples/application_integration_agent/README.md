# 應用程式整合代理 (Application Integration Agent) 範例

## 簡介

本範例展示如何在 ADK 代理 (Agent) 中使用 `ApplicationIntegrationToolset` 來與外部應用程式互動，此處以 Jira 為例。此代理 (`agent.py`) 被設定為使用預先配置的應用程式整合連線來管理 Jira 問題。

## 先決條件

1.  **設定整合連線 (Integration Connection)：**
    *   您需要一個已設定好的[整合連線](https://cloud.google.com/integration-connectors/docs/overview)來與您的 Jira 實例互動。請遵循[此文件](https://google.github.io/adk-docs/tools/google-cloud-tools/#use-integration-connectors)在 Google Cloud 中配置整合連接器 (Integration Connector)，然後使用[此文件](https://cloud.google.com/integration-connectors/docs/connectors/jiracloud/configure)來建立一個 JIRA 連線。請記下您的連線的 `Connection Name`、`Project ID` 和 `Location`。

2.  **設定環境變數：**
    *   在與 `agent.py` 相同的目錄中建立一個 `.env` 檔案（或加入您現有的檔案中）。
    *   將以下變數加入 `.env` 檔案中，並將預留位置的值替換為您實際的連線詳細資訊：

      ```dotenv
      CONNECTION_NAME=<您的_JIRA_連線名稱>
      CONNECTION_PROJECT=<您的_GOOGLE_CLOUD_專案_ID>
      CONNECTION_LOCATION=<您的_連線_位置>
      ```

## 如何使用

1.  **安裝依賴套件：** 確保您已安裝必要的函式庫（例如 `google-adk`、`python-dotenv`）。
2.  **執行代理 (Agent)：** 從您的終端機執行代理 (Agent) 腳本：
    ```bash
    python agent.py
    ```
3.  **互動：** 代理 (Agent) 啟動後，您可以透過輸入與 Jira 問題管理相關的提示來與之互動。

## 範例提示

以下是一些您可以如何與代理 (Agent) 互動的範例：

*   `你可以列出所有的問題嗎？`
*   `你可以列出所有的專案嗎？`
*   `你可以在 ABC 專案中建立一個問題：「產品 XYZ 中的錯誤」嗎？`
