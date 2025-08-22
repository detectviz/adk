
# GCP Observability 導入指南（Traces/Logs/Metrics）

## 依賴
```bash
pip install opentelemetry-exporter-otlp-proto-grpc opentelemetry-exporter-gcp-logging opentelemetry-exporter-gcp-monitoring opentelemetry-instrumentation-google-genai opentelemetry-instrumentation-vertexai google-auth
```

## 環境變數
```
GCP_PROJECT_ID=<your-project>
OTEL_SERVICE_NAME=sre-assistant
OTEL_SERVICE_VERSION=14.4
ENV=dev
OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json  # 或使用 GCE/GKE 預設憑證
```

## 啟用
在主進程啟動時呼叫：
```python
from sre_assistant.core.telemetry_gcp import init_gcp_observability
init_gcp_observability()
```

## 驗收
- Cloud Trace：可見到代理/工具呼叫 Span
- Cloud Logging：應用日誌出現在專案下
- Cloud Monitoring：自定義指標可查詢
