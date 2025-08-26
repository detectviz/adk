# `setup-cicd`

`setup-cicd` 指令是一個強大的工具，它可以自動化部署您完整的 CI/CD 基礎設施，透過單一操作即可設定您的 Google Cloud 專案和 GitHub 儲存庫。它能智慧地適應您專案的設定，支援 **Google Cloud Build** 和 **GitHub Actions** 作為 CI/CD 執行器。

**⚡️ 快速入門範例：**

入門非常簡單。在您產生的代理專案根目錄下，執行以下指令。該工具將引導您完成整個過程。

您可以使用 `pip` 工作流程進行傳統設定，或使用 `uvx` 在單一指令中建立專案而無需永久安裝。

```bash [uvx]
uvx agent-starter-pack setup-cicd
```

```bash [pip]
agent-starter-pack setup-cicd
```

*(系統將提示您輸入預備 (Staging) 和生產 (Production) 專案 ID)*

或者，您可以直接以旗標形式提供專案 ID 和其他詳細資訊：

```bash
uvx agent-starter-pack setup-cicd \
  --staging-project your-staging-project-id \
  --prod-project your-prod-project-id \
  --repository-name my-awesome-agent
```


**⚠️ 重要注意事項：**

*   **從專案根目錄執行：** 此指令必須從您產生的代理專案的根目錄 (包含 `pyproject.toml` 的目錄) 執行。
*   **生產環境使用：** 此指令旨在設定一個可用於生產的 CI/CD 管線。然而，對於高度客製化或複雜的生產環境，您可能希望在應用前檢閱 `deployment/terraform` 中產生的 Terraform 設定。

## 先決條件

1.  **必要工具：**
    *   **`uvx` 或 `agent-starter-pack`：** 該指令是入門套件 CLI 的一部分。
    *   **Terraform：** 基礎設施配置所需。
    *   **`gh` CLI (GitHub CLI)：** 該工具使用 GitHub CLI 與您的儲存庫互動。
        *   **驗證：** 您必須經過驗證。請執行 `gh auth login`。
        *   **必要範圍：** 您的 GitHub 權杖需要 **`repo`** 和 **`workflow`** 範圍，才能建立儲存庫和設定 CI/CD。如果缺少這些範圍，該工具會檢查並引導您。
    *   **`gcloud` CLI (Google Cloud SDK)：** 與 Google Cloud 互動所需。
        *   **驗證：** 您必須經過驗證。請執行 `gcloud auth application-default login`。

2.  **Google Cloud 專案：** 您至少需要兩個 Google Cloud 專案：一個用於 `staging`，一個用於 `production`。您還需要一個專案來託管 CI/CD 資源 (例如 Cloud Build、Artifact Registry、Terraform 狀態)。您可以使用 `--cicd-project` 指定此專案。如果省略，將使用生產專案來託管 CI/CD 資源。

3.  **權限：** 執行此指令的使用者或服務帳戶必須在指定的 Google Cloud 專案上擁有 `Owner` (擁有者) 角色。這是建立資源和指派 IAM 角色所必需的。

## 運作方式

`setup-cicd` 指令會自動執行以下步驟：

1.  **CI/CD 執行器偵測：** 它會檢查您的專案結構，以自動偵測您是使用 **Google Cloud Build** 還是 **GitHub Actions**。
2.  **GitHub 整合：** 它會提示您建立一個新的私有 GitHub 儲存庫或連接到現有的儲存庫。
3.  **專案 ID 確認：** 如果未透過旗標提供，它會提示輸入預備和生產專案 ID。
4.  **基礎設施設定 (Terraform)：**
    *   它會設定並應用位於 `deployment/terraform` 中的 Terraform 腳本。
    *   **對於 Google Cloud Build：** 它會設定一個到您 GitHub 儲存庫的 Cloud Build 連接，可以透過互動方式或程式化方式 (如果提供了 GitHub PAT)。
    *   **對於 GitHub Actions：** 它會設定 Workload Identity Federation (WIF)，以允許 GitHub Actions 安全地向 Google Cloud 進行驗證，而無需服務帳戶金鑰。它還會在您的 GitHub 儲存庫中建立必要的密鑰和變數。
    *   預設情況下，它會使用 Google Cloud Storage (GCS) 儲存桶設定遠端 Terraform 狀態管理。使用 `--local-state` 可選擇退出。
5.  **資源部署：** 它會執行 `terraform apply` 來在您的 Google Cloud 專案中建立所有必要的資源。
6.  **本地 Git 設定：** 它會在本地初始化一個 Git 儲存庫 (如果需要)，並將您的 GitHub 儲存庫新增為 `origin` 遠端。

## 執行指令

```bash
uvx agent-starter-pack setup-cicd \
    [--staging-project <YOUR_STAGING_PROJECT_ID>] \
    [--prod-project <YOUR_PROD_PROJECT_ID>] \
    [--cicd-project <YOUR_CICD_PROJECT_ID>] \
    [--dev-project <YOUR_DEV_PROJECT_ID>] \
    [--region <GCP_REGION>] \
    [--repository-name <GITHUB_REPO_NAME>] \
    [--repository-owner <GITHUB_USERNAME_OR_ORG>] \
    [--local-state] \
    [--auto-approve] \
    [--debug]
```

**主要選項：**

*   `--staging-project`, `--prod-project`：**必要資訊。** 您用於預備和生產環境的 Google Cloud 專案 ID。如果省略旗標，該指令將提示輸入。
*   `--cicd-project`：(可選) 用於託管 CI/CD 資源的專案 ID。如果省略，預設為生產專案 ID。
*   `--dev-project`：(可選) 用於專用開發環境的專案 ID。
*   `--region`：(可選) 資源的 GCP 區域 (預設：`us-central1`)。
*   `--repository-name`, `--repository-owner`：(可選) 您的 GitHub 儲存庫的詳細資訊。如果省略，將會提示您。
*   `--local-state`：(可選) 使用本地檔案作為 Terraform 狀態，而不是預設的 GCS 後端。
*   `--auto-approve`：(可選) 跳過所有互動式提示。
*   `--debug`：(可選) 啟用詳細日誌以進行疑難排解。

*(對於與 Google Cloud Build 的進階程式化使用，請參閱 `uvx agent-starter-pack setup-cicd --help` 中的 `--github-pat`、`--github-app-installation-id` 和 `--host-connection-name` 等選項)*

## 執行指令後

要觸發您的新 CI/CD 管線，您需要提交並推送您的程式碼：

```bash
git add .
git commit -m "Initial commit of agent starter pack"
git push -u origin main
```

推送後，您可以在您的 GitHub 儲存庫和 Google Cloud 專案中驗證已建立的資源和正在運行的管線。