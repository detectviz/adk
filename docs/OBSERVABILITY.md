# 觀測性整合（Prometheus SLO）

## 目標
- 從 `adk.yaml` 與 `experts/*.yaml` 取得每個專家的 SLO 門檻，導出 Prometheus 規則。
- 監控指標：
  - `agent_request_duration_seconds_bucket{agent=...}`：代理回應延遲直方圖。
  - `agent_requests_total{agent, status}`：代理請求數與成功率。

## 產出
- `observability/slo_rules.yaml`：由 `scripts/export_slo_rules.py` 生成，含 Recording 與 Alerting Rules。

## 使用
```bash
make export-slo
# 或
python3 scripts/export_slo_rules.py
```

## 部署
- 將 `observability/slo_rules.yaml` 複製到 Prometheus 的 `rule_files` 所在目錄，或以 ConfigMap 掛載至 Prometheus/Mimir/Cortex。
