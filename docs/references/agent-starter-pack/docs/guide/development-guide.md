# 開發指南

本指南將引導您完成建立、開發、部署和監控您的代理專案的整個生命週期。

::: tip 我們的理念：「帶上你自己的代理 (Bring Your Own Agent)」
這個入門套件提供了 UI、基礎設施、部署和監控的腳手架。您專注於建構您獨特的代理邏輯，剩下的由我們來處理。
:::

::: details 建立您的專案
您可以使用 `pip` 工作流程進行傳統設定，或使用 `uvx` 在單一指令中建立專案而無需永久安裝。

::: code-group
```bash [pip]
# 1. 建立並啟用虛擬環境
python -m venv .venv
source .venv/bin/activate

# 2. 安裝套件
pip install agent-starter-pack

# 3. 執行 create 指令
agent-starter-pack create my-awesome-agent
```

```bash [⚡ uvx]
# 這個單一指令會下載並執行最新版本
uvx agent-starter-pack create my-awesome-agent
```
:::

## 1. 本地開發與迭代

進入您的新專案以開始開發。

```bash
cd my-awesome-agent
```

在裡面，您會找到一個完整的專案結構：

*   `app/`: 後端代理程式碼 (提示、工具、業務邏輯)。目錄名稱可透過 `--agent-directory` 參數設定。
*   `.cloudbuild/`: Google Cloud Build 的 CI/CD 管線設定 (如果您選擇 Cloud Build 作為您的 CI/CD 執行器)。
*   `.github/`: GitHub Actions 的 CI/CD 管線設定 (如果您選擇 GitHub Actions 作為您的 CI/CD 執行器)。
*   `deployment/`: Terraform 基礎設施即程式碼檔案。
*   `tests/`: 單元、整合和負載測試。
*   `notebooks/`: 用於原型設計和評估的 Jupyter 筆記本。
*   `frontend/`: (如果適用) 與您的代理互動的 Web UI。
*   `README.md`: **您所選模板的專案特定說明。**
*   `GEMINI.md`: 將此檔案與 AI 工具 (如 [Gemini CLI](https://github.com/google-gemini/gemini-cli)) 搭配使用，以詢問有關模板、ADK 概念或專案結構的問題。

您的開發循環如下所示：

1.  **原型設計：** 使用 `notebooks/` 中的筆記本快速實驗您代理的核心邏輯。這是在整合新提示或工具之前進行嘗試的理想方式。
2.  **整合：** 編輯 `app/agent.py` 和代理目錄中的其他檔案 (通常是 `app/`，但可設定)，將您的新邏輯整合到主應用程式中。
3.  **測試：** 執行互動式 UI 遊樂場來測試您的變更。它具有熱重載、聊天歷史和使用者回饋功能。

```bash
# 安裝依賴項並啟動本地遊樂場
make install && make playground
```
> 注意：`make playground` 啟動的特定 UI 遊樂場取決於您在建立過程中選擇的代理模板。

## 2. 部署到雲端

一旦您對本地測試感到滿意，就可以將您的代理部署到 Google Cloud。此過程包括兩個主要階段：首先，部署到一個用於快速迭代的實作開發環境；其次，為預備 (staging) 和生產環境建立一個正式的 CI/CD 管線。

*所有 `make` 指令都應從您的代理專案根目錄 (`my-awesome-agent`) 執行。*

### 階段 1：部署到雲端開發環境

這個初始階段是為了在雲端中配置一個非生產環境，以進行遠端測試和迭代。

**i. 設定 Google Cloud 專案**

設定 `gcloud` 以指定您的開發專案。
```bash
# 將 YOUR_DEV_PROJECT_ID 替換為您實際的 Google Cloud 專案 ID
gcloud config set project YOUR_DEV_PROJECT_ID
```

**ii. 配置雲端資源**

此指令使用 Terraform 為您的開發環境設定必要的雲端資源。

::: tip 可選步驟
建議執行此步驟以建立一個與生產環境高度相似的開發環境 (包括專用的服務帳戶和 IAM 權限)。但是，對於簡單的部署，如果您有足夠的權限，可以考慮將此步驟視為可選，並直接部署後端。
:::

```bash
make setup-dev-env
```

**iii. 部署代理後端**

建置並將您的代理後端部署到開發環境。
```bash
make backend
```

### 階段 2：使用 CI/CD 建立通往生產的路徑

在開發環境中完善您的代理後，下一階段是建立一個完全自動化的 CI/CD 管線，以實現從預備到生產的無縫部署。

#### 選項 1：自動化 CI/CD 設定

從您的代理專案根目錄 (`my-awesome-agent`) 執行：
```bash
agent-starter-pack setup-cicd
```
這個單一指令處理所有事情：
- 建立一個 GitHub 儲存庫。
- 將其連接到您選擇的 CI/CD 提供者 (Google Cloud Build 或 GitHub Actions)。
- 使用 Terraform 為您的**預備和生產環境**配置所有必要的基礎設施。
- 設定部署觸發器。

有關詳細的演練，請參閱 [**`setup-cicd` CLI 參考**](../cli/setup_cicd)。

#### 選項 2：手動 CI/CD 設定

要完全控制或與其他 Git 提供者一起使用，請參閱[手動部署設定指南](./deployment.md)。

#### 觸發您的首次部署

CI/CD 設定完成後，提交並推送您的程式碼以觸發管線。這將首先將您的代理部署到預備環境。
```bash
git add -A
git config --global user.email "you@example.com" # 如果尚未設定
git config --global user.name "Your Name"     # 如果尚未設定
git commit -m "Initial commit of agent code"
git push --set-upstream origin main
```


## 3. 監控您已部署的代理

使用整合的可觀測性工具追蹤您代理的效能。OpenTelemetry 事件會自動傳送到 Google Cloud 服務。

*   **Cloud Trace & Logging**：檢查請求流程、分析延遲並審查提示/輸出。在以下位置存取追蹤：`https://console.cloud.google.com/traces/list?project=YOUR_PROD_PROJECT_ID`
*   **BigQuery**：將追蹤和日誌資料路由到 BigQuery 以進行長期儲存和進階分析。
*   **Looker Studio 儀表板**：使用預建模板將代理效能視覺化：
    *   ADK 代理：[Looker Studio ADK 儀表板](https://lookerstudio.google.com/c/reporting/46b35167-b38b-4e44-bd37-701ef4307418/page/tEnnC)
    *   非 ADK 代理：[Looker Studio 非 ADK 儀表板](https://lookerstudio.google.com/c/reporting/fa742264-4b4b-4c56-81e6-a667dd0f853f/page/tEnnC)
    *(請記得遵循儀表板內的「設定說明」以連接您的資料來源)。*

➡️ 有關詳細資訊，請參閱[可觀測性指南](./observability.md)。

## 4. 進階客製化

進一步調整入門套件以滿足您的特定需求。

*   **RAG 資料擷取**：對於檢索增強生成 (RAG) 代理，設定資料管線以處理您的資訊並將嵌入載入到 Vertex AI Search 或 Vector Search 中。
    ➡️ 請參閱[資料擷取指南](./data-ingestion.md)。
*   **自訂 Terraform**：修改 `deployment/terraform/` 中的 Terraform 設定以滿足獨特的基礎設施需求。
    ➡️ 請參閱[部署指南](./deployment.md)。
*   **CI/CD 管線**：CI/CD 工作流程定義位於 `.github/workflows` 或 `.cloudbuild` 目錄中。您可以客製化這些 YAML 檔案以新增新步驟、變更觸發器或修改部署邏輯。
