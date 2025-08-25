# SPEC.md - SRE Assistant 功能與代理規格

**版本**: 1.1.0
**狀態**: 草案
**關聯架構**: [ARCHITECTURE.md](ARCHITECTURE.md)
**關聯路線圖**: [ROADMAP.md](ROADMAP.md)

## 1. 總覽

本文件旨在詳細定義 SRE Assistant 聯邦化生態系統中各個組件的功能規格，特別是共享工具和專業化代理的設計。本文檔是將 [ARCHITECTURE.md](ARCHITECTURE.md) 中的宏觀設計轉化為可執行開發任務的橋樑。

---

## 2. 共享工具註冊表 (Shared Tool Registry)

為了促進程式碼的重用和一致性，所有代理都應盡可能使用此處定義的共享工具。每項工具都應有標準化的介面和配置方法。

*(註：此處為初步規劃，具體實現時將以程式碼中的工具註冊表為準)*

### 2.1 可觀測性工具 (Observability Tools)

- **`PrometheusQueryTool`**:
    - **描述**: 執行 PromQL 查詢，獲取指標數據。
    - **功能**: `run_query(query: str, time_range: str) -> dict`
    - **配置**: Prometheus API endpoint, authentication token.
- **`PrometheusConfigurationTool`**:
    - **描述**: 動態更新 Prometheus 監控目標，實現監控閉環。
    - **功能**: `add_scrape_target(job_name: str, target_url: str)`, `remove_scrape_target(job_name: str, target_url: str)`
    - **配置**: Prometheus reload endpoint or management API.
- **`LokiLogQueryTool`**:
    - **描述**: 執行 LogQL 查詢，獲取日誌數據。
    - **功能**: `search_logs(query: str, limit: int) -> list`
    - **配置**: Loki API endpoint.
- **`GrafanaIntegrationTool`**:
    - **描述**: 與 Grafana API 互動，用於儀表板操作和註解。
    - **功能**: `create_annotation(text: str, tags: list)`, `embed_panel(panel_id: str) -> str`
    - **配置**: Grafana URL, API Key.
- **`GrafanaOnCallTool`**:
    - **描述**: 與 Grafana OnCall 互動，管理告警和排班。
    - **功能**: `create_escalation(summary: str, details: str)`, `get_on_call_user() -> str`
    - **配置**: Grafana OnCall API endpoint, API Key.

### 2.2 基礎設施操作工具 (Infrastructure Operation Tools)

- **`KubernetesOperationTool`**:
    - **描述**: 對 Kubernetes 集群執行操作。
    - **功能**: `get_pods(namespace: str)`, `restart_deployment(name: str)`, `view_logs(pod_name: str)`
    - **配置**: Kubeconfig, context.
- **`TerraformTool`**:
    - **描述**: 透過 Terraform 管理基礎設施即代碼。
    - **功能**: `plan(directory: str)`, `apply(directory: str, auto_approve: bool)`
    - **配置**: Terraform binary path, state file location.
- **`HelmOperationTool`**:
    - **描述**: 管理 Helm charts。
    - **功能**: `upgrade_chart(release_name: str, chart: str)`, `rollback(release_name: str, revision: int)`
    - **配置**: Tiller host (if applicable).

### 2.3 版本控制工具 (VCS Tools)

- **`GitHubTool`**:
    - **描述**: 與 GitHub API 互動。
    - **功能**: `create_issue(title: str, body: str)`, `get_commit_details(sha: str)`
    - **配置**: GitHub API Token.

---

## 3. 專業化代理規格 (Specialized Agent Specifications)

根據 [ROADMAP.md](ROADMAP.md) 的規劃，SRE Assistant 將逐步演進為一個由以下專業化代理組成的聯邦。

## 4. 標準化介面與錯誤處理 (Standardized Interface & Error Handling)

### 4.1. 工具介面規格 (Tool Interface Specification)

所有工具的 `execute` 方法都必須遵循以下標準化輸入與輸出格式，以確保系統的穩定性和可預測性。

```python
from typing import Dict, Any, Optional, Protocol
from pydantic import BaseModel

class ToolError(BaseModel):
    """標準化的工具錯誤模型"""
    code: str  # e.g., "RATE_LIMIT_EXCEEDED", "API_AUTH_ERROR"
    message: str
    details: Optional[Dict[str, Any]] = None

class ToolResult(BaseModel):
    """標準化的工具返回結果"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[ToolError] = None
    metadata: Dict[str, Any] = {"timestamp": ..., "raw_output": ...}

class BaseTool(Protocol):
    """所有工具都應實現的協議"""
    async def execute(
        self,
        params: Dict[str, Any],
        context: InvocationContext
    ) -> ToolResult:
        """
        執行工具的核心邏輯。

        Returns:
            ToolResult: 一個包含執行結果的標準化物件。
        """
        pass
```

### 4.2. 錯誤處理策略 (Error Handling Strategy)

- **工具層級**: 工具內部應捕獲可預期的異常（如 API 錯誤、網絡問題），並將其包裝成 `ToolError` 返回。未預期的異常應向上拋出。
- **代理層級**: 代理在收到 `ToolResult` 後，應首先檢查 `success` 字段。如果為 `False`，則應根據 `error.code` 執行相應的錯誤處理邏輯（如重試、降級、請求人類介入）。
- **通用錯誤碼**:
    - `INVALID_PARAMS`: 輸入參數錯誤。
    - `AUTH_FAILURE`: 認證失敗。
    - `TIMEOUT`: 操作超時。
    - `NOT_FOUND`: 請求的資源未找到。
    - `EXTERNAL_API_ERROR`: 外部 API 調用失敗。

## 5. 版本管理策略 (Versioning Strategy)

- **代理版本**: 遵循語義化版本（SemVer, `MAJOR.MINOR.PATCH`）。`MAJOR` 版本變更表示有破壞性 API 變更。
- **工具版本**: 工具的版本應與其所屬的代理或共享庫的版本保持一致。
- **相容性**:
    - `MINOR` 和 `PATCH` 版本的更新必須向後相容。
    - 協調器（Orchestrator）在調用專業化代理時，應檢查其 `MAJOR` 版本號是否相容。
- **文檔**: 所有破壞性變更都必須在 `CHANGELOG.md` 中有清晰的記錄和遷移指南。

### 3.1 代理類別總覽 (Agent Categories)

| 代理名稱 (Agent Name) | 使用案例 (Use Case) | 標籤 (Tag) | 互動類型 (Interaction Type) | 複雜度 (Complexity) | 代理類型 (Agent Type) | 垂直領域 (Vertical) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 事件處理 Assistant | 端到端的事件響應與管理 | `Incident`, `Remediation`, `Postmortem`, `OnCall` | 工作流程 (Workflow) | 進階 (Advanced) | 多代理 (Multi Agent) | SRE/IT 營運 (SRE/IT Operations) |
| 預測維護 Assistant | 預測並預防潛在的系統故障 | `Forecasting`, `Anomaly Detection`, `ML` | 程式化 (Programmatic) | 進階 (Advanced) | 單一代理 (Single Agent) | SRE/可靠性 (SRE/Reliability) |
| 部署管理 Assistant | 自動化並保障 CI/CD 流程 | `Deployment`, `CI/CD`, `Canary`, `Terraform` | 工作流程 (Workflow) | 中等 (Intermediate) | 單一代理 (Single Agent) | DevOps/Release Engineering |
| 混沌工程 Assistant | 透過實驗測試系統韌性 | `Chaos`, `Resilience`, `Fault Injection` | 程式化 (Programmatic) | 中等 (Intermediate) | 單一代理 (Single Agent) | SRE/可靠性 (SRE/Reliability) |
| 容量規劃 Assistant | 分析資源使用並提供擴展建議 | `Capacity`, `Scaling`, `Resource Optimization` | 請求/回應 (Request/Response) | 中等 (Intermediate) | 單一代理 (Single Agent) | SRE/FinOps |
| 成本優化 Assistant | 監控雲成本並提供優化方案 | `FinOps`, `Cost`, `Cloud`, `Optimization` | 請求/回應 (Request/Response) | 中等 (Intermediate) | 單一代理 (Single Agent) | FinOps/Cloud Governance |

### 3.2 事件處理 Assistant (Incident Handler)

- **目標**: 負責對生產環境中發生的事件進行端到端的偵測、分析、修復和覆盤。
- **核心能力**:
    - `incident_detection`: 事件偵測
    - `root_cause_analysis`: 根因分析
    - `automated_remediation`: 自動化修復
    - `postmortem_generation`: 事後檢討報告生成
- **所需工具**:
    - `PrometheusQueryTool`
    - `LokiLogQueryTool`
    - `KubernetesOperationTool`
    - `GrafanaIntegrationTool`
    - `GrafanaOnCallTool`
    - `GitHubTool`
- **記憶體集合 (Memory Collections)**:
    - `incident_history`: 存儲過去所有事件的詳細資訊。
    - `runbook_library`: 存儲用於修復的標準化執行手冊。
    - `postmortem_archive`: 存儲所有已生成的覆盤報告。
- **代理特定配置 (`incident-handler.yaml`)**:
    ```yaml
    auto_remediation_threshold: "P2"  # P2 及以下嚴重性的事件才嘗試自動修復
    escalation_timeout: 300s          # 300秒未確認的事件將自動升級
    default_on_call_user: "sre-team"
    ```

### 3.3 預測維護 Assistant (Predictive Maintenance)

- **目標**: 基於歷史數據預測潛在的系統問題，並在問題發生前發出預警或採取預防措施。
- **核心能力**:
    - `anomaly_detection`: 異常檢測
    - `failure_prediction`: 故障預測
    - `capacity_forecasting`: 容量預測
    - `trend_analysis`: 趨勢分析
- **所需工具/模型**:
    - `PrometheusQueryTool`
    - 內建 ML 模型:
        - `time_series_forecasting` (e.g., ARIMA, Prophet)
        - `anomaly_detection_autoencoder` (e.g., Autoencoder)
        - `failure_prediction_classifier` (e.g., Random Forest)
- **記憶體集合**:
    - `metrics_time_series_db`: 長期存儲的指標數據。
    - `anomaly_patterns`: 已識別的異常模式庫。

### 3.4 部署管理 Assistant (Deployment)

- **目標**: 輔助和自動化軟體部署的全過程，確保部署的穩定性和可靠性。
- **核心能力**:
    - `deployment_planning`: 部署規劃
    - `canary_analysis`: 金絲雀發布分析
    - `rollback_management`: 回滾管理
    - `dependency_tracking`: 依賴追蹤
- **所需工具**:
    - `GitHubTool`
    - `TerraformTool`
    - `HelmOperationTool`
    - `PrometheusQueryTool` (用於金絲雀分析)
- **記憶體集合**:
    - `deployment_history`: 部署歷史記錄。
    - `dependency_graph`: 服務間依賴關係圖。

### 3.5 混沌工程 Assistant (Chaos Engineering)

- **目標**: 透過主動注入故障來測試系統的韌性，並找出潛在的弱點。
- **核心能力**:
    - `experiment_planning`: 混沌實驗規劃。
    - `fault_injection`: 故障注入 (e.g., pod-kill, network-latency)。
    - `result_analysis`: 實驗結果分析。
- **所需工具**:
    - `KubernetesOperationTool`
    - 一個混沌工程框架 (e.g., Litmus, Chaos Mesh) 的整合工具。
- **記憶體集合**:
    - `chaos_experiment_templates`: 混沌實驗範本庫。
    - `experiment_result_archive`: 歷史實驗結果歸檔。

### 3.6 容量規劃 Assistant (Capacity Planning)

- **目標**: 分析當前資源使用情況和未來增長趨勢，提供科學的容量規劃建議。
- **核心能力**:
    - `resource_usage_analysis`: 資源使用分析。
    - `growth_trend_prediction`: 增長趨勢預測。
    - `cost_effective_scaling`: 成本效益擴展建議。
- **所需工具**:
    - `PrometheusQueryTool`
    - 雲服務商計費 API 工具 (e.g., AWS Cost Explorer Tool)。
- **記憶體集合**:
    - `historical_usage_data`: 歷史資源使用數據。

### 3.7 成本優化 Assistant (FinOps)

- **目標**: 持續監控雲資源成本，識別浪費，並提供或執行優化建議（FinOps）。
- **核心能力**:
    - `cost_anomaly_detection`: 成本異常檢測。
    - `idle_resource_identification`: 閒置資源識別。
    - `rightsizing_recommendation`: 實例規格優化建議。
- **所需工具**:
    - 雲服務商計費 API 工具。
    - `KubernetesOperationTool` (用於獲取資源請求和限制)。
- **記憶體集合**:
    - `cost_and_usage_reports`: 歷史成本和用量報告。
    - `optimization_playbooks`: 成本優化劇本庫。
