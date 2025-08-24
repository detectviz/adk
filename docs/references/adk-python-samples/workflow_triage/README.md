# 工作流程分流範例

此範例示範如何建置一個多代理程式工作流程，該工作流程可智慧地分流傳入的請求，並將其委派給適當的專門代理程式。

## 總覽

工作流程包含三個主要元件：

1. **執行管理員代理** (`agent.py`) - 分析使用者輸入並決定哪些執行代理程式是相關的
2. **計畫執行代理** - 協調執行和摘要的循序代理程式
3. **工作執行代理** (`execution_agent.py`) - 平行執行特定工作的專門代理程式

## 架構

### 執行管理員代理 (`root_agent`)
- **模型**：gemini-2.5-flash
- **名稱**：`execution_manager_agent`
- **角色**：分析使用者請求並更新執行計畫
- **工具**：`update_execution_plan` - 更新應啟動哪些執行代理程式
- **子代理**：委派給 `plan_execution_agent` 進行實際工作執行
- **澄清**：如果使用者意圖不清楚，則在繼續之前要求澄清

### 計畫執行代理
- **類型**：SequentialAgent
- **名稱**：`plan_execution_agent`
- **元件**：
  - `worker_parallel_agent` (ParallelAgent) - 平行執行相關代理程式
  - `execution_summary_agent` - 摘要執行結果

### 工作代理
系統包含兩個平行執行的專門執行代理程式：

- **程式碼代理** (`code_agent`)：處理程式碼產生工作
  - 如果無關，則使用 `before_agent_callback_check_relevance` 跳過
  - 輸出儲存在 `code_agent_output` 狀態金鑰中
- **數學代理** (`math_agent`)：執行數學計算
  - 如果無關，則使用 `before_agent_callback_check_relevance` 跳過
  - 輸出儲存在 `math_agent_output` 狀態金鑰中

### 執行摘要代理
- **模型**：gemini-2.5-flash
- **名稱**：`execution_summary_agent`
- **角色**：摘要所有已啟動代理程式的輸出
- **動態指令**：根據啟動的代理程式產生
- **內容包含**：設定為「無」以專注於摘要

## 主要功能

- **動態代理程式選擇**：根據使用者輸入自動決定需要哪些代理程式
- **平行執行**：多個相關代理程式可以透過 `ParallelAgent` 同時工作
- **相關性篩選**：如果代理程式與目前狀態無關，則使用回呼機制跳過執行
- **狀態工作流程**：透過 `ToolContext` 維護執行狀態
- **執行摘要**：自動摘要所有已啟動代理程式的結果
- **循序協調**：使用 `SequentialAgent` 確保適當的執行流程

## 用法

工作流程遵循此模式：

1. 使用者向根代理程式 (`execution_manager_agent`) 提供輸入
2. 管理員分析請求並識別相關代理程式 (`code_agent`、`math_agent`)
3. 如果使用者意圖不清楚，管理員會在繼續之前要求澄清
4. 管理員使用 `update_execution_plan` 更新執行計畫
5. 控制權轉移到 `plan_execution_agent`
6. `worker_parallel_agent` (ParallelAgent) 僅根據更新的計畫執行相關代理程式
7. `execution_summary_agent` 摘要所有已啟動代理程式的結果

### 範例查詢

**需要澄清的模糊請求：**

```
> hi
> Help me do this.
```

根代理程式 (`execution_manager_agent`) 會問候使用者並要求澄清其特定工作。

**僅數學請求：**

```
> What's 1+1?
```

只有 `math_agent` 執行，而 `code_agent` 被跳過。

**多領域請求：**

```
> What's 1+11? Write a python function to verify it.
```

`code_agent` 和 `math_agent` 平行執行，然後進行摘要。

## 可用的執行代理程式

- `code_agent` - 用於程式碼產生和程式設計工作
- `math_agent` - 用於數學計算和分析

## 實作細節

- 使用 Google ADK 代理程式框架
- 透過 `before_agent_callback_check_relevance` 實作基於回呼的相關性檢查
- 透過 `ToolContext` 和狀態金鑰維護狀態
- 支援使用 `ParallelAgent` 進行平行代理程式執行
- 使用 `SequentialAgent` 進行協調的執行流程
- 根據已啟動的代理程式為摘要代理程式動態產生指令
- 代理程式輸出儲存在具有 `{agent_name}_output` 金鑰的狀態中
