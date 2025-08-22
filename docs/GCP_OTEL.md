
# GCP 直投 OpenTelemetry（OTLP over gRPC）

## 設定
- 端點：`OTEL_EXPORTER_OTLP_ENDPOINT=https://otel.googleapis.com:4317`
- 認證：使用 Application Default Credentials (ADC)。需確保執行環境有 `GOOGLE_APPLICATION_CREDENTIALS` 或在 GCE/GKE 上啟用對應服務帳戶。
- 本專案已內建 Bearer Token 取得：參見 `sre_assistant/observability/otel.py`。

## 驗證
- 以 `curl` 擷取健康檢查：`/healthz`
- 觀測 traces/metrics 是否在 Cloud Trace / Cloud Monitoring 中出現（需等待數十秒）。


## 直接投遞到 Google Telemetry API 的注意事項
1. 將環境變數設為：
   - `OTEL_EXPORTER_OTLP_ENDPOINT=https://otel.googleapis.com:4317`
   - `GOOGLE_OTLP_AUTH=true`
2. 使用 ADC：
   - 本地：`export GOOGLE_APPLICATION_CREDENTIALS=/path/key.json`
   - GKE/GCE：掛載對應 SA 與範圍即可
3. 端對端驗證：
   - 啟動服務 → 產生請求 → 在 Cloud Trace/Monitoring 查看資料


### 以 Cloud Build 注入 OTLP 設定
`deployment/cloudbuild.yaml` 在部署 `gcloud run deploy` 時會帶：
```
--set-env-vars=OTEL_EXPORTER_OTLP_ENDPOINT=$_OTEL_ENDPOINT,GOOGLE_OTLP_AUTH=true
```
可透過 substitutions 覆寫：
```yaml
substitutions:
  _OTEL_ENDPOINT: https://otel.googleapis.com:4317
```


### Resource 設定
- Cloud Build 會注入：`SERVICE_NAME=$_SERVICE_NAME`（可在 substitutions 覆寫）。
- 若未注入則從 `adk.yaml.agent.name` 推導，最後 fallback `sre-assistant`。
