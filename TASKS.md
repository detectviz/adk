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

```
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
    - [ ] 創建 `docker-compose.yml`，用於一鍵啟動本地開發環境 (ADK Backend, PostgreSQL, Redis, Weaviate, Grafana, Loki)。
    - [ ] 編寫開發環境的啟動與使用文檔。

- **後端服務 (Backend Service)**
    - [ ] 實現基於 ADK 的核心 `SREAssistant` Agent 服務。
    - [ ] 實現基於 `None` 選項的無認證模式，供本地測試使用。
    - [ ] 使用 ADK Web UI 作為主要的開發與互動介面。

- **核心工具 (Core Tools)**
    - [ ] 實現 `PrometheusQueryTool` 並整合到 Agent 中。
    - [ ] 實現 `LokiLogQueryTool` 並整合到 Agent 中。
    - [ ] 實現 `GitHubTool` 用於創建 Issue。

- **核心服務 (Core Services)**
    - [ ] **記憶體**: 實現 `MemoryProvider` 以對接 Weaviate/Postgres，並提供 RAG 檢索能力。
    - [ ] **會話**: 實現 `session_service_builder` 以對接 Redis/Postgres，提供持久化會話。
    - [ ] **認證**: 實現 `AuthProvider` 以支援 OAuth 2.0 流程。

### P1 - 重構 (Refactoring)

- [ ] **AuthManager 狀態管理**:
    - **來源**: `REFACTOR_PLAN.md`
    - **任務**: 將 `AuthManager` 重構為無狀態服務，所有狀態透過 `InvocationContext` 讀寫，並由 `SessionService` 持久化。
    - **驗收標準**: `AuthManager` 內部不再持有 `_auth_cache` 或 `_rate_limits` 等實例變數。

### P1 - 技術債 (Technical Debt)

- [ ] **增加測試覆蓋率**:
    - **來源**: `TASKS.md` (舊)
    - **任務**: 為 Phase 1 開發的核心模組（Auth, Memory, Session, Tools）增加單元和整合測試。
    - **驗收標準**: 核心模組的測試覆蓋率達到 80% 以上。

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