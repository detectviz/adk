# Agent Starter Pack - 程式開發代理指南

本文件為負責修改 Google Cloud Agent Starter Pack 的 AI 程式開發代理提供了必要的指導、架構見解和最佳實踐。遵循這些原則對於進行安全、一致且有效的變更是至關重要的。

## AI 代理的核心原則

1.  **保護與隔離：** 您的首要目標是精準操作。**僅**修改與使用者請求直接相關的程式碼片段。保留所有周圍的程式碼、註解和格式。不要為了做一個小小的變更而重寫整個檔案或函式。
2.  **遵循慣例：** 本專案高度依賴既定模式。在撰寫新程式碼之前，請分析周圍的檔案，以理解並複製現有的命名、模板邏輯和目錄結構慣例。
3.  **全面搜尋：** 一個變更通常需要在多個地方進行更新。在修改設定、變數或基礎設施時，您**必須**在整個儲存庫中進行搜尋，包括：
    *   `src/base_template/` (核心模板)
    *   `src/deployment_targets/` (特定環境的覆寫)
    *   `.github/` 和 `.cloudbuild/` (CI/CD 工作流程)
    *   `docs/` (使用者文件)

## 專案架構概覽

### 模板引擎：Cookiecutter + Jinja2

本入門套件使用 **Cookiecutter** 從模板生成專案腳手架，這些模板使用 **Jinja2** 模板語言進行了大量客製化。理解渲染過程是避免錯誤的關鍵。

**多階段模板處理：**

模板按特定順序處理。任何階段的失敗都會導致專案生成中斷。

1.  **Cookiecutter 變數替換：** 將 `{{cookiecutter.variable_name}}` 佔位符簡單替換為 `cookiecutter.json` 中的值。
2.  **Jinja2 邏輯執行：** 執行條件區塊 (`{% if %}`), 迴圈 (`{% for %}`) 和其他邏輯。這是最複雜且最容易出錯的階段。
3.  **檔案/目錄名稱模板化：** 渲染包含 Jinja2 區塊的檔案和目錄名稱。例如：`{% if cookiecutter.cicd_runner == 'github_actions' %}.github{% else %}unused_github{% endif %}`。

### 關鍵目錄結構

-   `src/base_template/`: 這是**核心模板**。大多數應適用於所有生成專案的變更都應從這裡開始。
-   `src/deployment_targets/`: 包含**覆寫或新增至** `base_template` 的檔案，用於特定的部署目標 (例如 `cloud_run`, `gke`, `agent_engine`)。如果一個檔案同時存在於 `base_template` 和部署目標中，通常會使用後者。
-   `agents/`: 包含預先打包、自成一體的代理範例。每個範例都有自己的 `.template/templateconfig.yaml` 來定義其特定的變數和依賴項。
-   `src/cli/commands`: 包含 CLI 命令的邏輯，例如 `create` 和 `setup-cicd`。

### CLI 命令

-   `create.py`: 處理新代理專案的建立。它協調模板處理、設定合併和部署目標選擇。
-   `setup_cicd.py`: 自動化 CI/CD 管線的設定。它與 `gcloud` 和 `gh` 互動，以設定 GitHub 儲存庫、Cloud Build 觸發器和 Terraform 後端。

### 模板處理

-   `template.py`: 位於 `src/cli/utils`，此腳本包含處理模板的核心邏輯。它複製基礎模板，覆蓋部署目標檔案，然後應用特定於代理的檔案。

## 關鍵 Jinja 模板規則

不遵守這些規則是專案生成錯誤最常見的來源。

### 1. 區塊平衡
**每個開啟的 Jinja 區塊必須有對應的關閉區塊。** 這是最關鍵的規則。

-   `{% if ... %}` 需要 `{% endif %}`
-   `{% for ... %}` 需要 `{% endfor %}`
-   `{% raw %}` 需要 `{% endraw %}`

**正確：**
```jinja
{% if cookiecutter.deployment_target == 'cloud_run' %}
  # Cloud Run 特定內容
{% endif %}
```

### 2. 變數使用
區分替換和邏輯：

-   **替換 (在檔案內容中):** 使用雙大括號：`{{ cookiecutter.project_name }}`
-   **邏輯 (在 `if`/`for` 區塊中):** 直接使用變數：`{% if cookiecutter.use_alloydb %}`

### 3. 空白控制
Jinja 對空白很敏感。使用連字號來控制換行符並防止在渲染的檔案中出現不必要的空行。

-   `{%-` 移除區塊前的空白。
-   `-%}` 移除區塊後的空白。

**範例：**
```jinja
{%- if cookiecutter.some_option %}
option = true
{%- endif %}
```

## Terraform 最佳實踐

### 統一的服務帳戶 (`app_sa`)
本專案在所有部署目標中使用單一、統一的應用程式服務帳戶 (`app_sa`)，以簡化 IAM 管理。

-   **不要**建立特定於目標的服務帳戶 (例如 `cloud_run_sa`)。
-   在 `app_sa_roles` 中定義此帳戶的角色。
-   在所有 Terraform 和 CI/CD 檔案中一致地引用此帳戶。

### 資源引用
對 Terraform 資源使用一致且清晰的命名。在引用資源時，尤其是那些有條件或使用 `for_each` 建立的資源，請確保引用也正確地鍵入。

**範例：**
```hcl
# 建立
resource "google_service_account" "app_sa" {
  for_each   = local.deploy_project_ids # 例如 {"staging" = "...", "prod" = "..."}
  account_id = "${var.project_name}-app"
  # ...
}

# 正確引用
# 在用於預備環境的 Cloud Run 模組中
service_account = google_service_account.app_sa["staging"].email
```

## CI/CD 整合 (GitHub Actions & Cloud Build)

本專案維護平行的 CI/CD 實作。**任何對 CI/CD 邏輯的變更都必須同時應用於兩者。**

-   **GitHub Actions:** 在 `.github/workflows/` 中設定。使用 `${{ vars.VAR_NAME }}` 表示儲存庫變數。
-   **Google Cloud Build:** 在 `.cloudbuild/` 中設定。使用 `${_VAR_NAME}` 表示替換變數。

在新增新變數或密鑰時，請確保在管理它們的 Terraform 腳本中為兩個系統都正確設定 (例如，`github_actions_variable` 資源和 Cloud Build 觸發器替換)。

## 進階模板系統模式

### 四層架構
模板處理遵循此層次結構 (後面的層會覆寫前面的層)：
1. **基礎模板** (`src/base_template/`) - 適用於所有專案
2. **部署目標** (`src/deployment_targets/`) - 環境覆寫
3. **前端類型** (`src/frontends/`) - UI 特定檔案
4. **代理模板** (`agents/*/`) - 個別代理邏輯

**規則**：始終將變更放在正確的層中。檢查部署目標是否需要相應的更新。

### 模板處理流程
1. 從 `cookiecutter.json` 解析變數
2. 檔案複製 (基礎 → 覆蓋)
3. 內容的 Jinja2 渲染
4. 檔案/目錄名稱渲染

### 跨檔案依賴
變更通常需要協調更新：
- **設定**: `templateconfig.yaml` → `cookiecutter.json` → 渲染後的模板
- **CI/CD**: `.github/workflows/` ↔ `.cloudbuild/` (必須保持同步)
- **基礎設施**: 基礎 terraform → 部署目標覆寫

### 條件邏輯模式
```jinja
{%- if cookiecutter.agent_name == "live_api" %}
# 代理特定邏輯
{%- elif cookiecutter.deployment_target == "cloud_run" %}
# 部署特定邏輯
{%- endif %}
```

### 測試策略
跨多個維度測試變更：
- 代理類型 (live_api, adk_base 等)
- 部署目標 (cloud_run, agent_engine)
- 功能組合 (data_ingestion, frontend_type)

### 常見陷阱
- **硬式編碼的 URL**: 對前端連線使用相對路徑
- **缺少條件式**: 將代理特定程式碼包在適當的 `{% if %}` 區塊中
- **依賴衝突**: 某些代理缺少某些額外功能 (例如 live_api + lint)

## 檔案修改檢查清單

-   [ ] **Jinja 語法：** 所有 `{% if %}` 和 `{% for %}` 區塊是否都已正確關閉？
-   [ ] **變數一致性：** `cookiecutter.` 變數拼寫是否正確？
-   [ ] **跨目標影響：** 基礎模板變更是否已對照部署目標進行檢查？
-   [ ] **CI/CD 一致性：** 變更是否已同時應用於 GitHub Actions 和 Cloud Build？
-   [ ] **多代理測試：** 是否已使用不同的代理類型和設定進行測試？

### 關鍵工具

-   **`uv` for Python：** 用於依賴管理和 CLI 執行的主要工具
