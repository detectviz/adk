此代理 (agent) 使用 Google Application Integration 工作流程和 Integrations Connector 連接到 Jira Cloud。

**連接到代理 (agent) 的說明：**

**使用 Integration Connectors**

使用 [Integration Connectors](https://cloud.google.com/integration-connectors/docs/overview) 將您的代理 (agent) 連接到企業應用程式。

**步驟：**

1. 若要使用 Integration Connectors 中的連接器，您需要透過點擊「QUICK SETUP」按鈕，在與您的連線相同的區域中[佈建](https://console.cloud.google.com/) Application Integration。
Google Cloud Tools
![image_alt](https://github.com/karthidec/adk-python/blob/adk-samples-jira-agent/contributing/samples/jira_agent/image-application-integration.png?raw=true)

2. 從範本庫中前往 [Connection Tool]((https://console.cloud.google.com/)) 範本，然後點擊「USE TEMPLATE」按鈕。
![image_alt](https://github.com/karthidec/adk-python/blob/adk-samples-jira-agent/contributing/samples/jira_agent/image-connection-tool.png?raw=true)

3. 將 Integration Name 填寫為 **ExecuteConnection** (強制僅使用此整合名稱)，並選擇與連線區域相同的區域。點擊「CREATE」。

4. 在 Application Integration Editor 中使用「PUBLISH」按鈕發佈整合。
![image_alt](https://github.com/karthidec/adk-python/blob/adk-samples-jira-agent/contributing/samples/jira_agent/image-app-intg-editor.png?raw=true)

**參考資料：**

https://google.github.io/adk-docs/tools/google-cloud-tools/#application-integration-tools
