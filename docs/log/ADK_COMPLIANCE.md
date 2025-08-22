

# ADK 對齊摘要（v15.7.13）
- A2A：僅使用官方包裝；未再維護自訂 proto。
- HITL：完全透過工具呼叫 request_credential 觸發；SSE 事件名 `adk_request_credential`。
- Runtime：由 experts/*.yaml 載入 tools_allowlist、model 與 slo；保留 BuiltInPlanner 占位。
- Observability：OTLP gRPC 匯出 Traces + Metrics；Resource 含 `service.name`、`cloud.provider=gcp`、`gcp.project_id`、`gcp.region`。
- Session：支援 InMemory 與 Database 兩種服務；以 `SESSION_BACKEND` 與 `DATABASE_URL` 決定。
