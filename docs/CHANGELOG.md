## v15.7.6 重要變更
- 移除非 ADK 協調器與自訂 ToolRegistry/agents 目錄，統一由 `adk_app/runtime.py` 組裝。
- 移除 `core/otel_grpc.py` 與 `core/policy.py`，採用官方推薦：追蹤由 OTel 自動化，策略檢查在工具內執行。
- `k8s_long_running`：長任務狀態僅存於 `session.state`；HITL 觸發嚴格依 `adk.yaml` 與高風險命名空間。
- `runtime.py` 引入 `BuiltInPlanner` 的占位導入，保持對齊官方設計。


## v15.7.7 打包版
- 封裝自 `v15.7.6-clean` 並套用 v15.7.7 修正：移除 `sub_agents/**`，改讀 `experts/*.yaml`；HITL 判斷內聚於 `k8s_long_running.py`。


## v15.7.8 變更
- 全域移除樣板註解字樣。
- K8s 高風險命名空間改由 `adk.yaml.policy.high_risk_namespaces` 配置，預設 `['prod','production','prd']`。
- 新增 `docs/HARDCODE_AUDIT.md`，列出疑似硬編碼以供人工審核。
- 再次清理可能造成雙執行模式的殘留目錄（`sub_agents/` 等）。


