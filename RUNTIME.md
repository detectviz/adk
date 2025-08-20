
# Runtime 抽象層說明

- `contracts/messages/sre_messages.py`：以 Python dataclass 模擬 proto message 結構。
- `agents/sre_assistant/runtime/tool_runner.py`：統一工具呼叫入口，將 `ToolRequest` 分派至對應工具模組。
- `agents/sre_assistant/runtime/http_client.py`：集中化 HTTP 請求與重試控制。
- `agents/sre_assistant/runtime/secrets_manager.py`：以環境變數為來源的 Secrets 抽象。
- `agents/sre_assistant/runtime/kv_store.py`：記憶體 KV，後續可替換為 Redis。

## 後續
- 等 `protoc` 與 `buf` 生成實際的 client/server 代碼後，將 dataclass 替換為自動生成的 Python/Go 類型。
