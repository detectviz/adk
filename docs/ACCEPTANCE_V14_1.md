
# v14.1 驗收說明

## 先決條件
- Prometheus：設定 `PROM_URL`（例如 http://localhost:9090）
- Kubernetes：設定 `KUBECONFIG` 或 `K8S_IN_CLUSTER=true`，並提供 `K8S_NS` 與 `K8S_DEPLOY`
- Grafana：設定 `GRAFANA_URL` 與 `GRAFANA_TOKEN`（service account token，需 dashboard:write 權限）

## 一鍵驗收
```bash
bash scripts/accept_v141.sh
```

## 測試內容
- Prometheus：`promql_query_tool("up","instant@<ts>")` 能成功呼叫 API 並返回結果格式
- K8s：`k8s_rollout_restart_tool` 能連上 K8s API 並嘗試 patch（即使 Deployment 不存在也應返回 JSON）
- Grafana：`grafana_create_dashboard_tool` 能呼叫 `/api/dashboards/db` 並回傳 UID 或錯誤訊息
