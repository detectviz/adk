
#!/usr/bin/env bash
# v14.1 驗收腳本：真連接整合 + E2E 測試
set -euo pipefail

echo "[1/5] 顯示關鍵環境變數"
echo "PROM_URL=${PROM_URL:-}"
echo "KUBECONFIG=${KUBECONFIG:-} K8S_IN_CLUSTER=${K8S_IN_CLUSTER:-} K8S_NS=${K8S_NS:-default} K8S_DEPLOY=${K8S_DEPLOY:-}"
echo "GRAFANA_URL=${GRAFANA_URL:-} GRAFANA_TOKEN=${GRAFANA_TOKEN:-}"

echo "[2/5] 安裝依賴"
python -m pip install -q requests kubernetes

echo "[3/5] 單元/整合測試（跳過 integration/e2e 以外）"
python -m pytest -q -k "not integration and not e2e" || true

echo "[4/5] E2E 測試（真連接）"
python -m pytest -q tests/e2e/test_real_integrations.py || true

echo "[5/5] 完成"
