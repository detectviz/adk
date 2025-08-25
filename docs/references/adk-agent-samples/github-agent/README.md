# A2A GitHub 代理 (Agent)

一個使用 A2A (Agent2Agent) SDK 建置的智慧型 GitHub 代理 (Agent)，可以使用自然語言查詢 GitHub 儲存庫、最近的更新、提交和專案活動。

## 🔧 主要模組邏輯

### 1. 主伺服器 (`__main__.py`)
- 使用 Starlette 框架初始化 A2A 伺服器
- 建立一個 `AgentCard`，定義代理 (Agent) 的能力和技能
- 設定帶有 GitHub 工具的 OpenAI 代理 (Agent) 執行器
- 在指定的主機和連接埠上啟動 HTTP 伺服器

### 2. GitHub 工具集 (`github_toolset.py`)
提供三個主要的 GitHub API 函式：
- **`get_user_repositories()`**：擷取使用者的最近儲存庫
- **`get_recent_commits()`**：擷取特定儲存庫的最近提交
- **`search_repositories()`**：搜尋最近有活動的儲存庫

所有函式都包含錯誤處理並支援用於篩選的可選參數。

### 3. OpenAI 代理 (Agent) 執行器 (`openai_agent_executor.py`)
- 管理與 OpenRouter API 的對話流程
- 將 GitHub 工具轉換為 OpenAI 函式呼叫格式
- 處理工具執行和回應串流
- 實作帶有工具呼叫的迭代對話

### 4. 代理 (Agent) 定義 (`openai_agent.py`)
- 使用系統提示和可用工具建立代理 (Agent)
- 定義代理 (Agent) 對於 GitHub 相關查詢的行為
- 設定代理 (Agent) 以提供有用的儲存庫資訊

## 📋 先決條件

- **Python 3.10 或更高版本**
- **[UV](https://docs.astral.sh/uv/)** - Python 套件管理器
- **OpenRouter API 金鑰** - 用於 AI 功能
- **GitHub 個人存取權杖**（可選，但建議用於更高的速率限制）

## 🚀 設定與執行的逐步說明

### 步驟 1：複製並設定環境

```bash
# 複製儲存庫
git clone https://github.com/a2aproject/a2a-samples.git
cd a2a-samples/samples/python/agents/github-agent

# 建立虛擬環境
uv venv
source .venv/bin/activate  # 在 Windows 上：.venv\Scripts\activate
```

### 步驟 2：安裝相依套件

```bash
# 使用 UV 安裝相依套件
uv sync
```

### 步驟 3：設定環境變數

在專案根目錄中建立一個 `.env` 檔案：

```bash
# OpenRouter API 金鑰（必要）
echo "OPENROUTER_API_KEY=your_openrouter_api_key_here" > .env

# GitHub 個人存取權杖（可選但建議）
echo "GITHUB_TOKEN=your_github_personal_access_token_here" >> .env
```

**注意**：GitHub 權杖是可選的。若沒有它，代理 (Agent) 將使用未經身份驗證的存取，速率限制較低（每小時 60 次請求，而使用權杖則為 5000 次）。

### 步驟 4：執行 A2A 伺服器

```bash
# 啟用虛擬環境
source .venv/bin/activate

# 執行伺服器
uv run .
```

伺服器預設將在 `http://localhost:10007` 上啟動。


## 🧪 用戶端測試

### 選項 1：使用 A2A 電影代理 (Agent) 用戶端

您可以使用 A2A 電影代理 (Agent) 用戶端來測試 GitHub 代理 (Agent)：

```bash
# 如果您尚未複製 A2A 範例，請先複製
git clone https://github.com/a2aproject/a2a-samples.git

cd a2a-samples/samples/python/hosts/cli/
# 執行 cli
uv run . http://localhost:10007
```

這將啟動一個互動式 CLI，連接到您的 GitHub 代理 (Agent) 伺服器。

### 選項 2：使用直接 HTTP 請求

您也可以使用 curl 或任何 HTTP 用戶端進行測試：

```bash
# 範例：使用簡單的查詢進行測試
curl -X POST http://localhost:10007/ \
  -H "Content-Type: application/json" \
  -d '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [
        {
          "kind": "text",
          "text": "顯示儲存庫 'facebook/react' 的最近提交"
        }
      ],
      "messageId": "9229e770-767c-417b-a0b0-f0741243c589"
    },
    "metadata": {}
  }
}'
```

## 💡 範例查詢

GitHub 代理 (Agent) 可以處理如下查詢：

- **最近提交**：「顯示儲存庫 'facebook/react' 的最近提交」
- **儲存庫搜尋**：「搜尋最近有活動的熱門 Python 儲存庫」
- **專案活動**：「機器學習儲存庫的最新更新是什麼？」


## 📄 授權

本專案採用 MIT 授權 - 詳情請參閱 LICENSE 檔案。

## 🔗 相關專案

- [A2A SDK](https://github.com/a2aproject/a2a-python) - 底層的 A2A 協定實作


## 免責聲明
重要提示：所提供的範例程式碼僅供示範之用，旨在說明代理對代理 (Agent-to-Agent, A2A) 協定的運作機制。在建構生產應用程式時，至關重要的是將任何在您直接控制範圍之外運作的代理 (Agent) 視為潛在不受信任的實體。

從外部代理 (Agent) 收到的所有資料——包括但不限於其代理名片 (AgentCard)、訊息、產物 (Artifact) 和任務狀態——都應視為不受信任的輸入。例如，惡意代理 (Agent) 可能會提供一個在其欄位（例如，描述、名稱、技能描述）中包含精心設計的資料的代理名片 (AgentCard)。如果此資料未經淨化就用於為大型語言模型 (LLM) 建構提示，則可能使您的應用程式面臨提示注入攻擊的風險。未能在使用前正確驗證和淨化此資料可能會在您的應用程式中引入安全漏洞。

開發人員有責任實施適當的安全措施，例如輸入驗證和安全處理憑證，以保護其系統和使用者。