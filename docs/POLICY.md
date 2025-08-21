
# 動態策略（policy.d）

- 放置於 `policy.d/*.yaml`，支援以下鍵：
  - `protected_namespaces`: 受保護命名空間清單
  - `maintenance_window`: 維護時窗（例如 00:00-06:00）
  - `param_limits`: 參數限制（regex/enum/max_len）
  - `deny_tools` / `allow_tools`: 黑白名單
- `SRESecurityPolicy` 會自動監看檔案的 mtime，變更後即時生效
