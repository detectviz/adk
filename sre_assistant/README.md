# SRE Assistant (SRE 助理)

本專案是一個基於 Google Agent Development Kit (ADK) 的智慧型 SRE 助理。其目標是根據 `ARCHITECTURE.md` 文件中定義的設計，實作一個能夠自動化處理 SRE 工作流程（診斷、修復、覆盤、配置）的多代理系統。

## 架構概覽

本助理採用以 `SRECoordinator` (`SequentialAgent`) 為核心的多代理架構，依序調度四個專家子代理：

1.  **DiagnosticExpert (診斷專家)**: 負責並行分析指標、日誌和追蹤，找出問題根因。
2.  **RemediationExpert (修復專家)**: 根據診斷結果執行修復操作。
3.  **PostmortemExpert (覆盤專家)**: 在事件解決後生成事後檢討報告。
4.  **ConfigExpert (配置專家)**: 根據覆盤建議優化系統配置。

詳細的設計請參閱專案根目錄下的 `ARCHITECTURE.md` 文件。

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
- **整合測試** (`test_agent.py`): 驗證 `SRECoordinator` 的初始化與基本工作流程。
- **契約測試** (`test_contracts.py`): 使用基於屬性的測試 (Hypothesis) 來驗證 Pydantic 資料模型。
- **並發測試** (`test_concurrent_sessions.py`): 確保系統能夠處理多個並發會話而不會產生競爭條件。

## 目前狀態

本專案已完成重大的重構與功能增強。已完成的關鍵里程碑包括：
- **進階配置系統**: 一個三層配置系統（基礎、環境、環境變數），用於彈性部署。
- **穩健的記憶體管理**: 使用官方 ADK API 進行記憶體與檢索，並採用工廠模式以支援多種後端（Weaviate, PostgreSQL, Vertex AI）。
- **版本化工具註冊表**: 一個 `VersionedToolRegistry` 用於管理工具版本並確保相容性。
- **量化的 SRE 指標**: 實作了 `SREErrorBudgetManager` 以進行 SLO 追蹤。
- **增強的 A2A 協議**: 一個穩健的代理對代理 (Agent-to-Agent) 實作，支援串流與回呼。
- **全面的測試**: 測試套件已擴展，包含契約測試與並發測試。
