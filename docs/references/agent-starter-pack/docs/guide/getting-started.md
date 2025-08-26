# 🚀 入門指南

本指南將快速引導您設定您的第一個代理專案。

**想要零設定嗎？** 👉 [在 Firebase Studio 中試用](https://studio.firebase.google.com/new?template=https%3A%2F%2Fgithub.com%2FGoogleCloudPlatform%2Fagent-starter-pack%2Ftree%2Fmain%2Fsrc%2Fresources%2Fidx) 或在 [Cloud Shell](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https%3A%2F%2Fgithub.com%2Feliasecchig%2Fasp-open-in-cloud-shell&cloudshell_print=open-in-cs) 中試用

### 先決條件

**Python 3.10+** | **Google Cloud SDK** [安裝指南](https://cloud.google.com/sdk/docs/install) | **Terraform** [安裝指南](https://developer.hashicorp.com/terraform/downloads) | **`uv` (可選，建議)** [安裝指南](https://docs.astral.sh/uv/getting-started/installation/)

### 1. 建立您的代理專案

您可以使用 `pip` 工作流程進行傳統設定，或使用 `uvx` 在單一指令中建立專案而無需永久安裝。請在下方選擇您偏好的方法。

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

無論您選擇哪種方法，`create` 指令都會：
*   讓您選擇一個代理模板 (例如 `adk_base`, `agentic_rag`)。
*   讓您選擇一個部署目標 (例如 `cloud_run`, `agent_engine`)。
*   產生一個完整的專案結構 (後端、可選的前端、部署基礎設施)。

**範例：**

```bash
# 您也可以傳遞旗標以跳過提示
agent-starter-pack create my-adk-agent -a adk_base -d agent_engine
```

### 2. 探索並在本機執行

現在，進入您的新專案並執行其設定指令。

```bash
cd my-awesome-agent && make install && make playground
```

在您的新專案目錄 (`my-awesome-agent`) 中，您會找到：

*   `app/`: 後端代理程式碼 (如果已設定，則為自訂目錄名稱)。
*   `deployment/`: Terraform 基礎設施程式碼。
*   `tests/`: 您的代理的單元和整合測試。
*   `notebooks/`: 用於開始評估的 Jupyter 筆記本。
*   `frontend/`: (如果適用) 與您的代理互動的 Web UI。
*   `README.md`: **用於在本機執行和部署的專案特定說明。**

➡️ **請遵循*您的新專案*的 `README.md` 中的說明以在本機執行它。**

### 後續步驟

您已準備就緒！請參閱[開發指南](/guide/development-guide)以獲取有關擴展、客製化和部署您的代理的詳細說明。

- **新增資料 (RAG):** 為知識型代理設定[資料擷取](/guide/data-ingestion)。
- **監控效能:** 探索用於生產監控的[可觀測性](/guide/observability)功能。
- **部署到生產環境:** 遵循[部署指南](/guide/deployment)將您的代理部署到 Google Cloud。