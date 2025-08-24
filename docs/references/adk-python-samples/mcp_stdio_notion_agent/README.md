# Notion MCP 代理 (Agent)

這是一個使用 Notion MCP 工具呼叫 Notion API 的代理 (agent)。它示範了如何傳入 Notion API 金鑰。

請依照以下說明使用：

* 依照以下頁面中的安裝說明取得 Notion API 的 API 金鑰：
https://www.npmjs.com/package/@notionhq/notion-mcp-server

* 將環境變數 `NOTION_API_KEY` 設定為您在上一步中取得的 API 金鑰。

```bash
export NOTION_API_KEY=<您的_notion_api_金鑰>
```

* 在 ADK Web UI 中執行代理 (agent)

* 傳送以下查詢：
  * 你能為我做什麼？
  * 在我的頁面中搜尋 `XXXX`。
