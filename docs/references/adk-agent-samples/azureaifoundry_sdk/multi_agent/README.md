# 使用 Azure AI Foundry 的多代理 (Multi-Agent) 系統

一個精密的多代理 (multi-agent) 系統，利用 Azure AI Foundry、A2A (代理對代理)、Semantic Kernel 和模型上下文協定 (MCP) 進行智慧任務路由並委派給專門的遠端代理 (Agent)。

## 🚀 總覽

此專案實作了一個 A2A 多代理 (multi-agent) 架構，其中一個由 Azure AI Foundry 提供支援的中央路由代理 (Agent) 會智慧地將任務委派給專門的遠端代理 (Agent)。該系統支援各種代理 (Agent) 類型，包括 Playwright 自動化代理 (STDIO) 和已啟用 MCP 的 Azure Functions (SSE)。

## 🏗️ 架構

```mermaid
graph TD
    A[使用者請求] --> B[主機代理 (Host Agent)<br/>Azure AI Foundry]
    B --> C{路由邏輯}
    C --> D[Playwright 代理 (Agent)<br/>STDIO]
    C --> E[MCP Azure Functions<br/>SSE]
    
    B -.-> F[Semantic Kernel]
    B -.-> G[A2A 協定]
    
    D --> H[網頁自動化]
    
    style B fill:#e1f5fe
    style C fill:#f3e5f5
    style D fill:#e8f5e8
    style E fill:#e8f5e8
    style F fill:#e8f5e8
```

**主要元件：**
- **主機代理 (Host Agent)**：由 Azure AI Foundry 提供支援的中央路由系統
- **A2A 協定**：代理對代理 (Agent-to-Agent) 的通訊標準
- **Semantic Kernel**：進階代理 (Agent) 框架
- **遠端代理 (Remote Agents)**：專門的任務執行器（Playwright、MCP）
- **MCP 整合**：用於可擴充功能的模型上下文協定 (Model Context Protocol)（Azure Function）

## 📂 專案結構

```
multi_agent/
├── host_agent/                 # 中央路由代理 (Agent)
│   ├── __main__.py            # Gradio 網頁介面
│   ├── routing_agent.py       # 使用 Azure AI 的核心路由邏輯
│   ├── remote_agent_connection.py  # A2A 協定處理
│   ├── diagnose_azure.py      # Azure 診斷
│   └── validate_setup.py      # 設定驗證
├── remote_agents/             # 專門的代理 (Agent) 實作
│   ├── playwright_agent/      # 網頁自動化代理 (Agent)
│   └── tool_agent/           # 通用工具代理 (Agent)
└── mcp_sse_server/           # MCP 伺服器實作
    └── MCPAzureFunc/         # Azure Functions MCP 伺服器
```

## 🚀 功能

### 主機代理 (Host Agent) (路由系統)
- **Azure AI Agents 整合**：由 Azure AI Foundry 提供支援，用於智慧決策
- **A2A 協定支援**：使用標準化協定進行代理對代理 (Agent-to-Agent) 通訊
- **Semantic Kernel 整合**：進階的語意理解與路由
- **網頁介面**：具有即時串流功能的現代化 Gradio 聊天介面
- **多代理 (Multi-Agent) 協調**：智慧任務委派與回應彙總
- **資源管理**：自動清理與全面的錯誤處理

### 遠端代理 (Remote Agents)
- **Playwright 代理 (Agent)**：網頁自動化與瀏覽器任務執行
- **MCP 整合**：模型上下文協定 (Model Context Protocol) 支援可擴充功能

### MCP 伺服器元件
- **Azure Functions 整合**：無伺服器 MCP 伺服器部署
- **Git 儲存庫管理**：自動化儲存庫複製與管理
- **可擴充架構**：易於新增新的 MCP 工具和功能

## 📋 先決條件

### 必要服務
1. **Azure AI Foundry 專案**，並已部署語言模型
2. 已設定的 **Azure 驗證**（CLI、服務主體或受控識別）
3. 所有元件皆需 **Python 3.13+**

### 選用元件
- 用於 MCP 伺服器部署的 **Azure Functions**
- 用於容器化部署的 **Docker**

## ⚙️ 安裝與設定

### 1. 複製儲存庫
```bash
git clone <repository-url>
cd multi_agent
```

### 2. MCP 伺服器設定

```bash
cd mcp_sse_server/MCPAzureFunc

docker run -p 10000:10000 -p 10001:10001 -p 10002:10002 \          
    mcr.microsoft.com/azure-storage/azurite

# 在終端機中開啟另一個分頁
func start 
```


### 3. 遠端代理 (Remote Agents) 設定
```bash
# Playwright 代理 (Agent)
cd remote_agents/playwright_agent
uv sync
uv run .

# 工具代理 (Tool Agent)
cd ../tool_agent
uv sync
uv run .
```

### 4. 主機代理 (Host Agent) 設定
```bash
cd host_agent
uv sync
uv run .
```

## ⚙️ 設定

### 環境變數
透過複製範例範本來建立一個 `.env` 檔案：

```bash
cd host_agent
cp .env.example .env
```

## 🚀 使用方式

### 啟動系統

1. **存取網頁介面**：
   在您的瀏覽器中開啟 `http://0.0.0.0:8083/`

### 互動範例

- **網頁自動化**："導覽至 example.com 並擷取螢幕截圖"
- **多代理 (Multi-Agent) 任務**："研究競爭對手並建立摘要報告"

## 🔄 版本紀錄

- **v0.1.0**：具有基本多代理 (multi-agent) 路由的初始版本
- **目前**：增強的 Azure AI 整合與 MCP 支援