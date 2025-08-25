# 使用經過驗證的工具的 ADK 代理 (Agent)

此範例展示如何建立一個 A2A 伺服器，該伺服器使用基於 ADK 的代理 (Agent)，並採用經過 Google 驗證的工具。

此代理 (Agent) 也提供一個如何使用伺服器驗證的範例。如果傳入的請求包含 JWT，代理 (Agent) 會將日曆 API 的授權與權杖的 `sub` 建立關聯，並在未來的請求中使用。如此一來，如果同一個使用者在多個會話中與代理 (Agent) 互動，授權就可以重複使用。

## 先決條件

- Python 3.10 或更高版本
- [UV](https://docs.astral.sh/uv/)
- 一個 Gemini API 金鑰
- 一個 [Google OAuth 用戶端](https://developers.google.com/identity/openid-connect/openid-connect#getcredentials)
  - 設定您的 OAuth 用戶端以處理 `localhost:10007/authenticate` 的重新導向 URL

## 執行範例

1. 使用您的 API 金鑰和 OAuth2.0 用戶端詳細資訊建立 .env 檔案

   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   echo "GOOGLE_CLIENT_ID=your_client_id_here" >> .env
   echo "GOOGLE_CLIENT_SECRET=your_client_secret_here" >> .env
   ```

2. 執行範例

   ```bash
   uv run .
   ```

## 測試代理 (Agent)

嘗試在 samples/python/hosts/cli 執行 CLI 主機以與代理 (Agent) 互動。

```bash
uv run . --agent="http://localhost:10007"
```

若要測試向代理 (Agent) 提供驗證，您可以使用 `gcloud` 向代理 (Agent) 提供一個 ID 權杖。

```bash
uv run . --agent="http://localhost:10007" --header="Authorization=Bearer $(gcloud auth print-identity-token)"
```
