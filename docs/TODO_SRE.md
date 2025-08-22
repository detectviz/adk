
# 未完成 / 需補強清單（v15.6）

## A. Observability
- [ ] OTLP/gRPC 到 Google Telemetry API 的實測適配與 credentials 自動載入。
- [ ] Cloud Logging / Monitoring Exporter 的生產級設定與重試策略。
- [ ] 指標名稱與 label 規範自動驗證（CI 檢查）。
- [ ] Alloy/OTel Collector 部署樣板與 Grafana 探索面板（drill-down 到 Metrics/Traces/Logs/Profile）。

## B. ADK 對齊
- [ ] A2A gRPC 通訊樣板與互通測試（與官方 samples 對接）。
- [ ] HITL 事件型流程的端到端 UI 驗證（Dev UI 介面聯動 tools_require_approval）。
- [ ] LongRunningFunctionTool 的 resume/cancel API 實作對齊範例。

## C. RAG 與知識治理
- [ ] pgvector 向量維度與嵌入模型切換（正式嵌入 API）之 E2E 測試。
- [ ] 引用追蹤（source_id/version）與退版機制。

## D. 安全與權限
- [ ] RBAC 細化（工具級 scope），並與 K8s RBAC 對齊。
- [ ] HITL 證跡保存規範（審計：誰核可、為何核可、在何時）。

## E. 發布與 DX
- [ ] `adk.yaml` schema 校驗器（pydantic/yamale），CI gate。
- [ ] Dev UI 工具清單與 allowlist/require_approval 同步的視覺指示。
- [ ] 本地 `docker-compose` 一鍵起（包含 Postgres/Prometheus/Grafana/Collector）。


## 本輪更新（v15.6.2）
- OTLP/gRPC 連 Google Telemetry：自動 Bearer（ADC）
- Cloud Monitoring Exporter（選用）
- Metrics 規範驗證腳本 scripts/validate_metrics_spec.py
- Collector 與 docker-compose 範本
- A2A gRPC proto/server/client 與煙霧測試
- RAG pgvector SQL 與工具補丁
- Dev UI 工具清單同步端點
- HITL 審批端點（session 記錄版）
