# 🚀 Agent Starter Pack (代理啟動套件)

![Version](https://img.shields.io/pypi/v/agent-starter-pack?color=blue) [![1-Minute Video Overview](https://img.shields.io/badge/1--Minute%20Overview-gray)](https://youtu.be/jHt-ZVD660g) [![Docs](https://img.shields.io/badge/Documentation-gray)](https://googlecloudplatform.github.io/agent-starter-pack/) <a href="https://studio.firebase.google.com/new?template=https%3A%2F%2Fgithub.com%2FGoogleCloudPlatform%2Fagent-starter-pack%2Ftree%2Fmain%2Fsrc%2Fresources%2Fidx">
  <picture>
    <source
      media="(prefers-color-scheme: dark)"
      srcset="https://cdn.firebasestudio.dev/btn/try_light_20.svg">
    <source
      media="(prefers-color-scheme: light)"
      srcset="https://cdn.firebasestudio.dev/btn/try_dark_20.svg">
    <img
      height="20"
      alt="Try in Firebase Studio"
      src="https://cdn.firebasestudio.dev/btn/try_blue_20.svg">
  </picture>
</a> [![Launch in Cloud Shell](https://img.shields.io/badge/Launch-in_Cloud_Shell-white)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https%3A%2F%2Fgithub.com%2Feliasecchig%2Fasp-open-in-cloud-shell&cloudshell_print=open-in-cs) ![Stars](https://img.shields.io/github/stars/GoogleCloudPlatform/agent-starter-pack?color=yellow)


`agent-starter-pack` 是一個 Python 套件，提供了一系列專為 Google Cloud 設計、可用於生產環境的生成式 AI 代理 (Generative AI Agent) 模板。<br>
它透過提供一個全面、可用於生產的解決方案，解決了建構和部署生成式 AI 代理時常見的挑戰（如部署與維運、評估、客製化、可觀測性），從而加速開發過程。

| ⚡️ 啟動 | 🧪 實驗 | ✅ 部署 | 🛠️ 客製化 |
|---|---|---|---|
| [預建的代理模板](./agents/) (ReAct, RAG, 多代理 (multi-agent), Live API)。 | [Vertex AI 評估](https://cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview) 和互動式遊樂場。 | 在 [Cloud Run](https://cloud.google.com/run) 或 [Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) 上具備[監控、可觀測性](https://googlecloudplatform.github.io/agent-starter-pack/guide/observability)和 [CI/CD](https://googlecloudplatform.github.io/agent-starter-pack/guide/deployment) 的生產就緒基礎架構。 | 根據您的需求擴展和客製化模板。 🆕 現已整合 [Gemini CLI](https://github.com/google-gemini/gemini-cli) |

---
 
## ⚡ 1 分鐘快速入門

準備好建構您的 AI 代理了嗎？只需執行此命令：

```bash
# 建立並啟用 Python 虛擬環境
python -m venv .venv && source .venv/bin/activate

# 安裝 agent starter pack
pip install --upgrade agent-starter-pack

# 建立一個新的代理專案
agent-starter-pack create my-awesome-agent
```

<details>
<summary> ✨ 替代方案：使用 uv</summary>

如果您已安裝 [`uv`](https://github.com/astral-sh/uv)，您可以使用單一指令來建立和設定您的專案：
```bash
uvx agent-starter-pack create my-fullstack-agent
```
此命令能夠處理專案的建立，無需預先在虛擬環境中安裝套件。
</details>

**就是這麼簡單！** 您現在擁有一個功能齊全的代理專案——包含後端、前端和部署基礎設施——隨時可供您探索和客製化。

### 🔧 強化現有代理

已經有代理了嗎？為其添加可用於生產的部署和基礎設施：

```bash
agent-starter-pack enhance my-existing-agent
```

請參閱[安裝指南](https://googlecloudplatform.github.io/agent-starter-pack/guide/installation)以獲得更多選項，或在 [Firebase Studio](https://studio.firebase.google.com/new?template=https%3A%2F%2Fgithub.com%2FGoogleCloudPlatform%2Fagent-starter-pack%2Ftree%2Fmain%2Fsrc%2Fresources%2Fidx) 或 [Cloud Shell](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https%3A%2F%2Fgithub.com%2Feliasecchig%2Fasp-open-in-cloud-shell&cloudshell_print=open-in-cs) 中進行零設定試用。

---

## 🤖 代理 (Agents)

| 代理名稱                  | 描述                                                                                                                       |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| `adk_base`      | 使用 Google 的 [Agent Development Kit (ADK)](https://github.com/google/adk-python) 實現的基礎 ReAct 代理 |
| `agentic_rag` | 一個用於文件檢索和問答的 RAG 代理。支援 [Vertex AI Search](https://cloud.google.com/generative-ai-app-builder/docs/enterprise-search-introduction) 和 [Vector Search](https://cloud.google.com/vertex-ai/docs/vector-search/overview)。       |
| `langgraph_base_react`      | 一個使用 LangGraph 實現的基礎 ReAct 代理 |
| `crewai_coding_crew`       | 一個使用 CrewAI 實現的多代理系統，旨在支援編碼活動       |
| `live_api`       | 一個由 Gemini 驅動的即時多模態 RAG 代理，支援音訊/視訊/文字聊天，並由向量資料庫支援回應                       |

**更多代理即將推出！** 我們正在持續擴展我們的[代理程式庫](https://googlecloudplatform.github.io/agent-starter-pack/agents/overview)。您心中有特定的代理類型嗎？[提出一個 issue 作為功能請求！](https://github.com/GoogleCloudPlatform/agent-starter-pack/issues/new?labels=enhancement)

**🔍 ADK 範例**

想要探索更多 ADK 範例嗎？請查看 [ADK 範例儲存庫](https://github.com/google/adk-samples) 以獲取更多展示 ADK 功能的範例和使用案例。

#### 額外功能

`agent-starter-pack` 提供兩個關鍵功能，以加速和簡化您代理的開發：
- **🔄 [CI/CD 自動化](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd)** - 只需一個命令即可為所有環境設定完整的 CI/CD 管線，支援 **Google Cloud Build** 和 **GitHub Actions**。
- **📥 [使用 Terraform/CI-CD 的 RAG 資料管線](https://googlecloudplatform.github.io/agent-starter-pack/guide/data-ingestion)** - 將處理 RAG 嵌入的資料管線無縫整合到您的代理系統中。支援 [Vertex AI Search](https://cloud.google.com/generative-ai-app-builder/docs/enterprise-search-introduction) 和 [Vector Search](https://cloud.google.com/vertex-ai/docs/vector-search/overview)。
- **[遠端模板](docs/guide/remote-templating.md)**：從任何 Git 儲存庫建立和分享您自己的代理啟動套件模板。
- **🤖 Gemini CLI 整合** - 使用 [Gemini CLI](https://github.com/google-gemini/gemini-cli) 和內含的 `GEMINI.md` 內容檔案，來詢問有關您的模板、代理架構以及產品化路徑的問題。直接在您的終端機中獲得即時指導和程式碼範例。

## 高層次架構

這個入門套件涵蓋了代理開發的所有方面，從原型設計和評估到部署和監控。

![高層次架構](docs/images/ags_high_level_architecture.png "Architecture")

---

## 🔧 需求

- Python 3.10+
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Terraform](https://developer.hashicorp.com/terraform/downloads) (用於部署)


## 📚 文件

請訪問我們的[文件網站](https://googlecloudplatform.github.io/agent-starter-pack/)以獲取全面的指南和參考！

- [入門指南](https://googlecloudplatform.github.io/agent-starter-pack/guide/getting-started) - agent-starter-pack 的第一步
- [安裝指南](https://googlecloudplatform.github.io/agent-starter-pack/guide/installation) - 設定您的環境
- [部署指南](https://googlecloudplatform.github.io/agent-starter-pack/guide/deployment) - 將您的代理投入生產
- [代理模板總覽](https://googlecloudplatform.github.io/agent-starter-pack/agents/overview) - 探索可用的代理模式
- [CLI 參考](https://googlecloudplatform.github.io/agent-starter-pack/cli/) - 命令列工具文件


### 影片教學：

- **[探索 Agent Starter Pack](https://www.youtube.com/watch?v=9zqwym-N3lg)**：一個全面的教學，示範如何使用 Agent Starter Pack 快速部署 AI 代理，涵蓋架構、模板和逐步部署。

- **[6 分鐘介紹](https://www.youtube.com/live/eZ-8UQ_t4YM?feature=shared&t=2791)** (2024 年 4 月)：解釋 Agent Starter Pack 並展示其關鍵功能。Kaggle GenAI 密集課程的一部分。

- **[120 分鐘直播示範](https://www.youtube.com/watch?v=yIRIT_EtALs&t=235s)** (2025 年 3 月 6 日)：觀看我們在 30 分鐘內使用 `agent-starter-pack` 建構 3 個代理！


正在尋找更多關於 Google Cloud 上生成式 AI 的範例和資源嗎？請查看 [GoogleCloudPlatform/generative-ai](https://github.com/GoogleCloudPlatform/generative-ai) 儲存庫，以獲取筆記本、程式碼範例等！

## 貢獻

歡迎貢獻！請參閱[貢獻指南](CONTRIBUTING.md)。

## 回饋

我們重視您的意見！您的回饋幫助我們改進這個入門套件，使其對社群更有用。

### 獲得協助

如果您遇到任何問題或有具體建議，請首先考慮在我們的 GitHub 儲存庫上[提出 issue](https://github.com/GoogleCloudPlatform/generative-ai/issues)。

### 分享您的經驗

對於其他類型的回饋，或者如果您想分享使用此入門套件的正面經驗或成功故事，我們很樂意聽取您的意見！您可以透過 <a href="mailto:agent-starter-pack@google.com">agent-starter-pack@google.com</a> 與我們聯繫。

感謝您的貢獻！

## 免責聲明

此儲存庫僅供示範之用，並非 Google 官方支援的產品。

## 服務條款

agent-starter-pack 模板化 CLI 和此入門套件中的模板利用了 Google Cloud API。當您使用此入門套件時，您將在自己的 Google Cloud 專案中部署資源，並對這些資源負責。請查閱 [Google Cloud 服務條款](https://cloud.google.com/terms/service-terms)以了解與這些 API 相關的服務條款詳情。
