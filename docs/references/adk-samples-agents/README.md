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

| 代理名稱 (Agent Name) | 使用案例 (Use Case) | 標籤 (Tag) | 互動類型 (Interaction Type) | 複雜度 (Complexity) | 代理類型 (Agent Type) | 垂直領域 (Vertical) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [A2A 分析代理程式 (A2A Analytics Agent)](analytics) | 一個輕量級的分析代理程式，可根據包含資料的使用者提示產生圖表 (例如長條圖)。它使用 CrewAI 來解譯提示，使用 pandas 進行資料處理，並使用 matplotlib 將圖表呈現為 PNG 影像。 | `Analytics`, `Data Visualization`, `Charts`, `CrewAI`, `pandas`, `matplotlib`, `A2A` | 請求/回應 (Request/Response) | 中等 (Intermediate) | 單一代理程式 (Single Agent) | 資料科學 / 分析 (Data Science / Analytics) |
| [A2A gRPC 代理程式 (A2A gRPC Agent)](dice_agent_grpc) | 建立一個支援 gRPC 傳輸的 A2A 伺服器來與代理程式互動。此範例也展示了一種代理程式發現機制，即在一個熟知的 URL 上提供公開的代理程式卡片。 | `gRPC`, `A2A`, `SDK Example`, `Discovery`, `Beginner` | 請求/回應 (Request/Response) | 簡單 (Easy) | 單一代理程式 (Single Agent) | 開發人員工具 / SDK 範例 (Developer Tools / SDK Sample) |
| [A2A GitHub 代理程式 (A2A GitHub Agent)](github-agent) | 一個智慧型 GitHub 代理程式，可以使用自然語言查詢 GitHub 儲存庫、最近的更新、提交和專案活動。它利用工具與 GitHub API 互動。 | `GitHub`, `API`, `Tools`, `Developer Tools`, `A2A`, `OpenRouter` | 對話式 (Conversational) | 中等 (Intermediate) | 單一代理程式 (Single Agent) | 軟體開發 / 開發人員工具 (Software Development / Developer Tools) |
| [A2A MCP 無框架範例 (A2A MCP No-Framework Example)](a2a-mcp-without-framework) | 展示一個使用 `a2a-python` SDK 的基本客戶端/伺服器設定，用於多輪對話協定 (MCP)，而沒有任何特定的 LLM 框架。 | `A2A`, `MCP`, `SDK`, `Client/Server` | 程式化 / CLI (Programmatic / CLI) | 簡單 (Easy) | 單一代理程式 (Single Agent) | 開發人員工具 / SDK 範例 (Developer Tools / SDK Sample) |
| [A2A MCP 旅遊規劃器 (A2A MCP Travel Planner)](a2a_mcp) | 一個多代理系統，使用模型內容協定 (MCP) 作為註冊表來發現和協調專門的代理程式（例如，航班、飯店、租車）來規劃和預訂一趟旅程。 | `Multi-agent`, `A2A`, `MCP`, `Orchestration`, `LangGraph`, `ADK` | 程式化 / CLI (Programmatic / CLI) | 進階 (Advanced) | 多代理程式 (Multi Agent) | 旅遊 (Travel) |
| [A2A 追蹤範例 (A2A Tracing Example)](a2a_telemetry) | 展示如何啟用和匯出 A2A 伺服器和客戶端的分布式追蹤到 Jaeger 和 Grafana，以進行視覺化和分析。 | `Tracing`, `Observability`, `OpenTelemetry`, `Jaeger`, `Grafana`, `A2A`, `SDK` | 對話式 (Conversational) | 中等 (Intermediate) | 單一代理程式 (Single Agent) | 開發人員工具 / SDK 範例 (Developer Tools / SDK Sample) |
| [學術研究 (Academic Research)](academic-research) | 協助研究人員識別最新出版物並發現新興研究領域。 | `Multi-agent`, `Custom tool`, `Evaluation` | 工作流程 (Workflow) | 簡單 (Easy) | 多代理 (Multi Agent) | 學術界 (Academia) |
| [ADK 生日規劃師 (ADK Birthday Planner)](birthday_planner_adk) | 一個多代理程式系統，用於協助規劃生日派對。主規劃代理程式會將日曆相關的任務（例如檢查空檔）委派給一個專門的日曆代理程式。 | `Multi-agent`, `ADK`, `A2A`, `Delegation`, `Planner` | 對話式 (Conversational) | 中等 (Intermediate) | 多代理程式 (Multi Agent) | 個人助理 / 活動規劃 (Personal Productivity / Event Planning) |
| [Cloud Run 上的 ADK 代理程式 (ADK Agent on Cloud Run)](adk_cloud_run) | 展示如何將一個啟用 A2A、以 ADK 建置的代理程式部署到 Google Cloud Run。它涵蓋了服務帳戶設定、IAM 權限、密碼管理和部署設定。 | `Deployment`, `Google Cloud Run`, `IAM`, `Secret Manager`, `AlloyDB`, `A2A`, `ADK` | 程式化 / CLI (Programmatic / CLI) | 進階 (Advanced) | 單一代理程式 (Single Agent) | 雲端基礎架構 / 開發人員工具 (Cloud Infrastructure / Developer Tools) |
| [ADK 費用報銷代理程式 (ADK Expense Reimbursement Agent)](adk_expense_reimbursement) | 一個處理費用報銷請求的代理程式。如果初始請求缺少詳細資訊，它會動態產生並回傳一個網頁表單，供使用者提供必要的資訊。 | `Human-in-the-loop`, `Web Form`, `ADK`, `A2A` | 對話式 / 網頁表單 (Conversational / Web Form) | 簡單 (Easy) | 單一代理程式 (Single Agent) | 金融 / 商業營運 (Finance / Business Operations) |
| [ADK 趣味知識代理程式 (ADK Fun Facts Agent)](adk_facts) | 一個簡單的代理程式，可針對給定主題產生趣味知識。它展示了 ADK 代理程式的基本結構，並且可以部署到 Cloud Run。 | `Beginner`, `ADK`, `A2A`, `Cloud Run` | 對話式 (Conversational) | 簡單 (Easy) | 單一代理程式 (Single Agent) | 娛樂 / 一般 (Entertainment / General) |
| [ADK 影片生成代理程式 (VEO) (ADK Video Generation Agent (VEO))](veo_video_gen) | 一個使用 Google 的 VEO 模型從文字提示生成影片的代理程式。它接受文字提示，啟動影片生成，提供串流進度更新，最後回傳一個指向 GCS 中生成影片的簽名 URL。 | `Video Generation`, `Generative AI`, `VEO`, `ADK`, `A2A`, `GCS` | 請求/回應 (Request/Response) | 進階 (Advanced) | 單一代理程式 (Single Agent) | 內容創作 / 多媒體 (Content Creation / Multimedia) |
| [對抗性代理程式模擬 (Adversarial Agent Simulation)](any_agent_adversarial_multiagent) | 一個多代理程式模擬，其中「攻擊者」代理程式試圖透過對話讓「防禦者」代理程式說出特定短語。旨在測試 AI 對抗性提示的穩健性。 | `Adversarial Testing`, `Simulation`, `Red Team`, `Blue Team`, `any-agent`, `A2A`, `Multi-agent` | 程式化 / 自動化模擬 (Programmatic / Automated Simulation) | 中等 (Intermediate) | 多代理程式 (Multi Agent) | AI 安全 / 資安 (AI Safety / Security) |
| [AG2 MCP 代理程式 (AG2 MCP Agent)](ag2) | 一個使用 AG2 框架建置的代理程式，它使用模型內容協定 (MCP) 來存取工具（如網頁瀏覽、程式碼執行）。它透過 A2A 協定公開，展示了不同代理程式框架如何通訊。 | `AG2`, `MCP`, `A2A`, `Interoperability`, `Frameworks`, `Container` | 對話式 (Conversational) | 進階 (Advanced) | 單一代理程式 (Single Agent) | 開發人員工具 / 框架整合 (Developer Tools / Framework Integration) |
| [Airbnb 與天氣規劃器 (Airbnb and Weather Planner)](airbnb_planner_multiagent) | 一個多代理系統，其中一個主機代理程式在兩個遠端的專門代理程式之間協調任務：一個用於尋找 Airbnb 房源，另一個用於取得天氣預報。 | `Multi-agent`, `A2A`, `ADK`, `Orchestration`, `MCP` | 對話式 (Conversational) | 進階 (Advanced) | 多代理程式 (Multi Agent) | 旅遊 (Travel) |
| [汽車保險代理 (Auto Insurance Agent)](auto-insurance-agent) | 管理會員、理賠、獎勵和道路救援的汽車保險代理。 | `Apigee`, `Apigee API hub`, `Agent Tool` | 對話式 (Conversational) | 簡單 (Easy) | 多代理 (Multi Agent) | 金融服務 (Financial Services) |
| [Azure AI Foundry SDK 範例 (Azure AI Foundry SDK Examples)](azureaifoundry_sdk) | 一系列範例，展示如何將 Microsoft 的 Azure AI Foundry Agent Service 與 Google 的 A2A 協定整合，涵蓋從簡單到複雜的多代理架構。 | `Azure AI`, `Microsoft`, `A2A`, `SDK`, `MCP`, `Semantic Kernel`, `Multi-agent`, `Interoperability` | 對話式 / 程式化 (Conversational / Programmatic) | 進階 (Advanced) | 單一 & 多代理 (Single & Multi Agent) | 雲端基礎架構 / 框架整合 (Cloud Infrastructure / Framework Integration) |
| [BeeAI 聊天代理程式 (BeeAI Chat Agent)](beeai-chat) | 展示如何使用 BeeAI 框架建立一個互動式聊天代理程式，並透過 A2A 協定使其可供其他代理程式使用。 | `BeeAI`, `A2A`, `Framework Integration`, `Conversational`, `Container` | 對話式 (Conversational) | 簡單 (Easy) | 單一代理程式 (Single Agent) | 開發人員工具 / 框架整合 (Developer Tools / Framework Integration) |
| [品牌搜尋優化 (Brand Search Optimization)](brand-search-optimization) | 透過分析和比較熱門搜尋結果來豐富電子商務產品資料。 | `Multi-agent`, `Custom tool`, `BigQuery`, `Evaluation`, `Computer use` | 工作流程 (Workflow) | 簡單 (Easy) | 多代理 (Multi Agent) | 零售 (Retail) |
| [CaMeL 安全代理 (CaMeL-Powered Secure Agent)](camel) | 展示 CaMeL 框架，用於安全執行和資料流管理，可防禦提示注入攻擊。 | `Security`, `Prompt Injection`, `CaMeL`, `Data Flow`, `Multi-agent`, `ADK` | 對話式 / CLI (Conversational / CLI) | 進階 (Advanced) | 多代理 (Multi Agent) | AI 安全 / 資安 (AI Safety / Security) |
| [內容規劃師代理程式 (Content Planner Agent)](content_planner) | 根據使用者提供的高階描述，建立詳細的內容大綱。這個代理程式可以作為更大型的內容創作多代理系統的一部分。 | `Content Creation`, `Planning`, `ADK`, `A2A` | 請求/回應 (Request/Response) | 簡單 (Easy) | 單一代理程式 (Single Agent) | 行銷 / 內容創作 (Marketing / Content Creation) |
| [CrewAI 圖片生成代理程式 (CrewAI Image Generation Agent)](crewai) | 一個使用 CrewAI 框架和 Gemini API 的簡單代理程式，可根據文字提示生成圖片。 | `CrewAI`, `Image Generation`, `Gemini`, `A2A`, `Framework Integration`, `Container` | 請求/回應 (Request/Response) | 中等 (Intermediate) | 單一代理程式 (Single Agent) | 內容創作 / 開發人員工具 (Content Creation / Developer Tools) |
| [Cymbal 居家與園藝客服代理 (Cymbal Home & Garden Customer Service Agent)](customer-service) | 提供居家裝修、園藝及相關用品的客戶服務、產品選擇、訂單管理。 | `Custom tool`, `Async tool`, `External system calls`, `Live streaming`, `Multimodal` | 對話式 (Conversational) | 進階 (Advanced) | 單一代理程式 (Single Agent) | 零售 (Retail) |
| [資料科學代理 (Data Science Agent)](data-science) | 一個為複雜資料分析而設計的多代理系統。 | `Python`, `Agent tool`, `NL2SQL`, `Structured Data`, `Database` | 對話式 (Conversational) | 進階 (Advanced) | 多代理 (Multi Agent) | 通用 (Horizontal) |
| [A2A REST 代理 (A2A REST Agent)](dice_agent_rest) | 建立一個支援 REST 傳輸的 A2A 伺服器，可與代理互動。此代理可以擲骰子並檢查質數。 | `REST`, `A2A`, `SDK Example`, `Beginner` | 請求/回應 (Request/Response) | 簡單 (Easy) | 單一代理 (Single Agent) | 開發人員工具 / SDK 範例 (Developer Tools / SDK Sample) |
| [財務顧問 (Financial Advisor)](financial-advisor) | 透過提供金融和投資相關主題的教育內容來協助人類財務顧問。 | `Risk Analysis`, `Strategy Generation`, `Summarization`, `Report Generation` | 工作流程 (Workflow) | 簡單 (Easy) | 多代理 (Multi Agent) | 金融服務 (Financial Services) |
| [聯邦公開市場委員會研究代理 (FOMC Research Agent)](fomc-research) | 市場事件分析。 | `Summarization`, `Report Generation` | 工作流程 (Workflow) | 進階 (Advanced) | 多代理 (Multi Agent) | 金融服務 (Financial Services) |
| [Gemini 全端 (Gemini Fullstack)](gemini-fullstack) | 一個使用 Gemini 建構複雜全端研究代理的藍圖。 | `Multi-agent`, `Function calling`, `Web search`, `React`, `FastAPI`, `Human-in-the-Loop` | 工作流程 (Workflow) | 進階 (Advanced) | 多代理 (Multi Agent) | 通用 (Horizontal) |
| [無頭代理程式的驗證 (Headless Agent Auth)](headless_agent_auth) | 展示無頭代理程式如何利用 Auth0 的客戶端發起後通道驗證 (CIBA) 流程，透過推播通知請求使用者授權，以取得存取外部 API 的權杖。 | `Authentication`, `Auth0`, `CIBA`, `OAuth`, `Security`, `Headless`, `A2A` | 程式化 / API 呼叫 (Programmatic / API calls) | 專家級 (Expert) | 單一代理程式 (Single Agent) | 安全性 / 企業應用 (Security / Enterprise Applications) |
| [Hello World 代理程式 (Hello World Agent)](helloworld) | 一個只會回傳訊息事件的「Hello World」範例代理程式，作為新開發人員的起點。 | `Beginner`, `Starter`, `Example`, `A2A`, `Container` | 請求/回應 (Request/Response) | 非常簡單 (Trivial) | 單一代理程式 (Single Agent) | 開發人員工具 / SDK 範例 (Developer Tools / SDK Sample) |
| [圖片評分 (Image Scoring)](image-scoring) | 根據政策生成圖片並對生成的圖片進行評分以衡量政策遵循度的圖片評分代理。 | `Python`, `Agent Tool`, `Imagen`, `Loop Agent` | 對話式 (Conversational) | 簡單 (Easy) | 多代理 (Multi Agent) | 通用 (Horizontal) |
| [LangGraph 貨幣代理程式 (LangGraph Currency Agent)](langgraph) | 一個使用 LangGraph 和 ReAct 模式建構的貨幣轉換代理程式。它能進行多輪對話，在資訊不足時要求使用者提供更多資訊。 | `LangGraph`, `LangChain`, `A2A`, `Framework Integration`, `Stateful`, `Workflow`, `ReAct`, `Streaming` | 對話式 (Conversational) | 進階 (Advanced) | 單一代理程式 (Single Agent) | 金融服務 / 開發人員工具 (Financial Services / Developer Tools) |
| [LlamaIndex 檔案聊天工作流程 (LlamaIndex File Chat Workflow)](llama_index_file_chat) | 一個使用 LlamaIndex Workflows 建構的對話式代理程式，允許使用者上傳檔案，解析檔案內容，然後針對該內容進行多輪問答。 | `LlamaIndex`, `RAG`, `File Chat`, `Workflow`, `LlamaParse`, `Streaming`, `Citations`, `A2A` | 對話式 (Conversational) | 進階 (Advanced) | 單一代理程式 (Single Agent) | 知識管理 / 開發人員工具 (Knowledge Management / Developer Tools) |
| [大型語言模型稽核員 (LLM Auditor)](llm-auditor) | 聊天機器人回應驗證、內容稽核。 | `Gemini`, `Google Search`, `Multi-agent` | 工作流程 (Workflow) | 簡單 (Easy) | 多代理 (Multi Agent) | 通用 (Horizontal) |
| [機器學習工程代理 (Machine Learning Engineering Agent)](machine-learning-engineering) | 自動建立/訓練機器學習 (ML) 模型，以在各種機器學習任務上達到最先進的性能。 | `ML`, `AutoML`, `Kaggle` | 對話式 (Conversational) | 進階 (Advanced) | 多代理 (Multi Agent) | 通用 (Horizontal) |
| [行銷代理 (Marketing Agency)](marketing-agency) | 簡化新網站和產品的發布流程。識別最佳的 DNS 網域、生成整個網站、制定行銷策略並設計品牌資產。 | `Content Generation`, `Website Creation`, `Code Generation`, `Strategy` | 工作流程 (Workflow) | 簡單 (Easy) | 多代理 (Multi Agent) | 通用 (Horizontal) |
| [Marvin 聯絡人提取代理程式 (Marvin Contact Extractor Agent)](marvin) | 使用 Marvin 框架從非結構化文字中提取結構化的聯絡資訊（姓名、電子郵件、電話等）。它能管理多輪對話狀態以收集必要的資訊。 | `Marvin`, `Structured Data Extraction`, `Stateful`, `A2A`, `Framework Integration` | 對話式 (Conversational) | 中等 (Intermediate) | 單一代理程式 (Single Agent) | 開發人員工具 / 資料處理 (Developer Tools / Data Processing) |
| [MindsDB 企業資料代理程式 (MindsDB Enterprise Data Agent)](mindsdb) | 使用 MindsDB 連接、查詢和分析來自數百個聯合資料來源的資料。它將自然語言問題轉換為 SQL 查詢。 | `MindsDB`, `In-Database ML`, `NL2SQL`, `Data Federation`, `A2A`, `Framework Integration` | 對話式 (Conversational) | 進階 (Advanced) | 單一代理程式 (Single Agent) | 資料庫 / 資料科學 (Databases / Data Science) |
| [猜數字遊戲 (Number-Guessing Game)](number_guessing_game) | 一個由三個輕量級 A2A 代理程式組成的合作遊戲，旨在以最少的需求（無 LLM）展示 A2A 的核心概念。 | `Multi-agent`, `Simulation`, `Game`, `Collaboration`, `Beginner`, `No-LLM` | CLI / 自動化模擬 (CLI / Automated Simulation) | 簡單 (Easy) | 多代理程式 (Multi Agent) | 娛樂 / SDK 範例 (Entertainment / SDK Sample) |
| [個人開銷助理 (Personal Expense Assistant)](personal-expense-assistant-adk) | 擷取和儲存個人發票和收據，將其儲存在資料庫中，並提供搜尋功能。 | `Multimodal`, `Firestore`, `GCS`, `Gradio`, `FastAPI`, `Gemini`, `RAG` | 對話式 / 網頁介面 (Conversational / Web Interface) | 中等 (Intermediate) | 單一代理程式 (Single Agent) | 金融 / 個人生產力 (Finance / Personal Productivity) |
| [個人化購物 (Personalized Shopping)](personalized-shopping) | 產品推薦。 | `eCommerce`, `Personalized`, `Shopping Assistant`, `Single Agent`, `Recommendations` | 對話式 (Conversational) | 簡單 (Easy) | 單一代理程式 (Single Agent) | 電子商務 (E-commerce) |
| [A2A 無框架範例 (A2A No-Framework Example)](purchasing-concierge-intro-a2a) | 展示如何在沒有任何代理框架的情況下，設定和使用 a2a-python SDK 來建立一個簡單的伺服器和客戶端。 | `A2A`, `SDK`, `Client/Server`, `No-Framework`, `Beginner` | 程式化 / CLI (Programmatic / CLI) | 簡單 (Easy) | 單一代理 (Single Agent) | 開發人員工具 / SDK 範例 (Developer Tools / SDK Sample) |
| [QA 測試計畫代理程式 (QA Test Planner Agent)](qa-test-planner-agent) | 分析 Confluence 中的產品需求文件 (PRD)，並以與 Jira Xray 相容的格式產生全面的測試計畫。 | `Confluence`, `Jira Xray`, `Test Planning`, `QA`, `Gemini` | 網頁介面 (Web Interface) | 中等 (Intermediate) | 單一代理程式 (Single Agent) | 軟體開發 / 品質保證 (Software Development / Quality Assurance) |
| [Semantic Kernel 旅遊代理程式 (Semantic Kernel Travel Agent)](semantickernel) | 一個使用 Microsoft Semantic Kernel 建構的旅遊代理程式。它利用外掛程式架構呼叫其他代理程式（如貨幣兌換）來建立旅遊計畫。 | `Semantic Kernel`, `Microsoft`, `Plugins`, `Planner`, `A2A`, `Framework Integration` | 對話式 (Conversational) | 進階 (Advanced) | 多代理程式 (架構上) (Architecturally Multi Agent) | 旅遊 / 開發人員工具 (Travel / Developer Tools) |
| [軟體錯誤助理 (Software Bug Assistant)](software-bug-assistant) | 透過查詢內部票務系統和外部知識來源來尋找相似問題和診斷方法，以協助解決軟體錯誤。 | `RAG`, `MCP`, `Bug Tracking`, `Google Search`, `IT Support`, `Database`, `API` | 工作流程/對話式 (Workflow/Conversational) | 中等 (Intermediate) | 單一代理程式 (Single Agent) | IT 支援 (IT Support) |
| [SRE 助理代理 (SRE Assistant Agent)](sre-bot) | 協助網站可靠性工程師 (SRE) 處理營運任務和監控，特別是針對 Kubernetes 和 AWS 的互動。 | `SRE`, `Kubernetes`, `AWS`, `Monitoring`, `Operations`, `Slack`, `Multi-agent` | 對話式 / Slack (Conversational / Slack) | 進階 (Advanced) | 多代理 (Multi Agent) | IT 營運 / 雲端 (IT Operations / Cloud) |
| [旅遊管家 (Travel Concierge)](travel-concierge) | 旅遊管家、數位任務助理。 | `Python`, `Custom tool`, `Agent tool`, `Schema`, `Context`, `Dynamic Prompts` | 對話式 (Conversational) | 進階 (Advanced) | 多代理 (Multi Agent) | 旅遊 (Travel) |
| [旅遊規劃助理 (Travel Planner Assistant)](travel_planner_agent) | 一個符合 OpenAI 模型規格的旅遊助理，能夠提供旅遊規劃服務。此範例展示了如何設定和使用不同的 LLM（如 OpenAI、Qwen）作為代理程式的後端。 | `Travel`, `Planner`, `OpenAI`, `Qwen`, `A2A` | 對話式 (Conversational) | 簡單 (Easy) | 單一代理程式 (Single Agent) | 旅遊 (Travel) |
| [Vertex AI 檢索代理 (Vertex AI Retrieval Agent)](RAG) | 由 RAG 驅動的代理，回答與上傳至 Vertex AI RAG 引擎的文件相關的問題。 | `RAG Engine` | 工作流程 (Workflow) | 中等 (Intermediate) | 單一代理程式 (Single Agent) | 通用 (Horizontal) |



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
