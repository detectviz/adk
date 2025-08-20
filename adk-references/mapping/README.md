# 改造計畫

## 主要目標
  - 把 agent 的「工具呼叫層」（MCP call_tool / subprocess / requests）全部替換成 runtime 提供的統一介面，並把 agent 的輸入/輸出以 proto message（上方 protos/agent_messages_software_bug.proto）作為 contract。
  - 增加單元測試與合約測試，確保行為不變且可測試。

## 要替換的典型 API（舊 -> 新）
  - call_tool(name, input) 或 subprocess.run("kubectl ...")
    -> runtime.tool_runner.invoke(tool_name, ToolRequest)  
      - ToolRequest: 包含 tool-specific params (map)，runtime 負責權限、審計與回傳標準化 ToolResponse。
  - requests.get/post(...)
    -> runtime.http_client.request(method, url, headers, body, retry_policy)
      - 使用 runtime 的 retry/backoff 與集中化 metrics、tracing。
  - os.environ.get(...) (直接讀 Secret)
    -> runtime.secrets_manager.get_secret(name)
  - local file read/write (open/read/write) for state
    -> runtime.kv_store.get/set/delete(key)
  - ad-hoc logging / print
    -> runtime.logger.info/debug/error(...) 與 runtime.metrics.increment(...)

## Agent I/O
  - 進入：所有外部 event/observation 先轉成 Observation proto，放入 AgentRequest。
  - 出口：Agent 回應（建議動作、patches、traces）封裝成 AgentResponse 並上報 AgentService（或回傳給 runtime for dispatch）。

## 測試設計重點（Unit/Integration/Contract）
  - Unit: mock runtime 接口（tool_runner/http_client/kv_store/secrets_manager），驗證 agent 的邏輯決策（給定觀察結果 -> 會呼叫哪些 tools、會產生哪種 Action）。
  - Contract: 啟動 fake AgentService，驗證 proto 的序列化/欄位完整性（AgentRequest 包含 observations、metadata、request_time）。
  - Integration: 對工具層做淺偽實作（local fake tool runner 回應 canned data），驗證 agent 能在非 mock 情況下完成 end-to-end 流程。
  - E2E: 容器化環境注入 fake runtime，做整體流程 smoke test。

## 產生 proto 與 stub 的注意事項
  - 在改造 branch 中加入 protos/agent_messages_software_bug.proto，並在 CI 中新增 proto-build step，確保生成語言特定 stubs（python: grpcio-tools / protoc-grpc）。
  - 把消息版本號放在 package 或 metadata 中（例如 metadata["proto_version"]）以利未來向後相容。

## 監控與可觀察性
  - 改造後，所有 tool call 都應該產生一致的 metric 標籤 (agent_id, tool_name, outcome, latency_ms)。
  - runtime.logger 取代 print，並使用 structured logging (JSON) 與 trace id。

## 風險與驗證
  - 風險：如果 agent 直接依賴 tool 的 side-effect（例如直接在本地 ssh / apply patch），需額外設計轉換層，把 side-effect 轉為 runtime 的安全執行 API（可做權限審計）。
  - 驗證：使用 contract tests 驗證 AgentRequest/AgentResponse 的結構；使用 unit tests 驗證決策邏輯不變。

## 已完成內容說明（此回合交付）
- 完整 mapping 條目（YAML）[software-bug-assistant.yaml](software-bug-assistant.yaml)
- 專屬 proto 建議檔 [agent_messages_software_bug.proto](agent_messages_software_bug.proto)
- 測試清單與具體測試名稱/斷言重點，便於直接實作單元與合約測試[software-bug-assistant-tests.md](software-bug-assistant-tests.md)
