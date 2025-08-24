# SRE Assistant 架構圖 (Mermaid)

## 1. 系統整體架構圖

```mermaid
graph TB
    subgraph "客戶端層"
        User[用戶]
        WebUI[Web UI]
        API[REST API]
        A2A[A2A Client]
    end

    subgraph "代理協調層"
        SRECoordinator[SRE Coordinator<br/>SequentialAgent]
        
        subgraph "診斷階段"
            DiagnosticAgent[診斷代理<br/>ParallelAgent]
            MetricsExpert[指標專家]
            LogsExpert[日誌專家]
            TracingExpert[追蹤專家]
        end
        
        subgraph "修復階段"
            RemediationAgent[修復代理<br/>LoopAgent]
            K8sExpert[K8s專家]
            ConfigExpert[配置專家]
            RollbackExpert[回滾專家]
        end
        
        subgraph "覆盤階段"
            PostmortemAgent[覆盤代理<br/>LlmAgent]
            RCAExpert[根因分析專家]
            ReportExpert[報告生成專家]
        end
        
        subgraph "配置優化階段"
            ConfigOptAgent[配置優化代理<br/>LlmAgent]
            SLOExpert[SLO專家]
            DashboardExpert[儀表板專家]
        end
    end

    subgraph "工具層"
        PromQL[PromQL查詢工具]
        LogSearch[日誌搜索工具]
        K8sTools[K8s操作工具]
        GrafanaTools[Grafana工具]
        RAGTools[RAG檢索工具]
    end

    subgraph "記憶體層"
        MemFactory[記憶體工廠]
        Weaviate[Weaviate]
        PostgreSQL[PostgreSQL]
        VertexAI[Vertex AI<br/>Vector Search]
        Redis[Redis]
    end

    subgraph "基礎設施層"
        ConfigMgr[配置管理器]
        SLOMgr[SLO管理器]
        CacheMgr[緩存管理器]
        AuditLog[審計日誌]
    end

    User --> WebUI
    WebUI --> API
    A2A --> API
    API --> SRECoordinator
    
    SRECoordinator --> DiagnosticAgent
    DiagnosticAgent --> MetricsExpert
    DiagnosticAgent --> LogsExpert
    DiagnosticAgent --> TracingExpert
    
    SRECoordinator --> RemediationAgent
    RemediationAgent --> K8sExpert
    RemediationAgent --> ConfigExpert
    RemediationAgent --> RollbackExpert
    
    SRECoordinator --> PostmortemAgent
    PostmortemAgent --> RCAExpert
    PostmortemAgent --> ReportExpert
    
    SRECoordinator --> ConfigOptAgent
    ConfigOptAgent --> SLOExpert
    ConfigOptAgent --> DashboardExpert
    
    MetricsExpert --> PromQL
    LogsExpert --> LogSearch
    K8sExpert --> K8sTools
    DashboardExpert --> GrafanaTools
    RCAExpert --> RAGTools
    
    RAGTools --> MemFactory
    MemFactory --> Weaviate
    MemFactory --> PostgreSQL
    MemFactory --> VertexAI
    MemFactory --> Redis
    
    SRECoordinator --> ConfigMgr
    SRECoordinator --> SLOMgr
    SRECoordinator --> CacheMgr
    SRECoordinator --> AuditLog

    classDef coordinator fill:#f9f,stroke:#333,stroke-width:4px
    classDef agent fill:#bbf,stroke:#333,stroke-width:2px
    classDef expert fill:#bfb,stroke:#333,stroke-width:1px
    classDef tool fill:#fbb,stroke:#333,stroke-width:1px
    classDef infra fill:#ff9,stroke:#333,stroke-width:2px
    
    class SRECoordinator coordinator
    class DiagnosticAgent,RemediationAgent,PostmortemAgent,ConfigOptAgent agent
    class MetricsExpert,LogsExpert,TracingExpert,K8sExpert,ConfigExpert,RollbackExpert,RCAExpert,ReportExpert,SLOExpert,DashboardExpert expert
    class PromQL,LogSearch,K8sTools,GrafanaTools,RAGTools tool
    class ConfigMgr,SLOMgr,CacheMgr,AuditLog infra
```

## 2. 工作流程圖

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Coordinator as SRE Coordinator
    participant Diagnostic as 診斷階段
    participant Remediation as 修復階段
    participant Postmortem as 覆盤階段
    participant Config as 配置優化
    participant HITL as HITL審批
    participant Tools as 工具層
    participant Memory as 記憶體

    User->>API: 報告問題
    API->>Coordinator: 創建事件
    
    rect rgb(200, 220, 250)
        Note over Coordinator,Diagnostic: 階段1: 診斷
        Coordinator->>Diagnostic: 啟動診斷
        Diagnostic->>Tools: 並行查詢指標/日誌
        Tools->>Memory: 檢索歷史事件
        Memory-->>Tools: 相似事件
        Tools-->>Diagnostic: 診斷結果
        Diagnostic-->>Coordinator: 根因分析
    end
    
    rect rgb(250, 220, 200)
        Note over Coordinator,Remediation: 階段2: 修復
        Coordinator->>Remediation: 執行修復
        
        alt 高風險操作
            Remediation->>HITL: 請求審批
            HITL->>User: SSE推送
            User->>HITL: 批准/拒絕
            HITL-->>Remediation: 審批結果
        end
        
        Remediation->>Tools: 執行修復操作
        
        loop 重試機制
            Tools->>Tools: 檢查狀態
            alt 失敗
                Tools->>Tools: 指數退避重試
            end
        end
        
        Tools-->>Remediation: 修復完成
        Remediation-->>Coordinator: 修復報告
    end
    
    rect rgb(200, 250, 200)
        Note over Coordinator,Postmortem: 階段3: 覆盤
        Coordinator->>Postmortem: 生成覆盤
        Postmortem->>Memory: 存儲事件詳情
        Postmortem-->>Coordinator: 覆盤報告
    end
    
    rect rgb(250, 250, 200)
        Note over Coordinator,Config: 階段4: 配置優化
        Coordinator->>Config: 優化建議
        Config->>Tools: 更新監控/SLO
        Tools-->>Config: 更新完成
        Config-->>Coordinator: 優化報告
    end
    
    Coordinator-->>API: 完整報告
    API-->>User: 返回結果
```

## 3. A2A Streaming 架構圖

```mermaid
graph LR
    subgraph "SRE Assistant (本地)"
        LocalAgent[SRE Agent]
        A2AClient[A2A Client]
        StreamHandler[Streaming Handler]
        TaskCallback[Task Callback]
    end
    
    subgraph "遠端代理"
        RemoteAgent1[異常檢測代理]
        RemoteAgent2[容量規劃代理]
        RemoteAgent3[成本優化代理]
    end
    
    subgraph "連接管理"
        ConnMgr[RemoteAgentConnections]
        OAuthMgr[OAuth Manager]
        CardResolver[Card Resolver]
    end
    
    subgraph "Streaming 協議"
        Queue[事件隊列<br/>deque maxlen=100]
        IdempotencyCheck[冪等性檢查]
        Backpressure[背壓控制]
    end
    
    LocalAgent --> A2AClient
    A2AClient --> ConnMgr
    ConnMgr --> OAuthMgr
    ConnMgr --> CardResolver
    
    ConnMgr --> RemoteAgent1
    ConnMgr --> RemoteAgent2
    ConnMgr --> RemoteAgent3
    
    RemoteAgent1 -.->|SSE| StreamHandler
    RemoteAgent2 -.->|SSE| StreamHandler
    RemoteAgent3 -.->|SSE| StreamHandler
    
    StreamHandler --> Queue
    Queue --> IdempotencyCheck
    IdempotencyCheck --> Backpressure
    Backpressure --> TaskCallback
    TaskCallback --> LocalAgent
    
    style Queue fill:#faa,stroke:#333,stroke-width:2px
    style IdempotencyCheck fill:#afa,stroke:#333,stroke-width:2px
    style Backpressure fill:#aaf,stroke:#333,stroke-width:2px
```

## 4. 配置與部署架構圖

```mermaid
graph TB
    subgraph "配置層級"
        Base[base.yaml<br/>基礎配置]
        Dev[development.yaml]
        Staging[staging.yaml]
        Prod[production.yaml]
        EnvVars[環境變數]
    end
    
    subgraph "配置管理"
        ConfigManager[ConfigManager<br/>單例模式]
        DeployConfig[DeploymentConfig<br/>Pydantic Model]
        MemoryConfig[MemoryConfig<br/>Pydantic Model]
    end
    
    subgraph "部署策略"
        DeployFactory[DeploymentFactory]
        AgentEngine[Agent Engine<br/>Strategy]
        CloudRun[Cloud Run<br/>Strategy]
        GKE[GKE<br/>Strategy]
        Local[Local<br/>Strategy]
    end
    
    subgraph "記憶體後端"
        MemFactory[MemoryBackendFactory]
        WeaviateBackend[Weaviate<br/>Backend]
        PostgresBackend[PostgreSQL<br/>Backend]
        VertexBackend[Vertex AI<br/>Backend]
        RedisBackend[Redis<br/>Backend]
    end
    
    Base --> ConfigManager
    Dev --> ConfigManager
    Staging --> ConfigManager
    Prod --> ConfigManager
    EnvVars -.->|覆蓋| ConfigManager
    
    ConfigManager --> DeployConfig
    ConfigManager --> MemoryConfig
    
    DeployConfig --> DeployFactory
    DeployFactory --> AgentEngine
    DeployFactory --> CloudRun
    DeployFactory --> GKE
    DeployFactory --> Local
    
    MemoryConfig --> MemFactory
    MemFactory --> WeaviateBackend
    MemFactory --> PostgresBackend
    MemFactory --> VertexBackend
    MemFactory --> RedisBackend
    
    style ConfigManager fill:#f9f,stroke:#333,stroke-width:4px
    style DeployFactory fill:#9ff,stroke:#333,stroke-width:2px
    style MemFactory fill:#ff9,stroke:#333,stroke-width:2px
```

## 5. SRE 量化指標管理圖

```mermaid
graph TD
    subgraph "SLO 管理"
        SLOTargets[SLO 目標<br/>99.9% 可用性]
        ErrorBudget[錯誤預算<br/>0.1%]
        BurnRate[燃燒率計算]
    end
    
    subgraph "監控窗口"
        Window1h[1小時窗口<br/>14.4x 閾值]
        Window6h[6小時窗口<br/>6.0x 閾值]
        Window72h[72小時窗口<br/>1.0x 閾值]
    end
    
    subgraph "警報級別"
        Critical[CRITICAL<br/>2小時內耗盡]
        High[HIGH<br/>1天內耗盡]
        Medium[MEDIUM<br/>1個月內耗盡]
    end
    
    subgraph "響應動作"
        AutoRemediation[自動修復]
        HITLApproval[人工審批]
        Rollback[自動回滾]
        IncidentCreate[創建事件]
    end
    
    SLOTargets --> ErrorBudget
    ErrorBudget --> BurnRate
    
    BurnRate --> Window1h
    BurnRate --> Window6h
    BurnRate --> Window72h
    
    Window1h --> Critical
    Window6h --> High
    Window72h --> Medium
    
    Critical --> HITLApproval
    Critical --> Rollback
    High --> AutoRemediation
    High --> IncidentCreate
    Medium --> IncidentCreate
    
    style Critical fill:#f44,stroke:#333,stroke-width:3px
    style High fill:#fa4,stroke:#333,stroke-width:2px
    style Medium fill:#ff4,stroke:#333,stroke-width:1px
```

## 6. 工具版本管理圖

```mermaid
graph LR
    subgraph "版本註冊"
        Registry[VersionedToolRegistry]
        ToolV1[PromQL v2.0.0]
        ToolV2[PromQL v2.1.0]
        ToolV3[K8s v3.0.0]
    end
    
    subgraph "相容性檢查"
        Matrix[相容性矩陣]
        Check[check_compatibility()]
        Fallback[降級策略]
    end
    
    subgraph "環境要求"
        Env1[Prometheus 2.35]
        Env2[Prometheus 2.40]
        K8sEnv[Kubernetes 1.25]
    end
    
    subgraph "版本選擇"
        Selector[版本選擇器]
        Default[默認版本]
        Compatible[相容版本]
    end
    
    Registry --> ToolV1
    Registry --> ToolV2
    Registry --> ToolV3
    
    ToolV1 --> Matrix
    ToolV2 --> Matrix
    ToolV3 --> Matrix
    
    Matrix --> Check
    Check --> Env1
    Check --> Env2
    Check --> K8sEnv
    
    Check --> Selector
    Selector --> Default
    Selector --> Compatible
    Selector --> Fallback
    
    style Registry fill:#9f9,stroke:#333,stroke-width:3px
    style Check fill:#99f,stroke:#333,stroke-width:2px
```

## 7. 安全與審計流程圖

```mermaid
flowchart TB
    subgraph "輸入層"
        UserInput[用戶輸入]
        A2AInput[A2A 輸入]
    end
    
    subgraph "安全層"
        PIIScrub[PII 清理]
        InputValidation[輸入驗證]
        RiskAssess[風險評估]
    end
    
    subgraph "認證授權"
        OAuth[OAuth 2.0]
        IAM[Google IAM]
        RBAC[角色權限]
    end
    
    subgraph "執行控制"
        SafetyCallback[安全回調]
        HITLGate[HITL 閘道]
        RateLimit[速率限制]
    end
    
    subgraph "審計追蹤"
        AuditCallback[審計回調]
        ImmutableLog[不可變日誌]
        DigitalSign[數字簽名]
    end
    
    UserInput --> PIIScrub
    A2AInput --> OAuth
    
    PIIScrub --> InputValidation
    OAuth --> IAM
    IAM --> RBAC
    
    InputValidation --> RiskAssess
    RBAC --> RiskAssess
    
    RiskAssess -->|低風險| SafetyCallback
    RiskAssess -->|高風險| HITLGate
    
    HITLGate -->|批准| SafetyCallback
    HITLGate -->|拒絕| AuditCallback
    
    SafetyCallback --> RateLimit
    RateLimit --> AuditCallback
    
    AuditCallback --> ImmutableLog
    ImmutableLog --> DigitalSign
    
    style HITLGate fill:#f44,stroke:#333,stroke-width:3px
    style SafetyCallback fill:#4f4,stroke:#333,stroke-width:2px
    style ImmutableLog fill:#44f,stroke:#333,stroke-width:2px
```

## 8. 測試架構圖

```mermaid
graph TB
    subgraph "測試類型"
        Unit[單元測試<br/>pytest]
        Contract[契約測試<br/>Hypothesis]
        Concurrent[並發測試<br/>50 sessions]
        Integration[整合測試]
        E2E[端到端測試]
        Perf[性能測試<br/>k6]
    end
    
    subgraph "測試覆蓋"
        Code[代碼覆蓋<br/>>80%]
        API[API 測試]
        Tools[工具測試]
        Workflow[工作流測試]
    end
    
    subgraph "測試數據"
        Fixtures[測試固件]
        Mocks[模擬對象]
        TestDB[測試數據庫]
    end
    
    subgraph "CI/CD 整合"
        PreCommit[Pre-commit<br/>hooks]
        GitHub[GitHub Actions]
        CloudBuild[Cloud Build]
    end
    
    Unit --> Code
    Contract --> API
    Concurrent --> Workflow
    Integration --> Tools
    E2E --> Workflow
    Perf --> API
    
    Code --> Fixtures
    API --> Mocks
    Tools --> TestDB
    Workflow --> TestDB
    
    PreCommit --> Unit
    PreCommit --> Contract
    GitHub --> Integration
    GitHub --> E2E
    CloudBuild --> Perf
    CloudBuild --> Concurrent
    
    style Concurrent fill:#f9f,stroke:#333,stroke-width:3px
    style Code fill:#9f9,stroke:#333,stroke-width:2px
```

## 總結

這些 Mermaid 圖表完整展示了 SRE Assistant 的：

1. **系統架構**：多層級代理協調設計
2. **工作流程**：四階段順序執行流程
3. **A2A 協議**：完整的 streaming 和連接管理
4. **配置管理**：三層配置和工廠模式
5. **SRE 指標**：錯誤預算和多窗口監控
6. **版本管理**：工具相容性檢查機制
7. **安全審計**：多層安全控制流程
8. **測試架構**：全面的測試覆蓋策略

每個圖表都反映了最新的技術實現，包括所有已解決的技術債務和最佳實踐。