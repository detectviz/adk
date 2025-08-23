# 未完成任務 (TASKS.md)

本文件追蹤 `SRE Assistant` 專案尚未完成的開發任務，主要依據 `ARCHITECTURE.md` 的規範。

## 核心功能

- [ ] **完成 `SRECoordinator` 實作**
    - [ ] 整合真實的 `SREErrorBudgetManager` 和 `ResponseQualityTracker`。
    - [ ] 實作 `SafetyCallback` 和 `AuditCallback` 的完整邏輯（風險評估、審批處理、日誌記錄）。
    - [ ] 實作完整的上下文豐富 (`_enrich_context`) 和 PII 清理邏輯。

- [ ] **實作 `RemediationExpert` (修復專家)**
    - [ ] 實作 `prompts.py` 和 `agent.py`。
    - [ ] 實作真實的 `tools.py`，特別是 `LongRunningFunctionTool` 用於 K8s 操作。

- [ ] **實作 `PostmortemExpert` (覆盤專家)**
    - [ ] 實作 `prompts.py` 和 `agent.py`。
    - [ ] 實作報告生成和知識庫提取工具。

- [ ] **實作 `ConfigExpert` (配置專家)**
    - [ ] 實作 `prompts.py` 和 `agent.py`。
    - [ ] 實作與 Grafana/Terraform 整合的工具。

## 支撐模組

- [ ] **記憶體管理 (`memory.py`)**
    - [ ] 實作與 Spanner 和 Vertex RAG 的連接。
    - [ ] 建立 `SREMemorySystem`。

- [ ] **工具註冊表 (`tools.py`)**
    - [ ] 建立版本化的 `ToolRegistry`。

- [ ] **A2A 整合 (`__init__.py`)**
    - [ ] 實作 `AgentCard` 的暴露。
    - [ ] 實作消費外部代理的客戶端邏輯 (`utils/a2a_client.py`)。

- [ ] **SRE 指標與安全**
    - [ ] 實作 `slo_manager.py`。
    - [ ] 實作 `response_quality.py`。
    - [ ] 實作 `safety.py`。
    - [ ] 實作 `utils/auth.py`。

## 部署與評估

- [ ] **部署配置 (`deployment/`)**
    - [ ] 編寫 `deploy.py` 以部署到 Vertex AI。
    - [ ] 建立 `Dockerfile` 和 `cloudbuild.yaml`。

- [ ] **評估框架 (`Eval/`)**
    - [ ] 實作 `SREAssistantEvaluator`。
    - [ ] 定義 SRE 專用評估指標。
    - [ ] 建立評估資料集。

## 文件與其他

- [ ] **資料檔案 (`data/`)**
    - [ ] 建立真實的 `agent_config.json` 和 `safety_rules.json`。
    - [ ] 填充 RAG 的源文件 (`runbooks/`, `kb_articles/`)。
