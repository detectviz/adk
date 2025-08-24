# 模型上下文協定 (Model Context Protocol, MCP)

## 什麼是模型上下文協定 (MCP)？

[模型上下文協定 (Model Context Protocol, MCP)](https://modelcontextprotocol.io/introduction) 是一個開放標準，旨在標準化大型語言模型 (LLM)，如 Gemini 和 Claude，與外部應用程式、資料來源和工具的通訊方式。您可以把它想像成一個通用的連接機制，簡化了 LLM 獲取上下文、執行操作以及與各種系統互動的方式。

## MCP 如何運作？

MCP 遵循客戶端-伺服器架構，定義了資料（資源）、互動式範本（提示）和可操作函式（工具）如何由 MCP 伺服器公開，並由 MCP 客戶端（可以是 LLM 主機應用程式或 AI 代理程式）使用。

## ADK 中的 MCP 工具

無論您是想建立一個工具來呼叫 MCP 服務，還是想為其他開發人員或代理程式公開一個 MCP 伺服器以與您的工具互動，ADK 都能幫助您在代理程式中使用和取用 MCP 工具。

請參閱 [MCP 工具文件](tools-mcp-tools.md) 以取得程式碼範例和設計模式，幫助您將 ADK 與 MCP 伺服器結合使用，包括：

- **在 ADK 中使用現有的 MCP 伺服器**：ADK 代理程式可以充當 MCP 客戶端，並使用由外部 MCP 伺服器提供的工具。
- **透過 MCP 伺服器公開 ADK 工具**：如何建立一個包裝 ADK 工具的 MCP 伺服器，使其可供任何 MCP 客戶端存取。

## 用於資料庫的 MCP 工具箱

[用於資料庫的 MCP 工具箱 (MCP Toolbox for Databases)](https://github.com/googleapis/genai-toolbox) 是一個開源的 MCP 伺服器，可幫助您建立生成式 AI 工具，以便您的代理程式可以存取資料庫中的資料。Google 的代理開發套件 (ADK) 內建了對用於資料庫的 MCP 工具箱的支援。

請參閱[用於資料庫的 MCP 工具箱](../tools/google-cloud-tools.md#toolbox-tools-for-databases)文件，了解如何將 ADK 與用於資料庫的 MCP 工具箱結合使用。若要開始使用用於資料庫的 MCP 工具箱，還有一篇部落格文章[教學：用於資料庫的 MCP 工具箱 - 公開 Big Query 資料集](https://medium.com/google-cloud/tutorial-mcp-toolbox-for-databases-exposing-big-query-datasets-9321f0064f4e)和一個 Codelab [用於資料庫的 MCP 工具箱：讓 BigQuery 資料集可供 MCP 客戶端使用](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en#0)可供參考。

![GenAI 工具箱](../assets/mcp_db_toolbox.png)

## ADK 代理程式與 FastMCP 伺服器
[FastMCP](https://github.com/jlowin/fastmcp) 處理所有複雜的 MCP 協定細節和伺服器管理，因此您可以專注於建立出色的工具。它的設計是高階且符合 Python 風格的；在大多數情況下，您只需要裝飾一個函式即可。

請參閱 [MCP 工具文件](tools-mcp-tools.md)文件，了解如何將 ADK 與在 Cloud Run 上執行的 FastMCP 伺erver 結合使用。

## 用於 Google Cloud Genmedia 的 MCP 伺服器

[用於 Genmedia 服務的 MCP 工具 (MCP Tools for Genmedia Services)](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia) 是一組開源的 MCP 伺服器，可讓您將 Google Cloud 的生成式媒體服務（例如 Imagen、Veo、Chirp 3 HD 語音和 Lyria）整合到您的 AI 應用程式中。

代理開發套件 (ADK) 和 [Genkit](https://genkit.dev/) 為這些 MCP 工具提供內建支援，讓您的 AI 代理程式能夠有效地協調生成式媒體工作流程。有關實作指南，請參閱 [ADK 範例代理程式](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/adk)和 [Genkit 範例](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/genkit)。
