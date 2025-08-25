# 使用 A2A 客戶端的 ADK 代理 (Agent)

此範例展示如何建立一個 A2A 伺服器，該伺服器使用基於 ADK 的代理 (Agent)，並透過 A2A 與另一個代理 (Agent) 進行通訊。

這個代理 (Agent) 協助規劃生日派對。它可以存取一個日曆代理 (Calendar Agent)，並將日曆相關的任務委派給它。此代理 (Agent) 是透過 A2A 存取的。

## 先決條件

- Python 3.10 或更高版本
- [UV](https://docs.astral.sh/uv/)
- 一個 Gemini API 金鑰

## 執行範例

1. 使用您的 API 金鑰建立 `.env` 檔案

   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

2. 執行日曆代理 (Calendar Agent)。請參閱 examples/google_adk/calendar_agent。

3. 執行範例

   ```sh
   uv run .
   ```
