# 帶有外掛程式 (Plugin) 的 ADK 代理

### 什麼是 ADK 外掛程式 (Plugin)？

ADK 的擴充性核心建立在 [**回呼 (callbacks)**](https://google.github.io/adk-docs/callbacks/) 的基礎上：您編寫的函式會在代理生命週期的關鍵階段由 ADK 自動執行。**外掛程式 (Plugin) 只是一個將這些獨立的回呼函式打包在一起以實現更廣泛目的的類別。**

標準的代理回呼 (Agent Callback) 是針對*特定任務*在*單一代理、單一工具*上設定的，而外掛程式 (Plugin) 則是在 `Runner` 上*註冊一次*，其回呼會*全域*套用至該執行器管理的所有代理、工具和 LLM 呼叫。這使得外掛程式 (Plugin) 成為實作橫跨整個應用程式的水平功能的理想解決方案。

### 外掛程式 (Plugin) 可以做什麼？

外掛程式 (Plugin) 的功能非常多樣。透過實作不同的回呼方法，您可以實現各種功能。

*   **日誌記錄與追蹤 (Logging & Tracing)**：建立代理、工具和 LLM 活動的詳細日誌，用於偵錯和效能分析。
*   **策略強制執行 (Policy Enforcement)**：實作安全護欄。例如，`before_tool_callback` 可以檢查使用者是否有權限使用特定工具，並透過傳回一個值來防止其執行。
*   **監控與指標 (Monitoring & Metrics)**：收集並匯出關於權杖使用量、執行時間和呼叫次數的指標到像 Prometheus 或 Stackdriver 這樣的監控系統。
*   **快取 (Caching)**：在 `before_model_callback` 或 `before_tool_callback` 中，您可以檢查請求是否曾經被發出過。如果是，您可以傳回快取的回應，完全跳過昂貴的 LLM 或工具呼叫。
*   **請求/回應修改 (Request/Response Modification)**：動態地將資訊新增至 LLM 提示 (例如，在 `before_model_callback` 中) 或標準化工具輸出 (例如，在 `after_tool_callback` 中)。

### 執行代理

**注意：`adk web` 尚不支援外掛程式 (Plugin)。**

使用以下指令執行 main.py

```bash
python3 -m contributing.samples.plugin_basic.main
```

它應該會輸出以下內容。請注意，來自外掛程式 (plugin) 的輸出會被印出。

```bash
[Plugin] Agent run count: 1
[Plugin] LLM request count: 1
** Got event from hello_world
Hello world: query is [hello world]
** Got event from hello_world
[Plugin] LLM request count: 2
** Got event from hello_world
```