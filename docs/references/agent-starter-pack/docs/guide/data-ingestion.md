# 用於 RAG 的資料擷取管線

Agent Starter Pack 簡化了將資料擷取整合到您的代理專案中的過程。這對於需要文件處理和檢索的代理特別有用，例如檢索增強生成 (Retrieval Augmented Generation, RAG) 應用程式。

## 總覽

資料擷取可自動化以下流程：

-   從各種來源載入資料。
-   處理文件並進行分塊。
-   使用 Vertex AI 生成嵌入 (embeddings)。
-   將處理後的資料和嵌入儲存在 **Vertex AI Search** 或 **Vertex AI Vector Search** 中。
-   排程定期資料更新。

## 何時包含資料擷取

在以下情況下，請考慮使用資料擷取：

-   您的代理需要搜尋或參考大量文件。
-   您正在開發一個基於 RAG 的應用程式。
-   您的代理的知識庫需要定期更新。
-   您希望保持代理內容的更新和可搜尋性。

## 使用方式

### 專案建立

在專案建立期間，可以透過兩種方式包含資料擷取：

1.  **自動包含**：某些代理 (例如專為 RAG 設計的 `agentic_rag`) 會因其性質而自動包含它。如果未指定，系統將提示您選擇一個資料儲存庫 (`vertex_ai_search` 或 `vertex_ai_vector_search`)。

2.  **可選包含**：對於其他代理，使用 `--include-data-ingestion` 旗標並透過 `--datastore` (或 `-ds`) 指定所需的資料儲存庫來新增它：

    ```bash
    # 使用 Vertex AI Search
    agent-starter-pack create my-agent-project --include-data-ingestion -ds vertex_ai_search

    # 使用 Vertex AI Vector Search
    agent-starter-pack create my-agent-project --include-data-ingestion -ds vertex_ai_vector_search
    ```
    如果在指定 `--include-data-ingestion` 時省略了 `--datastore`，系統將提示您選擇一個。

### 基礎設施設定

Terraform IaC (基礎設施即程式碼) 會根據您選擇的資料儲存庫設定必要的基礎設施：

-   **Vertex AI Search**：資料儲存庫。
-   **Vertex AI Vector Search**：索引、索引端點和用於暫存資料的儲存桶。
-   必要的服務帳戶和權限。
-   用於管線產物的儲存桶。
-   BigQuery 資料集 (如果適用)。

## 入門

1.  建立您的專案並包含資料擷取，同時指定您的資料儲存庫：

    ```bash
    # 使用 Vertex AI Search 的範例
    agent-starter-pack create my-project -ds vertex_ai_search

    # 使用 Vertex AI Vector Search 的範例
    agent-starter-pack create my-project -ds vertex_ai_vector_search
    ```

2.  遵循產生的 `data_ingestion/README.md` 中的設定說明。在執行資料管線之前，請先部署 Terraform 基礎設施 (至少在您的開發專案中)。

## 了解更多

-   [Vertex AI Pipelines](https://cloud.google.com/vertex-ai/docs/pipelines/introduction) 用於管線管理。
-   [Vertex AI Search 文件](https://cloud.google.com/generative-ai-app-builder/docs/enterprise-search-introduction) 用於搜尋功能。
-   [Vertex AI Vector Search 文件](https://cloud.google.com/vertex-ai/docs/vector-search/overview) 用於向量資料庫功能。
