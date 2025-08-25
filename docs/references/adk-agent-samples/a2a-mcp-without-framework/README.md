# 範例：在沒有 LLM 框架的情況下使用 a2a-python SDK

本程式庫示範如何在不依賴任何代理 (Agent) 框架的情況下，設定並使用 [a2a-python SDK](https://github.com/google/a2a-python) 來建立一個簡單的伺服器和客戶端。

## 總覽

- **A2A (Agent-to-Agent):** 一種用於與 AI 代理 (AI Agents) 通訊的協定和 SDK。
- **此範例:** 展示如何執行一個基本的 A2A 伺服器和客戶端，交換訊息並查看回應。

## 先決條件

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (用於快速的依賴管理和執行)
- Gemini 的 API 金鑰 (設定為 `GEMINI_API_KEY`)

## 安裝

1. **複製此程式庫:**

   ```bash
   git clone <this-repo-url>
   cd <repo-directory>
   ```

2. **安裝依賴套件:**

   ```bash
   uv pip install -e .
   ```

3. **設定環境變數:**

   ```bash
   export GEMINI_API_KEY=your-gemini-api-key
   ```

   或建立一個 `.env` 檔案，內容如下：

   ```sh
   GEMINI_API_KEY=your-gemini-api-key
   ```

## 執行範例

### 1. 啟動伺服器

```bash
uv run --env-file .env python -m src.no_llm_framework.server.__main__
```

- 伺服器將啟動於通訊埠 `9999`。

### 2. 執行客戶端

在新的終端機中：

```bash
uv run --env-file .env python -m src.no_llm_framework.client --question "What is A2A protocol?"
```

- 客戶端將連接到伺服器並發送請求。

### 3. 查看回應

- 來自客戶端的回應將被儲存到 [`response.xml`](./response.xml)。

## 檔案結構

- `src/no_llm_framework/server/`: 伺服器實作。
- `src/no_llm_framework/client/`: 客戶端實作。
- `response.xml`: 客戶端的回應範例。

## 疑難排解

- **缺少依賴套件:** 請確保您已安裝 `uv`。
- **API 金鑰錯誤:** 請確保 `GEMINI_API_KEY` 設定正確。
- **通訊埠衝突:** 請確保通訊埠 9999 未被佔用。

## 免責聲明

重要提示：此處提供的範例程式碼僅供示範之用，旨在說明代理對代理 (A2A) 協定的運作機制。在建構實際應用程式時，至關重要的是將任何在您直接控制範圍之外運作的代理 (Agent) 視為潛在不受信任的實體。

所有從外部代理 (Agent) 接收的資料——包括但不限於其 AgentCard、訊息、產物和任務狀態——都應作為不受信任的輸入來處理。舉例來說，一個惡意代理 (Agent) 可能在其 AgentCard 的欄位（例如：description、name、skills.description）中提供經過精心設計的資料。如果這些資料在未經清理的情況下被用來建構大型語言模型 (LLM) 的提示，可能會使您的應用程式遭受提示注入攻擊 (prompt injection attacks)。若未能在使用前對這些資料進行適當的驗證和清理，可能會為您的應用程式帶來安全漏洞。

開發人員有責任實施適當的安全措施，例如輸入驗證和安全處理憑證，以保護他們的系統和使用者。
