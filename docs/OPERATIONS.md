
# 營運手冊（Operations）

## HITL 審批流
1. 透過 `/api/v1/chat` 觸發變更類步驟（例如 K8s restart），API 會返回 `approval_id`。
2. 使用者在後台或 CLI 對該 `approval_id` 執行核准或拒絕：
   - `POST /api/v1/approvals/{aid}/decision`
3. 核准後執行該步驟：
   - `POST /api/v1/approvals/{aid}/execute`

## 回放與重跑
- `GET /api/v1/decisions` 查詢歷史決策。
- `POST /api/v1/replay` 重跑某次決策的步驟並產生新決策。

## 監控與 SLO
- Prometheus 指標位於 `/metrics`。
- 端到端延遲由 `SLOGuardian` 評估，超標時於回應 `slo_advice` 中提供降級建議。

## 常見問題
- DB 準備：`/health/ready` 若回 503，請確認 `/mnt/data` 可寫入或調整 `SQLITE_PATH`。
- 驗證失敗：請建立 API Key 或使用開發金鑰 `devkey`。
