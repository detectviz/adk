# 建立遠端模板

本指南適用於想要建立和分享自己的遠端模板的開發者。遠端模板讓您可以將自訂的代理邏輯、依賴項和基礎設施定義打包到一個可重複使用的 Git 儲存庫中，其他人可以使用它來產生可用於生產的代理。

## 模板建立者的要求

在建立遠端模板時，您需要考慮：

### 依賴項 (`pyproject.toml`)
**對於自訂依賴項為必需：** 如果您的代理有自訂的 Python 依賴項，您**必須**在模板根目錄中包含一個 `pyproject.toml` 檔案，並列出這些依賴項。

有關 `pyproject.toml` 的結構和內容的指導，您可以參考[基礎模板的 pyproject.toml](https://github.com/GoogleCloudPlatform/agent-starter-pack/blob/main/src/base_template/pyproject.toml) 作為預期格式和常見依賴項的範例。

### 設定 (`[tool.agent-starter-pack]`)
**可選但建議：** 將此部分新增到您的 `pyproject.toml` 中，以：
- **可發現性：** 帶有此部分的模板會出現在 `uvx agent-starter-pack list` 指令中
- **客製化：** 覆寫預設行為，如基礎模板、部署目標等。
- **元資料：** 為您的模板提供清晰的名稱和描述

### 智慧預設值
由於基於您儲存庫結構的智慧預設值，即使沒有明確的設定，模板也能運作。

## 快速入門：建立您的第一個模板

讓我們建構一個簡單的遠端模板，來自訂內建的 `adk_base` 代理。

### 步驟 1：建立模板結構

遠端模板反映了一個標準的代理程式碼庫：

```
my-first-remote-template/
├── pyproject.toml           # 依賴項和設定
├── app/
│   └── agent.py             # 您的自訂代理邏輯
└── README.md                # 模板文件
```

### 步驟 2：設定依賴項和設定

建立一個 `pyproject.toml` 檔案：

```toml
[project]
name = "my-first-remote-template"
version = "0.1.0"
description = "一個會打招呼的簡單模板"
dependencies = [
    "google-adk>=1.8.0",
]

[tool.agent-starter-pack]
# 作為基礎的內建代理
base_template = "adk_base"

# 模板元資料 (可選 - 會退回到 [project] 部分)
name = "我的第一個遠端模板"
description = "一個展示自訂問候語的簡單模板"

# 覆寫基礎模板的設定
[tool.agent-starter-pack.settings]
# 此模板僅支援 'agent_engine' 部署目標
deployment_targets = ["agent_engine"]
# 可選：自訂代理檔案的目錄名稱 (預設："app")
agent_directory = "app"

```

### 步驟 3：建立您的自訂代理邏輯

在 `app/agent.py` 中建立您的自訂代理邏輯：

```python
from google.adk.agents import Agent

def get_greeting(name: str = "World") -> str:
    """從遠端模板返回友好的問候語。"""
    return f"你好，{name}！這個問候來自遠端模板。"

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    instruction="你是一個有幫助的 AI 助理。使用你的工具來回答問題。",
    tools=[get_greeting],
)
```

### 步驟 4：本地測試

在發布之前，在本地測試您的模板：

```bash
# 從 'my-first-remote-template' 的父目錄執行
uvx agent-starter-pack create my-test-agent -a local@./my-first-remote-template
```

### 步驟 5：發布和分享

初始化一個 Git 儲存庫並推送到 GitHub：

```bash
cd my-first-remote-template
git init
git add .
git commit -m "Initial remote template"
git remote add origin https://github.com/your-username/my-first-remote-template
git push -u origin main
```

現在任何人都可以使用您的模板：
```bash
uvx agent-starter-pack create my-remote-agent -a https://github.com/your-username/my-first-remote-template
```

## 模板結構詳情

### 必要檔案

**pyproject.toml (對於自訂依賴項為必需)：**
- 必須位於您儲存庫的根目錄
- 定義您代理的 Python 依賴項
- 包含可選的 `[tool.agent-starter-pack]` 設定

### 建議結構

```
my-awesome-template/
├── pyproject.toml           # 依賴項和設定
├── uv.lock                  # (建議) 鎖定的依賴項
├── app/
│   └── agent.py             # 您的自訂代理邏輯
├── tests/
│   └── test_agent.py        # 您的自訂測試
├── deployment/
│   └── terraform/
│       └── custom.tf        # 自訂基礎設施
└── README.md                # 模板文件
```

### 設定格式

```toml
[project]
name = "my-awesome-template"
description = "一個很棒的 AI 代理模板"
dependencies = ["google-adk>=1.8.0", "custom-lib"]

[tool.agent-starter-pack]
base_template = "adk_base"
name = "我的超讚模板"  # 可選：會退回到 [project].name
description = "自訂描述"  # 可選：會退回到 [project].description

[tool.agent-starter-pack.settings]
deployment_targets = ["cloud_run", "agent_engine"]
frontend_type = "adk_streamlit"
# 可選：自訂代理檔案的目錄名稱 (預設："app")
agent_directory = "app"
```

## 設定參考

### 設定的退回行為

系統會智慧地在設定來源之間進行退回：

1. **`[tool.agent-starter-pack]` 部分** (最高優先級)
2. **`[project]` 部分** (`name` 和 `description` 的退回選項)
3. **智慧預設值** (基於儲存庫結構)

**帶有退回的範例：**
```toml
[project]
name = "my-agent-template"
description = "一個用於建構聊天機器人的模板"

# 此部分是可選的 - 沒有它，會退回到 [project] + 預設值
[tool.agent-starter-pack]
base_template = "adk_base"  # 覆寫預設值
# name 和 description 將使用 [project] 的值
```

### 代理目錄設定

預設情況下，代理檔案應位於 `app/` 目錄中。您可以使用 `agent_directory` 設定來自訂此項：

```toml
[tool.agent-starter-pack.settings]
agent_directory = "my_agent"  # 自訂目錄名稱
```

這在以下情況下很有用：
- 您希望使用不同的目錄名稱以與您的專案結構保持一致
- 您正在建立具有領域特定命名的專業模板 (例如 `chatbot/`, `assistant/`, `agent/`)
- 您需要避免與使用 `app/` 於其他目的的現有程式碼庫發生衝突

**重要提示：** 當使用自訂的 `agent_directory` 時，請確保您的 Python 匯入和 Docker 設定與新的目錄名稱相符。

有關完整的設定選項，請參閱[模板設定參考](../guide/template-config-reference.md)。


## 檔案合併如何運作

當有人使用您的模板時，檔案會按以下順序複製和覆蓋 (後面的步驟會覆寫前面的步驟)：

1. **基礎模板檔案**：來自入門套件的基礎檔案
2. **部署目標檔案**：所選部署目標的檔案 (例如 `cloud_run`)
3. **前端檔案** (可選)：如果指定了 `frontend_type`
4. **基礎代理檔案**：來自 `base_template` 的應用程式邏輯 (例如 `adk_base`)
5. **遠端模板檔案** (最高優先級)：來自您儲存庫根目錄的所有檔案

這意味著您的模板檔案將覆寫來自基礎系統的任何衝突檔案。

## 管理依賴項

### Python 依賴項

**pyproject.toml (對於自訂依賴項為必需)：**
```toml
[project]
dependencies = [
    "google-adk>=1.8.0",
    "your-custom-package>=1.0.0",
    "another-dependency",
]
```

**uv.lock (強烈建議)：**
- 在變更依賴項後執行 `uv lock`
- 提交產生的 `uv.lock` 檔案以確保可重現性
- 如果存在，它能保證使用者的依賴項版本完全相同

**最佳實踐：** 始終包含一個 `uv.lock` 檔案以實現可重現的建置。

### Makefile 客製化

如果您的模板包含一個 `Makefile`，它將被智慧地合併：
- **您的指令優先**：如果一個指令同時存在於兩個 makefile 中，則保留您的
- **新增新指令**：您的 Makefile 中的任何唯一指令都會被包含
- **保留基礎指令**：來自基礎 Makefile 的必要指令會被附加

這讓您可以在保留入門套件功能的同時客製化建置過程。

## 客製化基礎設施

### Terraform 覆寫

您可以透過新增或替換 Terraform 檔案來自訂產生的代理的基礎設施：

- **新增新檔案**：將新的 `.tf` 檔案放置在適當的目錄中
- **覆寫基礎檔案**：建立同名檔案以完全替換基礎檔案

### 特定環境的設定

**生產/預備環境設定：**
```
deployment/terraform/
├── service.tf      # 替換 'staging' 和 'prod' 的基礎 service.tf
└── variables.tf    # 自訂變數
```

**開發環境設定：**
```
deployment/terraform/dev/
├── service.tf      # 僅替換 'dev' 的基礎 service.tf
└── variables.tf    # 開發特定變數
```

**範例結構：**
```
my-terraform-template/
├── pyproject.toml
└── deployment/
    └── terraform/
        ├── service.tf      # 生產/預備環境覆寫
        └── dev/
            └── service.tf  # 開發環境覆寫
```

有關完整的基礎設施客製化選項，請參閱[部署指南](../guide/deployment.md)。

## 測試您的模板

### 本地測試
```bash
# 從父目錄測試
uvx agent-starter-pack create test-project -a local@./your-template

# 使用不同選項測試
uvx agent-starter-pack create test-project -a local@./your-template --deployment-target cloud_run
```

### 驗證檢查清單

在發布之前，請驗證：
- [ ] `pyproject.toml` 包含所有必要的依賴項
- [ ] 代理程式碼位於適當的目錄結構中 (通常是 `/app` 或設定的 `agent_directory`)
- [ ] `uv lock` 能無誤地產生
- [ ] 本地測試能建立可運作的代理
- [ ] README 文件說明了用法和要求
- [ ] 設定部分啟用了可發現性

## 發布最佳實踐

### 儲存庫組織
- 使用清晰、描述性的儲存庫名稱
- 包含帶有用法範例的完整 README
- 為穩定版本標記發行版
- 記錄任何特殊要求或設定

### 版本控制
```bash
# 標記穩定版本
git tag v1.0.0
git push origin v1.0.0

# 使用者可以引用特定版本
uvx agent-starter-pack create my-agent -a github.com/user/template@v1.0.0
```

### 文件
在您的模板的 README 中包含：
- 模板的用途和使用案例
- 用法範例
- 設定選項
- 先決條件或特殊要求
- 更新的變更日誌

## 模板作者疑難排解

### 「模板可運作但未顯示在 `list` 中」
- 將 `[tool.agent-starter-pack]` 部分新增到您的 `pyproject.toml`
- `list` 指令僅顯示具有明確設定的模板

### 「模板因依賴錯誤而失敗」
- 確保您的 `pyproject.toml` 包含所有必要的依賴項
- 執行 `uv lock` 以產生 `uv.lock` 檔案以確保可重現性
- 本地測試：`uvx agent-starter-pack create test -a local@./your-template`

### 「模板使用錯誤的基礎或缺少功能」
- 檢查您的 `[tool.agent-starter-pack]` 設定
- 驗證 `base_template` 是否設定正確 (預設為 "adk_base")
- 在[模板設定參考](../guide/template-config-reference.md)中檢閱可用的設定

### 「使用者回報缺少依賴項」
- 您的 `pyproject.toml` 可能不完整
- 考慮提供更全面的依賴項清單
- 在您的 README 中包含使用說明

## 範例與靈感

### 熱門模板模式

**資料科學代理：**
```toml
[tool.agent-starter-pack]
base_template = "adk_base"
[tool.agent-starter-pack.settings]
deployment_targets = ["cloud_run"]
extra_dependencies = ["pandas", "numpy", "scikit-learn"]
```

**聊天機器人模板：**
```toml
[tool.agent-starter-pack]
base_template = "adk_base"
[tool.agent-starter-pack.settings]
frontend_type = "adk_streamlit"
deployment_targets = ["agent_engine", "cloud_run"]
```

**企業模板：**
```toml
[tool.agent-starter-pack]
base_template = "adk_base"
[tool.agent-starter-pack.settings]
session_type = "alloydb"
deployment_targets = ["cloud_run"]
include_data_ingestion = true
```

### 官方範例
- 瀏覽 [google/adk-samples](https://github.com/google/adk-samples) 以獲取可用於生產的範例
- 使用 `uvx agent-starter-pack list --adk` 查看可用的官方模板

## 後續步驟

- **從簡單開始**：從基本的代理邏輯開始，逐步增加複雜性
- **研究範例**：檢查 adk-samples 中的成功模板
- **獲取回饋**：與社群分享並根據使用情況進行迭代
- **保持更新**：關注入門套件的更新以獲取新功能和最佳實踐