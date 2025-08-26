# Agentic RAG

此代理透過一個可用於生產的資料擷取管線來增強 Agent Starter Pack，豐富您的檢索增強生成 (Retrieval Augmented Generation, RAG) 應用程式。您將能夠擷取、處理和嵌入自訂資料，從而提高生成回應的相關性和上下文。您可以根據您的具體需求，在包括 Vertex AI Search 和 Vertex AI Vector Search 在內的不同資料儲存選項之間進行選擇。

該代理提供了使用您的自訂程式碼建立 Vertex AI Pipeline 的基礎設施。由於它建構在 Vertex AI Pipelines 之上，您可以受益於排程執行、週期性執行和隨選觸發等功能。對於處理 TB 等級的資料，我們建議將 Vertex AI Pipelines 與 BigQuery 或 Dataflow 等資料分析工具結合使用。

![搜尋代理示範](https://storage.googleapis.com/github-repo/generative-ai/sample-apps/e2e-gen-ai-app-starter-pack/starter-pack-search-pattern.gif)

## 架構

該代理實現了以下架構：

![架構圖](https://storage.googleapis.com/github-repo/generative-ai/sample-apps/e2e-gen-ai-app-starter-pack/agentic_rag_vertex_ai_search_architecture.png)

### 主要功能

- **建構於代理開發套件 (ADK) 之上：** ADK 是一個用於開發和部署 AI 代理的靈活、模組化的框架。它與 Google 生態系統和 Gemini 模型整合，支援各種大型語言模型 (LLM) 和開源 AI 工具，從而實現簡單和複雜的代理架構。
- **靈活的資料儲存選項：** 根據您的特定需求，在 Vertex AI Search 或 Vertex AI Vector Search 之間進行選擇，以實現高效的資料儲存和檢索。
- **自動化資料擷取管線：** 自動化從輸入來源擷取資料的過程。
- **自訂嵌入：** 使用 Vertex AI Embeddings 生成嵌入，並將其整合到您的資料中，以增強語意搜尋。
- **Terraform 部署：** 擷取管線與入門套件的其餘基礎設施一起透過 Terraform 進行實例化。
- **CI/CD 整合：** 擷取管線的部署已新增到入門套件的 CD 管線中。
- **可客製化的程式碼：** 輕鬆調整和客製化程式碼，以適應您特定的應用程式需求和資料來源。
