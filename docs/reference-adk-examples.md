# SRE Assistant 專案 ADK 關鍵參考範例

**文件目的**: 本文件旨在為 SRE Assistant 的開發團隊提供一份精選的 Google Agent Development Kit (ADK) 範例列表。這些範例經過首席架構師的審慎評估，被認為對本專案的成功，特別是 **Phase 1 (後端優先與核心能力建設)** 階段，具有最高的技術參考價值。

**使用指南**: 開發人員在執行 `TASKS.md` 中指定的任務時，應優先參考此處對應的範例，以確保實現方式符合 ADK 的最佳實踐和本專案的架構設計。

---

## 自定義工具與整合 (Custom Tools & Integration)

這些範例展示了如何構建與外部系統互動的工具，是完成 `TASK-P1-TOOL-01` 到 `TASK-P1-TOOL-03` 的核心參考。

- ### **檔案路徑**: `docs/references/adk-examples/jira_agent/`
  - **參考原因**: 這是實現 **`TASK-P1-TOOL-01`**, **`TASK-P1-TOOL-02`**, 和 **`TASK-P1-TOOL-03`** 的**最佳實踐範本**。`jira_agent/tools.py` 完美演示了如何封裝一個與第三方 REST API 互動的工具，並包含了處理認證、參數傳遞和結果解析的完整邏輯。其結構和錯誤處理模式應被我們所有共享工具所遵循，以符合 `SPEC.md` 的標準化介面要求。

- ### **檔案路徑**: `docs/references/adk-examples/adk_answering_agent/`
  - **參考原因**: 這是一個將**記憶體 (RAG)** 和**工具**結合的綜合性範例。它展示了一個完整的 Agent 如何利用 RAG (`upload_docs_to_vertex_ai_search.py`) 來增強其知識，並透過工具 (`tools.py`) 與外部服務互動。這為我們設計 `SREWorkflow` (`TASK-P1-SVC-01`)，使其能同時協調 RAG 檢索和工具調用提供了寶貴的架構參考。

- ### **檔案路徑**: `docs/references/adk-examples/google_search_agent/`
  - **參考原因**: 此範例是 Agent **獲取即時資訊能力**的基礎。它極其簡潔地展示了如何將 ADK 內建的 `google_search` 工具直接整合到 Agent 中。這對於 SRE Assistant 在進行根因分析時，能夠查詢最新的技術文檔、CVE 漏洞資訊或外部服務狀態至關重要，是 RAG 系統的重要補充。

## 進階參考 (Advanced References)


- ### **檔案路徑**: `docs/references/adk-examples/hello_world_ollama/`
  - **參考原因**: 此範例是實現**模型可配置性**的關鍵。它展示了如何透過 ADK 的 `LiteLlm` 封裝，輕易地將預設的 Gemini 模型替換為本地運行的 Ollama 模型（如 Mistral）。這為我們在開發環境中降低成本、離線運行、以及未來支援更多元的 LLM 後端提供了直接的技術路徑。

---

## Phase 1 & 2: 核心能力與 Grafana 整合 (Core Capabilities & Grafana Integration)

- ### **檔案路徑**: `docs/references/adk-examples/callbacks/`
  - **參考原因**: 此範例對於**提升系統可觀測性**和**實現 `TASK-P2-PLUGIN-02` (Grafana ChatOps 介面)** 至關重要。它展示了如何註冊回調函數來監聽 Agent 的內部事件（如工具調用、LLM 請求）。我們能藉此將詳細的執行追蹤實時推送到 Loki，並在 Grafana UI 中為用戶提供透明的進度更新。

- ### **檔案路徑**: `docs/references/adk-examples/live_bidi_streaming_tools_agent/`
  - **參考原因**: 這是實現**無縫 Grafana ChatOps 體驗 (`TASK-P2-PLUGIN-02`, `TASK-P2-PLUGIN-03`)** 的關鍵技術。範例展示了如何將工具執行的中間輸出以流式（Streaming）方式傳回客戶端。這將允許用戶在 Grafana 介面中實時看到長時間運行任務（如日誌分析、數據庫查詢）的進展，而不是長時間的等待，極大地提升了用戶體驗。

- ### **檔案路徑**: `docs/references/adk-examples/human_in_loop/`
  - **參考原因**: 直接對應 `ARCHITECTURE.md` 中定義的 **P0 級事件需要人類介入** 的核心安全要求。此範例提供了實現手動審批環節的標準模式。我們將參考它來設計 SRE Assistant 在執行高風險修復操作前的“請求人類批准”工作流。


- ### **檔案路徑**: `docs/references/adk-examples/mcp_sse_agent/`
  - **參考原因**: 此範例與 `live_bidi_streaming_tools_agent` 互為補充，展示了另一種關鍵的**網頁串流技術：Server-Sent Events (SSE)**。SSE 是單向的、從伺服器到客戶端的串流，非常適合將 Agent 的執行日誌、狀態更新推送到前端（如 Grafana 插件）。理解此模式有助於我們為 Phase 2 選擇最適合的串流解決方案。

## Phase 3 & 4: 聯邦化與進階工作流 (Federation & Advanced Workflows)

- ### **檔案路徑**: `docs/references/adk-examples/a2a_basic/` 和 `a2a_auth/`
  - **參考原因**: 這兩個範例是實現 **`TASK-P3-A2A-01` (A2A 通訊)** 的基石。`a2a_basic` 演示了 Agent-to-Agent (A2A) 通信的基礎，而 `a2a_auth` 則在其之上增加了認證機制。這為我們將 `PostmortemAgent` (`TASK-P3-AGENT-01`) 等專業化代理從主服務中分離出來，並透過安全的 gRPC 協議進行協同工作提供了清晰的實現路徑。

- ### **檔案路徑**: `docs/references/adk-examples/multi_agent_seq_config/` 和 `multi_agent_loop_config/`
  - **參考原因**: 隨著 SRE Assistant 功能的擴展，我們需要編排由多個 Agent 參與的複雜工作流。這兩個範例分別展示了**順序執行**和**循環執行**兩種多 Agent 協作模式。這對於實現 `ROADMAP.md` 中提到的多步驟自動化修復流程 (Runbooks) 和需要迭代優化的任務（如 `TASK-P3-AGENT-01` 的報告生成）至關重要。


---

## 進階工作流與工程實踐 (Advanced Workflow & Engineering Practices)

這些範例專注於提升 SRE Assistant 的智能、彈性和工程品質，是實現 Phase 2 和 Phase 3 路線圖中複雜功能與長期穩定性的關鍵。

- ### **檔案路徑**: `docs/references/adk-examples/code_execution/`
  - **參考原因**: 直接賦予 Agent **執行自動化修復腳本**的能力，是 `SPEC.md` 中定義的 `KubernetesOperationTool` 和 **`TASK-P2-DEVOPS-01` (TerraformTool)** 等操作工具的基礎。此範例提供了在安全的沙箱環境中執行程式碼的標準模式，是將 SRE Assistant 從“分析者”變為“行動者”的核心技術，對實現真正的**監控閉環 (`TASK-P3-MONITOR-01`)** 至關重要。

- ### **檔案路徑**: `docs/references/adk-examples/artifact_save_text/`
  - **參考原因**: 此範例對於實現**覆盤報告 (`Postmortem`) 自動生成 (`TASK-P3-AGENT-01`)** 至關重要。它展示了 Agent 如何將其最終的思考過程或生成內容，透過 `save_artifact` 函數保存為一個文字檔案。這是將 Agent 的內部狀態或工作成果持久化為外部可訪問資源（如報告、日誌、配置檔）的基礎。

---

## 工程實踐與開發體驗 (Engineering Practices & Developer Experience)

這些範例專注於改善開發流程、提升使用者體驗和增強系統的工程品質，是確保專案可維護性和擴展性的關鍵。

- ### **檔案路徑**: `docs/references/adk-examples/history_management/`
  - **參考原因**: 此範例是對 **`TASK-P1-CORE-02` (實現持久化會話)** 的重要補充。它展示了如何在**應用層面**有效**使用和管理**對話歷史。這對於處理 LLM 的上下文視窗限制、實現長期對話記憶至關重要。

- ### **檔案路徑**: `docs/references/adk-examples/live_tool_callbacks_agent/`
  - **參考原因**: 這是實現 **`TASK-P2-PLUGIN-02` (Grafana 原生體驗)** 中**即時反饋**功能的關鍵。`live_bidi_streaming_tools_agent` 範例展示了如何流式返回**最終結果**，而此範例則展示了如何在工具執行過程中，透過回調**即時串流中間日誌和進度**。這將極大地提升用戶在 Grafana UI 上執行長時間任務（如日誌分析）時的體驗。

---

## 開發者實踐補充範例 (Developer's Cookbook)

本章節旨在補充首席架構師挑選的宏觀範例，提供一系列更貼近日常開發任務的、精簡且專注的「食譜式」程式碼範例。開發者在實現 `TASKS.md` 中的具體功能時，可以優先參考此處的模式。

- ### **檔案路徑**: `docs/references/adk-examples/tool_functions_config/`
  - **參考原因**: 這是實現 **`TASK-P1-TOOL-01`**, **`TASK-P1-TOOL-02`**, 和 **`TASK-P1-TOOL-03`** 的**最簡起點**。相較於 `jira_agent` 的複雜性，此範例展示了如何用最少的程式碼，將一個標準的 Python 函數 (`def add(a: int, b: int): ...`) 直接轉換為一個 ADK 工具。這對於快速創建和測試工具的原型非常有幫助。

- ### **檔案路徑**: `docs/references/adk-examples/output_schema_with_tools/`
  - **參考原因**: 此範例是實現 **`SPEC.md` 中 4.1 節 `ToolResult` 標準化介面**的**直接程式碼實現**。它演示了如何定義一個 Pydantic `BaseModel` 作為工具的輸出綱要 (Output Schema)，並強制工具的返回結果遵循此結構。所有工具的開發都應遵循此模式，以確保數據一致性。

- ### **檔案路徑**: `docs/references/adk-examples/history_management/`
  - **參考原因**: 這是對 **`TASK-P1-CORE-02` (實現持久化會話)** 的重要**應用層補充**。此範例則展示了 Agent 如何在程式碼中**實際讀取和操作**對話歷史 (`use_history=True`)。這對於構建真正具備上下文理解能力的 Agent 至關重要。

- ### **檔案路徑**: `docs/references/adk-examples/session_state_agent/`
  - **參考原因**: 此範例同樣是對 **`TASK-P1-CORE-02`** 的關鍵補充，它展示了如何**在會話中讀寫自定義狀態** (`context.state`)。這對於在多個對話輪次之間傳遞非聊天記錄的數據（例如，用戶偏好、已獲取的事件 ID）非常有用，是構建複雜工作流的基礎。

- ### **檔案路徑**: `docs/references/adk-examples/simple_sequential_agent/`
  - **參考原因**: 此範例是實現 **`TASK-P1-SVC-01` (核心 `SREWorkflow`)** 的一個**簡化藍圖**。它清晰地展示了如何定義一個由多個步驟組成的順序工作流 (Sequential Workflow)，其中每一步都可以是一個 LLM 調用或一個工具調用。這為我們構建結構清晰、可擴展的 SRE 自動化流程提供了基礎模式。

- ### **檔案路徑**: `docs/references/adk-examples/bigquery/`
  - **參考原因**: 雖然我們的目標是 Prometheus 和 Loki，但此範例是實現 **`TASK-P1-TOOL-01`** 和 **`TASK-P1-TOOL-02`** 的一個**絕佳的通用模式參考**。它展示了一個工具如何處理與**需要認證的外部數據源**的連接、查詢和錯誤處理。開發者可以借鑒其結構，將 `bigquery_client` 替換為 `prometheus_client` 或 `loki_client`。

---

## 開發團隊補充建議參考 (Additional Team-Proposed References)

本章節由開發團隊根據對 `adk-examples` 目錄的深入分析後補充，旨在提供更多針對 SRE Assistant 獨特需求的關鍵技術模式。

- ### **檔案路徑**: `docs/references/adk-examples/toolbox_agent/`
  - **參考原因**: 此範例是實現 `TASKS.md` 中定義的 `tool_registry.py` 的關鍵參考。它演示了如何使用 `ToolboxToolset` 從外部的、由配置驅動的來源（一個“工具箱服務器”）加載工具集。此模式比在代理程式碼中直接定義工具更具擴展性和可維護性，它實現了關注點分離，允許 SRE Assistant 從一個集中的註冊表中消費工具，這與我們為所有當前和未來的專業化代理提供共享、可擴展工具集的目標完全一致。

- ### **檔案路徑**: `docs/references/adk-examples/workflow_triage/`
  - **參考原因**: 此範例為 `SPEC.md` 中描述的**“智慧分診”**能力和 `TASKS.md` 中的 `SREIntelligentDispatcher` 概念提供了直接的藍圖。它展示了一個根代理作為管理者或分派器，分析用戶輸入，使用工具更新計劃，然後將工作委派給適當的子代理。這正是 SRE Assistant 在分析傳入的警報並將其路由到正確的專業化工作流（例如 `IncidentHandlerAgent`）時所需遵循的模式。

- ### **檔案路徑**: `docs/references/adk-examples/parallel_functions/`
  - **參考原因**: 此範例是 `SPEC.md` 中提到的關鍵差異化特性**“並行診斷”**的完美實現參考。它展示了一個能夠在單一步驟中並發調用多個 `async` 工具以收集不同信息（如天氣、貨幣、距離）的代理。這對於 SRE Assistant 的效率至關重要，因為它需要同時從 Prometheus 查詢指標、從 Loki 查詢日誌、從 Tempo 查詢追蹤，以快速形成對事件的整體視圖。

- ### **檔案路徑**: `docs/references/adk-examples/workflow_agent_seq/`
  - **參考原因**: 此範例為順序工作流程提供了比 `simple_sequential_agent` 更進階、更實用的藍圖。它展示了一個真正的“鏈”，其中一個子代理的輸出透過 `output_key` 寫入會話狀態，然後注入到下一個子代理的提示中。這種狀態傳遞模式是建構 SRE Assistant 多步驟自動化執行手冊（例如，診斷 -> 提出修復方案 -> 等待批准 -> 應用修復 -> 驗證）所需的核心機制。

- ### **檔案路徑**: `docs/references/adk-examples/session_state_agent/`
  - **參考原因**: 此範例對於理解持久化會話至關重要，它演示了如何有效地**使用**會話。它清楚地解釋了 `context.state` 的生命週期，展示資料在一個回合中如何快取並在結束時持久化。理解這一點對於 `TASK-P1-CORE-02` 以及建構任何需要跨多個互動維護自訂狀態（例如，事件 ID、使用者偏好、收集的證據）的複雜工作流程至關重要。

- ### **檔案路徑**: `docs/references/adk-examples/adk_triaging_agent/`
  - **參考原因**: 此範例提供了 `workflow_triage` 中分派器模式的強大替代方案。它不是路由到不同的代理，而是在單一代理中執行複雜的、基於規則的分類流程，方法是將詳細的指令（提示工程）與特定的工具集結合。對於許多需要結構化、可重複決策制定而無需多個代理開銷的 SRE 任務來說，這是一種非常有價值的模式。

- ### **檔案路徑**: `docs/references/adk-examples/application_integration_agent/`
  - **參考原因**: 此範例展示了一種更抽象、企業級的工具整合模式。它利用 `ApplicationIntegrationToolset` 透過託管的整合層連接到第三方系統（如 Jira），而不是為每個外部 API 編寫自訂的 Python 程式碼。隨著 SRE Assistant 需要連接到越來越多的系統（PagerDuty、Slack 等），這種架構為建構和維護大量客製化工具提供了一個更具擴展性和穩健性的替代方案。

- ### **檔案路徑**: `docs/references/adk-examples/oauth_calendar_agent/`
  - **參考原因**: 此範例展示了身份驗證如何在**工具層級**實際**使用**。它演示了 `AuthCredential` 物件如何在執行時傳遞到工具的上下文中，並用於進行經過身份驗證的 API 呼叫。對於在 SRE Assistant 中實現任何需要與受 OAuth 2.0 保護的端點互動的工具（例如 `PrometheusQueryTool` 或 `GrafanaIntegrationTool`），這是一個強制性的參考。
