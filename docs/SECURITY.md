
# 資安說明（Security）

## API 金鑰與角色
- 金鑰以 SHA-256 雜湊儲存於 `api_keys` 表。
- 角色等級：viewer < operator < admin。部分端點需 operator/admin 權限。

## 工具與策略
- 每個工具以 YAML 定義：參數/回傳/錯誤碼/超時/重試/風險等級。
- `SRESecurityPolicy` 會合併 YAML 與動態規則（受保護命名空間、regex/enum 限制、維護時窗）。

## 秘密與佈署
- Docker/K8s 部署以環境變數注入敏感設定。
- K8s `Secret` 管理 API Key，Deployment 讀取並注入容器環境。
