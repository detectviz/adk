# 範例代理 (Sample Agents)

此資料夾包含 [Python 代理開發套件 (Python Agent Development Kit)](https://github.com/google/adk-python) (Python ADK) 的範例代理。

此目錄中的每個資料夾都包含一個不同的代理範例。

## 入門指南 (Getting Started)

1.  **先決條件：**

    *   Python 代理開發套件 (Python Agent Development Kit)。請參閱 [ADK 快速入門指南](https://google.github.io/adk-docs/get-started/quickstart/)。
    *   Python 3.9+ 和 [Poetry](https://python-poetry.org/docs/#installation)。
    *   存取 Google Cloud (Vertex AI) 及/或 Gemini API 金鑰 (依代理而定 - 請參閱各個代理的 README)。

2.  **執行範例代理：**

    *   導航至特定代理的目錄 (例如 `cd agents/llm-auditor`)。
    *   將 `.env.example` 檔案複製為 `.env` 並填入必要的環境變數 (API 金鑰、專案 ID 等)。有關所需變數的詳細資訊，請參閱代理的特定 README。
    *   使用 Poetry 安裝依賴項：`poetry install`
    *   遵循代理 `README.md` 中的說明來執行它 (例如，使用 `adk run .` 或 `adk web`)。


## 代理類別 (Agent Categories)

請查看以下按類別組織的代理範例：

| 代理名稱 (Agent Name)                                  | 使用案例 (Use Case)                                                                                                                              | 標籤 (Tag) | 互動類型 (Interaction Type) | 複雜度 (Complexity) | 代理類型 (Agent Type)   | 垂直領域 (Vertical)                      |
| :------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------- | :--- | :--------------- | :--------- | :----------- | :---------------------------- |
| [學術研究 (Academic Research)](academic-research) | 協助研究人員識別最新出版物並發現新興研究領域。 |   多代理 (Multi-agent), 自訂工具 (Custom tool), 評估 (Evaluation) | 工作流程 (Workflow) | 簡單 (Easy) | 多代理 (Multi Agent) | 學術界 (Academia)                        |
| [品牌搜尋優化 (Brand Search Optimization)](brand-search-optimization) | 透過分析和比較熱門搜尋結果來豐富電子商務產品資料。有助於解決「空值和低回收率」/「零結果」搜尋等問題，並找出產品資料中的差距。                                 |   多代理 (Multi-agent), 自訂工具 (Custom tool), BigQuery 連線, 評估 (Evaluation), 電腦使用 (Computer use)   | 工作流程 (Workflow) | 簡單 (Easy) | 多代理 (Multi Agent) | 零售 (Retail)                        |
| [Cymbal 居家與園藝客服代理 (Cymbal Home & Garden Customer Service Agent)](customer-service) | 提供居家裝修、園藝及相關用品的客戶服務、產品選擇、訂單管理。                                |  自訂工具 (Custom tool), 非同步工具 (Async tool), 外部系統呼叫 (External system calls), 即時串流 (Live streaming), 多模態 (Multimodal)   | 對話式 (Conversational)         | 進階 (Advanced)     | 單一代理 (Single Agent)       | 零售 (Retail)                        |
| [資料科學代理 (Data Science Agent)](data-science) | 一個為複雜資料分析而設計的多代理系統。                                                                          |  函式工具 (Python), 代理工具 (Agent tool), NL2SQL, 結構化資料, 資料庫   | 對話式 (Conversational) | 進階 (Advanced) | 多代理 (Multi Agent) | 通用 (Horizontal)                    |
| [財務顧問 (Financial Advisor)](financial-advisor) |  透過提供金融和投資相關主題的教育內容來協助人類財務顧問。  |   風險分析, 策略生成, 摘要, 報告生成  | 工作流程 (Workflow) | 簡單 (Easy) | 多代理 (Multi Agent) | 金融服務 (Financial Services)            |
| [聯邦公開市場委員會研究代理 (FOMC Research Agent)](fomc-research) | 市場事件分析。                                                                                                                   |   摘要, 報告生成  | 工作流程 (Workflow) | 進階 (Advanced) | 多代理 (Multi Agent) | 金融服務 (Financial Services)            |
| [Gemini 全端 (Gemini Fullstack)](gemini-fullstack) | 一個使用 Gemini 建構複雜全端研究代理的藍圖。展示了複雜的代理工作流程、模組化代理和人在環 (Human-in-the-Loop, HITL) 步驟。 | 多代理 (Multi-agent), 函式呼叫 (Function calling), 網頁搜尋, React 前端, FastAPI 後端, 人在環 (Human-in-the-Loop) | 工作流程 (Workflow) | 進階 (Advanced) | 多代理 (Multi Agent) | 通用 (Horizontal) |
| [大型語言模型稽核員 (LLM Auditor)](llm-auditor)                   | 聊天機器人回應驗證、內容稽核。                                                                                         |   Gemini 搭配 Google 搜尋, 多代理 (Multi-agent)  | 工作流程 (Workflow)         | 簡單 (Easy)       | 多代理 (Multi Agent)  | 通用 (Horizontal)                    |
| [機器學習工程代理 (Machine Learning Engineering Agent)](machine-learning-engineering)                   | 自動建立/訓練機器學習 (ML) 模型，以在各種機器學習任務上達到最先進的性能。 | 機器學習 (ML) 任務, 自動化機器學習模型改進, Kaggle 競賽 | 對話式 (Conversational)         | 進階 (Advanced)       | 多代理 (Multi Agent)  | 通用 (Horizontal)                    |
| [行銷代理 (Marketing Agency)](marketing-agency)                   | 簡化新網站和產品的發布流程。識別最佳的 DNS 網域、生成整個網站、制定行銷策略並設計品牌資產。 | 內容生成, 網站創建, 程式碼生成, 策略發展  | 工作流程 (Workflow)         | 簡單 (Easy)       | 多代理 (Multi Agent)  | 通用 (Horizontal)                    |
| [個人化購物 (Personalized Shopping)](personalized-shopping) | 產品推薦。                                                                                                               | 電子商務, 個人化代理, 購物助理, 單一代理, 產品推薦, 產品發現, 聊天機器人    | 對話式 (Conversational)         | 簡單 (Easy)        | 單一代理 (Single Agent)     | 電子商務 (E-commerce)                    |
| [Vertex AI 檢索代理 (Vertex AI Retrieval Agent)](RAG) | 由 RAG 驅動的代理 / 回答與上傳至 Vertex AI RAG 引擎的文件相關的問題，提供附有來源資料引用的資訊性回應。                              |  RAG 引擎   | 工作流程 (Workflow)              | 中等 (Intermediate)        | 單一代理 (Single Agent)       | 通用 (Horizontal)                    |
| [軟體錯誤助理 (Software Bug Assistant)](software-bug-assistant)         | 透過查詢內部票務系統和外部知識來源 (GitHub, StackOverflow, Google 搜尋) 來尋找相似問題和診斷方法，以協助解決軟體錯誤。 | RAG, MCP, 錯誤追蹤, Google 搜尋, IT 支援, 資料庫整合, API  | 工作流程 (Workflow)/對話式 (Conversational) | 中等 (Intermediate) | 單一代理 (Single Agent) | 通用 (Horizontal) / IT 支援 (IT Support)            |
| [旅遊管家 (Travel Concierge)](travel-concierge) | 旅遊管家、數位任務助理。                                                                                               |   函式工具 (Python), 自訂工具, 代理工具, 輸入與輸出結構描述 (Schema), 可更新的上下文 (Context), 動態指令  | 對話式 (Conversational) | 進階 (Advanced) | 多代理 (Multi Agent) | 旅遊 (Travel)                        |
| [汽車保險代理 (Auto Insurance Agent)](auto-insurance-agent) | 管理會員、理賠、獎勵和道路救援的汽車保險代理。                                                                                              |   [Apigee](https://cloud.google.com/apigee/docs/api-platform/get-started/what-apigee), [Apigee API 中心 (Apigee API hub)](https://cloud.google.com/apigee/docs/apihub/what-is-api-hub), 代理工具 (Agent Tool)  | 對話式 (Conversational) | 簡單 (Easy) | 多代理 (Multi Agent) | 金融服務 (Financial Services)       
| [圖片評分 (Image Scoring)](image-scoring) | 根據政策生成圖片並對生成的圖片進行評分以衡量政策遵循度的圖片評分代理。  | 函式工具 (Python), 代理工具, Imagen, 循環代理 (Loop Agent) | 對話式 (Conversational) | 簡單 (Easy)       | 多代理 (Multi Agent)  | 通用 (Horizontal) 



## 如何使用本儲存庫中的代理 (Using the Agents in this Repository)

本節提供有關如何執行、測試、評估和潛在部署本儲存庫中代理範例的一般性指導。雖然核心步驟相似，但**每個代理在其專屬的 `README.md` 檔案中都有其特定的要求和詳細說明。**

**請務必查閱特定代理目錄內的 `README.md` (例如 `agents/fomc-research/README.md`) 以獲得最準確、最詳細的步驟。**

以下是您可以預期的一般工作流程：

1.  **選擇一個代理：** 從上表中選擇一個符合您興趣或使用案例的代理。
2.  **導航至代理目錄：** 開啟您的終端機，並從主儲存庫目錄變更到代理的主目錄：
    ```bash
    cd python/agents/<agent-name>
    # 範例: cd python/agents/fomc-research
    ```
3.  **檢閱代理的 README：** **這是最關鍵的步驟。** 開啟此目錄中的 `README.md` 檔案。它將包含：
    *   代理用途和架構的詳細概述。
    *   特定的先決條件 (例如，API 金鑰、雲端服務、資料庫設定)。
    *   逐步的設定和安裝說明。
    *   在本機執行代理的指令。
    *   執行評估的說明 (如果適用)。
    *   執行測試的說明 (如果適用)。
    *   部署步驟 (如果適用)。

4.  **設定與配置：**
    *   **先決條件：** 確保您已滿足主要「入門指南」部分列出的一般先決條件，*以及*代理 README 中提到的任何特定先決條件。
    *   **依賴項：** 使用 Poetry 安裝代理特定的 Python 依賴項 (此指令通常在代理的主目錄中執行)：
        ```bash
        poetry install
        ```
    *   **環境變數：** 大多數代理需要透過環境變數進行配置。將代理目錄中的 `.env.example` 檔案複製為 `.env`，並填入您的特定值 (API 金鑰、專案 ID 等)。有關所需變數的詳細資訊，請參閱代理的 README。您可能需要將這些變數載入到您的 shell 環境中 (例如，在 bash 中使用 `source .env` 或 `set -o allexport; . .env; set +o allexport`)。

5.  **在本機執行代理：**
    *   代理通常可以使用 ADK CLI 或 ADK Dev UI 在本機執行以進行測試和互動。具體指令可能略有不同 (例如，執行的確切目錄)，因此請檢查代理的 README。
    *   **CLI：** 通常涉及從代理的*核心程式碼*目錄 (例如 `agents/fomc-research/fomc_research/`) 中執行 `adk run .`。
        ```bash
        # 範例 (請檢查代理的 README 以獲得確切路徑)
        cd agents/fomc-research/fomc_research/
        adk run .
        ```
    *   **ADK Dev UI：** 通常涉及從代理的*主*目錄 (例如 `agents/fomc-research/`) 中執行 `adk web .`。
        ```bash
        # 範例 (請檢查代理的 README 以獲得確切路徑)
        cd agents/fomc-research/
        adk web
        ```
        然後，在您的瀏覽器中打開提供的 URL，並從下拉式選單中選擇代理。

6.  **評估代理：**
    *   許多代理包含一個 `eval/` 目錄，其中包含用於評估性能的腳本和資料。
    *   代理的 README 將解釋如何執行這些評估 (例如，`python eval/test_eval.py`)。這有助於驗證代理在特定任務上的有效性。

7.  **測試代理組件：**
    *   `tests/` 目錄通常包含單元或整合測試 (例如，針對自訂工具)。
    *   這些測試確保各個程式碼組件功能正常。
    *   代理的 README 可能會提供如何執行這些測試的說明，通常使用像 `pytest` 這樣的框架。

8.  **部署代理：**
    *   某些代理設計用於部署，通常部署到 [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)。
    *   `deployment/` 目錄包含必要的腳本 (如 `deploy.py`) 和配置文件。
    *   部署通常需要特定的 Google Cloud 設定 (專案 ID、已啟用的 API、權限)。代理的 README 和 `deployment/` 資料夾中的腳本提供了詳細說明，類似於 `fomc-research` 代理文件中顯示的範例。

透過遵循每個代理 `README.md` 中的具體說明，您可以有效地設定、執行、評估、測試和潛在地部署這些多樣化的範例。

## 代理的目錄結構 (Directory Structure of Agents)
此處展示的每個代理都按以下方式組織：

```bash
├── agent-name
│   ├── agent_name/
│   │   ├── shared_libraries/               # 包含工具輔助函式的資料夾
│   │   ├── sub_agents/                     # 每個子代理的資料夾
│   │   │   │   ├── tools/                  # 子代理的工具資料夾
│   │   │   │   ├── agent.py                # 子代理的核心邏輯
│   │   │   │   └── prompt.py               # 子代理的提示詞
│   │   │   └── ...                         # 更多子代理
│   │   ├── __init__.py                     # 初始化代理
│   │   ├── tools/                          # 包含路由器代理使用的工具程式碼
│   │   ├── agent.py                        # 包含代理的核心邏輯
│   │   ├── prompt.py                       # 包含代理的提示詞
│   ├── deployment/                         # 部署到 Agent Engine
│   ├── eval/                               # 包含評估方法的資料夾
│   ├── tests/                              # 包含工具單元測試的資料夾
│   ├── agent_pattern.png                   # 代理模式的圖表
│   ├── .env.example                        # 儲存代理特定的環境變數
│   ├── pyproject.toml                      # 專案配置
│   └── README.md                           # 提供代理的概述
```
### 通用結構 (General Structure)

每個代理的根目錄都位於 `agents/` 下的自己的目錄中。例如，`llm-auditor` 代理位於 `agents/llm-auditor/`。


#### 目錄詳解 (Directory Breakdown)

1.  **`agent_name/` (核心代理程式碼)**:
    *   此目錄包含代理的核心邏輯。
    *   **`shared_libraries/`**: (可選) 包含多個子代理共享的程式碼。
    *   **`sub_agents/`**: 包含子代理的定義和邏輯。
        *   每個子代理都有自己的目錄 (例如，`llm-auditor` 中的 `critic/`、`reviser/`)。
        *   **`tools/`**: 包含特定於該子代理的任何自訂工具。
        *   **`agent.py`**: 定義子代理的行為，包括其模型、工具和指令。
        *   **`prompt.py`**: 包含用於指導子代理行為的提示詞。
    *   **`__init__.py`**: 一個初始化檔案，它從資料夾中匯入 `agent.py`，以將 `agent_name` 目錄標記為 Python 套件。
    *   **`tools/`**: 包含主代理使用的任何自訂工具。
    *   **`agent.py`**: 定義主代理的行為，包括其子代理、模型、工具和指令。
    *   **`prompt.py`**: 包含用於指導主代理行為的提示詞。

    請注意，初始資料夾名稱中的單字之間使用「-」，而核心邏輯則儲存在單字之間使用「_」的同名資料夾中 (例如 `llm_auditor`)。這是由於 poetry 強制的專案結構所致。

2.  **`deployment/`**

    *   包含將代理部署到像 Vertex AI Agent Engine 這樣的平台所需的腳本和檔案。
    *   `deploy.py` 腳本通常位於此處，處理部署過程。

3.  **`eval/`**

    *   包含用於評估代理性能的資料和腳本。
    *   測試資料 (例如 `.test.json` 檔案) 和評估腳本 (例如 `test_eval.py`) 通常位於此處。

4.  **`tests/`**

    *   包含代理的單元和整合測試。
    *   測試檔案 (例如 `test_agents.py`) 用於驗證代理的功能。

5.  **`agent_pattern.png`**

    *   一個視覺化圖表，說明代理的架構，包括其子代理及其互動。

6.  **`.env.example`**

    *   一個範例檔案，顯示執行代理所需的環境變數。
    *   使用者應將此檔案複製為 `.env` 並填入其特定值。

7.  **`pyproject.toml`**

    *   包含專案元數據、依賴項和建置系統配置。
    *   由 Poetry 管理以進行依賴項管理。

8.  **`README.md`**

    *   提供特定於代理的詳細文件，包括其用途、設定說明、使用範例和自訂選項。

## 範例：`llm-auditor`

`llm-auditor` 代理有效地展示了這種結構。它具有：

*   一個核心 `llm_auditor/` 目錄。
*   位於 `llm_auditor/sub_agents/` 中的子代理，例如 `critic/` 和 `reviser/`。
*   位於 `deployment/` 中的部署腳本。
*   位於 `eval/` 中的評估資料和腳本。
*   位於 `tests/` 中的測試。
*   一個 `.env.example` 檔案。
*   一個 `pyproject.toml` 檔案。
*   一個 `README.md` 檔案。
