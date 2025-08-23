# SRE Assistant

本專案是一個基於 Google Agent Development Kit (ADK) 的智慧 SRE 助理。其目標是根據 `ARCHITECTURE.md` 中定義的設計，實現一個能夠自動化處理 SRE 工作流（診斷、修復、覆盤、配置）的多代理系統。

## 架構概覽

本助理採用以 `SRECoordinator` (`SequentialAgent`) 為核心的多代理架構，依序調度四個專家子代理：

1.  **DiagnosticExpert**: 負責並行分析指標、日誌和追蹤，找出問題根因。
2.  **RemediationExpert**: 根據診斷結果執行修復操作。
3.  **PostmortemExpert**: 在事件解決後生成事後檢討報告。
4.  **ConfigExpert**: 根據覆盤建議優化系統配置。

詳細的設計請參閱專案根目錄下的 `ARCHITECTURE.md` 文件。

## 開發環境設置

本專案使用 `pyproject.toml` 來定義其依賴項。

### 1. 安裝依賴

建議使用虛擬環境。在專案根目錄（包含 `pyproject.toml` 的目錄）下執行以下指令來安裝所有必要的套件：

```bash
pip install .
```
或者，如果您在開發模式下安裝，可以使用：
```bash
pip install -e .
```

這將會安裝 `google-adk`, `pydantic`, `pytest` 等核心依賴。

### 2. 執行測試

我們使用 `pytest` 來進行測試。在安裝完依賴後，您可以從專案根目錄執行以下指令來運行測試套件：

```bash
pytest
```

目前的測試套件包含一個基本的整合測試 (`sre_assistant/test/test_agent.py`)，用來驗證 `SRECoordinator` 是否可以被成功初始化。

## 目前進度

本專案目前處於初期建構階段。已完成以下項目：
- 專案骨架與目錄結構。
- `DiagnosticExpert` 的基礎實作（提示、工具、代理）。
- 其餘專家代理的預留位置 (placeholder)。
- 可運行的整合測試。
- 依賴管理 (`pyproject.toml`)。
