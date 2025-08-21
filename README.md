
# SRE Assistant（ADK 對齊，顯式工具註冊）

- 全檔繁體中文註解
- 工具採「YAML 規格 + 註冊表」；不使用裝飾器
- 核心能力：Policy Gate、HITL、快取、RAG 版本化、觀測性、持久化、規劃器
- API Key 認證 + RBAC + 速率限制

## 快速開始
```bash
make dev
export X_API_KEY=devkey
make api
# 測試對話
curl -s -H "X-API-Key: $X_API_KEY" -X POST localhost:8000/api/v1/chat -H 'Content-Type: application/json' -d '{"message":"diagnose orders latency"}' | jq
```

## 端點
- `POST /api/v1/chat`：對話入口（需 `X-API-Key`）
- `GET /api/v1/approvals/{id}`、`POST .../decision`、`POST .../execute`：HITL 流程
- `POST /api/v1/rag/entries`、`POST /api/v1/rag/entries/{id}/status`、`POST /api/v1/rag/retrieve`：RAG 管理與檢索
- `GET /metrics`：Prometheus 指標

## 測試
```bash
make test
```

## 組態
- `SRE_API_HOST`、`SRE_API_PORT`
- `SQLITE_PATH`
- `MODEL_NAME`、`RAG_CORPUS`（預留）
