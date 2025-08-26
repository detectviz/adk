# 使用遠端模板

遠端模板讓您能立即從 Git 儲存庫建立可用於生產的 AI 代理。任何 Git 儲存庫都可以作為模板使用——系統會自動處理擷取、設定以及產生您完整的代理專案。

## 運作方式

當您使用遠端模板時，系統會：

1. **擷取** 來自 Git 的模板儲存庫
2. **應用智慧預設值** 基於儲存庫結構
3. **合併** 模板檔案與基礎代理基礎設施
4. **產生** 一個完整、可用於生產的代理專案

檔案合併遵循以下優先順序：
1. 基礎模板檔案 (地基)
2. 部署目標檔案 (Cloud Run、Agent Engine 等)
3. 前端檔案 (如果指定)
4. 內建代理檔案 (adk_base 等)
5. **遠端模板檔案 (最高優先級)**

## 快速入門

使用遠端模板很簡單——只需提供任何 Git 儲存庫 URL：

```bash
# 使用任何 GitHub 儲存庫作為模板
uvx agent-starter-pack create my-agent -a https://github.com/user/my-template

# 使用簡寫表示法
uvx agent-starter-pack create my-agent -a github.com/user/my-template@main

# 使用官方 ADK 範例
uvx agent-starter-pack create my-agent -a adk@gemini-fullstack

# 使用您現有的專案
uvx agent-starter-pack create my-agent -a local@./path/to/project
```

系統會自動處理剩下的事情——擷取模板、應用智慧預設值，並產生您可用於生產的代理。

## 模板 URL 格式

### 完整的 GitHub URL
```bash
# 完整的 GitHub URL (從瀏覽器複製)
uvx agent-starter-pack create my-agent -a https://github.com/my-org/my-repo/tree/main/path-to-template
```

### 簡寫 URL
```bash
# GitHub 簡寫
uvx agent-starter-pack create my-agent -a github.com/my-org/my-repo/path-to-template

# 使用 @ 指定分支或標籤
uvx agent-starter-pack create my-agent -a github.com/my-org/my-repo/path-to-template@develop

# 也適用於 GitLab、Bitbucket 等
uvx agent-starter-pack create my-agent -a gitlab.com/my-org/my-repo/template@v1.0
```

### ADK 範例捷徑
一個方便的別名，用於來自 [google/adk-samples](https://github.com/google/adk-samples) 儲存庫的官方 Google 代理範例：

```bash
# 從 adk-samples 中的 'gemini-fullstack' 模板建立一個代理
uvx agent-starter-pack create my-agent -a adk@gemini-fullstack

# 其他熱門的 ADK 範例
uvx agent-starter-pack create my-agent -a adk@data-science
uvx agent-starter-pack create my-agent -a adk@chat-agent
```

### 您現有的專案
```bash
# 使用您現有的專案作為來源
uvx agent-starter-pack create my-test-agent -a local@./path/to/your/project
uvx agent-starter-pack create my-test-agent -a local@/absolute/path/to/project
```

## 進階用法

### 在資料夾內建立
直接在您目前的目錄中建立代理檔案，而不是建立一個新的子目錄：

```bash
# 標準：建立 ./my-agent/ 目錄
uvx agent-starter-pack create my-agent -a template-url

# 在資料夾內：在目前目錄中建立檔案
uvx agent-starter-pack create my-agent -a template-url --in-folder
```

有關 `--in-folder` 旗標的完整詳細資訊，請參閱 [create CLI 文件](../cli/create.md)。

### 增強現有專案
使用 `enhance` 指令為現有專案新增代理功能：

```bash
# 為目前專案新增代理功能
uvx agent-starter-pack enhance adk@gemini-fullstack
```

有關完整的使用詳情，請參閱 [enhance CLI 文件](../cli/enhance.md)。

### 模板選項
所有 `create` 指令選項都適用於遠端模板：

```bash
# 指定部署目標
uvx agent-starter-pack create my-agent -a template-url --deployment-target cloud_run

# 包含資料擷取
uvx agent-starter-pack create my-agent -a template-url --include-data-ingestion --datastore alloydb

# 自訂會話儲存
uvx agent-starter-pack create my-agent -a template-url --session-type alloydb

# 跳過驗證檢查
uvx agent-starter-pack create my-agent -a template-url --skip-checks
```

## 發現模板

### 列出可用模板

**內建代理：**
```bash
uvx agent-starter-pack list
```

**官方 ADK 範例：**
```bash
uvx agent-starter-pack list --adk
```

**特定儲存庫中的模板：**
```bash
uvx agent-starter-pack list --source https://github.com/my-org/my-templates
```

**注意：** 只有具有適當設定的模板才會出現在 `list` 結果中。沒有明確設定的模板仍然可以運作，但無法透過 `list` 指令發現。

### 互動式瀏覽 ADK 範例
```bash
# 啟動 ADK 範例的互動式瀏覽器
uvx agent-starter-pack create my-agent
# (在提示時選擇瀏覽 ADK 範例)
```

## 疑難排解

### 常見問題

**「找不到遠端模板或存取被拒」**
- 驗證儲存庫 URL 是否正確且可公開存取
- 對於私有儲存庫，請確保您已設定正確的 Git 憑證
- 嘗試使用完整的 GitHub URL 格式：`https://github.com/user/repo`

**「模板已產生但缺少依賴項」**
- 該模板可能沒有正確的 `pyproject.toml` - 請聯繫模板作者
- 作為解決方法，手動將缺少的依賴項新增到產生的專案中

**「指令因 Git 錯誤而失敗」**
- 確保已安裝並設定 Git
- 檢查您的網路連線
- 對於私有儲存庫，請驗證您的 SSH 金鑰或存取權杖

**「產生的專案無法執行」**
- 在產生的專案中執行 `make install` 以安裝依賴項
- 檢查專案的 README 以獲取特定的設定說明
- 確保您有必要的 Python 版本 (檢查 `pyproject.toml`)

### 取得協助

如果您遇到特定模板的問題：
1. 檢查模板儲存庫的 README 以獲取使用說明
2. 在模板儲存庫中尋找 issue 或討論
3. 透過儲存庫的 issue 追蹤器聯繫模板作者

對於一般的 Agent Starter Pack 問題：
- 造訪 [Agent Starter Pack 儲存庫](https://github.com/GoogleCloudPlatform/agent-starter-pack)
- 檢查[疑難排解指南](../guide/troubleshooting.md)

## 後續步驟

- **使用模板**：從 `adk@gemini-fullstack` 開始，以獲得一個功能齊全的範例
- **建立您自己的模板**：請參閱[建立遠端模板](./creating-remote-templates.md)
- **CLI 參考**：在 [create](../cli/create.md) 和 [enhance](../cli/enhance.md) 指令中探索所有選項