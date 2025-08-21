
# SRE Assistant（ADK 顯式工具範式）

## 快速開始
```bash
make dev
make api
# 另開終端測試
curl -H 'X-API-Key: devkey' -H 'Content-Type: application/json' \
  -d '{"message":"diagnose cpu","session_id":"demo"}' \
  localhost:8000/api/v1/chat | jq .
```

## 主要端點
- `POST /api/v1/chat` 對話入口（含 SLO 建議）
- `GET  /api/v1/tools` 工具清單（require_approval、risk_level）
- `GET  /api/v1/tools/{name}/spec` 工具規格 YAML 展示（JSON）
- `GET  /api/v1/decisions` 決策回放
- `POST /api/v1/replay` 重跑既有決策
- `POST /api/v1/rag/entries` / `.../status` / `.../retrieve`
- `GET  /metrics` Prometheus 指標
- 健康檢查：`/health/live`、`/health/ready`

## 工具註冊模式
以「工具描述檔（YAML）+ 明確函式」註冊到 `ToolRegistry`：
```python
from adk_runtime.main import build_registry
registry = build_registry()
# registry.list_tools() -> { name: {spec, func}, ... }
```

## 策略與安全
- `SRESecurityPolicy` 合併 YAML 與動態規則（namespace 受保護、regex/enum、維護時窗）。
- OpenAPI 已宣告 `ApiKeyHeader`，所有路徑需 `X-API-Key`。

## 測試
```bash
make test
```
