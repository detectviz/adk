# 使用 A2A SDK 建置多代理 (Multi-Agent) 系統

----
> **⚠️ 免責聲明**：此示範僅供示範之用。不適用於生產環境。
>
> **⚠️ 重要提示：** A2A 尚在開發中 (WIP)，因此在不久的將來可能會出現與此處所示範的內容不同的變更。
----

本文件描述了一個網頁應用程式，該應用程式示範了 Agent2Agent (A2A)、Google 代理開發套件 (ADK) 與模型上下文協定 (MCP) 客戶端的多代理 (multi-agent) 協調整合。該應用程式的特色是一個主機代理 (host agent)，它負責協調遠端代理 (remote agents) 之間的任務，這些遠端代理 (remote agents) 與各種 MCP 伺服器互動以滿足使用者請求。

## 架構

該應用程式採用多代理 (multi-agent) 架構，其中主機代理 (host agent) 根據使用者的查詢將任務委派給遠端代理 (remote agents)（Airbnb 和 Weather）。然後，這些代理 (Agent) 與對應的 MCP 伺服器互動。

![architecture](assets/A2A_multi_agent.png)

### 應用程式 UI

![screenshot](assets/screenshot.png)

## 設定與部署

### 先決條件

在本機執行應用程式之前，請確保您已安裝以下項目：

1. **Node.js：** 在本機測試 Airbnb MCP 伺服器功能時需要。
2. **uv：** 此專案中使用的 Python 套件管理工具。請遵循安裝指南：[https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
3. **Python 3.13** 執行 a2a-sdk 需要 Python 3.13
4. **設定 .env**

- 在 `airbnb_agent` 和 `weather_agent` 資料夾中建立一個 `.env` 檔案，內容如下：

    ```bash
    GOOGLE_API_KEY="your_api_key_here" 
    ```

- 在 `host_agent/` 資料夾中建立一個 `.env` 檔案，內容如下：

    ```bash
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    GOOGLE_CLOUD_PROJECT="your project"
    GOOGLE_CLOUD_LOCATION=global
    AIR_AGENT_URL=http://localhost:10002
    WEA_AGENT_URL=http://localhost:10001
    ```

## 1. 執行 Airbnb 代理 (Agent)

執行 airbnb 代理 (Agent) 伺服器：

```bash
cd samples/python/agents/airbnb_planner_multiagent/airbnb_agent
uv run .
```

## 2. 執行天氣代理 (Weather Agent)

開啟一個新終端機並執行天氣代理 (weather agent) 伺服器：

```bash
cd samples/python/agents/airbnb_planner_multiagent/weather_agent
uv run .
```

## 3. 執行主機代理 (Host Agent)

開啟一個新終端機並執行主機代理 (host agent) 伺服器

```bash
cd samples/python/agents/airbnb_planner_multiagent/host_agent
uv run .
```

## 4. 在 UI 進行測試

以下是範例問題：

- "告訴我加州洛杉磯的天氣"

- "請在加州洛杉磯找一間房間，入住日期為 2025 年 6 月 20 日至 25 日，兩位成人"

## References

- <https://github.com/google/a2a-python>
- <https://codelabs.developers.google.com/intro-a2a-purchasing-concierge#1>
- <https://google.github.io/adk-docs/>

## 免責聲明

重要提示：此處提供的範例程式碼僅供示範之用，旨在說明代理對代理 (A2A) 協定的運作機制。在建構實際應用程式時，至關重要的是將任何在您直接控制範圍之外運作的代理 (Agent) 視為潛在不受信任的實體。

所有從外部代理 (Agent) 接收的資料——包括但不限於其 AgentCard、訊息、產物和任務狀態——都應作為不受信任的輸入來處理。舉例來說，一個惡意代理 (Agent) 可能在其 AgentCard 的欄位（例如：description、name、skills.description）中提供經過精心設計的資料。如果這些資料在未經清理的情況下被用來建構大型語言模型 (LLM) 的提示，可能會使您的應用程式遭受提示注入攻擊 (prompt injection attacks)。若未能在使用前對這些資料進行適當的驗證和清理，可能會為您的應用程式帶來安全漏洞。

開發人員有責任實施適當的安全措施，例如輸入驗證和安全處理憑證，以保護他們的系統和使用者。
