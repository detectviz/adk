# 部署

這個入門套件使用一個穩健、可用於生產的部署策略，該策略結合了用於基礎設施即程式碼的 **Terraform** 和用於自動化建置、測試和部署的 CI/CD 管線。您可以選擇 **Google Cloud Build** 或 **GitHub Actions** 作為您的 CI/CD 執行器。

部署您的代理的建議方法是使用 `agent-starter-pack setup-cicd` 指令，該指令會自動化整個過程。

## 部署工作流程

CI/CD 管線的設計遵循了安全可靠地部署應用程式的最佳實踐。

![部署工作流程](https://storage.googleapis.com/github-repo/generative-ai/sample-apps/e2e-gen-ai-app-starter-pack/deployment_workflow.png)

**描述：**

1. **CI 管線** (例如 `.github/workflows/pr_checks.yaml` 或 `.cloudbuild/pr_checks.yaml`):
   - 在建立/更新拉取請求時觸發。
   - 執行單元和整合測試以確保程式碼品質。

2. **預備 (Staging) CD 管線** (例如 `.github/workflows/staging.yaml` 或 `.cloudbuild/staging.yaml`):
   - 在合併到 `main` 分支時觸發。
   - 建置應用程式容器並將其推送到 Artifact Registry。
   - 將新版本部署到**預備環境**。
   - 對預備環境執行自動化負載測試。

3. **生產部署** (例如 `.github/workflows/deploy-to-prod.yaml` 或 `.cloudbuild/deploy-to-prod.yaml`):
   - 在預備部署成功後觸發。
   - 在進入生產環境前需要**手動批准**。
   - 將在預備環境中測試過的相同容器映像部署到**生產環境**。

## 開發環境部署

如果您想部署一個獨立的開發環境而不安裝完整的 CI/CD 管線，您可以使用 `make setup-dev-env` 指令。

1. **設定您的開發專案：**
   ```bash
   gcloud config set project <your-dev-project-id>
   ```

2. **部署開發基礎設施：**
   此指令會執行 `deployment/terraform/dev` 中的 Terraform 設定，以配置一個開發環境。
   ```bash
   make setup-dev-env
   ```

3. **部署應用程式：**
   基礎設施準備就緒後，將您的代理部署到開發環境。
   ```bash
   make backend
   ```
   
## 使用 `setup-cicd` 自動化部署

要以一個指令流暢地部署整個 CI/CD 管線和基礎設施，請從您產生的專案根目錄執行 `setup-cicd` 指令。

```bash
uvx agent-starter-pack setup-cicd
```

此指令處理所有必要的步驟：
- **基礎設施配置：** 使用 Terraform 在您的預備和生產 Google Cloud 專案中建立和設定必要的資源。
- **CI/CD 設定：** 使用您選擇的執行器 (Google Cloud Build 或 GitHub Actions) 設定一個完整的 CI/CD 管線，包括對拉取請求和合併到 main 分支的觸發器。
- **儲存庫連接：** 將您的 GitHub 儲存庫連接到 CI/CD 提供者。

有關該指令及其選項的完整指南，請參閱 [**`setup-cicd` CLI 參考**](../cli/setup_cicd.html)。

## 必要變數

部署使用需要為您的環境設定的 Terraform 變數。這些變數定義在 `src/base_template/deployment/terraform/variables.tf` 中：

### 核心設定
- **`project_name`**：資源命名的基礎名稱 (預設：從 cookiecutter 自動產生)
- **`prod_project_id`**：用於生產部署的 Google Cloud 專案 ID
- **`staging_project_id`**：用於預備部署的 Google Cloud 專案 ID
- **`cicd_runner_project_id`**：CI/CD 管線執行的 Google Cloud 專案 ID
- **`region`**：資源的 Google Cloud 區域 (預設：`us-central1`)

### 儲存庫連接
- **`repository_name`**：您的 GitHub 儲存庫名稱
- **`repository_owner`**：GitHub 使用者名稱或組織名稱
- **`host_connection_name`**：Cloud Build 連接的名稱 (預設：自動產生)

### 服務帳戶權限
- **`cloud_run_app_roles`** / **`agentengine_sa_roles`**：應用程式服務帳戶的角色
- **`cicd_roles`**：CI/CD 執行器服務帳戶的角色
- **`cicd_sa_deployment_required_roles`**：預備/生產專案的部署角色

### CI/CD 提供者特定
對於 **Cloud Build**：
- **`github_app_installation_id`**：GitHub 應用程式安裝 ID
- **`github_pat`** / **`github_pat_secret_id`**：GitHub 個人存取權杖
- **`create_cb_connection`**：是否建立新的 Cloud Build 連接

對於 **GitHub Actions**：
- **`create_repository`**：儲存庫是否已存在

### 資料擷取 (可選)
如果啟用資料擷取：
- **`pipeline_cron_schedule`**：自動化擷取的 Cron 排程 (預設：每週)
- **`pipelines_roles`**：Vertex AI Pipelines 服務帳戶的角色

### Vector Search 設定 (可選)
如果使用 Vertex AI Vector Search：
- **`vector_search_embedding_size`**：嵌入維度 (預設：768)
- **`vector_search_approximate_neighbors_count`**：要返回的鄰居數 (預設：150)
- **`vector_search_min/max_replica_count`**：擴展設定
- **`vector_search_shard_size`**：分片大小 (預設：SHARD_SIZE_SMALL)
- **`vector_search_machine_type`**：執行個體類型 (預設：e2-standard-2)

### 日誌設定
- **`telemetry_logs_filter`**：遙測資料的日誌過濾器
- **`feedback_logs_filter`**：回饋資料的日誌過濾器

### 端到端示範影片

<a href="https://storage.googleapis.com/github-repo/generative-ai/sample-apps/e2e-gen-ai-app-starter-pack/template_deployment_demo.mp4">
  <img src="https://storage.googleapis.com/github-repo/generative-ai/sample-apps/e2e-gen-ai-app-starter-pack/preview_video.png" alt="觀看影片" width="300"/>
</a>