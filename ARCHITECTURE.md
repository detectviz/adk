# 系統架構文檔

> **文檔職責**：定義 SRE Assistant 的系統架構、設計決策、AI Agent 架構和開發指導原則
> **版本**：1.0.0
> **最後更新**：2025-08-20

## 文檔定位

- **目標受眾**：架構師、AI工程師、開發者、技術負責人
- **更新頻率**：季度評審，重大架構變更時更新

## 文檔關係

```bash
README.md → AGENT.md → [ARCHITECTURE.md] → SPEC.md → TASKS.md
```

**相關文檔**：
- **前置閱讀**：[README.md - 專案概覽](README.md#專案概覽)
- **技術規格**：[SPEC.md - 技術實作規格](SPEC.md#技術棧與依賴)
- **協作指南**：[AGENT.md - AI協作指南](AGENT.md#ai協作原則)

---

## 系統架構設計

### 核心設計原則

1. **助理優先 (Assistant-First)**: 所有平台能力都必須透過一個統一的、對話式的 SREAssistant 暴露給使用者。使用者無需與後端系統直接互動。  
2. **專家解耦 (Decoupled Expertise)**: 平台的核心是一個輕量級的協調器。所有具體的業務邏輯（如診斷、配置）都必須被封裝在獨立、可插拔的「專家 Agent」中。  
3. **契約驅動 (Contract-Driven)**: 平台核心與 Agent 執行環境之間的通訊，必須透過一份最小化且極度穩定的 gRPC 契約來定義。  
4. **知識閉環 (Knowledge Loop)**: 平台必須內建一個核心的知識庫服務。所有 Agent 的行動和成果都應被記錄、學習，並反哺未來的決策。  
5. **開發者體驗至上 (DX First)**: Agent 的開發框架 (ADK) 必須極度簡潔，將所有底層複雜性（通訊、狀態管理）完全抽象，讓開發者能專注於創造價值。

### 系統架構

平台由三個主要部分構成：

1. **協調核心 (Orchestration Core)**:  
   * **語言**: Go  
   * **職責**: 穩定性、安全性、資源管理。作為平台的「作業系統」。  
2. **Agent 執行環境 (Agent Runtime)**:  
   * **語言**: Python  
   * **職責**: 敏捷性、智慧邏輯、快速迭代。作為 Agent 的「大腦和身體」。  
3. **通訊契約 (Communication Contract)**:  
   * **技術**: gRPC / Protobuf  
   * **職責**: 定義兩者之間清晰、高效的通訊邊界。

# 專案目錄結構

```bash
sre-assistant/
├── contracts/               # -> 獨立的、版本化的「法律」
│   └── v1/
│       └── agent_bridge.proto
│
├── orchestrator/            # -> 完全獨立的「市政廳」 (Go 專案)
│   ├── cmd/
│   ├── internal/
│   └── plugins/
│
├── adk-runtime/             # -> 完全獨立的「創新中心」 (Python 專案)
│   ├── adk/                 # 核心開發套件 (BaseAgent, ToolRegistry...)
│   ├── agents/              # 所有專家 Agent 的家
│   └── tools/               # 所有可複用工具的庫
│
├── tests/ 
├── eval/
├── deployment/
├── project.toml
├── .env.example
└── Makefile                
```

## 1. contracts/ 

- **職責單一**: 這是整個架構中**最重要**的目錄。它用 proto 檔案定義了 Go 和 Python 兩個世界之間唯一的、神聖的通訊協定。  
- **強制解耦**: 這種設計**從物理上**阻止了 Go 和 Python 之間產生任何直接的、混亂的依賴。任何跨語言的互動，都必須先在這裡進行明確的、深思熟慮的定義。這正是避免技術債的關鍵所在。


## 2. orchestrator/

- **職責單一**: 這裡只存放 Go 程式碼，負責平台的核心穩定性、資源管理和安全。  
- **可預測的擴展**: 在 go-platform/ 內部，我們可以遵循標準的 Go 專案佈局（如 cmd/, internal/, pkg/）。這種內部結構的複雜性被完美地封裝在 go-platform 這個頂層目錄中，不會影響到其他部分。

## 3. adk-runtime/ - 清晰的邊界

- **職責單一**: 這裡只存放 Python 程式碼，負責所有 Agent 的智慧邏輯和快速迭代。  
- **可預測的擴展**: 這是未來擴展最頻繁的地方，而這種簡潔的頂層結構恰好支持了其內部的有序擴展。一個理想的內部結構會是：
- 您可以看到，所有的複雜性（多個 Agent、多個 Tool）都被有組織地管理在 python-adk-runtime 這個清晰的邊界之內。

## 4. tests/, eval/, deployment/ - 專業工程實踐的體現
 
- tests/: 成為存放**端到端 (End-to-End) 整合測試**的最佳場所。這些測試的職責是驗證 orchestrator 和 adk-runtime 是否能透過 contracts 成功協同工作。  
- eval/: 預留了**模型評估 (Evaluation)** 的空間。這非常有遠見，因為當我們的 Agent 變得越來越複雜時，我們將需要一個獨立的地方來存放評估腳本、數據集和報告，以客觀地衡量 Agent 的決策品質。  
- deployment/: 將所有與部署相關的配置（如 Kubernetes YAML, Docker Compose, Terraform）集中管理，使得平台的部署和維運變得標準化和可重複。

## 5. project.toml, .env.example, Makefile - 統一的專案管理

這三個根檔案為整個專案提供了統一的管理入口：  

- project.toml (或 pyproject.toml): 標示著這是一個現代化的 Python 專案，並統一管理 Python 相關的依賴和配置。  
- .env.example: 為新加入的開發者提供了最清晰的環境變數配置指南。  
- Makefile: 作為頂層的「總指揮」，提供了如 make test, make build, make deploy 這樣簡潔的、與語言無關的命令，隱藏了底層的複雜性。


### 核心設計理念

#### Agent vs Tool 職責劃分

> **黃金準則**：Agent 負責智能決策，Tool 負責具體執行

```
Agent (決策大腦)           Tool (執行手臂)
────────────────           ──────────────
WHY - 為什麼做             HOW - 如何做
WHAT - 做什麼             WHERE - 在哪做
WHEN - 何時做             WITH - 用什麼做
```

**職責邊界**：
- **Agent 負責決策**：分析情況、制定策略、協調資源
- **Tool 負責執行**：查詢數據、調用 API、生成報告
- **Agent 不直接碰數據**：所有數據操作必須通過 Tool
- **Tool 不做決策**：只提供能力，不判斷是否應該執行

### AI Agent 分層架構

```mermaid
graph TB
    subgraph "用戶介面層"
        UI[ADK Web UI / CLI]
    end
    
    subgraph "Agent 決策層 (Python)"
        A1[SREAssistant - 統一入口]
        A2[ObservabilityExpert]
        A3[IncidentInvestigator]
        A4[PredictiveAnalyst]
        A5[AutoRemediator]
    end
    
    subgraph "Tool 執行層 (Go)"
        T1[MetricsProvider]
        T2[HealthAggregator]
        T3[Dashboard Builder]
        T4[Runbook Executor]
    end
    
    subgraph "數據層"
        D1[Prometheus]
        D2[PostgreSQL]
        D3[Redis]
        D4[Grafana]
    end
    
    UI --> A1
    A1 --> A2
    A1 --> A3
    A1 --> A4
    A1 --> A5
    
    A2 --> T1
    A3 --> T2
    A4 --> T3
    A5 --> T4
    
    T1 --> D1
    T2 --> D1
    T3 --> D4
    T4 --> D2
    
    style A1 fill:#FFD700
    style UI fill:#90EE90
```

---

## 技術架構

### 技術棧

```yaml
UI 層:
  - MVP: ADK Web (內建)
  - 後續: 自定義 Web UI (可選)

AI/ML 框架:
  - LLM: ADK 原生支援 (Gemini/Claude/GPT)
  - 備選: Ollama + 開源模型
  - Agent Framework: Google ADK
  - 向量DB: pgvector

執行層:
  - 語言: Go
  - 框架: ToolBridge + Plugin Host
  - 通訊: gRPC + Protocol Buffers

數據層:
  - 時序數據: Prometheus
  - 關係數據: PostgreSQL
  - 狀態管理: Redis
  - 可視化: Grafana
```
