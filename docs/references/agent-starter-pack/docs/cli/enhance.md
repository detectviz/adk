# enhance

`enhance` 指令可將 agent-starter-pack 的功能新增至現有專案，而無需建立新目錄。它專為將原型就地升級為可用於生產的代理而設計。

## 使用方式

```bash
uvx agent-starter-pack enhance [TEMPLATE_PATH] [OPTIONS]
```

## 參數

- `TEMPLATE_PATH` (可選)：可以是：
  - `.` (預設) - 使用目前目錄作為模板
  - 本地目錄路徑 - 使用另一個本地目錄作為模板
  - 代理名稱 - 使用內建代理 (例如 `adk_base`)
  - 遠端模板 - 使用遠端模板 (例如 `adk@gemini-fullstack`)

## 選項

`enhance` 指令支援與 [`create`](./create.md) 相同的所有選項，外加：

### `--base-template` TEMPLATE
在增強您現有專案時，覆寫用於繼承的基礎模板。可用的基礎模板包括：
- `adk_base` - 基本代理模板 (預設)
- `langgraph_base_react` - 基於 LangGraph 的 ReAct 代理
- `agentic_rag` - 啟用 RAG 的代理模板

### 其他選項
- `--name, -n` - 專案名稱 (預設為目前目錄名稱)
- `--deployment-target, -d` - 部署目標 (`agent_engine`, `cloud_run`)
- `--include-data-ingestion, -i` - 包含資料擷取管線
- `--session-type` - 會話儲存類型
- `--auto-approve` - 跳過確認提示
- 以及所有其他 `create` 指令選項

## 範例

### 基本增強

```bash
# 使用預設模板增強目前專案
uvx agent-starter-pack enhance

# 使用特定的代理模板增強
uvx agent-starter-pack enhance adk@gemini-fullstack

# 使用自訂專案名稱增強
uvx agent-starter-pack enhance --name my-enhanced-agent
```

### 進階選項

```bash
# 使用特定的部署目標增強
uvx agent-starter-pack enhance adk@data-science --deployment-target cloud_run

# 增強資料擷取功能
uvx agent-starter-pack enhance --include-data-ingestion --datastore alloydb

# 使用自訂會話儲存增強
uvx agent-starter-pack enhance --session-type alloydb
```

### 基礎模板繼承

```bash
# 使用 LangGraph 功能增強目前專案
uvx agent-starter-pack enhance . --base-template langgraph_base_react

# 使用啟用 RAG 的基礎模板增強
uvx agent-starter-pack enhance . --base-template agentic_rag
```

## 專案結構驗證

enhance 指令會驗證您的專案結構並提供指引：

**✅ 理想結構：**
```
your-project/
├── app/
│   └── agent.py    # 您的代理程式碼
├── tests/
└── README.md
```

**⚠️ 缺少 /app 資料夾：**
如果您的專案沒有 `/app` 資料夾，該指令將：
1. 顯示有關專案結構的警告
2. 解釋預期的結構
3. 要求確認以繼續 (除非使用 `--auto-approve`)

## 運作方式

`enhance` 指令基本上是以下指令的別名：
```bash
uvx agent-starter-pack create PROJECT_NAME --agent TEMPLATE --in-folder
```

它會自動：
- 使用目前目錄名稱作為專案名稱 (除非指定了 `--name`)
- 啟用 `--in-folder` 模式以直接在目前目錄中進行模板化
- 驗證專案結構的相容性
- 應用與 `create` 指令相同的檔案合併邏輯

### 基礎模板繼承

在增強您現有的專案時 (使用 `local@.` 或 `local@/path/to/project`)，enhance 指令將：

1. **顯示目前繼承**：顯示您的專案繼承自哪個基礎模板
2. **提供指引**：顯示可用的替代基礎模板以及如何使用它們
3. **支援 CLI 覆寫**：使用 `--base-template` 覆寫 `pyproject.toml` 中指定的基礎模板

繼承層次結構如下：
```
您現有的專案
    ↓ (繼承自)
基礎模板 (adk_base, langgraph_base_react 等)
    ↓ (提供)
核心基礎設施與功能
```

## 使用案例

**從原型到生產：**
```bash
# 您在 /app/agent.py 中有一個原型代理
uvx agent-starter-pack enhance adk@production-ready
```

**新增基礎設施：**
```bash
# 新增 Terraform 和部署功能
uvx agent-starter-pack enhance --deployment-target cloud_run
```

**新增資料管線：**
```bash
# 為現有代理新增資料擷取
uvx agent-starter-pack enhance --include-data-ingestion --datastore alloydb
```

**升級代理基礎：**
```bash
# 從基本升級到進階代理模板
uvx agent-starter-pack enhance adk@gemini-fullstack

# 或變更基礎模板繼承
uvx agent-starter-pack enhance . --base-template langgraph_base_react
```

## 自動備份

`enhance` 指令在進行任何變更之前會自動建立您專案的完整備份：

- **位置：** 父目錄中的 `.backup_[dirname]_[timestamp]`
- **內容：** 您整個專案目錄的完整副本
- **時機：** 在應用任何模板檔案之前建立

## 最佳實踐

1. **檢閱備份：** 檢查備份是否已成功建立
2. **遵循結構：** 將您的代理程式碼組織在 `/app/agent.py` 中以獲得最佳相容性
3. **本地測試：** 在 CI/CD 中使用 `--auto-approve`，但先進行互動式測試
4. **檢閱變更：** 增強後，檢閱產生的檔案和設定

## 疑難排解

**「專案結構警告」**
- 將您的代理程式碼組織在 `/app` 資料夾中
- 使用 `--auto-approve` 跳過確認提示

**「增強已取消」**
- 建立一個帶有您的 `agent.py` 檔案的 `/app` 資料夾
- 重新執行指令

**「依賴衝突」**
- 檢閱並解決您 `pyproject.toml` 中的衝突
- 考慮使用虛擬環境