# K8s 操作與 RBAC
- 部署 `deploy/k8s/rbac.yaml` 與 `deploy/k8s/deploy.yaml`
- 需要權限：get/list/watch/patch deployments；建立 selfsubjectaccessreviews；讀取 events。
- 透過 API 呼叫長任務 `K8sRolloutRestartLongRunningTool`，prod 命名空間會觸發 HITL。
