
# 開發環境設定

## 依賴
```bash
make dev opt adk
python -m pip install 'google-adk[web]'
```

## 本地啟動
```bash
make api      # REST API on :8000
make adk-web  # ADK Dev UI on :8080
```

## 重要變數
- `SESSION_BACKEND=memory|db`；`SESSION_DB_URI=sqlite:///./sessions.db`。
- `PROM_URL`、`GRAFANA_URL`、`GRAFANA_TOKEN`。
- `KUBECONFIG` 或 `K8S_IN_CLUSTER=true`；`K8S_NS`、`K8S_DEPLOY`。
- `RAG_CORPUS` 或 `PG_DSN`。

## 生產注意
- Dev UI 僅限內網；請勿公開暴露。
- Session 請使用 `DatabaseSessionService` 或 Agent Engine 的 Session。
- 高風險工具務必使用 HITL（request_credential）。
