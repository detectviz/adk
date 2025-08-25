# 工具代理 (Tool Agent)

一個專門的遠端代理 (Agent)，透過模型上下文協定 (MCP) 工具提供全面的開發和任務協助。此代理 (Agent) 可在多代理 (multi-agent) 系統中啟用 git 操作、IDE 整合和各種開發公用程式。

## 🚀 總覽

工具代理 (Tool Agent) 是一個多功能的遠端代理 (Agent)，它利用：
- **MCP SSE 外掛程式**：透過模型上下文協定 (Model Context Protocol) 伺服器傳送事件 (Server-Sent Events) 的開發工具
- **Azure AI Agents**：核心智慧與決策能力
- **Semantic Kernel**：進階的語意理解與外掛程式管理
- **A2A 協定**：用於無縫任務委派的代理對代理 (Agent-to-Agent) 通訊

## 🏗️ 架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   主機代理 (Host Agent)    │───▶│   工具代理 (Tool Agent)    │───▶│  開發工具 MCP  │
│                 │    │                 │    │     伺服器      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ • Azure AI      │    │ • Git Clone     │
                       │ • Semantic      │    │ • VSCode 開啟   │
                       │   Kernel        │    │ • 檔案操作      │
                       │ • MCP SSE       │    │ • 開發   │
                       └─────────────────┘    └─────────────────┘
```

## 📂 檔案結構

```
tool_agent/
├── __main__.py              # 主要進入點與伺服器啟動
├── agent.py                 # 具有 MCP 整合的核心代理 (Agent) 實作
├── agent_executor.py        # A2A 協定執行處理常式
├── pyproject.toml          # 專案相依性與設定
├── uv.lock                 # 相依性鎖定檔案
└── README.md               # 本文件
```

## 🔧 元件

### 1. 核心代理 (Core Agent) (`agent.py`)

**`SemanticKernelMCPAgent`** - 主要代理 (Agent) 類別，功能如下：
- 使用 Azure 憑證初始化 Azure AI Agent
- 為開發工具設定 MCP SSE 外掛程式
- 管理開發任務執行和工具協調
- 提供串流和同步回應功能

**主要方法：**
- `initialize(mcp_url)`：使用可設定的伺服器 URL 設定 MCP SSE 外掛程式
- `invoke(user_input, session_id)`：具有完整回應的同步任務處理
- `stream(user_input, session_id)`：非同步串流任務執行
- `cleanup()`：適當的資源清理和連線管理

### 2. 代理 (Agent) 執行器 (`agent_executor.py`)

**`SemanticKernelMCPAgentExecutor`** - A2A 協定處理常式，功能如下：
- 實作 `AgentExecutor` 介面以進行標準化的代理 (Agent) 通訊
- 透過全面的狀態追蹤管理任務生命週期
- 處理事件佇列和即時通知
- 提供具有強大錯誤處理和復原功能的串流執行

### 3. 伺服器應用程式 (`__main__.py`)

**主伺服器** - HTTP 伺服器，功能如下：
- 透過 A2A Starlette 應用程式公開代理 (Agent) 功能
- 定義具有開發工具技能的綜合代理卡 (agent card)
- 為即時回應設定串流功能
- 在可設定的主機和通訊埠上執行（預設：localhost:10002）

## 🎯 功能

### 開發工具
- **Git 操作**：儲存庫複製、分支管理、提交操作
- **IDE 整合**：VSCode 和 VSCode Insiders 專案開啟
- **檔案管理**：檔案系統操作、目錄導覽
- **專案設定**：開發環境初始化

### 進階功能
- **儲存庫管理**：複製儲存庫並在偏好的 IDE 中開啟
- **開發工作流程**：簡化的開發任務自動化
- **工具鏈整合**：與開發工具的無縫整合
- **跨平台支援**：可在不同作業系統上運作

## 📋 先決條件

### 系統需求
- **Python 3.13+**
- **MCP 伺服器**：執行開發工具 MCP 伺服器
- **Azure AI Foundry** 專案，並已部署模型
- **Git**：用於儲存庫操作（可選）
- **VSCode/VSCode Insiders**：用於 IDE 整合（可選）

### 相依性
透過 `pyproject.toml` 管理的核心相依性：
```toml
dependencies = [
    "a2a-sdk>=0.2.7",
    "mcp>=1.9.4",
    "azure-ai-agents>=1.1.0b1", 
    "semantic-kernel>=1.33.0",
]
```

## ⚙️ 安裝與設定

### 1. 安裝相依性
```bash
cd remote_agents/tool_agent

# 使用 uv (建議)
uv sync
```


### 3. 設定環境
透過複製範例範本來建立一個 `.env` 檔案：

```bash
cp .env.example .env
```


### 任務範例

此代理 (Agent) 可以處理各種開發和工具相關的任務：

**Git 操作：**
```
"複製 https://github.com/kinfey/mcpdemo1"
"複製儲存庫並在 VSCode 中開啟"
"複製 https://github.com/user/repo 並使用 VSCode Insiders 開啟"
```

