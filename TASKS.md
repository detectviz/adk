# TASKS.md - SRE Assistant 統一任務清單

**版本**: 4.0.0
**狀態**: 生效中
**關聯架構**: [ARCHITECTURE.md](ARCHITECTURE.md)
**關聯路線圖**: [ROADMAP.md](ROADMAP.md)
**關聯規格**: [SPEC.md](SPEC.md)

## 總覽

本文件是 SRE Assistant 專案的**唯一真實來源 (Single Source of Truth)**，用於追蹤所有開發任務。它根據 [ROADMAP.md](ROADMAP.md) 的階段進行組織，並整合了所有新功能、重構計畫和已知的技術債。

---

## 🎯 目標目錄結構 (Target Directory Structure)

所有開發任務應朝著以下目標目錄結構進行，此結構符合 ADK 最佳實踐並反映了我們的聯邦化架構。

```bash
sre_assistant/
├── __init__.py                 # A2A 服務暴露與註冊
├── workflow.py                 # SREWorkflow - 主工作流程協調器
├── contracts.py                # Pydantic 資料模型 (Events, Incidents, etc.)
├── prompts.py                  # 全域/共享的 Prompt 模板
├── tool_registry.py            # 全域共享工具的註冊與管理
│
├── auth/                       # 認證與授權模組
│   ├── __init__.py
│   ├── auth_factory.py         # 根據配置創建 AuthProvider
│   └── auth_manager.py         # 統一管理認證流程
│
├── config/                     # 配置管理模組
│   ├── config_manager.py
│   └── environments/
│       ├── development.yaml
│       └── production.yaml
│
├── memory/                     # 長期記憶體 (RAG) 模組
│   └── backend_factory.py      # 根據配置創建 MemoryProvider
│
├── session/                    # 會話 (短期記憶) 管理模組
│   └── backend_factory.py      # 根據配置創建 SessionProvider
│
├── sub_agents/                 # 專業化代理 (聯邦化階段)
│   ├── __init__.py
│   ├── incident_handler/       # 事件處理 Assistant
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   └── tools.py            # incident_handler 專用工具
│   └── predictive_maintenance/ # 預測維護 Assistant
│       ├── __init__.py
│       ├── agent.py
│       └── ...
│
├── deployment/                 # 部署相關配置 (Docker, K8s, etc.)
│   ├── Dockerfile
│   └── cloud_run/
│
├── eval/                       # 評估框架與腳本
│   └── evaluation.py
│
└── tests/                      # 測試套件
    ├── test_workflow.py
    ├── test_auth.py
    └── ...
```

---

## Phase 1: MVP - 後端優先與核心能力建設 (預計 1-2 個月)

### P1 - 新功能 (New Features)

- **基礎設施 (Infrastructure)**
    - [ ] **TASK-P1-INFRA-01**: 創建 `docker-compose.yml`
      - **依賴**: 無
      - **驗收標準**:
        - [ ] 能夠透過 `docker-compose up` 成功啟動所有服務。
        - [ ] 服務之間網絡互通。
        - [ ] 數據卷掛載正確，數據可持久化。
    - [ ] **TASK-P1-INFRA-02**: 編寫開發環境的啟動與使用文檔
      - **依賴**: [TASK-P1-INFRA-01]
      - **驗收標準**:
        - [ ] 文檔應包含環境要求、啟動步驟、停止步驟和常見問題排查。
        - [ ] 新成員能夠根據文檔獨立完成環境設置。

- **後端服務 (Backend Service)**
    - [ ] **TASK-P1-SVC-01**: 實現核心 `SREAssistant` Agent 服務
      - **依賴**: [TASK-P1-INFRA-01]
      - **驗收標準**:
        - [ ] 服務能成功啟動並監聽指定端口。
        - [ ] `SREWorkflow` 能夠接收請求並返回基礎回應。
    - [ ] **TASK-P1-SVC-02**: 實現無認證模式
      - **依賴**: [TASK-P1-SVC-01]
      - **驗收標準**:
        - [ ] 當 `auth.provider` 設置為 `None` 時，所有請求無需認證即可通過。
        - [ ] `InvocationContext` 中有模擬的用戶資訊。
    - [ ] **TASK-P1-SVC-03**: 使用 ADK Web UI 進行開發與互動
      - **依賴**: [TASK-P1-SVC-01]
      - **驗收標準**:
        - [ ] 可透過 ADK Web UI 與後端服務進行問答互動。
        - [ ] 能夠正確顯示工具調用和最終結果。

- **核心工具 (Core Tools)**
    - [ ] **TASK-P1-TOOL-01**: 實現 `PrometheusQueryTool`
      - **依賴**: [TASK-P1-SVC-01]
      - **驗收標準**:
        - [ ] 能夠成功查詢 Prometheus 並返回指標數據。
        - [ ] 遵循 `SPEC.md` 中定義的 `ToolResult` 格式。
        - [ ] 有對應的單元測試。
    - [ ] **TASK-P1-TOOL-02**: 實現 `LokiLogQueryTool`
      - **依賴**: [TASK-P1-SVC-01]
      - **驗收標準**:
        - [ ] 能夠成功查詢 Loki 並返回日誌數據。
        - [ ] 遵循 `SPEC.md` 中定義的 `ToolResult` 格式。
        - [ ] 有對應的單元測試。
    - [ ] **TASK-P1-TOOL-03**: 實現 `GitHubTool`
      - **依賴**: [TASK-P1-SVC-01]
      - **驗收標準**:
        - [ ] 能夠成功在指定的 GitHub Repo 中創建 Issue。
        - [ ] 遵循 `SPEC.md` 中定義的 `ToolResult` 格式。
        - [ ] 有對應的單元測試，並使用 mock 進行隔離。

- **核心服務 (Core Services)**
    - [ ] **TASK-P1-CORE-01**: 實現 `MemoryProvider` (RAG)
      - **依賴**: [TASK-P1-INFRA-01]
      - **驗收標準**:
        - [ ] 能夠將文檔向量化並存儲到 Weaviate。
        - [ ] 能夠根據查詢進行語義搜索並返回相關文檔片段。
        - [ ] 有整合測試驗證 RAG 流程。
    - [ ] **TASK-P1-CORE-02**: 實現 `session_service_builder` (持久化會話)
      - **依賴**: [TASK-P1-INFRA-01]
      - **驗收標準**:
        - [ ] 多輪對話的上下文能夠被正確保存和讀取。
        - [ ] 服務重啟後，可以從 Redis/Postgres 中恢復會話狀態。
        - [ ] 有整合測試驗證會話持久化。
    - [ ] **TASK-P1-CORE-03**: 實現 `AuthProvider` (OAuth 2.0)
      - **依賴**: [TASK-P1-SVC-01]
      - **驗收標準**:
        - [ ] 能夠與一個 OIDC Provider (如 Google) 完成認證流程。
        - [ ] 成功獲取並驗證 `id_token` 和 `access_token`。
        - [ ] 有整合測試（可使用 mock OIDC server）。

### P1 - 重構 (Refactoring)

- [✅] **TASK-P1-REFACTOR-01**: AuthManager 狀態管理
    - **來源**: `REFACTOR_PLAN.md`
    - **任務**: 將 `AuthManager` 重構為無狀態服務，所有狀態透過 `InvocationContext` 讀寫，並由 `SessionService` 持久化。
    - **依賴**: 無 (已完成)
    - **驗收標準**:
        - [ ] `AuthManager` 內部不再持有 `_auth_cache` 或 `_rate_limits` 等實例變數。
        - [ ] 狀態讀寫均通過 `InvocationContext`。

### P1 - 技術債 (Technical Debt)

- [ ] **TASK-P1-DEBT-01**: 增加測試覆蓋率
    - **來源**: `TASKS.md` (舊)
    - **任務**: 為 Phase 1 開發的核心模組（Auth, Memory, Session, Tools）增加單元和整合測試。
    - **依賴**: [TASK-P1-CORE-01], [TASK-P1-CORE-02], [TASK-P1-CORE-03], [TASK-P1-TOOL-01], [TASK-P1-TOOL-02], [TASK-P1-TOOL-03]
    - **驗收標準**:
        - [ ] `pytest --cov` 報告顯示核心模組測試覆蓋率 > 80%。
        - [ ] CI 流水線中包含測試覆蓋率檢查步驟。

---

## Phase 2: Grafana 原生體驗 (預計 2-3 個月)

### P2 - 新功能 (New Features)

- **Grafana 插件 (Plugin Development)**
    - [ ] 開發 SRE Assistant Grafana App Plugin v1.0。
    - [ ] 在插件中實現 ChatOps 面板。
    - [ ] 實現插件與後端服務的 WebSocket / RESTful 安全通訊。
- **Grafana 整合 (Deep Integration)**
    - [ ] 實現 `GrafanaIntegrationTool` 的 `embed_panel` 功能，並在聊天中提供對應指令。
    - [ ] 實現 `GrafanaIntegrationTool` 的 `create_annotation` 功能，並在聊天中提供對應指令。
    - [ ] 實現 `GrafanaOnCallTool`，用於創建告警升級和獲取值班人員。
- **DevOps 工具 (DevOps Tools)**
    - [ ] 實現 `TerraformTool`，用於基礎設施即代碼的管理。
- **修復後驗證 (Post-Remediation Verification)**
    - **來源**: `TASKS.md` (舊)
    - **任務**: 在工作流程中新增 `VerificationPhase`，包含 `HealthCheckAgent` 和 `VerificationCriticAgent`，確保修復操作的有效性。
- **事件管理 (Incident Management)**
    - **來源**: `TASKS.md` (舊)
    - **任務**: 整合 `GitHubTool`，實現從事件到 Issue 的自動創建和狀態同步。

### P2 - 重構 (Refactoring)

- [ ] **智慧分診系統**:
    - **來源**: `REFACTOR_PLAN.md`
    - **任務**: 使用基於 LLM 的 `SREIntelligentDispatcher` 替換靜態的條件判斷邏輯，以動態選擇最合適的專家代理。
    - **驗收標準**: 系統能夠根據診斷摘要，動態調度在 `SPEC.md` 中定義的專家代理。

### P2 - 技術債 (Technical Debt)

- [ ] **令牌儲存安全強化**:
    - **來源**: `TASKS.md` (舊)
    - **任務**: 將敏感的認證令牌（特別是 Refresh Token）從會話狀態中移出，存儲到 Google Secret Manager 或 HashiCorp Vault 中。
    - **驗收標準**: `context.state` 中只儲存對秘密的引用。
- [ ] **文檔更新**:
    - **任務**: 更新所有面向使用者的文檔，引導使用者從 ADK Web UI 過渡到 Grafana 插件。

---

## Phase 3 & 4: 聯邦化與未來 (Federation & Future)

*(註：此處為高階史詩級任務，將在 P1/P2 完成後進一步細化)*

- [ ] **(P3) 專業化代理**: 將覆盤報告生成功能重構為第一個獨立的 `PostmortemAgent`。
- [ ] **(P3) A2A 通訊**: 實現 gRPC A2A 通訊協議，用於協調器與 `PostmortemAgent` 的通訊。
- [ ] **(P3) 主動預防**: 整合機器學習模型，實現異常檢測和趨勢預測能力。
- [ ] **(P3) 監控閉環**: 實現 `PrometheusConfigurationTool` 以動態更新監控目標。
- [ ] **(P4) 聯邦協調器**: 開發功能完備的 SRE Orchestrator 服務。
- [ ] **(P4) 代理矩陣**: 開發並部署 `CostOptimizationAgent` 和 `ChaosEngineeringAgent`。
- [ ] **(P4) 服務發現**: 建立代理註冊中心。