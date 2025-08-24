# 使用 AgentOps 實現代理程式可觀測性

**只需兩行程式碼**，[AgentOps](https://www.agentops.ai) 即可為代理程式提供會話重播、指標和監控功能。

## 為何為 ADK 選擇 AgentOps？

可觀測性是開發和部署對話式 AI 代理程式的關鍵環節。它能讓開發人員了解其代理程式的執行效能、與使用者的互動方式，以及如何使用外部工具和 API。

透過整合 AgentOps，開發人員可以深入了解其 ADK 代理程式的行為、大型語言模型 (LLM) 互動和工具使用情況。

Google ADK 包含其自有的基於 OpenTelemetry 的追蹤系統，主要旨在為開發人員提供一種追蹤其代理程式內部基本執行流程的方法。AgentOps 在此基礎上進行了增強，提供了一個專用且更全面的可觀測性平台，具備以下特點：

*   **統一追蹤與重播分析：** 整合來自 ADK 和您 AI 技術堆疊中其他元件的追蹤資料。
*   **豐富的視覺化：** 直觀的儀表板，可視覺化代理程式執行流程、LLM 呼叫和工具效能。
*   **詳細的偵錯：** 深入研究特定的跨度 (span)，查看提示、完成、權杖計數和錯誤。
*   **LLM 成本與延遲追蹤：** 追蹤延遲、成本（透過權杖使用量）並識別瓶頸。
*   **簡化設定：** 只需幾行程式碼即可開始使用。

![AgentOps 代理程式可觀測性儀表板](https://raw.githubusercontent.com/AgentOps-AI/agentops/refs/heads/main/docs/images/external/app_screenshots/overview.png)

![AgentOps 儀表板顯示一個帶有巢狀代理程式、LLM 和工具跨度的 ADK 追蹤。](../assets/agentops-adk-trace-example.jpg)

*AgentOps 儀表板顯示了來自多步驟 ADK 應用程式執行的追蹤。您可以看到跨度的階層結構，包括主代理程式工作流程、單個子代理程式、LLM 呼叫和工具執行。請注意清晰的階層結構：主工作流程代理程式跨度包含用於各種子代理程式操作、LLM 呼叫和工具執行的子跨度。*

## 開始使用 AgentOps 與 ADK

將 AgentOps 整合到您的 ADK 應用程式中非常簡單：

1.  **安裝 AgentOps：**
    ```bash
    pip install -U agentops
    ```

2. **建立 API 金鑰**
    在此處建立使用者 API 金鑰：[建立 API 金鑰](https://app.agentops.ai/settings/projects) 並設定您的環境：

    將您的 API 金鑰新增至您的環境變數：
    ```
    AGENTOPS_API_KEY=<您的_AGENTOPS_API_金鑰>
    ```

3.  **初始化 AgentOps：**
    在您的 ADK 應用程式腳本的開頭（例如，執行 ADK `Runner` 的主 Python 檔案）新增以下幾行：

    ```python
    import agentops
    agentops.init()
    ```

    這將啟動一個 AgentOps 會話，並自動追蹤 ADK 代理程式。

    詳細範例：

    ```python
    import agentops
    import os
    from dotenv import load_dotenv

    # 載入環境變數（可選，如果您使用 .env 檔案儲存 API 金鑰）
    load_dotenv()

    agentops.init(
        api_key=os.getenv("AGENTOPS_API_KEY"), # 您的 AgentOps API 金鑰
        trace_name="my-adk-app-trace"  # 可選：您的追蹤名稱
        # auto_start_session=True 是預設值。
        # 如果您想手動控制會話的開始/結束，請設為 False。
    )
    ```

    > 🚨 🔑 您可以在註冊後於您的 [AgentOps 儀表板](https://app.agentops.ai/) 上找到您的 AgentOps API 金鑰。建議將其設定為環境變數 (`AGENTOPS_API_KEY`)。

初始化後，AgentOps 將自動開始檢測您的 ADK 代理程式。

**這就是捕捉 ADK 代理程式所有遙測資料所需的全部操作**

## AgentOps 如何檢測 ADK

AgentOps 採用一種複雜的策略，以提供無縫的可觀測性，而不會與 ADK 的原生遙測發生衝突：

1.  **中和 ADK 的原生遙測：**
    AgentOps 會偵測 ADK 並智慧地修補 ADK 的內部 OpenTelemetry 追蹤器（通常是 `trace.get_tracer('gcp.vertex.agent')`）。它會將其替換為 `NoOpTracer`，確保 ADK 自身建立遙測跨度的嘗試被有效抑制。這可以防止重複的追蹤，並讓 AgentOps 成為可觀測性資料的權威來源。

2.  **由 AgentOps 控制的跨度建立：**
    AgentOps 透過包裝關鍵的 ADK 方法來控制，以建立一個邏輯性的跨度階層：

    *   **代理程式執行跨度（例如，`adk.agent.MySequentialAgent`）：**
        當 ADK 代理程式（如 `BaseAgent`、`SequentialAgent` 或 `LlmAgent`）啟動其 `run_async` 方法時，AgentOps 會為該代理程式的執行啟動一個父跨度。

    *   **LLM 互動跨度（例如，`adk.llm.gemini-pro`）：**
        對於代理程式對 LLM 的呼叫（透過 ADK 的 `BaseLlmFlow._call_llm_async`），AgentOps 會建立一個專用的子跨度，通常以 LLM 模型命名。此跨度會捕捉請求詳細資訊（提示、模型參數），並在完成時（透過 ADK 的 `_finalize_model_response_event`）記錄回應詳細資訊，如完成內容、權杖使用量和結束原因。

    *   **工具使用跨度（例如，`adk.tool.MyCustomTool`）：**
        當代理程式使用工具時（透過 ADK 的 `functions.__call_tool_async`），AgentOps 會建立一個以該工具命名的單一、全面的子跨度。此跨度包含工具的輸入參數及其返回的結果。

3.  **豐富的屬性收集：**
    AgentOps 重複使用 ADK 的內部資料提取邏輯。它會修補 ADK 的特定遙測函式（例如 `google.adk.telemetry.trace_tool_call`、`trace_call_llm`）。這些函式的 AgentOps 包裝器會獲取 ADK 收集的詳細資訊，並將其作為屬性附加到*當前活動的 AgentOps 跨度*上。

## 在 AgentOps 中視覺化您的 ADK 代理程式

當您使用 AgentOps 檢測您的 ADK 應用程式時，您將在 AgentOps 儀表板中獲得代理程式執行的清晰、階層式視圖。

1.  **初始化：**
    當 `agentops.init()` 被呼叫時（例如 `agentops.init(trace_name="my_adk_application")`），如果 `init` 參數 `auto_start_session=True`（預設為 true），則會建立一個初始的父跨度。此跨度通常命名類似於 `my_adk_application.session`，將成為該追蹤中所有操作的根。

2.  **ADK Runner 執行：**
    當 ADK `Runner` 執行一個頂層代理程式時（例如，一個協調工作流程的 `SequentialAgent`），AgentOps 會在會話追蹤下建立一個相應的代理程式跨度。此跨度將反映您的頂層 ADK 代理程式的名稱（例如 `adk.agent.YourMainWorkflowAgent`）。

3.  **子代理程式與 LLM/工具呼叫：**
    當這個主代理程式執行其邏輯，包括呼叫子代理程式、LLM 或工具時：
    *   每個**子代理程式執行**將顯示為其父代理程式下的巢狀子跨度。
    *   對**大型語言模型**的呼叫將產生更深層的巢狀子跨度（例如 `adk.llm.<model_name>`），捕捉提示詳細資訊、回應和權杖使用量。
    *   **工具調用**也將產生不同的子跨度（例如 `adk.tool.<your_tool_name>`），顯示其參數和結果。

這會建立一個跨度的瀑布流，讓您可以看到 ADK 應用程式中每一步的順序、持續時間和詳細資訊。所有相關屬性，如 LLM 提示、完成內容、權杖計數、工具輸入/輸出和代理程式名稱，都會被捕捉和顯示。

作為一個實際的示範，您可以探索一個範例 Jupyter Notebook，它說明了使用 Google ADK 和 AgentOps 的人工批准工作流程：
[GitHub 上的 Google ADK 人工批准範例](https://github.com/AgentOps-AI/agentops/blob/main/examples/google_adk_example/adk_human_approval_example.ipynb)。

這個範例展示了如何在 AgentOps 中視覺化一個帶有工具使用的多步驟代理程式流程。

## 優點

*   **輕鬆設定：** 最少的程式碼變更即可實現全面的 ADK 追蹤。
*   **深度可見性：** 了解複雜 ADK 代理程式流程的內部運作。
*   **更快的偵錯：** 透過詳細的追蹤資料快速找出問題。
*   **效能優化：** 分析延遲和權杖使用量。

透過整合 AgentOps，ADK 開發人員可以顯著增強其建立、偵錯和維護強大 AI 代理程式的能力。

## 更多資訊

若要開始，請[建立一個 AgentOps 帳戶](http://app.agentops.ai)。有關功能請求或錯誤報告，請透過 [AgentOps Repo](https://github.com/AgentOps-AI/agentops) 聯繫 AgentOps 團隊。

### 額外連結
🐦 [Twitter](http://x.com/agentopsai)   •   📢 [Discord](http://x.com/agentopsai)   •   🖇️ [AgentOps 儀表板](http://app.agentops.ai)   •   📙 [文件](http://docs.agentops.ai)
