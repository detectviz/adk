# 範例：在沒有 LLM 框架的情況下使用 a2a-python SDK

本儲存庫示範如何在不依賴任何代理 (Agent) 框架的情況下，設定和使用 [a2a-python SDK](https://github.com/google/a2a-python) 來建立一個簡單的伺服器和客戶端。

## 總覽

- **A2A (Agent-to-Agent)：** 一種用於與 AI 代理通訊的協定和 SDK。
- **本範例：** 展示如何執行一個基本的 A2A 伺服器和客戶端、交換訊息以及檢視回應。

## 先決條件

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (用於快速的依賴管理和執行)
- 一個 Gemini 的 API 金鑰（設定為 `GEMINI_API_KEY`）

## 安裝

1. **複製儲存庫：**

   ```bash
   git clone <this-repo-url>
   cd <repo-directory>
   ```

2. **安裝依賴：**

   ```bash
   uv pip install -e .
   ```

3. **設定環境變數：**

   ```bash
   export GEMINI_API_KEY=your-gemini-api-key
   ```

   或建立一個包含以下內容的 `.env` 檔案：

   ```sh
   GEMINI_API_KEY=your-gemini-api-key
   ```

## 執行範例

### 1. 啟動伺服器

```bash
uv run --env-file .env python -m src.no_llm_framework.server.__main__
```

- 伺服器將在埠 9999 上啟動。

### 2. 執行客戶端

在新的終端機中：

```bash
uv run --env-file .env python -m src.no_llm_framework.client --question "What is A2A protocol?"
```

- 客戶端將連接到伺服器並發送請求。

### 3. 檢視回應

- 來自客戶端的回應將被儲存到 [`response.xml`](./response.xml)。

## 檔案結構

- `src/no_llm_framework/server/`：伺服器實作。
- `src/no_llm_framework/client/`：客戶端實作。
- `response.xml`：來自客戶端的回應範例。

## 疑難排解

- **缺少依賴：** 請確保您已安裝 uv。
- **API 金鑰錯誤：** 請確保 `GEMINI_API_KEY` 設定正確。
- **埠衝突：** 請確保埠 9999 未被佔用。

## 免責聲明

重要提示：所提供的範例程式碼僅供示範之用，並說明了代理對代理 (Agent-to-Agent, A2A) 協定的機制。在建置生產應用程式時，將任何在您直接控制之外運作的代理視為潛在不受信任的實體至關重要。

從外部代理接收的所有資料——包括但不限於其代理卡 (AgentCard)、訊息、產出成品和任務狀態——都應被視為不受信任的輸入。例如，惡意代理可能會在其欄位（例如，描述、名稱、技能描述）中提供包含精心設計的資料的代理卡。如果在使用這些資料時未經淨化就用於建構大型語言模型 (LLM) 的提示，可能會使您的應用程式遭受提示注入攻擊。在使用前未能正確驗證和淨化這些資料可能會給您的應用程式帶來安全漏洞。

開發人員有責任實施適當的安全措施，例如輸入驗證和安全處理憑證，以保護其系統和使用者。
