# SRE Assistant - 程式碼重構與驗證計畫

## 前言

本文件提供了一份詳細的、逐模組的計畫，旨在根據 ADK 參考範例中識別出的最佳實踐，對 SRE Assistant 的程式碼庫進行重構和驗證。它作為 [TASKS.md](TASKS.md) 中高階路線圖的技術性配套文件。

每個章節都將 `sre_assistant` 的一個核心模組與其主要參考範例對應，並概述具體的行動計畫。

---

## 1. 主工作流程 (`workflow.py`)

-   **目前實現**: 一個 `SequentialAgent`，負責協調 SRE 流程的主要階段。它使用硬編碼的條件邏輯來進行修復。
-   **主要參考**: `google-adk-workflows/dispatcher/` 和 `google-adk-workflows/self_critic/`。
-   **行動計畫**:
    1.  **實現智慧分診**: 重構目前的修復階段。引入一個 `SRE_Triage_Dispatcher` 代理，取代簡單的條件代理。此代理將使用 LLM 分析診斷結果，並動態選擇適當的修復代理（例如 `RollbackAgent`, `ScalingAgent`, `ChaosEngineeringAgent`）。
    2.  **實現修復後驗證**: 在修復步驟之後，於主工作流程中新增一個 `Verification` 階段。此階段將是一個 `SequentialAgent`，包含：
        -   一個 `HealthCheckAgent`，負責重新運行關鍵的診斷檢查（例如，檢查服務健康端點、查詢錯誤率）。
        -   一個 `VerificationCritic`，負責分析健康檢查結果，以正式判斷修復是否成功、失敗或引發了新問題。
    3.  最終的工作流程應如下所示：`並行診斷 -> 智慧分診 -> 驗證後修復 -> 事後檢討`。

---

## 2. 認證與授權 (`auth/`)

-   **目前實現**: 一個穩健的 `AuthFactory` 和 `AuthManager`，支援多種憑證類型。
-   **主要參考**: `google_api/agent.py` 和 `spanner/agent.py`。
-   **行動計畫**:
    1.  **驗證精細化控制**: 審計現有的 `AuthManager` 和所有 `Toolset` 整合。確保最小權限原則無處不在，不僅針對憑證，也針對暴露給每個代理的工具。
    2.  **實現 `tool_filter`**: 對於任何使用廣泛 `Toolset`（例如假設的 `GCloudToolset`）的代理，實現 `tool_filter` 以僅暴露其特定任務所需的功能。例如，診斷代理絕不應有權限存取可以修改資源的工具。
    3.  **無需重大重構**，但需要基於參考模式進行安全審計。

---

## 3. SLO 管理 (`slo_manager.py`)

-   **目前實現**: 包含計算錯誤預算的核心邏輯。
-   **主要參考**: `machine-learning-engineering/` (用於迭代循環模式) 和 `google-sre-book`。
-   **行動計畫**:
    1.  **實現迭代式 SLO 調優器**: 創建一個新的 `SLO_Tuning_LoopAgent`。此代理將由主工作流程的 `IterativeOptimization` 階段觸發。
    2.  該循環將包含：
        -   一個 `ProposeChangeAgent`，建議對 SLO 相關配置進行微小修改（例如，調整快取 TTL、增加副本數）。
        -   一個 `SimulateImpactAgent`，使用歷史數據預測變更對錯誤預算的影響。
        -   一個 `TuningCriticAgent`，評估模擬結果。當評論者確定 SLO 已滿足或無法進一步改善時，循環終止。

---

## 4. 修復子代理 (`sub_agents/remediation/`)

-   **目前實現**: 一個基本的修復代理。
-   **主要參考**: `human_in_loop/agent.py`。
-   **行動計畫**:
    1.  **為 HITL 重構**: 修改高風險的修復工具（例如 `failover_database`, `revert_release`），以使用 `LongRunningFunctionTool` 模式。
    2.  當被調用時，這些工具不應執行操作。相反，它們應該：
        -   生成一個 `ticketId`。
        -   向外部通知系統發送結構化的核准請求（初期將是一個模擬整合）。
        -   返回 `pending` 狀態。
    3.  代理必須能夠處理來自外部系統的回呼，以便在收到核准後恢復操作。

---

## 5. A2A 通訊 (`a2a/`)

-   **目前實現**: 基本的協議定義。
-   **主要參考**: `airbnb_planner_multiagent/`。
-   **行動計畫**:
    1.  這是一個 P2 任務，但現在應制定架構計畫。
    2.  **實現安全端點**: SRE Assistant 在作為遠端代理時，必須暴露一個安全的 HTTP 端點。此端點必須使用 `AuthManager` 來認證和授權所有傳入的 A2A 請求。
    3.  **開發 `AgentCard`**: 創建一個動態的 `agent-card.json` 端點，準確地宣告 SRE Assistant 的能力和結構。
    4.  **重構 `a2a_client.py`**: 客戶端工具應更新以處理完整的 A2A 交握，包括獲取 Agent Card 和處理對遠端代理的認證。
