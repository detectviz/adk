# SRE Assistant 架構設計文檔

## 索引
```bash
grep -E "^## |^### " ARCHITECTURE.md
```

[執行摘要](#執行摘要)
[1. 系統架構概覽](#1-系統架構概覽)
[1.1 核心架構模式](#11-核心架構模式) ([ADK 多代理架構](docs/references/adk-docs/agents/multi-agents.md))
[1.2 目錄結構](#12-目錄結構)
[1.3 代理層級設計](#13-代理層級設計) ([ADK 工作流代理](docs/references/adk-docs/agents/workflow-agents/))
[2. 主協調器設計](#2-主協調器設計)
[2.1 協調器實作](#21-協調器實作) ([SequentialAgent](docs/references/adk-docs/agents/workflow-agents/sequential-agents.md))
[2.2 工作流控制邏輯](#22-工作流控制邏輯)
[2.3 新增：Pydantic 契約模型](#23-新增pydantic-契約模型) ([ADK 模型](docs/references/adk-docs/agents/models.md))
[3. 子代理設計](#3-子代理設計)
[3.1 診斷專家 (DiagnosticExpert)](#31-診斷專家-diagnosticexpert) ([RAG 範例](docs/references/adk-samples-agents/RAG/README.md))
[3.2 修復專家 (RemediationExpert)](#32-修復專家-remediationexpert) ([長任務工具範例](docs/references/adk-samples-agents/machine-learning-engineering/README.md))
[3.3 覆盤專家 (PostmortemExpert)](#33-覆盤專家-postmortemexpert) ([SRE Postmortem 文化](docs/references/google-sre-book/Chapter%2015%20-%20Postmortem%20CultureLearning%20from%20Failure.md))
[3.4 配置專家 (ConfigExpert)](#34-配置專家-configexpert)
[4. 記憶體管理](#4-記憶體管理)
[4.1 記憶體管理](#41-記憶體管理) ([ADK 記憶體](docs/references/adk-docs/sessions/memory.md))
[5. 工具註冊與管理](#5-工具註冊與管理)
[5.1 工具註冊與管理](#51-工具註冊與管理) ([ADK 工具](docs/references/adk-docs/tools/index.md))
[6. A2A 整合](#6-a2a-整合) ([ADK A2A](docs/references/adk-docs/a2a/index.md))
[6.1 暴露代理服務](#61-暴露代理服務) ([A2A 暴露服務](docs/references/adk-docs/a2a/quickstart-exposing.md))
[6.2 A2A Discovery 機制](#62-a2a-discovery-機制)
[6.3 消費外部代理](#63-消費外部代理) ([A2A 消費服務](docs/references/adk-docs/a2a/quickstart-consuming.md))
[7. 評估框架實現](#7-評估框架實現)
[7.1 SRE Assistant 評估系統](#71-sre_assistant-評估系統) ([ADK 評估](docs/references/adk-docs/evaluate/index.md))
[7.2 評估指標定義](#72-評估指標定義)
[8. HITL (Human-in-the-Loop) 機制](#8-hitl-human-in-the-loop-機制) ([HITL 範例](docs/references/adk-python-samples/human_in_loop/README.md))
[8.1 審批流程設計](#81-審批流程設計)
[8.2 風險評估矩陣](#82-風險評估矩陣)
[9. 資料流設計](#9-資料流設計)
[9.1 請求處理流程](#91-請求處理流程)
[9.2 Session 狀態管理](#92-session-狀態管理) ([ADK 會話](docs/references/adk-docs/sessions/session.md))
[10. 工具層設計](#10-工具層設計)
[10.1 工具分類](#101-工具分類)
[10.2 長任務工具實作](#102-長任務工具實作) ([ADK 長任務工具](docs/references/adk-docs/streaming/streaming-tools.md))
[11. 部署架構](#11-部署架構)
[11.1 Vertex AI Agent Engine 部署](#111-vertex-ai-agent-engine-部署) ([Vertex 部署](docs/references/adk-docs/deploy/agent-engine.md))
[11.2 Kubernetes 部署](#112-kubernetes-部署) ([GKE 部署](docs/references/adk-docs/deploy/gke.md))
[12. 監控與 SLO](#12-監控與-slo)
[12.1 關鍵指標](#121-關鍵指標)
[12.2 SRE 量化指標管理](#122-sre-量化指標管理) ([SRE SLO](docs/references/google-sre-book/Chapter%204%20-%20Service%20Level%20Objectives.md))
[13. 安全性設計](#13-安全性設計)
[13.1 ADK Safety Framework 和 SRE 錯誤預算整合](#131-adk-safety-framework-和-sre-錯誤預算整合) ([ADK 安全框架](docs/references/adk-docs/safety/index.md))
[13.2 認證與授權](#132-認證與授權)
[13.3 審計日誌](#133-審計日誌) ([ADK 回調](docs/references/adk-docs/callbacks/types-of-callbacks.md))
[14. 性能優化](#14-性能優化)
[14.1 智能緩存管理](#141-智能緩存管理)
[14.2 性能優化策略](#142-性能優化策略)
[15. 擴展性設計](#15-擴展性設計)
[15.1 新增專家代理](#151-新增專家代理)
[15.2 新增工具](#152-新增工具)
[16. 測試策略](#16-測試策略)
[16.1 測試層級](#161-測試層級) ([ADK 測試](docs/references/adk-docs/get-started/testing.md))
[16.2 效能基準](#162-效能基準)
[17. 發展路線圖](#17-發展路線圖)
[18. ADK 最佳實踐整合](#18-adk-最佳實踐整合)

## 執行摘要

SRE Assistant 是基於 Google Agent Development Kit (ADK) 開發的企業級智慧運維助理，採用多代理架構實現自動化診斷、修復、覆盤和配置管理。採用 **SequentialAgent** 作為主協調器，統籌管理四個專業子代理，並整合 HITL (Human-in-the-Loop)、RAG (Retrieval-Augmented Generation)、多種觀測工具，提供端到端的 SRE 工作流自動化。

系統嚴格遵循 ADK 官方 Python API 標準和最佳實踐，具備完整的類型安全、Pydantic 模型驗證和契約測試，確保與 Google Cloud 生態系統的完美整合。其核心特性包括：

- **標準化 API 設計**：利用 Pydantic 實現完整的 type hints 和 Request/Response/ToolOutput 模型。
- **企業級安全框架**：整合官方 SafetyCallback/AuditCallback，並包含 PII 清理和不可變審計日誌功能。
- **SRE 專用功能**：內建 SLOManager、ErrorBudgetTracker 和 ResponseQualityTracker。
- **A2A 協議**：支援 streaming、mTLS/JWT 認證、重試策略和流量控制。
- **持續評估系統**：擁有自動化評估管道、SRE 特定指標和多場景測試。

系統設計參考 ADK 官方文檔和樣本，包括多代理協作、工具整合和安全模式，同時深度融入 Google SRE 書籍的最佳實踐，在類型安全、SRE 指標管理和企業級功能方面達到生產就緒水準。

## 1. 系統架構概覽

### 1.1 核心架構模式

基於 ADK 的多代理架構，支援層級化設計：根代理使用 SequentialAgent 協調子代理，子代理使用 LlmAgent 實現 LLM 驅動邏輯。工具層使用 FunctionTool 和 LongRunningFunctionTool 實現，記憶體管理透過自訂 SessionService 整合 Spanner/Vertex RAG。

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
    │            │            │            │
┌──────────────────────────────────────────────────────┐
│                    Tools Layer                       │
│      PromQL | K8s | Grafana | RAG | Ingestion        │
└──────────────────────────────────────────────────────┘
    │            │            │            │
┌──────────────────────────────────────────────────────┐
│                Infrastructure Layer                  │
│      Prometheus | Kubernetes | PostgreSQL | VertexAI │
└──────────────────────────────────────────────────────┘
```

### 1.2 目錄結構

符合 ADK Python 儲存庫和樣本的結構，聚焦 code-first 開發。採用 ADK 官方推薦的模組化設計，包括專門的 callbacks、evaluation 和 A2A 整合模組。

```bash
sre_assistant/
├── __init__.py                 # 組合根代理入口和 A2A 暴露
├── agent.py                    # 定義 SequentialAgent/LoopAgent 組合
├── contracts.py                # Pydantic 契約模型（Request/Response/ToolOutput/AgentState）
├── memory.py                   # 配置 Spanner/Vertex RAG 後端（完整 MatchingEngine API）
├── artifacts.py                # RAG 文件載入邏輯
├── prompts.py                  # SRE 全域系統指令
├── tools.py                    # 共用工具函數（含版本管理和相容性檢查）
├── callbacks.py                # 官方 SafetyCallback/AuditCallback 實現（含 PII 清理）
├── safety.py                   # ADK SafetyFramework 整合（獨立微服務）
├── slo_manager.py              # SRE 錯誤預算和 SLO 管理（完整 Google SRE Book 實現）
├── response_quality.py         # ADK v1.2.1 ResponseQualityTracker 整合
│
├── sub_agents/                 # 子代理目錄 (符合 ADK 多代理最佳實踐)
│   ├── __init__.py
│   ├── diagnostic/             # 診斷專家
│   │   ├── __init__.py
│   │   ├── agent.py            # DiagnosticAgent 定義
│   │   ├── prompts.py          # 診斷提示模板
│   │   └── tools.py            # Prometheus/metrics 工具
│   ├── remediation/            # 修復專家
│   │   ├── __init__.py
│   │   ├── agent.py            # RemediationAgent 定義
│   │   ├── prompts.py          # 修復提示模板
│   │   └── tools.py            # K8s rollout 工具
│   ├── postmortem/             # 事後檢討專家
│   │   ├── __init__.py
│   │   ├── agent.py            # PostmortemAgent 定義
│   │   ├── prompts.py          # 檢討提示模板
│   │   └── tools.py            # 報告生成工具
│   └── config/                 # 配置專家
│       ├── __init__.py
│       ├── agent.py            # ConfigAgent 定義
│       ├── prompts.py          # 配置提示模板
│       └── tools.py            # Grafana/alert 工具
│
├── utils/                      # 通用工具（非特定代理）
│   ├── __init__.py
│   ├── validators.py           # 輸入驗證
│   ├── formatters.py           # 格式化工具
│   └── auth.py                 # 認證輔助 (A2A 相容)
│
├── data/                       # 配置和文件
│   ├── configs/
│   │   ├── agent_config.json
│   │   └── safety_rules.json
│   └── documents/              # RAG 源文件
│       ├── runbooks/
│       └── kb_articles/
│
├── deployment/                 # 部署配置 (ADK 部署相容)
│   ├── deploy.py               # AdkApp 部署到 Vertex AI Agent Engine
│   ├── Dockerfile              # 容器化（可選）
│   └── cloudbuild.yaml         # Cloud Build 配置
│
├── Eval/                       # 評估框架 (ADK 內建評估)
│   ├── evaluation.py           # 評估邏輯
│   ├── sre_metrics.py          # SRE 特定評估指標
│   ├── response_quality.py     # 回應品質評估
│   └── safety_evaluation.py    # 安全性評估
│
├── test/                       # 測試
│   └── test_agent.py           # 單元和整合測試
│
├── pyproject.toml              # Poetry 依賴管理 (包括 google-adk v1.2.1)
└── README.md                   # 專案文檔
```

### 1.3 代理層級設計

主協調器採用 **SequentialAgent** 模式，依序執行 SRE 標準工作流（參考 Google SRE 書籍的 Incident Response 流程）：

1. **診斷階段** → DiagnosticExpert（內嵌 ParallelAgent 同時執行多項檢查）
2. **修復階段** → RemediationExpert（使用 LoopAgent 處理重試邏輯）  
3. **覆盤階段** → PostmortemExpert
4. **配置優化** → ConfigExpert

支援動態路由和 A2A 整合，例如調用外部 ML 異常檢測代理。

## 2. 主協調器設計

### 2.1 協調器實作

主協調器 `SRECoordinator` 是整個 SRE Assistant 的核心。它被實作為一個 `SequentialAgent`，負責按順序執行 SRE 工作流的各個階段（診斷、修復、覆盤）。該代理整合了 HITL 的回調機制、Pydantic 模型驗證以及 SRE 指標追蹤，以確保工作流的可靠性和可控性。其詳細實作位於 [`sre_assistant/agent.py`](sre_assistant/agent.py)。

### 2.2 工作流控制邏輯

主協調器負責（增強版）：
- **智能路由決策**：LLM 驅動意圖分類 + SRE 指標影響評估。支援動態 A2A 路由。
- **強化狀態管理**：使用 ADK SessionService + Pydantic AgentState 模型驗證。整合 SLO/錯誤預算狀態。
- **分級錯誤處理**：`continue_on_error=True` + 基於 SRE 風險等級的自適應重試策略。
- **進階 HITL 協調**：多層審批流程（緊急/加速/標準） + SLO 違規自動升級。
- **實時監控**：整合 ResponseQualityTracker + SRE 指標即時追蹤。
- **合規性保障**：PII 清理 + 不可變審計 + 數位簽名。

### 2.3 新增：Pydantic 契約模型

此專案的所有資料契約模型均使用 Pydantic v2 進行定義，以確保類型安全和資料驗證。

完整的模型定義，請參閱原始碼檔案：[`sre_assistant/contracts.py`](sre_assistant/contracts.py)。

## 3. 子代理設計

### 3.1 診斷專家 (DiagnosticExpert)

參考 ADK Samples: RAG agent, software-bug-assistant。使用 LlmAgent 整合 RAG 和工具，具備完整類型安全和 Pydantic 驗證。

請參閱原始碼檔案：[`sre_assistant/sub_agents/diagnostic/agent.py`](sre_assistant/sub_agents/diagnostic/agent.py)。

請參閱原始碼檔案：[`sre_assistant/sub_agents/diagnostic/prompts.py`](sre_assistant/sub_agents/diagnostic/prompts.py)。

請參閱原始碼檔案：[`sre_assistant/sub_agents/diagnostic/tools.py`](sre_assistant/sub_agents/diagnostic/tools.py)。

### 3.2 修復專家 (RemediationExpert)

使用 LongRunningFunctionTool 處理長任務，符合 ADK v1.2.1 安全增強。

由於其程式碼在開發過程中經過多次修改以符合 ADK 的實際 API，詳細的、最新的實作請直接參考原始碼檔案：
- [`sre_assistant/sub_agents/remediation/agent.py`](sre_assistant/sub_agents/remediation/agent.py)
- [`sre_assistant/sub_agents/remediation/tools.py`](sre_assistant/sub_agents/remediation/tools.py)

### 3.3 覆盤專家 (PostmortemExpert)

使用 LlmAgent 生成報告，整合 TimelineGeneratorTool。

由於其程式碼在開發過程中經過多次修改以符合 ADK 的實際 API，詳細的、最新的實作請直接參考原始碼檔案：[`sre_assistant/sub_agents/postmortem/agent.py`](sre_assistant/sub_agents/postmortem/agent.py)。

### 3.4 配置專家 (ConfigExpert)

使用 FunctionTool 生成 IaC 和配置。

由於其程式碼在開發過程中經過多次修改以符合 ADK 的實際 API，詳細的、最新的實作請直接參考原始碼檔案：[`sre_assistant/sub_agents/config/agent.py`](sre_assistant/sub_agents/config/agent.py)。


## 4. 記憶體管理

記憶體管理採用工廠模式，允許根據配置動態選擇後端（如 Weaviate, PostgreSQL, Vertex AI）。此設計確保了部署的靈活性和可測試性。

核心實作位於以下檔案：
- [`sre_assistant/memory/backend_factory.py`](sre_assistant/memory/backend_factory.py): 定義了記憶體後端的統一介面和工廠。
- [`sre_assistant/memory.py`](sre_assistant/memory.py): 實現了 `SREMemorySystem`，整合了後端工廠和嵌入模型。


## 5. 工具註冊與管理

使用 ADK ToolRegistry 管理。

由於其程式碼在開發過程中經過多次修改以符合 ADK 的實際 API，詳細的、最新的實作請直接參考原始碼檔案：[`sre_assistant/tools.py`](sre_assistant/tools.py)。

由於其程式碼在開發過程中經過多次修改以符合 ADK 的實際 API，詳細的、最新的實作請直接參考原始碼檔案：[`sre_assistant/tools.py`](sre_assistant/tools.py)。

此處的程式碼已完全實現版本化工具註冊表，包括相容性檢查。

## 6. A2A 整合

符合 A2A 協議 (2025 I/O 增強)，使用代理卡片暴露服務。

### 6.1 暴露代理服務

A2A (Agent-to-Agent) 協議的暴露服務，使用 `AgentCard` 來定義代理的元數據和能力。這允許其他代理發現和調用 SRE Assistant。

由於其程式碼在開發過程中經過多次修改以符合 ADK 的實際 API，詳細的、最新的實作請直接參考原始碼檔案：[`sre_assistant/__init__.py`](sre_assistant/__init__.py)。

### 6.2 A2A Discovery 機制

A2A 服務發現機制允許代理在運行時動態尋找和註冊其他代理。此功能的核心是 `AgentCard`，它定義了代理的服務端點和能力。

完整的 A2A 協議（包括服務發現）已在以下檔案中定義和實現：
- [`sre_assistant/a2a/protocol.py`](sre_assistant/a2a/protocol.py): 定義了 `AgentCard` 和其他 A2A 資料契約。
- [`sre_assistant/utils/a2a_client.py`](sre_assistant/utils/a2a_client.py): 包含了消費遠端代理和處理連接的邏輯。

### 6.3 消費外部代理

消費外部代理使用 `RemoteAgentConnections` 來調用遠端代理（如外部 ML 異常檢測代理或安全掃描代理）。這符合 A2A 協議的客戶端部分，支援非同步調用和認證。

由於其程式碼在開發過程中經過多次修改以符合 ADK 的實際 API，詳細的、最新的實作請直接參考原始碼檔案：[`sre_assistant/utils/a2a_client.py`](sre_assistant/utils/a2a_client.py)。

## 7. 評估框架實現

### 7.1 SRE Assistant 評估系統

SRE Assistant 的評估框架旨在實現自動化的持續評估，追蹤 SRE 特定指標，並確保高品質的回應。

此框架的完整實現（包括 `SREAssistantEvaluator` 類別）已從本文件遷移至原始碼檔案，以作為單一事實來源。詳細資訊請參閱：
- [`sre_assistant/Eval/evaluation.py`](sre_assistant/Eval/evaluation.py)

### 7.2 評估指標定義

#### ADK 標準指標
| 指標類型 | 指標名稱 | 目標值 | 描述 | 參考來源 |
|---------|---------|--------|------|----------|
| 準確性 | diagnosis_accuracy | > 95% | 診斷準確率 | ADK 內建評估標準 |
| 性能 | response_time_p95 | < 30s | P95 回應時間 | ADK LatencyMetric |
| 安全性 | production_safety | 0% false_positives | 生產環境安全性 | ADK SafetyMetric |
| 成本 | api_cost_per_incident | < $2.00 | 每事件處理成本 | ADK CostMetric |

#### SRE 專用指標 (Google SRE 書籍)
| 指標類型 | 指標名稱 | 目標值 | 描述 | 參考來源 |
|---------|---------|--------|------|----------|
| 可靠性 | mttr_performance | < 15min | 平均修復時間 | Google SRE Book Ch.2 |
| SLO 合規 | slo_preservation | > 99.5% | SLO 保持率 | Google SRE Book Ch.4 |
| 預算效率 | error_budget_efficiency | > 80% | 錯誤預算使用效率 | Google SRE Book Ch.3 |
| 事後品質 | postmortem_quality | > 90% | 事後檢討質量分數 | Google SRE Book Ch.15 |

#### 響應品質指標 (ADK v1.2.1)
| 指標類型 | 指標名稱 | 目標值 | 描述 | 參考來源 |
|---------|---------|--------|------|----------|
| 事實準確性 | factual_accuracy | > 98% | 事實陳述準確性 | ADK ResponseQualityTracker |
| 幻覺檢測 | hallucination_rate | < 2% | 幻覺內容檢測率 | ADK v1.2.1 功能 |
| 最佳實踐 | sre_practices_adherence | > 95% | SRE 最佳實踐遵循度 | 自定義擴展 |

## 8. HITL (Human-in-the-Loop) 機制

### 8.1 審批流程設計

HITL (Human-in-the-Loop) 審批流程對於在高風險環境中安全地執行自動化操作至關重要。它確保了在執行關鍵變更之前，有人工監督和批准。

此功能的設計理念是，高風險操作（如在生產環境中重啟服務）會自動觸發審批請求。此請求透過即時通訊（如 SSE）推送到前端，等待操作員批准。

核心邏輯的抽象實現已從本文件遷移至相關的原始碼檔案，以作為單一事實來源。

### 8.2 風險評估矩陣

| 操作類型 | 命名空間 | 風險等級 | 需要審批 |
|---------|---------|---------|---------|
| 查詢指標 | * | LOW | 否 |
| 重啟 Pod | dev/staging | MEDIUM | 否 |
| 重啟 Pod | prod | HIGH | 是 |
| 變更配置 | prod | CRITICAL | 是 |
| 刪除資源 | * | CRITICAL | 是 |

## 9. 資料流設計

### 9.1 請求處理流程

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Runner
    participant Orchestrator
    participant Experts
    participant Tools
    participant HITL
    
    User->>API: POST /api/v1/chat
    API->>Runner: run_async(message)
    Runner->>Orchestrator: execute_workflow()
    
    loop 對每個專家
        Orchestrator->>Experts: invoke_expert()
        Experts->>Tools: execute_tool()
        
        alt 需要審批
            Tools->>HITL: request_credential()
            HITL-->>User: SSE event
            User->>HITL: approve/reject
            HITL-->>Tools: approval_result
        end
        
        Tools-->>Experts: tool_result
        Experts-->>Orchestrator: expert_result
    end
    
    Orchestrator-->>Runner: workflow_result
    Runner-->>API: final_response
    API-->>User: JSON response
```

### 9.2 Session 狀態管理

會話狀態管理的核心是維護一個表示當前工作流狀態的結構。這確保了代理在長時間運行的多步驟任務中能夠保持上下文。

其高級設計已從本文件遷移至相關的原始碼檔案，以作為單一事實來源。

## 10. 工具層設計

### 10.1 工具分類

| 類別 | 工具 | 用途 | 風險等級 |
|-----|------|------|---------|
| 觀測 | PromQLQueryTool | 查詢 Prometheus 指標 | LOW |
| 觀測 | LogAnalysisTool | 分析日誌 | LOW |
| 知識 | RAGSearchTool | 檢索知識庫 | LOW |
| 知識 | RAGIngestionTool | 新增知識 | MEDIUM |
| 執行 | K8sRolloutRestartTool | 重啟 Deployment | HIGH |
| 執行 | ScaleDeploymentTool | 調整副本數 | MEDIUM |
| 配置 | GrafanaDashboardTool | 建立儀表板 | LOW |

### 10.2 長任務工具實作

長任務工具（Long-Running Function Tool）是 ADK 的一個關鍵功能，用於處理需要較長時間才能完成的操作，例如重啟一個大型服務。

其設計理念是將任務的啟動、輪詢和完成分離。這允許代理在等待任務完成時可以執行其他操作。

核心邏輯的抽象實現已從本文件遷移至相關的原始碼檔案，以作為單一事實來源。

## 11. 部署架構

### 11.1 Vertex AI Agent Engine 部署

部署到 Vertex AI Agent Engine 是推薦的生產環境部署方式，它提供了完整的生命週期管理、自動擴縮容和與 Google Cloud 生態系統的深度整合。

部署腳本的參考實現位於：
- [`sre_assistant/deployment/deployment_factory.py`](sre_assistant/deployment/deployment_factory.py) (工廠模式，支援多種部署目標)

### 11.2 Kubernetes 部署

對於需要更高自訂性的環境，可以將代理容器化並部署到 GKE (Google Kubernetes Engine)。

部署腳本的參考實現位於：
- [`sre_assistant/deployment/deployment_factory.py`](sre_assistant/deployment/deployment_factory.py) (工廠模式，支援多種部署目標)

## 12. 監控與 SLO

### 12.1 關鍵指標

此處定義了用於監控 SRE Assistant 自身性能和可靠性的關鍵指標（SLI）。這些指標是計算 SLO 和錯誤預算的基礎。

其設定已從本文件遷移至相關的原始碼檔案，以作為單一事實來源。

### 12.2 SRE 量化指標管理

#### SLO 目標和錯誤預算

SRE 量化指標管理的核心是 `SREErrorBudgetManager`，它負責計算錯誤預算和燃燒率。

此功能的完整實現位於：
- [`sre_assistant/slo_manager.py`](sre_assistant/slo_manager.py)

#### SLO 目標表

| 指標 | 目標 | 錯誤預算 | 測量窗口 | 觸發閥值 |
|-----|------|----------|---------|----------|
| 可用性 | 99.9% | 0.1%/30天 | 30 天 | 燃烧率 > 2.0 |
| P95 延遲 | < 30s | 5%違規 | 5 分鐘 | P95 > 45s |
| 診斷成功率 | > 95% | 5%失敗 | 24 小時 | 成功率 < 90% |
| HITL 響應時間 | < 5 分鐘 | 10%超時 | 即時 | 響應 > 10分鐘 |

## 13. 安全性設計

### 13.1 ADK Safety Framework 和 SRE 錯誤預算整合

此設計將 ADK 的安全框架與 SRE 的錯誤預算概念相結合，創建一個既能防止危險操作又能適應風險的系統。

核心邏輯的抽象實現已從本文件遷移至相關的原始碼檔案，以作為單一事實來源。

### 13.2 認證與授權

統一的認證和授權服務是確保只有合法用戶和系統才能訪問代理的關鍵。

核心邏輯的抽象實現已從本文件遷移至相關的原始碼檔案，以作為單一事實來源。

### 13.3 審計日誌

審計日誌提供了所有代理活動的不可變記錄，對於安全審計和事後分析至關重要。

核心邏輯的抽象實現已從本文件遷移至相關的原始碼檔案，以作為單一事實來源。

## 14. 性能優化

### 14.1 智能緩存管理

智能緩存管理對於提高代理性能和降低外部 API 調用成本至關重要。

核心邏輯的抽象實現已從本文件遷移至相關的原始碼檔案，以作為單一事實來源。

### 14.2 性能優化策略

| 優化類型 | 策略 | 預期提升 |
|---------|------|----------|
| 查詢緩存 | 監控數據緩存 60s | 響應時間減少 70% |
| 知識緩存 | Runbook 緩存 24h | 檢索速度提升 5x |
| 連接池 | Database 連接池 | 併發性能提升 3x |
| 異步處理 | 工具調用並行化 | 總體延遲減少 50% |

## 15. 擴展性設計

### 15.1 新增專家代理

1. 在 `sre_assistant/sub_agents/` 建立新模組 (例如 `sre_assistant/sub_agents/security_expert/`)
2. 在新模組中定義 `agent.py`, `prompts.py`, `tools.py`
3. 在主協調器 (`sre_assistant/agent.py`) 中註冊新的子代理
4. 編寫對應的測試

### 15.2 新增工具

1. 在 `sre_assistant/tools.py` 或相關子代理的 `tools.py` 中實現工具函數
2. 使用 `@tool` 裝飾器或 `FunctionTool` 進行封裝
3. 在相關代理的 `tool_config` 中加入
4. 編寫單元測試

## 16. 測試策略

### 16.1 測試層級

由於其程式碼在開發過程中經過多次修改以符合 ADK 的實際 API，詳細的、最新的實作請直接參考原始碼檔案：
- [`sre_assistant/test/test_agent.py`](sre_assistant/test/test_agent.py)
- [`sre_assistant/test/test_contracts.py`](sre_assistant/test/test_contracts.py)
- [`sre_assistant/test/test_concurrent_sessions.py`](sre_assistant/test/test_concurrent_sessions.py)

### 16.2 效能基準

效能基準測試是確保代理在高負載下仍能滿足性能要求的關鍵。我們使用 k6 進行壓力測試。

壓力測試腳本的參考實現已從本文件遷移至相關的原始碼檔案，以作為單一事實來源。

## 17. 發展路線圖

### Phase 1: 基礎功能 (當前)
- ✅ 四大專家代理實作
- ✅ 基本 HITL 流程
- ✅ Prometheus/K8s 整合

### Phase 2: 進階功能 
- ⏳ 完整 A2A 整合
- ⏳ ML 異常檢測整合
- ⏳ 多租戶支援

### Phase 3: 企業功能
- 📋 自訂工作流編排
- 📋 Compliance 報告
- 📋 成本優化建議

## 18. ADK 最佳實踐整合

本系統的設計遵循 ADK 的核心最佳實踐，包括：
- **多代理協作架構**: 使用 `SequentialAgent` 作為根協調器，管理多個專業子代理，實踐了關注點分離。
- **標準化工具整合**: 採用 `FunctionTool` 和 `LongRunningFunctionTool` 來處理同步和異步操作，並透過類型提示和標準化註冊表確保一致性。
- **企業級安全框架**: 整合 `SafetyCallback` 和 `AuditCallback`，並納入 PII 清理和不可變日誌等安全措施。
- **A2A 協議整合**: 支援透過 `AgentCard` 進行服務發現，並能以 `RemoteA2aAgent` 消費外部代理，支援 streaming 和安全認證。
- **SRE 領域整合**: 深度整合 SRE 工作流模式（診斷、修復、覆盤），並透過 `SLOManager` 和 `ErrorBudgetTracker` 實現量化指標管理。
- **程式碼品質**: 廣泛使用 Pydantic 模型確保類型安全，並透過單元測試、契約測試和並發測試保證程式碼的穩定性。
- **標準化部署**: 支援透過 Vertex AI Agent Engine 和容器化（Docker/Kubernetes）進行部署，並提供相應的配置。