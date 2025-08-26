# SRE Assistant - 本地開發環境設定指南 (完整版)

## 摘要

本文件旨在提供一份清晰、完整的指南，說明如何在您的本地機器上設定 SRE Assistant 專案以進行開發與測試。

本設定將建立一個包含以下服務的完整本地環境：
- **SRE Assistant**: 核心應用程式。
- **PostgreSQL**: 用於 RAG 長期記憶的資料庫。
- **Prometheus**: 用於收集指標的監控系統。
- **Grafana**: 用於將指標視覺化的儀表板。

## 1. 先決條件

在開始之前，請確保您的系統已安裝以下工具：

- **Git**: 用於版本控制。
- **Python**: 版本需為 `3.9` 或更高。
- **Poetry**: 用於管理 Python 專案依賴。([安裝指南](https://python-poetry.org/docs/#installation))
- **Docker** 與 **Docker Compose**: 用於輕鬆管理本地的所有背景服務。([安裝指南](https://docs.docker.com/get-docker/))
- **gcloud CLI (建議)**: Google Cloud 命令列工具。建議預先安裝並完成認證。
  ```bash
  gcloud auth application-default login
  ```

---

## 2. 設定步驟

請依照以下步驟進行設定：

### 步驟一：取得原始碼

首先，使用 `git` 從版本庫中複製專案：

```bash
git clone <YOUR_REPOSITORY_URL>
cd <REPOSITORY_DIRECTORY>
```

### 步驟二：啟動背景服務

專案中已包含一個 `docker-compose.yml` 檔案，它定義了所有開發所需的背景服務。您只需執行以下指令即可一次性啟動 PostgreSQL, Prometheus, 和 Grafana：

```bash
docker-compose up -d
```

- **驗證**：您可以執行 `docker ps` 來確認 `postgres`, `prometheus`, `grafana` 三個容器正在運行。
- **關閉**：當您完成開發工作時，可以使用 `docker-compose down` 來關閉並移除所有服務。

### 步驟三：安裝 Python 依賴

本專案使用 Poetry 管理依賴。執行以下指令來建立虛擬環境並安裝所有必要的套件：

```bash
poetry install
```

安裝完成後，使用 `poetry shell` 進入專案的虛擬環境。後續所有指令都應在此環境中執行。

```bash
poetry shell
```

### 步驟四：設定環境變數

為了讓應用程式在本地開發模式下正確運行並連接到 Docker 中的資料庫，您需要設定以下環境變數：

```bash
# 設定要使用的環境
export SRE_ASSISTANT_ENV=development

# 設定資料庫連線字串 (包含使用者和密碼)
export SRE_ASSISTANT_MEMORY__POSTGRES_CONNECTION_STRING="postgresql://postgres:postgres@localhost:5432/sre_dev"
```

> **註**：`MEMORY__POSTGRES_CONNECTION_STRING` 中的雙底線 `__` 是設定管理器用來解析巢狀 YAML鍵 (如 `memory.postgres_connection_string`) 的慣例。

### 步驟五：執行應用程式

一切準備就緒後，您可以使用 ADK CLI 來啟動 SRE Assistant 服務。

在專案根目錄執行：

```bash
adk run .
```

如果一切順利，您將在終端機上看到應用程式的啟動日誌，並提示服務正在 `http://0.0.0.0:8080` 上運行。

### 步驟六：驗證完整環境

1.  **SRE Assistant**: 檢查終端機日誌，確認 Uvicorn 正在 `http://0.0.0.0:8080` 運行。
2.  **Prometheus**:
    - 在瀏覽器中打開 `http://localhost:9090`。
    - 導航到 `Status -> Targets`。
    - 您應該能看到 `prometheus` 和 `sre_assistant` 兩個目標 (target) 的狀態為 `UP`。
3.  **Grafana**:
    - 在瀏覽器中打開 `http://localhost:3000`。
    - 使用預設帳號密碼登入：
      - **使用者**: `admin`
      - **密碼**: `admin`
    - 登入後，導航到 `Connections -> Data sources`，您應該能看到 `Prometheus` 已被自動設定為預設資料來源。

---

## 3. 日常開發流程

當您日常進行開發時，可以遵循以下簡化流程：

1.  **啟動環境**:
    ```bash
    # 進入專案目錄
    cd <REPOSITORY_DIRECTORY>
    # 啟動所有背景服務 (如果尚未運行)
    docker-compose up -d
    # 進入 Poetry 虛擬環境
    poetry shell
    # 設定環境變數
    export SRE_ASSISTANT_ENV=development
    export SRE_ASSISTANT_MEMORY__POSTGRES_CONNECTION_STRING="postgresql://postgres:postgres@localhost:5432/sre_dev"
    ```

2.  **執行與測試**:
    ```bash
    # 執行應用程式
    adk run .
    # (在另一個終端機) 執行測試
    poetry run pytest sre_assistant/tests/
    ```

3.  **結束工作**:
    ```bash
    # 在執行 adk 的終端機按下 Ctrl+C 停止應用程式
    # 關閉所有背景服務
    docker-compose down
    ```
