
# 設定檔管理

## 建議做法（分離）
- `adk.yaml`：定義代理行為（模型、工具權限、安全策略）。
- `adk_config.yaml`：開發輔助（Web Dev UI、Runner 行為旗標）。

## 可選做法（合併）
- 將 `adk_config.yaml` 之內容合併到 `adk.yaml` 的新節點：
```yaml
dev_ui:
  enable: true
  port: 8088
  features:
    events_timeline: true
    tool_registry: true
runner:
  max_iterations: 10
  sse_resume_guard: true
```
- 並調整載入程式讀取新節點。


## policy.risk_threshold
- 允許值：Low / Medium / High / Critical
- 工具應自行以此門檻判斷是否需要觸發 `request_credential()`。


## 合併規則（runtime）
- `adk.yaml` 為主設定；若存在 `experts/*.yaml`，則覆蓋到 `experts` 區塊對應專家。
- `experts.*.model` > `agent.model` > `ADK_MODEL`。工具白名單同理以 `experts.*.tools_allowlist` 覆蓋。
