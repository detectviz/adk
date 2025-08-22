# 日誌與追蹤整合
- 追蹤：OTLP gRPC 以 Traces 匯出，於 `observability/otel.py` 初始化。
- 日誌：若環境具備 `opentelemetry-exporter-otlp` 且 Python 版本相容，會啟用 OTel Logs 匯出。
- 端點：由 `OTEL_EXPORTER_OTLP_ENDPOINT` 提供（建議 Cloud Build substitutions 注入）。
- Resource：與 Traces/Metrics 相同，包含 `service.name`、`cloud.provider=gcp`、`gcp.project_id`、`gcp.region`。
