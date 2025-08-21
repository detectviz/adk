
# 觀測堆疊（Alloy + Tempo + Loki + Mimir + Pyroscope）

## 啟動
```bash
make obs-up
# Alloy: 4317/4318，UI: 12345
# Tempo: 3200，Loki: 3100，Mimir: 9009，Pyroscope: 4040，Grafana: 3000
```

## 服務端環境變數
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_TRACES_EXPORTER=otlp
export OTEL_METRICS_EXPORTER=otlp
export OTEL_LOGS_EXPORTER=otlp
export OTEL_RESOURCE_ATTRIBUTES="service.name=sre-assistant,service.version=14.3,env=dev"
export PYROSCOPE_SERVER=http://localhost:4040
export PYROSCOPE_APP_NAME=sre-assistant
```

## Grafana Drilldown
- Metrics → **Exemplars** 開啟後，點擊圖上 exemplar 跳至 Tempo。
- Logs → 在 Loki Data Source 新增 derived field `traceID`（若應用將 trace_id 放入 log），即可自動鏈到 Tempo。
- Profiles → 在 Trace 視圖中連結到 Pyroscope flamegraph（需相同 service.name 與時間範圍）。
