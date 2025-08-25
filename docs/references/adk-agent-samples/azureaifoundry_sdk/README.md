# 適用於 Azure AI Foundry Agent SDK 的 A2A 範例

此目錄包含三個全面的範例，示範如何將 **Azure AI Foundry Agent Service** 與 Google 的 **代理對代理 (A2A) 協定** 整合。這些範例展示了使用 Azure 的 AI 服務建置智慧代理 (Agent) 的不同方法，從簡單的日曆管理到精密的多代理 (multi-agent) 協調系統。

## 🔋 核心技術

- **Azure AI Foundry Agent Service**：使用 Azure AI 的智慧代理 (Agent) 功能
- **Google A2A SDK**：代理對代理 (Agent-to-agent) 通訊框架
- **模型上下文協定 (MCP)**：標準化的工具通訊
- **Azure Functions**：用於 MCP 服務的無伺服器託管

## 📁 範例總覽

### 1. Azure Foundry Agent (`./azurefoundryagent`)

一個**日曆管理代理 (Agent)**，示範了 Azure AI Foundry 與 A2A 協定的核心整合。

#### 主要功能：
- 🤖 **AI Foundry 整合**：使用 Azure AI Foundry 建置智慧代理 (Agent)
- 📅 **日曆管理**：檢查排程可用性、取得即將到來的活動
- 🔄 **A2A 框架**：支援代理對代理 (agent-to-agent) 的通訊與協作
- 💬 **對話能力**：自然語言處理與多輪對話
- 🛠️ **工具整合**：模擬的日曆 API 工具整合

#### 使用案例：
- "檢查我明天的日曆"
- "我這週有哪些會議？"
- "我星期五下午有空嗎？"

#### 技術：
- Azure AI Foundry Agent Service
- Azure AI Projects SDK
- 適用於 Python 的 A2A SDK
- Starlette 網頁框架

### 2. 貨幣代理 (Currency Agent) 示範 (`./currencyagentdemo`)

一個**全面的貨幣兌換系統**，結合了 Azure AI Foundry、MCP 服務和 A2A 協定，可進行即時貨幣換算。

#### 架構元件：
1. **🔌 MCP 伺服器**：提供貨幣兌換工具的 Azure Functions 服務
2. **💱 貨幣代理 (Currency Agent)**：與 A2A 協定整合的 Azure AI Foundry 代理 (Agent)

#### 主要功能：
- **🎯 Azure AI Agent Service**：利用 Azure AI Foundry 提供智慧回應
- **🔧 模型上下文協定 (MCP)**：標準化的工具通訊協定
- **🤝 Google A2A SDK**：代理對代理 (Agent-to-agent) 通訊框架
- **☁️ Azure Functions**：無伺服器 MCP 服務託管
- **💰 即時匯率**：使用 Frankfurter API 取得即時貨幣資料
- **📡 串流回應**：即時回應串流

#### 可用工具：
- `hello_mcp`：連線測試工具
- `get_exchange_rate`：具有 `currency_from` 和 `currency_to` 參數的貨幣換算

#### 使用案例：
- "將 100 美元換算成歐元"
- "目前英鎊兌日圓的匯率是多少？"
- "50 加幣等於多少澳幣？"

#### 技術：
- Azure AI Foundry Agent Service
- Azure Functions (用於 MCP 伺服器)
- 模型上下文協定 (MCP)
- 適用於 Python 的 A2A SDK
- Frankfurter API (用於匯率)

### 3. 多代理 (Multi-Agent) 系統 (`./multi_agent`)

一個**精密的多代理 (multi-agent) 架構**，示範了使用 Azure AI Foundry、A2A 協定和 Semantic Kernel 將任務智慧路由和委派給專門的遠端代理 (Agent)。

#### 架構元件：
1. **🎯 主機代理 (Host Agent)**：由 Azure AI Foundry 提供支援的中央路由系統
2. **🤖 遠端代理 (Remote Agents)**：專門的任務執行器（Playwright、工具代理 (Tool agents)）
3. **🔌 MCP 伺服器**：提供可擴充功能的 Azure Functions 服務
4. **🧠 Semantic Kernel**：用於智慧路由的進階代理 (Agent) 框架

#### 主要功能：
- **🎯 智慧路由**：由 Azure AI Foundry 提供支援的中央代理 (Agent)，用於任務委派
- **🤝 多代理 (Multi-Agent) 協調**：使用 A2A 協定的代理對代理 (agent-to-agent) 通訊
- **🧠 Semantic Kernel 整合**：進階的語意理解與路由
- **🌐 網頁介面**：具有即時串流功能的現代化 Gradio 聊天介面
- **🔧 Playwright 整合**：網頁自動化與瀏覽器任務執行
- **☁️ MCP Azure Functions**：與模型上下文協定 (Model Context Protocol) 的無伺服器工具整合
- **📡 多種通訊協定**：支援 STDIO、SSE 和 A2A 協定

#### 可用代理 (Agent) 類型：
- **Playwright Agent**：網頁自動化與瀏覽器任務
- **工具代理 (Tool Agent)**：通用工具執行


#### 技術：
- Azure AI Foundry Agent Service
- Semantic Kernel
- 適用於 Python 的 A2A SDK
- 模型上下文協定 (MCP)
- Azure Functions
- Playwright (用於網頁自動化)
- Gradio (用於網頁介面)

## 🚀 入門

### 先決條件
- Python 3.12+ (azurefoundryagent) 或 Python 3.13+ (currencyagentdemo)
- Azure AI Foundry 專案與部署
- Azure 訂閱（用於貨幣示範中的 Functions）
- UV 套件管理器（建議）

### 快速設定
1. 選擇一個範例目錄
2. 將 `.env.template` 複製為 `.env` 並設定 Azure
3. 安裝相依性：`uv sync`
4. 執行代理 (Agent)：`uv run .`

### 必要環境變數
```env
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=您的 Azure AI Foundry 專案端點
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME=您的 Azure AI Foundry 部署模型名稱
```

## 🎯 何時使用各個範例

### 當您想進行以下操作時，請使用 Azure Foundry Agent：
- 學習核心的 Azure AI Foundry + A2A 整合
- 建置簡單的基於工具的代理 (Agent)
- 了解基本的日曆/排程功能
- 以最少的設定開始

### 當您想進行以下操作時，請使用 Currency Agent Demo：
- 建置可與外部服務搭配使用的生產就緒代理 (Agent)
- 使用 Azure Functions 實作 MCP 協定
- 建立可與即時 API 互動的代理 (Agent)
- 了解複雜的多服務架構


