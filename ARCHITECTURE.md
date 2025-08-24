# SRE Assistant 架構設計文檔

## 執行摘要

SRE Assistant 是基於 Google ADK 的智慧型 SRE 助理，採用**進階工作流程 (Advanced Workflow)** 架構，實現自動化診斷、修復、覆盤和配置優化。此架構以 `SREWorkflow` 為核心，透過組合 `ParallelAgent`、`ConditionalRemediation` (條件代理) 和 `LoopAgent` (循環代理) 等模式，取代了原有的簡單 `SequentialAgent` 模型，提供更高效、更靈活的 SRE 自動化能力。

## 1. 系統架構概覽

### 1.1 分類評估

根據 ADK 範例的分類標準來評估 SRE Assistant，並確認工作流程模式的適用性。

| 屬性 | SRE Assistant 評估 | 理由 |
|------|-------------------|------|
| **代理名稱** | SRE Assistant | 智慧型 SRE 助理系統 |
| **使用案例** | 自動化 SRE 工作流程：診斷、修復、覆盤、配置優化 | 處理生產環境事件的完整生命週期 |
| **標籤** | `Multi-agent`, `RAG`, `HITL`, `Monitoring`, `Kubernetes`, `Prometheus`, `GitHub`, `Workflow` | 結合多種技術和整合 |
| **互動類型** | **工作流程 (Workflow)** | 主要是自動化工作流程，次要支援對話 |
| **複雜度** | **進階 (Advanced)** | 多代理協作、複雜狀態管理、外部整合 |
| **代理類型** | **多代理 (Multi Agent)** | 4個專家代理 + 協調器 |
| **垂直領域** | **DevOps/SRE** | 專門針對站點可靠性工程 |

### 1.2 核心架構模式

基於 ADK 的**工作流程驅動多代理架構**，其特點如下：
- **工作流程核心**：使用 `SREWorkflow` (`SequentialAgent`) 作為頂層協調器，定義了清晰的自動化階段。
- **並行處理**：在診斷階段，使用 `ParallelAgent` 同時運行多個分析工具，大幅縮短問題定位時間。
- **條件邏輯**：`ConditionalRemediation` 代理根據事件的嚴重性動態選擇不同的修復路徑（如自動化修復或人工介入）。
- **迭代優化**：`LoopAgent` 用於需要持續調整的任務，如 SLO 配置優化，直到滿足終止條件。
- **領域專家**：各階段由專門的子代理負責，如 `DiagnosticAgent`、`RemediationAgent` 等。


```mermaid
graph TD
    subgraph "User Interface (Clients)"
        UI[REST API / SSE / Web UI]
    end

    subgraph "ADK Runtime"
        Runner[ADK Runner]
    end

    subgraph "SRE Assistant Core Services"
        direction TB
        Auth[Auth Manager]
        Config[Config Manager]
        Memory[Memory Service]
        Session[Session Service]
        SLO[SLO Manager]
    end

    subgraph "SRE Workflow (SREWorkflow)"
        direction LR
        A[Phase 1: Parallel Diagnostics] --> B[Phase 2: Conditional Remediation]
        B --> C[Phase 3: Postmortem]
        C --> D[Phase 4: Iterative Optimization]
    end

    subgraph "Phase 1 Details (ParallelAgent)"
        direction TB
        P1[Metrics Analyzer]
        P2[Log Analyzer]
        P3[Trace Analyzer]
    end

    subgraph "Phase 2 Details (ConditionalRemediation)"
        direction TB
        C1{Severity Check} -- P0 --> C2[HITL Remediation]
        C1 -- P1 --> C3[Automated Remediation]
        C1 -- P2 --> C4[Scheduled Remediation]
    end

    subgraph "Phase 4 Details (LoopAgent)"
        direction TB
        L1(Tune SLO) --> L2{SLO Met?}
        L2 -- No --> L1
        L2 -- Yes --> L3(End)
    end

    UI --> Runner
    Runner --> SREWorkflow

    SREWorkflow -- Uses --> Auth
    SREWorkflow -- Uses --> Config
    SREWorkflow -- Uses --> Memory
    SREWorkflow -- Uses --> Session
    SREWorkflow -- Uses --> SLO

    SREWorkflow -- Contains --> A
    SREWorkflow -- Contains --> B
    SREWorkflow -- Contains --> C
    SREWorkflow -- Contains --> D

    A -- Contains --> P1 & P2 & P3
    B -- Contains --> C1
    D -- Contains --> L1

    style SREWorkflow fill:#bbf,stroke:#333,stroke-width:2px
    style A fill:#cde4ff
    style B fill:#cde4ff
    style C fill:#cde4ff
    style D fill:#cde4ff
```

### 1.3 目錄結構

- [官方建議目錄結構](adk-repository-structure.md)：請務必遵守

```bash
sre_assistant/
├── __init__.py                 # A2A 暴露和服務註冊
├── README.md                   # SRE Assistant 模組說明
├── workflow.py                 # SREWorkflow 工作流程協調器
├── contracts.py                # Pydantic 資料模型
├── tools.py                    # 版本化工具註冊表
├── citation_manager.py         # RAG 引用格式管理
├── slo_manager.py              # SLO/錯誤預算管理器
├── prompts.py                  # 共享的 Prompt 模板
├── response_quality.py         # 回應品質評估工具
├── memory.py                   # (待釐清，可能與 memory/ 衝突)
│
├── a2a/                        # A2A (Agent-to-Agent) 協議實作
│   └── protocol.py
│
├── auth/                       # 認證授權模組
│   ├── __init__.py
│   ├── auth_factory.py         # 認證提供者工廠
│   └── auth_manager.py         # 統一管理器 (含速率限制、審計)
│
├── config/                     # 配置管理系統
│   ├── config_manager.py       # 三層配置管理器
│   ├── base.yaml               # 基礎配置
│   └── environments/           # 環境特定配置
│       ├── development.yaml
│       ├── production.yaml
│       └── staging.yaml
│
├── deployment/                 # 部署工廠
│   └── deployment_factory.py
│
├── memory/                     # 長期記憶體 (RAG) 模組
│   └── backend_factory.py      # 向量數據庫後端工廠
│
├── session/                    # 會話 (短期記憶) 持久化模組
│   └── firestore_task_store.py # Firestore 會話存儲
│
├── sub_agents/                 # 領域專家代理
│   ├── __init__.py
│   ├── diagnostic/             # 診斷專家 (含 RAG)
│   ├── remediation/            # 修復專家 (含 HITL)
│   ├── postmortem/             # 覆盤專家 (含報告生成)
│   └── config/                 # 配置專家 (含 IaC)
│
├── tests/                      # 測試套件
│   ├── test_agent.py           # 工作流程整合測試
│   ├── test_auth.py            # 認證授權測試
│   ├── test_contracts.py       # Pydantic 契約測試
│   ├── test_citation.py        # 引用系統測試
│   ├── test_concurrent_sessions.py # 並發會話測試
│   ├── test_session.py         # 會話持久化測試
│   └── verify_config.py        # 配置驗證腳本
│
├── utils/                      # 通用工具函式
│   └── a2a_client.py
│
└── Eval/                       # 評估框架
    └── evaluation.py
```

## 2. 核心模組與服務設計

### 2.1 核心服務模組 (Core Service Modules)

除了主工作流程外，SRE Assistant 還包含一系列核心服務模組，為整個系統提供基礎支撐。

#### 2.1.1 配置管理 (`config/`)

- **實作**: `sre_assistant/config/config_manager.py`
- **設計**: 系統採用一個強大的**三層配置架構**，以提供最大的靈活性和環境隔離。
    1.  **基礎配置 (`base.yaml`)**: 定義所有環境共享的預設值。
    2.  **環境配置 (`environments/*.yaml`)**: 為特定環境（如 `development`, `staging`, `production`）提供專屬配置，並覆寫基礎值。
    3.  **環境變數覆寫**: 在啟動時，可以透過環境變數覆寫任何配置，這是容器化部署（如 Docker, Kubernetes）的最佳實踐。
- **功能**: `ConfigManager` 是一個單例服務，它在啟動時自動載入、深度合併和驗證（使用 Pydantic）所有配置層，確保整個應用程式在執行期間都能安全、一致地存取配置。

#### 2.1.2 認證授權 (`auth/`)

- **實作**: `sre_assistant/auth/auth_manager.py`, `auth_factory.py`
- **設計**: 一個基於**工廠模式**的認證授權系統。`AuthFactory` 根據配置動態創建不同的認證提供者（如 Google IAM, OAuth2, API Key），而 `AuthManager` 作為統一的入口，處理所有安全相關操作。
- **功能**:
    - **多提供者支援**: 靈活適應不同部署環境的安全要求。
    - **RBAC**: 支援基於角色的存取控制。
    - **安全中間件**: 整合了速率限制、審計日誌和安全快取功能。

#### 2.1.3 會話持久化 (`session/`)

- **實作**: `sre_assistant/session/firestore_task_store.py`
- **設計**: 將會話（短期記憶）管理與長期記憶（RAG）分離，是一個獨立的模組。
- **功能**: 目前的核心實作是 `FirestoreTaskStore`，它將每個任務 (Task/Session) 的狀態作為一個文檔存儲在 Google Cloud Firestore 中。這確保了服務在無狀態、可水平擴展的環境（如 Cloud Run, GKE）中重啟或擴展時，用戶的對話狀態不會遺失。

#### 2.1.4 長期記憶 (`memory/`)

- **實作**: `sre_assistant/memory/backend_factory.py`
- **設計**: 系統的長期記憶（用於 RAG）是透過一個**向量數據庫後端工廠** `MemoryBackendFactory` 來管理的。
- **功能**: 提供一個統一的 `VectorBackend` 接口，並透過工廠模式支援多種後端，包括 `Weaviate`、`PostgreSQL (pgvector)` 和 `VertexAIBackend` (Vertex AI Vector Search)，使得在不同環境中切換知識庫後端變得輕而易舉。

#### 2.1.5 SLO 管理 (`slo_manager.py`)

- **實作**: `sre_assistant/slo_manager.py`
- **設計**: `SREErrorBudgetManager` 是對 Google SRE 手冊中錯誤預算理念的直接程式碼實現。
- **功能**:
    - **計算錯誤預算**: 根據配置的 SLO 目標（如 99.9%）計算允許的錯誤量。
    - **多窗口燃燒率警報**: 實作了基於多個時間窗口（如 1 小時、6 小時、3 天）的燃燒率計算和警報機制。這可以幫助團隊區分需要立即處理的緊急事件和需要關注的長期趨勢，避免警報疲勞。

#### 2.1.6 其他模組
- **`deployment/`**: 包含一個部署工廠，用於根據配置創建和管理不同平台的部署資源。
- **`a2a/`**: 實現了 Agent-to-Agent 通訊協議，允許 SRE Assistant 與其他外部代理進行協作。
- **`utils/`**: 提供跨模組共享的通用工具函式。
- **`Eval/`**: 包含了用於評估代理性能和準確性的框架和腳本。

### 2.2 主工作流程 (SREWorkflow)

`SREWorkflow` 是系統的核心，它繼承自 `SequentialAgent`，負責按順序調度四個主要階段：

```python
class SREWorkflow(SequentialAgent):
    """
    主工作流程：實現一個基於工作流程的 SRE 自動化過程。
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # --- 階段 1: 並行診斷 (帶引用) ---
        diagnostic_phase = CitingParallelDiagnosticsAgent(...)

        # --- 階段 2: 條件化修復 ---
        remediation_phase = ConditionalRemediation(...)

        # --- 階段 3: 覆盤 ---
        postmortem_phase = PostmortemAgent(...)

        # --- 階段 4: 迭代優化 ---
        optimization_phase = IterativeOptimization(...)

        super().__init__(
            name="SREWorkflowCoordinator",
            sub_agents=[
                diagnostic_phase,
                remediation_phase,
                postmortem_phase,
                optimization_phase
            ]
        )
```

### 2.2 認證授權系統

系統內建一個強大的認證授權模組，透過工廠模式提供靈活性和可擴展性。

- **AuthFactory**: 根據配置創建不同的認證提供者 (IAM, OAuth2, API Key, JWT, mTLS, Local)。
- **AuthManager**: 作為單例，統一處理認證、授權、速率限制、審計日誌和快取。
- **AuthProvider**: 定義了所有提供者必須實現的統一介面。

```python
# sre_assistant/auth/auth_manager.py
class AuthManager:
    def __init__(self):
        # 根據配置創建提供者
        self.provider = AuthFactory.create(config)

    async def authenticate(...) -> bool: ...
    async def authorize(...) -> bool: ...
```

### 2.3 RAG 引用系統

為了確保所有由 LLM 生成的內容都有據可循，系統包含一個 `SRECitationFormatter`。

- **統一格式**: 將來自不同源頭 (文件、配置、日誌) 的證據格式化為標準引用。
- **自動整合**: `CitingParallelDiagnosticsAgent` 在診斷流程結束時，會自動收集所有工具產生的證據，並使用 `SRECitationFormatter` 進行格式化，附加到最終輸出中。

```python
class SRECitationFormatter:
    def format_citation(self, sources: List[Dict]) -> str:
        """格式化多種來源的引用"""
        # 支援：配置檔、事件記錄、文檔、知識庫
        pass
```

## 3. 子代理設計

### 3.1 診斷專家 (DiagnosticExpert)

- **核心功能**：並行分析指標、日誌、追蹤
- **P0 增強**：整合 RAG 引用系統
- **P1 增強**：GitHub Issues 查詢
- **P2 增強**：多模態分析（截圖、影片）

### 3.2 修復專家 (RemediationExpert)  

- **核心功能**：執行修復操作
- **P0 增強**：HITL 審批機制
- **P1 增強**：迭代優化框架
- **P2 增強**：自動回滾機制

### 3.3 覆盤專家 (PostmortemExpert)

- **核心功能**：生成事後檢討報告
- **P1 增強**：5 Whys 模板實現
- **P1 增強**：自動時間線生成
- **P2 增強**：視覺化報告

### 3.4 配置專家 (ConfigExpert)

- **核心功能**：優化系統配置
- **P1 增強**：配置沙盒測試
- **P2 增強**：Terraform 模組生成

## 4. 記憶體與會話管理

### 4.1 Session 持久化

會話狀態的持久化是透過一個可插拔的後端實現的，目前的核心實作是 `FirestoreTaskStore`。

- **實作**: `sre_assistant/session/firestore_task_store.py`
- **功能**: 將每個任務 (Task/Session) 的狀態作為一個文檔存儲在 Google Cloud Firestore 中，確保了服務在重啟或擴展時的狀態一致性。
- **對應 `TASKS.md`**: 這實現了 "遷移到 `VertexAiSessionService`" 的目標，因為 Firestore 是 Vertex AI Agent Builder 的底層會話管理技術之一。

### 4.2 Memory (RAG) 持久化

系統的長期記憶 (用於 RAG) 是透過一個向量數據庫後端工廠 `MemoryBackendFactory` 來管理的。

- **實作**: `sre_assistant/memory/backend_factory.py`
- **功能**: 提供一個統一的 `VectorBackend` 接口，並透過工廠模式支援多種後端，包括 `Weaviate`、`PostgreSQL (pgvector)` 和 `VertexAIBackend` (Vertex AI Vector Search)。
- **對應 `TASKS.md`**: `VertexAIBackend` 的實作完成了 "實作 `VertexAiMemoryBankService`" 的目標。

## 5. 外部整合（P1 新增）

### 5.1 GitHub 整合

```python
class SREIncidentTracker:
    """GitHub Issues 事件追蹤"""
    async def create_incident_issue(self, incident: Dict) -> str:
        # 自動創建和更新 Issues
        pass
```

### 5.2 MCP 工具箱

```python
class MCPDatabaseToolbox:
    """資料庫操作標準化"""
    def get_safe_query_tool(self) -> Tool:
        # 防 SQL 注入的查詢工具
        pass
```

## 6. 評估框架

### 6.1 SRE 專用指標

| 指標類型 | 指標名稱 | 目標值 | 優先級 |
|---------|---------|--------|--------|
| 準確性 | diagnosis_accuracy | > 95% | P0 |
| 性能 | response_time_p95 | < 30s | P0 |
| 可靠性 | mttr_performance | < 15min | P1 |
| SLO | error_budget_efficiency | > 80% | P1 |
| 成本 | cost_per_incident | < $2.00 | P2 |

## 7. 部署架構

### 7.1 環境策略

| 環境 | 配置 | 用途 | 優先級 |
|------|------|------|--------|
| 開發 | Local + PostgreSQL | 功能開發 | P0 |
| 測試 | Cloud Run + Weaviate | 整合測試 | P1 |
| 生產 | Agent Engine + Vertex AI | 正式服務 | P1 |

### 7.2 部署優化（P2）

- 金絲雀部署
- 藍綠部署
- 自動回滾

## 8. 安全性設計

### 8.1 認證授權（P0）

- 多因素認證
- RBAC 權限管理
- API Key 輪換

### 8.2 審計日誌（P0）

- 所有操作記錄
- 不可變日誌存儲
- 合規報告生成

## 9. 性能優化

### 9.1 緩存策略（P1）

- Prometheus 查詢緩存 60 秒
- Runbook 緩存 24 小時
- 智能緩存失效

### 9.2 並行處理（P1）

- 工具調用並行化
- 連接池管理
- 合理超時設置

## 10. 監控與 SLO

### 10.1 關鍵指標（P0）

```python
class SREMetricsCollector:
    metrics = {
        "availability": "99.95%",
        "latency_p99": "< 1s",
        "error_rate": "< 0.1%"
    }
```

### 10.2 錯誤預算管理（P1）

```python
class SREErrorBudgetManager:
    def calculate_remaining_budget(self) -> float:
        # 實時計算剩餘錯誤預算
        pass
```

## 11. A2A 協議（P2）

### 11.1 服務暴露

```python
# 在 __init__.py 中暴露服務
agent_card = AgentCard(
    name="sre_assistant",
    version="1.0.0",
    capabilities=["diagnosis", "remediation", "postmortem"],
    endpoints=["https://api.sre-assistant.io"]
)
```

### 11.2 服務消費

```python
class RemoteAgentClient:
    async def call_ml_anomaly_detector(self, data: Dict) -> Dict:
        # 調用外部 ML 異常檢測代理
        pass
```

## 12. 實施路線圖

### Phase 0: 核心架構重構 (已完成)
- ✅ **工作流程架構**: 從簡單 `SequentialAgent` 遷移到 `SREWorkflow`，整合並行、條件和循環模式。
- ✅ **認證授權系統**: 實現 `AuthFactory` 和 `AuthManager`，支援多種認證方式、RBAC、速率限制和審計。
- ✅ **RAG 引用系統**: 實作 `SRECitationFormatter` 並整合到診斷流程中。
- ✅ **Session/Memory 持久化**: 透過 `FirestoreTaskStore` 和 `MemoryBackendFactory` (含 `VertexAIBackend`) 實現持久化。

### Phase 1: 功能擴展 (下一步)
- 📋 **P1 GitHub 整合**: 自動化事件追蹤。
- 📋 **P1 SRE 量化指標**: 實現完整的 SLO 管理和 5 Whys 模板。
- 📋 **P1 迭代優化框架**: 完善 `SLOTuningAgent` 等的內部邏輯。
- 📋 **P1 端到端測試**: 為 HITL 和 API 添加完整的測試。

### Phase 2: 企業就緒（長期）
- 📋 **P2 A2A 協議**: 實現跨代理服務發現與通訊。
- 📋 **P2 多模態分析**: 支援監控面板截圖分析。
- 📋 **P2 可觀測性**: 整合 OpenTelemetry。
- 📋 **P2 部署與成本優化**: 實現進階部署策略和成本分析。

## 13. 技術債務管理

### 已識別的技術債務

| 項目 | 影響 | 優先級 | 計劃 |
|------|------|--------|------|
| 測試覆蓋率不足 | 中 | P1 | 為 P0 新增的工作流程和模組增加單元和整合測試，目標覆蓋率 80%。 |
| 文檔更新滯後 | 低 | P2 | 考慮引入自動化工具從程式碼註解生成部分文檔。 |

## 14. 關鍵設計決策

### 14.1 為何選擇工作流程 (Workflow) 架構

- **問題**: 傳統的 `SequentialAgent` 無法高效處理複雜的 SRE 場景，例如，無法同時分析日誌和指標，也無法根據問題嚴重性採取不同措施。
- **解決方案**: 採用了以 `SREWorkflow` 為核心的混合式工作流程架構。
  - **並行效率**: `ParallelAgent` 允許併發執行多個診斷任務，將診斷時間從幾分鐘縮短到幾十秒。
  - **決策靈活性**: `ConditionalRemediation` 代理可以根據數據動態決定是自動修復、請求人工批准 (HITL) 還是僅發出警報，從而提高了安全性與自動化程度。
  - **持續改進**: `LoopAgent` 使得代理能夠自我迭代和優化，例如不斷調整配置直到 SLO 達標，實現了真正的自動化運維閉環。
- **權衡**: 這種架構雖然比單純的 `SequentialAgent` 複雜，但它帶來的性能、靈活性和可擴展性對於 SRE 自動化場景是至關重要的。

### 14.2 為何實現工廠模式

- **優點**：靈活性、可測試性、關注點分離
- **缺點**：額外的抽象層
- **權衡**：長期維護性優於簡單性

## 15. 附錄

### 15.1 參考資源

- [ADK 官方文檔](docs/references/adk-docs)
- [Google SRE Book](google-sre-book.md)
- [內部參考文檔](docs/references/)

### 15.2 術語表

| 術語 | 定義 |
|------|------|
| ADK | Agent Development Kit |
| SRE | Site Reliability Engineering |
| HITL | Human-in-the-Loop |
| RAG | Retrieval-Augmented Generation |
| A2A | Agent-to-Agent |
| MCP | Model Context Protocol |

### 15.3 版本歷史

| 版本 | 日期 | 變更摘要 |
|------|------|----------|
| 1.0.0 | 2025-08 | 初始架構 |
| 1.1.0 | 2025-08 | 加入 HITL |
| 2.0.0 | 2025-08 | 重構為 ADK |
| 2.1.0 | 2025-08 | P0 增強計劃 |

---

**文檔維護者**：Google ADK 首席架構師  
**最後更新**：2025-08-24  
**下次審查**：2025-09-24