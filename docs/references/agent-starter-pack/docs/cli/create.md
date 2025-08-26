# create

從內建代理或遠端模板建立新的基於 GCP 的 AI 代理專案。

## 使用方式

```bash
uvx agent-starter-pack create PROJECT_NAME [OPTIONS]
```

## 參數

- `PROJECT_NAME`: 您的新代理專案目錄的名稱，以及資源命名的基礎。
  *注意：此名稱將被轉換為小寫，且長度必須為 26 個字元或更少。*

## 模板選擇

### `--agent`, `-a` TEMPLATE
指定要用於您的代理的模板：

**內建代理：**
```bash
uvx agent-starter-pack create my-agent -a adk_base
uvx agent-starter-pack create my-agent -a chat_agent
```

**遠端模板：**
```bash
# 完整的 GitHub URL
uvx agent-starter-pack create my-agent -a https://github.com/user/repo

# 簡寫表示法
uvx agent-starter-pack create my-agent -a github.com/user/repo@main

# ADK 範例捷徑
uvx agent-starter-pack create my-agent -a adk@gemini-fullstack

# 使用您現有的專案作為來源
uvx agent-starter-pack create my-agent -a local@./path/to/project
```

如果省略，您將看到一個可用的代理互動式清單。

## 部署選項

### `--deployment-target`, `-d` TARGET
您的代理的部署目標：
- `cloud_run` - 部署到 Google Cloud Run
- `agent_engine` - 部署到 Google Cloud Agent Engine

### `--cicd-runner` RUNNER
要使用的 CI/CD 執行器：
- `google_cloud_build` - 使用 Google Cloud Build
- `github_actions` - 使用 GitHub Actions

### `--region` REGION
用於部署的 GCP 區域 (預設：`us-central1`)

## 資料與儲存選項

### `--include-data-ingestion`, `-i`
在專案中包含資料擷取管線元件。

### `--datastore`, `-ds` DATASTORE
用於資料擷取的資料儲存庫類型 (需要 `--include-data-ingestion`)：
- `vertex_ai_search`
- `vertex_ai_vector_search`
- `alloydb`

### `--session-type` TYPE
會話儲存類型 (用於 Cloud Run 部署)：
- `in_memory` - 在記憶體中儲存會話
- `alloydb` - 在 AlloyDB 中儲存會話
- `agent_engine` - 使用 Agent Engine 會話管理

## 專案建立選項

### `--output-dir`, `-o` DIRECTORY
專案的輸出目錄 (預設：目前目錄)

### `--agent-directory`, `-dir` DIRECTORY
代理目錄的名稱 (覆寫模板預設值，通常是 `app`)。這決定了您的代理程式碼檔案在專案結構中的位置。

### `--in-folder`
直接在目前目錄中建立代理檔案，而不是建立一個新的專案子目錄。

**標準行為：**
```bash
uvx agent-starter-pack create my-agent -a template
# 建立：./my-agent/[project files]
```

**資料夾內行為：**
```bash
uvx agent-starter-pack create my-agent -a template --in-folder
# 建立：./[project files] (在目前目錄中)
```

**使用案例：**
- 為現有專案新增代理功能
- 在已建立的儲存庫結構中工作
- 容器化的開發環境

**自動備份：** 使用 `--in-folder` 時，在進行任何變更之前，會自動將您的目錄完整備份為 `.backup_[dirname]_[timestamp]`。

## 自動化選項

### `--auto-approve`
跳過對 GCP 憑證和區域的互動式確認提示。

### `--skip-checks`
跳過對 GCP 驗證和 Vertex AI 連線的驗證檢查。

### `--debug`
啟用除錯日誌以進行疑難排解。

## 範例

### 基本用法

```bash
# 互動式地建立一個新專案
uvx agent-starter-pack create my-agent-project

# 使用特定的內建代理建立
uvx agent-starter-pack create my-agent -a adk_base -d cloud_run
```

### 遠端模板

```bash
# 使用 ADK 範例
uvx agent-starter-pack create my-agent -a adk@gemini-fullstack

# 使用 GitHub 儲存庫
uvx agent-starter-pack create my-agent -a https://github.com/user/my-template

# 使用帶有分支的簡寫表示法
uvx agent-starter-pack create my-agent -a github.com/user/template@develop

# 使用您現有的專案
uvx agent-starter-pack create my-agent -a local@./my-project
```

### 進階設定

```bash
# 包含具有特定資料儲存庫的資料擷取
uvx agent-starter-pack create my-rag-agent -a adk_base -i -ds alloydb -d cloud_run

# 使用自訂區域和 CI/CD 建立
uvx agent-starter-pack create my-agent -a template-url --region europe-west1 --cicd-runner github_actions

# 資料夾內建立 (新增至現有專案)
uvx agent-starter-pack create my-agent -a adk@data-science --in-folder

# 自訂代理目錄名稱
uvx agent-starter-pack create my-agent -a adk_base --agent-directory chatbot

# 為自動化跳過所有提示
uvx agent-starter-pack create my-agent -a template-url --auto-approve --skip-checks
```

### 輸出目錄

```bash
# 在特定目錄中建立
uvx agent-starter-pack create my-agent -o ./projects/

# 在目前目錄中使用資料夾內建立
uvx agent-starter-pack create existing-project -a template-url --in-folder
```

## 相關指令

- [`enhance`](./enhance.md) - 為現有專案新增代理功能 (自動使用 `--in-folder`)
- [`list`](./list.md) - 列出可用的模板和代理

## 另請參閱

- [使用遠端模板](../remote-templates/using-remote-templates.md) - 使用遠端模板的完整指南
- [建立遠端模板](../remote-templates/creating-remote-templates.md) - 建立您自己的模板的指南
