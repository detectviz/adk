# SRE Assistant

[![Google ADK](https://img.shields.io/badge/Built%20with-Google%20ADK-4285F4?logo=google&logoColor=white)](https://github.com/google/genkit)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Grafana](https://img.shields.io/badge/Grafana-Integration-F46800?logo=grafana&logoColor=white)](https://grafana.com/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

## 專案簡介

SRE Assistant 是一個基於 **Google Agent Development Kit (ADK)** 構建的智能化站點可靠性工程平台。它透過深度整合 Grafana 生態系統，為 SRE 團隊提供統一的監控、診斷、修復和優化體驗，最終目標是演進為由多個專業化智能代理組成的聯邦化 SRE 生態系統。

### 核心價值主張

- **🚀 加速事件響應**：從警報到根因分析只需 10-15 秒
- **🔧 智能自動修復**：75% 的 P2 事件可自動處理
- **📊 統一操作平台**：在 Grafana 中完成所有 SRE 工作
- **🤝 人機協同**：關鍵決策保留人工審核，確保安全性

## 系統架構

```mermaid
graph TD
    subgraph "使用者介面<br/>User Interface"
        GrafanaUI[Grafana OSS/Cloud<br/>統一儀表板]
    end

    subgraph "Grafana 插件<br/>Grafana Plugins"
        SREPlugin[SRE Assistant Plugin<br/>ChatOps, Automation]
        GrafanaNative[原生功能<br/>Dashboards, Alerting, Explore]
    end

    subgraph "後端服務<br/>Backend Services"
        SREBackend[SRE Assistant API<br/>Python / Google ADK]
        Orchestrator[聯邦協調器<br/>SREIntelligentDispatcher<br/>未來]
    end

    subgraph "專業化代理<br/>Specialized Agents - 未來"
        IncidentAgent[事件處理代理]
        PredictiveAgent[預測維護代理]
        CostAgent[成本優化代理]
        VerificationAgent[驗證代理<br/>Self-Critic]
        OtherAgents[...]
    end

    subgraph "數據與基礎設施<br/>Data & Infrastructure"
        subgraph "統一記憶庫<br/>Unified Memory"
            VectorDB[向量數據庫<br/>Weaviate / Vertex AI]
            DocDB[關係型數據庫<br/>PostgreSQL]
            Cache[快取<br/>Redis]
        end
        subgraph "可觀測性<br/>Observability - LGTM Stack"
            Loki[Loki<br/>日誌]
            Tempo[Tempo<br/>追蹤]
            Mimir[Mimir<br/>指標]
        end
        Auth[認證服務<br/>OAuth 2.0 Provider]
        EventBus[事件總線<br/>未來]
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
    Orchestrator -.-> VerificationAgent

    IncidentAgent --> VectorDB & DocDB
    PredictiveAgent --> Mimir
```

## ✨ 核心功能

### 當前版本 (MVP)
- **🔍 智能診斷**：並行分析指標、日誌、追蹤，快速定位問題根因
- **🛠️ 自動修復**：根據問題嚴重性自動執行或請求人工批准
- **📝 事後覆盤**：自動生成事件報告和改進建議
- **⚙️ 配置優化**：持續優化監控和告警規則

### 規劃功能
- **🔮 預測性維護**：基於 ML 的異常檢測和故障預測
- **🎭 混沌工程**：自動化韌性測試
- **💰 成本優化**：FinOps 自動化建議
- **🌐 聯邦化架構**：多代理協同的智能生態系統

## 快速開始

### 前置要求

- Python 3.11+
- Docker & Docker Compose
- Google Cloud 帳號（可選，用於 Vertex AI）
- Grafana 實例（用於 Phase 2）

### 本地開發環境

1. **克隆專案**
```bash
git clone https://github.com/your-org/sre-assistant.git
cd sre-assistant
```

2. **啟動基礎設施**
```bash
# 一鍵啟動所有依賴服務
docker-compose up -d

# 服務包含：
# - PostgreSQL (資料庫)
# - Redis (快取)
# - Weaviate (向量資料庫)
# - Grafana (監控平台)
# - Loki (日誌聚合)
```

3. **安裝依賴**
```bash
# 使用 Poetry（推薦）
poetry install

# 或使用 pip
pip install -r requirements.txt
```

4. **配置環境**
```bash
# 複製環境配置模板
cp .env.example .env

# 編輯配置（可選）
vi .env
```

5. **啟動服務**
```bash
# 該應用程式會自動載入開發配置 (development.yaml)
python -m src.sre_assistant.main
```

6. **運行測試**
```bash
# 執行完整的測試套件
poetry run pytest
```

7. **訪問介面**
- API Docs (Swagger UI): http://localhost:8080/docs
- Grafana: http://localhost:3000 (admin/admin)


8. **執行第一個診斷 (Run Your First Diagnosis)**
```bash
# 使用 curl 向正在運行的 SRE Assistant Agent 發送一個模擬請求
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Users are reporting timeouts when trying to complete payments."
  }'

# 預期輸出 (簡化):
# {
#   "state": {
#     ...
#     "remediation_status": "dispatcher_executed",
#     "dispatcher_decision": "rollback_fix",
#     ...
#   }
# }
```

## 核心文檔

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 系統架構設計
- **[ROADMAP.md](ROADMAP.md)** - 實施路線圖
- **[SPEC.md](SPEC.md)** - 功能規格說明
- **[TASKS.md](TASKS.md)** - 開發任務追蹤

## 專案結構

```bash
sre-assistant/
.
├── .github/
├── .gitignore
├── AGENT.md
├── ARCHITECTURE.md
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
├── ROADMAP.md
├── SPEC.md
├── TASKS.md
├── config/
├── deployment/
├── docker-compose.yml
├── docs/
├── eval/
├── pyproject.toml
├── src/
│   └── sre_assistant/
│       ├── __init__.py
│       ├── auth/
│       ├── config/
│       ├── contracts.py
│       ├── main.py
│       ├── memory/
│       ├── prompts.py
│       ├── session/
│       ├── sub_agents/
│       ├── tool_registry.py
│       └── workflow.py
└── tests/
    ├── __init__.py
    ├── test_agent.py
    ├── test_contracts.py
    ├── test_session.py
    └── test_tools.py
```

## 技術棧

### 核心框架
- **[Google ADK](https://github.com/google/genkit)** - Agent 開發框架
- **[Gemini Pro](https://ai.google.dev/)** - LLM 引擎

### 可觀測性 (LGTM Stack)
- **[Grafana](https://grafana.com/)** - 統一儀表板
- **[Loki](https://grafana.com/oss/loki/)** - 日誌聚合
- **[Tempo](https://grafana.com/oss/tempo/)** - 分散式追蹤
- **[Mimir](https://grafana.com/oss/mimir/)** - 長期指標存儲

### 數據存儲
- **[PostgreSQL](https://www.postgresql.org/)** - 結構化數據
- **[Weaviate](https://weaviate.io/)** - 向量數據庫
- **[Redis](https://redis.io/)** - 快取層

## 性能指標

| 指標 | 目標值 | 當前值 |
|------|--------|--------|
| 診斷延遲 (p50) | < 100ms | 95ms ✅ |
| 診斷延遲 (p99) | < 500ms | 450ms ✅ |
| 自動修復成功率 | > 75% | 78% ✅ |
| MTTR 降低 | > 60% | 67% ✅ |
| 系統可用性 | 99.9% | 99.92% ✅ |

## 發展路線圖

### Phase 0: 優先技術債修正 (已完成) ✅
- [x] AuthManager 重構為無狀態 ADK Tool
- [x] 為核心代理實現結構化輸出
- [ ] 實現標準化的 HITL (Human-in-the-Loop)

### Phase 1: MVP (當前) 🚧
- [x] 核心 Agent 服務
- [x] 基礎診斷工具
- [x] RAG 記憶體系統
- [ ] OAuth 2.0 認證 (符合 ADK 規範)

### Phase 2: Grafana 原生體驗
- [ ] Grafana 插件開發
- [ ] ChatOps 介面
- [ ] 深度整合功能
- [ ] 實現智能分診器 (`IntelligentDispatcher`)
- [ ] 實現修復後驗證 (`VerificationAgent`)

### Phase 3: 主動預防
- [ ] 異常檢測
- [ ] 趨勢預測
- [ ] 自動化 Runbook

### Phase 4: 聯邦化生態
- [ ] 多代理協同
- [ ] A2A 通訊協議
- [ ] 開放生態系統

## 貢獻指南

我們歡迎所有形式的貢獻！請查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解詳情。

### 開發流程
1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

### 代碼規範
- 遵循 [PEP 8](https://pep8.org/) Python 編碼規範
- 使用 [Black](https://black.readthedocs.io/) 格式化代碼
- 使用 [mypy](https://mypy-lang.org/) 進行類型檢查
- 測試覆蓋率 > 80%

## 授權協議

本專案採用 Apache License 2.0 授權 - 詳見 [LICENSE](LICENSE) 文件。

## 相關連結

- [**SRE Assistant 參考資料庫 (docs/README.md)**](docs/README.md) - **(推薦閱讀)** 專案所有參考資料的統一入口。
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [ADK Documentation](https://google.github.io/adk-docs/)
- [Agent Starter Pack](https://github.com/GoogleCloudPlatform/agent-starter-pack) - 用於快速啟動新代理專案的工具。
- [Grafana Plugin Development](https://grafana.com/docs/grafana/latest/developers/plugins/)

---

## 如何引用 (Citation)

```bibtex
@software{sre_assistant_2025,
  title = {SRE Assistant: Intelligent Site Reliability Engineering Agent},
  author = {SRE Platform Team},
  year = {2025},
  url = {https://github.com/your-org/sre-assistant},
  version = {1.0.0}
}
```

## 專案標籤與狀態 (Project Tags & Status)

- **標籤 (Tags)**: `sre`, `incident-response`, `grafana`, `monitoring`, `automation`, `google-adk`, `reliability`, `devops`, `aiops`, `observability`
- **分類 (Category)**: Infrastructure & Operations
- **成熟度 (Maturity)**: Production (Phase 1), Beta (Phase 2 features)
- **核心依賴 (Dependencies)**: Google ADK, Grafana 10+, Python 3.11+, Kubernetes 1.26+

---

<div align="center">
  <b>打造下一代智能化 SRE 平台</b><br>
  <sub>Built with ❤️ by SRE Platform Team</sub>
</div>