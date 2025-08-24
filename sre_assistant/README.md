# SRE Assistant (SRE 助理)

本專案是一個基於 Google Agent Development Kit (ADK) 的智慧型 SRE 助理。其目標是根據 `ARCHITECTURE.md` 文件中定義的設計，實作一個能夠自動化處理 SRE 工作流程（診斷、修復、覆盤、配置）的多代理系統。

## 架構概覽

本助理採用以 `SREWorkflow` 為核心的**進階工作流程 (Advanced Workflow)** 架構，取代了原有的簡單循序模型。該工作流程定義了清晰的自動化階段：

1.  **並行診斷 (Parallel Diagnostics)**: 使用 `ParallelAgent` 同時分析指標、日誌和追蹤，以快速定位問題。
2.  **條件修復 (Conditional Remediation)**: 根據問題的嚴重性，動態選擇不同的修復策略，如全自動修復、需要人工審批 (HITL) 的修復等。
3.  **覆盤 (Postmortem)**: 事件解決後，自動生成事後檢討報告。
4.  **迭代優化 (Iterative Optimization)**: 使用 `LoopAgent` 持續調整系統配置，直到滿足預設的 SLO 目標。

這種基於工作流程的架構提供了更高的效率、靈活性和安全性。詳細的設計請參閱專案根目錄下的 `ARCHITECTURE.md` 文件。

## 開發環境設置

本專案使用 Poetry 進行依賴管理。

### 1. 安裝依賴

建議使用虛擬環境。在專案根目錄（`pyproject.toml` 所在的目錄），執行以下指令來安裝所有必要的套件：

```bash
poetry install
```

此指令將會安裝 `google-adk`, `pydantic`, `pytest` 等核心依賴。

### 2. 執行測試

我們使用 `pytest` 進行測試。安裝依賴後，您可以從專案根目錄執行以下指令來運行測試套件：

```bash
poetry run pytest
```

測試套件包含：
- **整合測試** (`test_agent.py`): 驗證 `SREWorkflow` 的初始化與核心工作流程。
- **認證測試** (`test_auth.py`): 驗證 `AuthManager` 和 `AuthFactory` 的功能。
- **引用測試** (`test_citation.py`): 確保 RAG 的引用能被正確格式化。
- **並發測試** (`test_concurrent_sessions.py`): 確保系統能處理多個並發會話而不會產生競爭條件。
- **契約測試** (`test_contracts.py`): 使用基於屬性的測試 (Hypothesis) 來驗證 Pydantic 資料模型。
- **會話測試** (`test_session.py`): 驗證會話狀態的持久化與讀取。
- **配置驗證** (`verify_config.py`): 一個用於檢查配置完整性的腳本。

## 目前狀態

本專案已完成 P0 階段的核心架構重構與功能開發，達成了以下關鍵里程碑：

- **工作流程架構 (Workflow Architecture)**: 核心邏輯已從簡單的循序代理重構為一個包含並行、條件和循環模式的進階工作流程，顯著提升了處理效率和靈活性。
- **認證授權系統 (Auth System)**: 內建一個基於工廠模式的強大認證授權系統，支援 IAM, OAuth2, API Key 等多種方式，並包含速率限制、審計日誌和 RBAC 功能。
- **RAG 引用系統 (RAG Citation System)**: 實作了標準化的引用格式化工具 (`SRECitationFormatter`)，確保所有 AI 生成的分析結果都有據可循。
- **持久化 Session/Memory**: 實現了基於 Firestore 的會話持久化和基於 `MemoryBackendFactory` (支援 Vertex AI) 的向量記憶體持久化。
- **進階配置系統**: 一個三層配置系統（基礎、環境、環境變數），用於彈性部署。
- **版本化工具註冊表**: 一個 `VersionedToolRegistry` 用於管理工具版本並確保相容性。
- **全面的測試**: 測試套件已擴展，包含契約測試與並發測試。
