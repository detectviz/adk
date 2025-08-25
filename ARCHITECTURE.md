# ARCHITECTURE.md - SRE Assistant 統一架構設計

**版本**: 4.0.0
**狀態**: 草案
**維護者**: SRE Platform Team

## 1. 架構願景 (Architectural Vision)

本架構旨在將 SRE Assistant 從一個單體智能代理，演進為一個以 **Grafana 為統一指揮中心**、由**多個專業化智能代理協同工作**的**聯邦化 SRE 生態系統**。我們的目標是打造一個不僅能自動化解決當前問題，更能預測和預防未來故障的智能平台，同時為 SRE 團隊提供無縫、統一的操作體驗。

- **短期目標 (Tactical Goal)**: 透過深度整合 Grafana，提供一個集監控、告警、日誌、追蹤和 ChatOps 於一體的單一操作平台，快速提升 SRE 工作效率，減少上下文切換。
- **長期願景 (Strategic Vision)**: 建立一個開放、可擴展的代理聯邦，每個代理都是特定領域（如事件處理、成本優化、混沌工程）的專家，它們可以獨立演進、自由組合，共同應對複雜的可靠性挑戰。

## 2. 核心設計原則 (Core Design Principles)

1.  **Grafana 中心化 (Grafana-Centric)**: 以 Grafana 為所有 SRE 工作流的統一入口和介面，最大化利用其生態系統能力。
2.  **後端即服務，前端即插件 (BaaS, FaaP)**: SRE Assistant 核心能力由基於 Google ADK 的後端服務提供，使用者主要透過 Grafana 插件與之互動。
3.  **聯邦化設計 (Federated Design)**: 後端架構從長遠來看是為多代理協同工作設計的，支持關注點分離、獨立演進和可組合性。
4.  **可觀測性驅動 (Observability-Driven)**: 深度整合 LGTM (Loki, Grafana, Tempo, Mimir) 技術棧，確保系統自身的每一個決策和行動都高度可觀測。
5.  **ADK 原生擴展 (ADK-Native Extensibility)**: 充分利用 ADK 的 Provider 模型，以符合框架最佳實踐的方式實現認證、記憶體和會話管理等核心功能。
6.  **漸進式演進 (Phased Evolution)**: 優先交付價值最高的 Grafana 整合功能，並在此基礎上逐步、平滑地向聯邦化生態系統演進。

## 3. 總體架構 (Overall Architecture)

```mermaid
graph TD
    subgraph "使用者介面 (User Interface)"
        GrafanaUI[Grafana OSS/Cloud<br/>統一儀表板]
    end

    subgraph "Grafana 插件 (Grafana Plugins)"
        SREPlugin[SRE Assistant Plugin<br/>(ChatOps, Automation)]
        GrafanaNative[原生功能<br/>(Dashboards, Alerting, Explore)]
    end

    subgraph "後端服務 (Backend Services)"
        SREBackend[SRE Assistant API<br/>(Python / Google ADK)]
        Orchestrator[聯邦協調器<br/>(未來)]
    end

    subgraph "專業化代理 (Specialized Agents) - 未來"
        IncidentAgent[事件處理代理]
        PredictiveAgent[預測維護代理]
        CostAgent[成本優化代理]
        OtherAgents[...]
    end

    subgraph "數據與基礎設施 (Data & Infrastructure)"
        subgraph "統一記憶庫 (Unified Memory)"
            VectorDB[向量數據庫<br/>Weaviate]
            DocDB[文檔/關係型數據庫<br/>PostgreSQL]
            Cache[快取<br/>Redis]
        end
        subgraph "可觀測性 (Observability) - LGTM Stack"
            Loki[Loki (日誌)]
            Tempo[Tempo (追蹤)]
            Mimir[Mimir (指標)]
        end
        Auth[認證服務<br/>OAuth 2.0 Provider]
        EventBus[事件總線<br/>(未來)]
    end

    %% Connections
    User([User]) --> GrafanaUI
    GrafanaUI --> SREPlugin
    GrafanaUI --> GrafanaNative

    SREPlugin -- WebSocket/REST --> SREBackend
    GrafanaNative -- Queries --> Loki & Tempo & Mimir

    SREBackend --> VectorDB & DocDB & Cache
    SREBackend --> Auth
    SREBackend -- Telemetry --> Tempo & Loki

    %% Future Connections
    SREBackend -.-> Orchestrator
    Orchestrator -. A2A Protocol .-> IncidentAgent
    Orchestrator -. A2A Protocol .-> PredictiveAgent
    Orchestrator -. A2A Protocol .-> CostAgent
    Orchestrator -. A2A Protocol .-> OtherAgents

    IncidentAgent --> VectorDB & DocDB
    PredictiveAgent --> Mimir
```

## 4. 系統組件 (System Components)

### 4.1 介面層 (Interface Layer)
- **Grafana**: 作為整個系統的基礎平台，提供儀表板、告警、探索等原生功能。
- **SRE Assistant Grafana Plugin**: 一個自定義的 Grafana 應用插件，是人機交互的核心。
  - **職責**: 提供 ChatOps 介面、自動化工作流觸發器、與 Grafana 原生功能（如圖表嵌入、註解創建）的深度整合。
  - **技術**: TypeScript, React, Grafana Plugin SDK。

### 4.2 後端服務層 (Backend Service Layer)
- **SRE Assistant API**: 系統的核心大腦，一個無狀態的後端服務。
  - **職責**: 處理來自 Grafana 插件的請求，執行核心業務邏輯（診斷、修復、覆盤），管理工具，協調對記憶庫的訪問。
  - **技術**: Python, Google Agent Development Kit (ADK)。
- **聯邦協調器 (Orchestrator)**: (未來階段) 負責將複雜任務分解並路由到不同專業化代理的服務。在初期，其部分職責由 SRE Assistant API 承擔。

### 4.3 專業化代理層 (Specialized Agent Layer)
- (未來階段) 一系列獨立的、專注於特定領域的智能代理。例如：`IncidentHandlerAgent`, `PredictiveMaintenanceAgent`, `ChaosEngineeringAgent` 等。它們將透過 A2A 協議與協調器通訊。

### 4.4 數據與基礎設施層 (Data & Infrastructure Layer)
- **統一記憶庫 (Unified Memory)**: 為所有代理提供短期、長期、程序和語義記憶。
  - **Weaviate**: 存儲向量化數據，用於語義搜索和 RAG。
  - **PostgreSQL**: 存儲結構化數據，如事件歷史、Runbook 定義、審計日誌。
  - **Redis**: 用於高速快取和短期會話管理。
- **可觀測性 (Observability)**: 採用 Grafana LGTM Stack。
  - **Loki**: 集中化日誌聚合。
  - **Tempo**: 分散式追蹤。
  - **Mimir/Prometheus**: 指標的長期存儲與查詢。
- **認證服務 (Authentication)**: 採用基於 OAuth 2.0/OIDC 的標準化認證流程，與 Grafana 的認證機制整合。

## 5. 技術棧 (Technology Stack)

| 類別 | 技術選型 | 備註 |
|---|---|---|
| **核心框架** | Google Agent Development Kit (ADK) | Python 3.11+ |
| **前端** | Grafana Plugin SDK, TypeScript, React | 內嵌於 Grafana |
| **後端語言** | Python 3.11+ | |
| **LLM** | Gemini Pro / GPT-4 | 可配置 |
| **可觀測性** | Grafana (OSS / Cloud), Loki, Tempo, Mimir | LGTM Stack |
| **向量數據庫** | Weaviate / Vertex AI Vector Search | |
| **關係型數據庫** | PostgreSQL | |
| **快取** | Redis / InMemory | 支援記憶體快取以簡化本地開發 |
| **容器化** | Docker, Kubernetes | |
| **A2A 通訊** | gRPC + Protocol Buffers | 未來階段 |
| **認證授權** | OAuth 2.0 / OIDC / None | `None` 選項方便本地無認證測試 |

## 6. ADK 擴展性應用 (ADK Extensibility)

為了確保架構與框架的最佳實踐一致，我們將充分利用 ADK 的可擴展性介面：
- **`session_service_builder`**: 將實現自定義的會話服務，以整合 PostgreSQL（存儲任務狀態）和 Redis（快取會話上下文），提供一個高效且持久化的會話層。
- **`MemoryProvider`**: 將根據配置，橋接到底層的 Weaviate 和 PostgreSQL，為代理提供統一的記憶體訪問介面，將記憶體管理的複雜性與代理的核心邏輯分離。
- **`AuthProvider`**: 將實現一個 OAuth 2.0/OIDC 提供者，與 Grafana 的用戶身份驗證和組織架構進行對接，實現單點登錄 (SSO) 和基於角色的訪問控制 (RBAC)。

## 7. 安全架構 (Security Architecture)

安全是系統設計的基石，採用縱深防禦策略：
- **認證**: Grafana 和 SRE Assistant 後端共享同一個 OAuth 2.0/OIDC 身份提供者。
- **授權**: 利用 Grafana 的團隊和角色，在 SRE Assistant 後端實現細粒度的 RBAC。
- **通訊加密**: 所有外部通訊使用 TLS 1.3。服務間通訊（K8s 內部）將利用 Service Mesh (如 Istio) 實現 mTLS。
- **秘密管理**: 所有密鑰、API Token 等敏感資訊都將存儲在 HashiCorp Vault 或雲提供商的 Secret Manager 中。
- **數據安全**: 敏感數據在靜態時使用 AES-256 加密，並在日誌和追蹤中進行 PII 遮罩。

## 8. 實施路線圖 (Implementation Roadmap)

本架構將分階段實施，詳細的時程、里程碑和交付物，請參閱我們的官方路線圖文件：
[**ROADMAP.md**](ROADMAP.md)