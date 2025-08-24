# 專案測試指南

本文件提供如何在本地環境中設定和執行 SRE Assistant 專案測試的詳細步驟。

## 1. 環境設定

在開始測試之前，請確保您已安裝以下工具：

- **Python 3.9+**
- **Poetry**: 本專案使用 Poetry 進行相依套件管理。如果您尚未安裝，請參考 [Poetry 官方文件](https://python-poetry.org/docs/#installation) 進行安裝。

## 2. 安裝相依套件

首先，請複製本專案的程式碼庫，並進入專案根目錄。然後，使用 Poetry 安裝所有必要的相依套件，包括開發環境所需的 `pytest`。

```bash
# 進入專案根目錄
cd path/to/sre-assistant

# 使用 Poetry 安裝相依套件
poetry install
```

此指令會建立一個虛擬環境，並將所有定義在 `pyproject.toml` 中的套件安裝進去。

## 3. 執行單元與整合測試

本專案使用 `pytest` 作為測試框架。在修復了多個導入問題和程式碼錯誤後，目前所有核心測試案例都應能成功通過。

### 執行所有測試

若要執行 `sre_assistant` 應用程式的所有測試，請在專案根目錄下執行以下指令：

```bash
poetry run pytest sre_assistant/tests/
```

**重要提示**：請務必指定 `sre_assistant/tests/` 目錄。若只執行 `poetry run pytest`，`pytest` 會試圖執行專案中所有符合 `test_*.py` 格式的檔案，包含 `docs/` 目錄下的範例專案，這將會因為缺少那些範例專案的相依套件而導致大量的測試收集錯誤。

預期輸出應顯示所有測試通過（`passed`）或被跳過（`skipped`），而不應有任何失敗（`failed`）或錯誤（`error`）。

### 執行特定測試檔案

如果您只想執行某個特定的測試檔案（例如 `test_auth.py`），可以使用以下指令：

```bash
poetry run pytest sre_assistant/tests/test_auth.py
```

這有助於在開發特定功能時，集中測試相關的程式碼。

## 4. 透過 ADK 開發人員 UI 進行手動測試

除了自動化測試外，您也可以使用 ADK 的網頁介面來啟動並手動測試代理程式。

### 啟動 ADK Web 伺服器

在專案的根目錄下，執行以下指令來啟動網頁伺服器：

```bash
poetry run adk web
```

伺服器成功啟動後，您會看到類似以下的輸出：

```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 存取與驗證

1.  **開啟瀏覽器**：前往 <http://localhost:8000>。
2.  **查看介面**：您應該能看到 ADK 的開發人員 UI。
3.  **測試代理程式**：您可以在介面中輸入查詢，與 SRE 助理代理程式進行互動，並查看其回應、狀態和所使用的工具。這對於進行端到端的流程驗證和即時偵錯非常有用。

## 5. 測試覆蓋範圍

雖然我們已經修復了現有的測試，但仍有許多方面可以增加測試案例，以提高程式碼的穩定性和可靠性，例如：

- **錯誤處理**：針對外部工具（如 Prometheus API）回傳非預期回應或超時的情境。
- **邊界條件**：測試輸入為空值、無效憑證或非預期格式資料時的處理情況。
- **設定檔驗證**：確保不同環境（開發、預備、生產）的設定檔能被正確載入和覆寫。

歡迎社群貢獻更多、更全面的測試案例。
