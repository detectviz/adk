# Playwright 代理 (Agent)

一個專門的遠端代理 (Agent)，透過使用模型上下文協定 (MCP) 和 Semantic Kernel 的 Playwright 整合提供網頁自動化功能。此代理 (Agent) 可在多代理 (multi-agent) 系統中啟用瀏覽器自動化、網頁抓取和 UI 測試功能。

## 🚀 總覽

Playwright 代理 (Agent) 是一個利用以下技術的遠端代理 (Agent)：
- **Playwright MCP 外掛程式**：透過模型上下文協定 (Model Context Protocol) 進行瀏覽器自動化
- **Azure AI Agents**：核心智慧與決策制定
- **Semantic Kernel**：進階的語意理解與外掛程式管理
- **A2A 協定**：用於任務委派的代理對代理 (Agent-to-Agent) 通訊

## 🏗️ 架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   主機代理 (Host Agent)    │───▶│ Playwright 代理 (Agent)│───▶│  瀏覽器任務  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ • Azure AI      │    │ • 導覽    │
                       │ • Semantic      │    │ • 螢幕截圖   │
                       │   Kernel        │    │ • 表單填寫  │
                       │ • MCP 外掛程式    │    │ • 資料擷取  │
                       └─────────────────┘    └─────────────────┘
```

## 📂 檔案結構

```
playwright_agent/
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
- 使用憑證初始化 Azure AI Agent
- 設定 Playwright MCP STDIO 外掛程式
- 管理瀏覽器自動化任務
- 提供串流回應功能

**主要方法：**
- `initialize_playwright()`：使用 npx 指令設定 Playwright MCP 外掛程式
- `initialize_with_stdio()`：通用 MCP STDIO 外掛程式初始化
- `stream()`：以串流回應處理任務
- `cleanup()`：適當的資源清理

### 2. 代理 (Agent) 執行器 (`agent_executor.py`)

**`SemanticKernelMCPAgentExecutor`** - A2A 協定處理常式，功能如下：
- 實作 `AgentExecutor` 介面以進行 A2A 通訊
- 管理任務生命週期和狀態更新
- 處理事件佇列和通知
- 提供具有適當錯誤處理的串流執行

### 3. 伺服器應用程式 (`__main__.py`)

**主伺服器** - HTTP 伺服器，功能如下：
- 透過 A2A Starlette 應用程式公開代理 (Agent) 功能
- 定義具有 Playwright 工具技能的代理卡 (agent card)
- 設定串流功能
- 在可設定的主機和通訊埠上執行（預設：localhost:10001）

## 🎯 功能

### 瀏覽器自動化
- **導覽**：造訪 URL、處理重新導向、管理瀏覽器狀態
- **元素互動**：點擊、輸入、捲動、懸停操作
- **表單處理**：填寫表單、提交資料、處理檔案上傳
- **螢幕截圖擷取**：全頁或特定元素的螢幕截圖
- **內容擷取**：文字內容、HTML 結構、資料抓取

### 進階功能
- **多分頁管理**：處理多個瀏覽器分頁和視窗
- **等待條件**：等待元素、網路請求、頁面載入
- **行動裝置模擬**：測試響應式設計和行動裝置介面
- **效能監控**：擷取網路請求和效能指標

## 📋 先決條件

### 系統需求
- **Python 3.13+**
- **Node.js** (用於 Playwright MCP 伺服器)
- **Azure AI Foundry** 專案，並已部署模型

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


### 1. 安裝 Playwright MCP 伺服器

```bash
# 全域安裝 Playwright MCP 套件
npm install -g @playwright/mcp
```

### 2. 設定環境
透過複製範例範本來建立一個 `.env` 檔案：

```bash
cp .env.example .env
```

