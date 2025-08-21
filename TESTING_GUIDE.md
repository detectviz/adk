
# 測試指南

## 層級
1. 單元測試：工具 I/O Schema、錯誤碼、超時/重試。
2. 整合測試：子專家與工具交互、長任務 start/poll 流程。
3. 端到端（E2E）：REST/SSE→Runner→Agents→Tools→外部系統。

## 指令
```bash
make test    # 單元/整合（非 e2e）
make e2e     # 真連接 E2E（需環境變數）
make accept  # v14.1 一鍵驗收
```

## 環境變數
- Prometheus：`PROM_URL`
- Kubernetes：`KUBECONFIG` 或 `K8S_IN_CLUSTER=true`；`K8S_NS`、`K8S_DEPLOY`
- Grafana：`GRAFANA_URL`、`GRAFANA_TOKEN`

## 觀測
- OpenTelemetry：啟動時初始化；匯出至 OTLP（可自設端點）。
- 指標：`agent_requests_total`、`agent_request_duration_seconds_bucket`、`tool_executions_total`。
