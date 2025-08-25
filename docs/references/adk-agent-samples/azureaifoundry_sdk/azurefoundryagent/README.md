# AI Foundry A2A 示範

一個展示 Azure AI Foundry 與代理對代理 (A2A) 框架整合的示範專案。此專案實作了一個智慧日曆管理代理 (Agent)，具有以下功能：

## 功能

- 🤖 **AI Foundry 整合**：使用 Azure AI Foundry 建置智慧代理 (Agent)
- 📅 **日曆管理**：檢查排程可用性、取得即將到來的活動
- 🔄 **A2A 框架**：支援代理對代理 (agent-to-agent) 的通訊與協作
- 💬 **對話能力**：自然語言處理與多輪對話
- 🛠️ **工具整合**：模擬的日曆 API 工具整合

## 專案結構

```
├── foundry_agent.py           # AI Foundry 日曆代理 (Agent)
├── foundry_agent_executor.py  # A2A 框架執行器
├── __main__.py                # 主要應用程式
├── pyproject.toml             # 專案相依性
├── test_client.toml           # 測試
└── .env.template              # 環境變數範本
```

## 快速入門

### 1. 環境設定

```bash

# 複製環境變數範本
cp .env.template .env

# 編輯 .env 檔案並填入您的 Azure 設定
```

### 2. 安裝相依性

```bash
# 使用 uv (建議)
uv sync
```

### 3. 設定 Azure AI Foundry

在 `.env` 檔案中設定以下必要的環境變數：

```env
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=您的 Azure AI Foundry 專案端點
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME=您的 Azure AI Foundry 部署模型名稱
```

### 4. 執行示範

開啟終端機

```bash
# 啟動您的 Azure AI Foundry 代理 (Agent)
uv run .
```

在終端機中開啟另一個分頁

```bash
# 測試
uv run test_client.py
```


## 代理 (Agent) 功能

### 日曆管理技能

1. **檢查可用性** (`check_availability`)
   - 檢查特定時間段的排程安排
   - 範例："我明天下午 2 點到 3 點有空嗎？"

2. **取得即將到來的活動** (`get_upcoming_events`)
   - 取得未來的日曆活動
   - 範例："我今天有哪些會議？"

3. **日曆管理** (`calendar_management`)
   - 一般日曆管理和排程助理
   - 範例："幫我優化明天的排程"

### 對話範例

```
使用者：你好，可以幫我管理我的日曆嗎？
代理 (Agent)：當然！我是 AI Foundry 日曆代理 (Agent)，可以幫您檢查排程可用性、檢視即將到來的活動並優化您的排程。您需要什麼協助？

使用者：我明天下午 2 點到 3 點有空嗎？
代理 (Agent)：讓我查詢您明天下午 2 點到 3 點的空閒時間...
```

## 技術架構

### 核心元件

1. **FoundryCalendarAgent**: 
   - Azure AI Foundry 代理 (Agent) 的核心實作
   - 處理對話邏輯和工具呼叫

2. **FoundryAgentExecutor**:
   - A2A 框架執行器
   - 處理請求路由和狀態管理

3. **A2A 整合**:
   - 代理卡 (Agent card) 定義
   - 技能和功能宣告
   - 訊息轉換與處理

### 主要功能

- **非同步處理**：完全支援 Python 非同步程式設計
- **錯誤處理**：完整的例外處理和日誌記錄
- **狀態管理**：工作階段和執行緒狀態管理
- **可擴充性**：易於新增新工具和技能
