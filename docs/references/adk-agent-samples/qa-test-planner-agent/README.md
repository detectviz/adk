# QA 測試計畫代理

![Python](https://img.shields.io/badge/python-v3.12+-blue.svg)
![Google ADK](https://img.shields.io/badge/Built%20with-Google%20ADK-green)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)

> **⚠️ 免責聲明：這不是 Google 官方支援的產品。此專案僅供示範之用，不適用於生產環境。**

## 總覽

QA 測試計畫代理是一款智慧助理 (intelligent assistant)，採用 Google Agent Development Kit (ADK) 並結合 Gemini Flash 2.5 的思維能力，旨在簡化軟體開發團隊 (software development teams) 的測試計畫 (test planning) 流程。這款由 AI 驅動的代理可自動分析 Confluence 中的產品需求文件 (Product Requirement Documents, PRD)，並以與 Jira Xray 相容的格式產生全面的測試計畫，從而彌補產品需求與品質保證 (quality assurance) 之間的差距。

### 為何使用 QA 測試計畫代理？

- **節省時間**：減少從產品需求建立測試計畫的人工作業
- **提高涵蓋範圍**：AI 驅動的分析有助於找出可能被忽略的測試情境 (testing scenarios)
- **標準化流程**：產生與您現有工具整合的一致測試計畫格式 (test plan formats)

## 功能

- **🔍 搜尋 Confluence**：輕鬆在您的 Confluence 空間中搜尋並擷取產品需求文件 (PRD) 和其他相關文件
- **📊 文件評估**：取得 AI 專家對 PRD 的分析，並提供需要釐清或改進之處的建議
- **📝 測試計畫產生**：以與 Jira Xray 相容的格式（Markdown 表格）建立詳細的測試計畫，以便實作

## 入門

這些說明將協助您取得專案的複本，並在您的本機電腦上執行以進行開發和測試。

### 先決條件

- Python 3.12 或更高版本
- [uv](https://github.com/astral-sh/uv) - 一款極速的 Python 套件安裝程式 (package installer) 和解析器 (resolver)
- 具有 API 存取權的 Atlassian Confluence 帳戶，其中包含產品需求文件 (PRD) 的空間

### 安裝

1. **複製儲存庫：**
   ```bash
   git clone https://github.com/yourusername/qa-test-planner-agent.git
   cd qa-test-planner-agent
   ```

2. **安裝相依性：**
   ```bash
   uv sync
   ```

### 設定

代理需要憑證 (credentials) 才能存取 Confluence。這些憑證是透過 `qa_test_planner` 目錄中的 `.env` 檔案進行管理。

1. 將 qa_test_planner_example 重新命名為 qa_test_planner 目錄，並將 .env.example 檔案複製為 .env

2. **將以下環境變數 (environment variables)**新增至 `.env` 檔案，並填寫您的 Confluence 詳細資料：

   ```env
   CONFLUENCE_URL="https://your-domain.atlassian.net"
   CONFLUENCE_USERNAME="your-email@example.com"
   CONFLUENCE_TOKEN="your-confluence-api-token"
   CONFLUENCE_PRD_SPACE_ID="YOUR_PRD_SPACE_ID"
   ```

   - `CONFLUENCE_URL`：您的 Confluence 執行個體的 URL
   - `CONFLUENCE_USERNAME`：您用於 Confluence 的電子郵件地址
   - `CONFLUENCE_TOKEN`：您的 Confluence API 權杖（可在此處產生[一個](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)）
   - `CONFLUENCE_PRD_SPACE_ID`：包含您的 PRD 的 Confluence 空間的 ID

## 使用方式

從專案根目錄使用以下指令啟動代理：

```bash
uv run adk web
```

這將會初始化代理並啟動一個網頁介面 (web interface)，您可以在其中：

1. **依標題、內容或其他條件搜尋 PRD**
2. **在 AI 協助下檢視和分析**文件內容
3. **根據選定的 PRD 產生測試計畫**
4. **將產生的測試計畫匯出**為 CSV

## 範例工作流程

1. 使用 `uv run adk web` 啟動代理
2. 在網頁 UI 中，依名稱或內容搜尋特定的 PRD
3. 透過 AI 產生的洞見檢閱 PRD
4. 要求產生測試計畫
5. 將測試計畫匯出為 CSV

## 部署到 Cloud Run

gcloud run deploy qa-test-planner-agent \
                  --source . \
                  --port 8080 \
                  --project {YOUR_PROJECT_ID} \
                  --allow-unauthenticated \
                  --region us-central1 \
                  --update-env-vars GOOGLE_GENAI_USE_VERTEXAI=1 \
                  --update-env-vars GOOGLE_CLOUD_PROJECT={YOUR_PROJECT_ID} \
                  --update-env-vars GOOGLE_CLOUD_LOCATION=global \
                  --update-env-vars CONFLUENCE_URL={YOUR_CONFLUENCE_URL} \
                  --update-env-vars CONFLUENCE_USERNAME={YOUR_CONFLUENCE_USERNAME} \
                  --update-env-vars CONFLUENCE_TOKEN={YOUR_CONFLUENCE_TOKEN} \
                  --update-env-vars CONFLUENCE_PRD_SPACE_ID={YOUR_PRD_SPACE_ID} \
                  --memory 1G
