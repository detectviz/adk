
# 設定與覆寫優先序（繁中）
系統採用「環境變數 > adk.yaml > 預設值」的策略；以 `sre_assistant/core/config.py` 讀取。

## 常用鍵值
- `agent.name`：服務名稱（亦可由 `SERVICE_NAME` 覆寫，用於 OTel `service.name`）
- `agent.tools_require_approval`：需 HITL 審批的工具清單（也可由 `ADK_AGENT_TOOLS_REQUIRE_APPROVAL` 以逗號覆寫）
- `policy.high_risk_namespaces`：高風險命名空間，預設 `['prod','production','prd']`，可用 `ADK_POLICY_HIGH_RISK_NAMESPACES` 覆寫
- `gcp.project_id` / `gcp.region`：若 Cloud Run/Build 未注入，系統將使用此欄位
- `OTEL_EXPORTER_OTLP_ENDPOINT`：OTLP gRPC 端點（Cloud Build 會以 substitutions 注入）
