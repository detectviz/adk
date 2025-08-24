# SRE Assistant 架構設計文檔

## 執行摘要

SRE Assistant 是基於 Google ADK 的智慧型 SRE 助理，採用多代理架構實現自動化診斷、修復、覆盤和配置管理。採用 SequentialAgent 作為主協調器，統籌管理四個專業子代理，並整合 HITL (Human-in-the-Loop)、RAG (Retrieval-Augmented Generation)、多種觀測工具，提供端到端的 SRE 工作流自動化。

## 1. 系統架構概覽

### 1.1 核心架構模式

基於 ADK 的多代理架構，支援層級化設計：
- **根代理**：使用 `SequentialAgent` 協調子代理
- **子代理**：使用 `LlmAgent` 實現領域專家邏輯
- **工具層**：`FunctionTool` 和 `LongRunningFunctionTool` 實現
- **記憶體**：透過自訂 `SessionService` 整合 Spanner/Vertex RAG

```
┌──────────────────────────────────────────────────────┐
│                    User Interface Layer              │
│           REST API | SSE | ADK Web Dev UI            │
└──────────────────────────────────────────────────────┘
                         │
┌──────────────────────────────────────────────────────┐
│                 ADK Runner + Sessions                │
│              (google.adk.runners.Runner)             │
└──────────────────────────────────────────────────────┘
                         │
┌──────────────────────────────────────────────────────┐
│          Coordinator (SequentialAgent)               │
│              sre_assistant/agent.py                  │
└──────────────────────────────────────────────────────┘
                         │
    ┌────────────────────┴────────────────────┐
    ▼                                         ▼
┌──────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐
│Diagnostic│  │Remediation│  │Postmortem │  │Config    │
│Expert    │  │Expert     │  │Expert     │  │Expert    │
└──────────┘  └───────────┘  └───────────┘  └──────────┘
```

### 1.2 目錄結構

- [官方建議目錄結構](adk-repository-structure.md)：請務必遵守

```bash
sre_assistant/
├── __init__.py                 # A2A 暴露和服務註冊
├── agent.py                    # SequentialAgent 協調器
├── contracts.py                # Pydantic 資料模型
├── memory.py                   # 記憶體系統配置
├── tools.py                    # 版本化工具註冊表
├── auth_factory.py             # 認證授權工廠（P0 新增）
├── citation_manager.py         # 引用格式管理（P0 新增）
│
├── sub_agents/                 
│   ├── diagnostic/             # 診斷專家（含 RAG）
│   ├── remediation/            # 修復專家（含 HITL）
│   ├── postmortem/             # 覆盤專家（含報告生成）
│   └── config/                 # 配置專家（含 IaC）
│
├── integrations/               # 外部整合（P1 新增）
│   ├── github_tracker.py       # GitHub Issues 整合
│   ├── mcp_toolbox.py          # MCP 資料庫工具
│   └── cost_advisor.py         # 成本優化顧問
│
├── evaluation/                 
│   └── sre_evaluator.py       # SRE 特定評估指標
│
├── deployment/                 
│   ├── terraform/             # IaC 模組（P2）
│   ├── docker/                # 容器配置
│   └── k8s/                   # Kubernetes 部署
│
└── tests/                      
    ├── test_agent.py          # 整合測試
    ├── test_contracts.py      # 契約測試
    ├── test_concurrent.py     # 並發測試
    └── test_e2e.py            # 端到端測試（P1）
```

## 2. 核心模組設計

### 2.1 主協調器 (SequentialAgent)

負責工作流程協調，依序調用專家代理：

```python
class SRECoordinator(SequentialAgent):
    def __init__(self):
        super().__init__(
            name="sre_coordinator",
            agents=[
                DiagnosticExpert(),
                RemediationExpert(),
                PostmortemExpert(),
                ConfigExpert()
            ],
            # P0: 整合認證工廠
            auth_provider=AuthFactory.create("production")
        )
```

### 2.2 認證授權工廠（P0 新增）

統一管理多種認證方式：

```python
class AuthFactory:
    @staticmethod
    def create(environment: str) -> AuthProvider:
        if environment == "production":
            return IAMAuthProvider()
        elif environment == "development":
            return LocalAuthProvider()
        else:
            return OAuth2Provider()
```

### 2.3 RAG 引用系統（P0 新增）

標準化引用格式管理：

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

### 4.1 Session 管理（P0 優化）

```python
# 從 InMemory 遷移到 Vertex AI
session_service = VertexAiSessionService(
    project_id=PROJECT_ID,
    location=LOCATION
)
```

### 4.2 Memory 管理（P0 優化）

```python
# 使用 Vertex AI Memory Bank
memory_service = VertexAiMemoryBankService(
    corpus_id=CORPUS_ID,
    agent_engine_id=AGENT_ENGINE_ID
)
```

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

### Phase 1: 基礎強化（當前 - 2週）
- ✅ 四大專家代理基礎實作
- ⏳ P0 認證授權系統
- ⏳ P0 RAG 引用系統  
- ⏳ P0 Session/Memory 持久化

### Phase 2: 功能擴展（3-8週）
- 📋 P1 GitHub 整合
- 📋 P1 SRE 量化指標
- 📋 P1 迭代優化框架
- 📋 P1 MCP 工具箱

### Phase 3: 企業就緒（長期）
- 📋 P2 A2A 協議
- 📋 P2 多模態分析
- 📋 P2 成本優化
- 📋 P2 進階部署

## 13. 技術債務管理

### 已識別的技術債務

| 項目 | 影響 | 優先級 | 計劃 |
|------|------|--------|------|
| 測試覆蓋率不足 | 中 | P1 | 增加到 80% |
| 文檔更新滯後 | 低 | P2 | 自動化文檔生成 |

## 14. 關鍵設計決策

### 14.1 為何選擇 SequentialAgent

- **優點**：清晰的工作流程、易於調試
- **缺點**：較低的並行度
- **權衡**：SRE 工作流程本質上是順序的

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