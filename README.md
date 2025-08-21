
# SRE Assistant (ADK)

ADK 驅動的智慧 SRE 助理。以單一協調器代理，結合診斷/修復/覆盤專家與顯式工具，支援 HITL、RAG、真連接 Prometheus/K8s/Grafana，並內建 ADK Web Dev UI。

## 快速開始
```bash
make dev opt adk
make api         # 啟動 REST API → http://localhost:8000
make adk-web     # 啟動 ADK Dev UI → http://localhost:8080
```

### 重要環境變數
- `SESSION_BACKEND=memory|db`，`SESSION_DB_URI=sqlite:///./sessions.db`。
- `PROM_URL`、`GRAFANA_URL`、`GRAFANA_TOKEN`、`KUBECONFIG|K8S_IN_CLUSTER`、`K8S_NS`、`K8S_DEPLOY`。
- `RAG_CORPUS` 或 `PG_DSN`（pgvector）。

## 主要能力
- 對話：`/api/v1/chat`，或 SSE：`/api/v1/chat_sse`、`/api/v1/resume_sse`。
- HITL：工具內觸發 `request_credential`，前端回傳 `FunctionResponse` 後續跑。
- Dev UI：檢視 Sessions、Events、State、Tools 與即時互動。

## 測試與驗收
```bash
make test        # 單元與非 e2e
make e2e         # 真連接 E2E（需設定環境）
make accept      # 一鍵驗收（v14.1）
```

## 文件
- `SPEC.md`、`docs/ADK_WEB_UI.md`、`docs/ACCEPTANCE_V14_1.md`
- `AGENT.md`、`TESTING_GUIDE.md`、`DEVELOPMENT_SETUP.md`
