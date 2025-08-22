
## v13.2 追加事項（完全對齊 ADK）

- **Runner/SessionService**：以 `InMemoryRunner` + `session_service` 建立/管理會話，透過 `run_async` 串流 `Event`（官方 Runtime 模式）。
- **LongRunningFunctionTool**：`K8sRolloutRestartLongRunningTool` 以 `start_func/poll_func` 實作。示範以 `before_tool_callback` 作為政策閘，並於註解中說明如何改為 `tool_context.request_credential(...)` 啟用正式 HITL。

### gRPC / proto 檢核結論
- **ADK Python** 公開 API 無 gRPC 服務定義；官方互動介面為 `Runner.run_async` 與（可選）ADK FastAPI 的 `/run`、`/run_sse`。gRPC/ReasoningEngine 端點屬 **Vertex AI Agent Engine** 範疇，非 ADK 本體，禁止在本專案內仿造自訂 proto。

### 驗收要點（對照官方文件）
- 子代理僅掛載一次（以 `AgentTool` 掛載至 `main_llm`），`LoopAgent.agents=[main_llm]`。
- 工具皆以 `FunctionTool/LongRunningFunctionTool` 顯式定義，無隱式 decorator。
- Callback：`before_tool_callback` 進行政策檢查；可擴展認證/HITL；工具結果可選擇跳過摘要。
- Session：使用 `session_service.create_session` 與 `session.state` 維持上下文。
