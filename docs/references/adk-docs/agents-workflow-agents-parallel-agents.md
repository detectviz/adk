# 平行代理

`ParallelAgent` 是一個[工作流程代理](index.md)，它可以*同時*執行其子代理。這大大加快了可以獨立執行任務的工作流程。

在以下情況下使用 `ParallelAgent`：對於優先考慮速度並涉及獨立、資源密集型任務的場景，`ParallelAgent` 有助於高效的平行執行。**當子代理在沒有依賴關係的情況下操作時，它們的任務可以同時執行**，從而顯著減少整體處理時間。

與其他[工作流程代理](index.md)一樣，`ParallelAgent` 不由 LLM 驅動，因此其執行方式是確定性的。也就是說，工作流程代理只關心其執行 (即平行執行子代理)，而不關心其內部邏輯；工作流程代理的工具或子代理可能會或可能不會利用 LLM。

### 範例

這種方法對於多源資料擷取或大量計算等操作特別有益，因為平行化可以帶來顯著的效能提升。重要的是，此策略假設同時執行的代理之間沒有共用狀態或直接資訊交換的內在需求。

### 運作方式

當呼叫 `ParallelAgent` 的 `run_async()` 方法時：

1. **並行執行：** 它會*同時*啟動 `sub_agents` 列表中*每個*子代理的 `run_async()` 方法。這意味著所有代理（大約）在同一時間開始執行。
2. **獨立分支：** 每個子代理都在自己的執行分支中操作。在執行期間，這些分支之間***沒有*自動共用對話歷史記錄或狀態**。
3. **結果收集：** `ParallelAgent` 管理平行執行，並且通常在每個子代理完成後提供一種存取其結果的方式 (例如，透過結果或事件列表)。結果的順序可能不是確定性的。

### 獨立執行和狀態管理

了解 `ParallelAgent` 中的子代理是獨立執行的，這一點*至關重要*。如果您*需要*在這些代理之間進行通訊或資料共用，則必須明確地實作它。可能的方法包括：

* **共用 `InvocationContext`：** 您可以將一個共用的 `InvocationContext` 物件傳遞給每個子代理。此物件可以充當共用資料儲存。但是，您需要仔細管理對此共用上下文的並行存取 (例如，使用鎖) 以避免競爭條件。
* **外部狀態管理：** 使用外部資料庫、訊息佇列或其他機制來管理共用狀態並促進代理之間的通訊。
* **後處理：** 從每個分支收集結果，然後實作邏輯以在之後協調資料。

![Parallel Agent](../../assets/parallel-agent.png){: width="600"}

### 完整範例：平行網路研究

想像一下同時研究多個主題：

1. **研究員代理 1：** 一個研究「可再生能源」的 `LlmAgent`。
2. **研究員代理 2：** 一個研究「電動車技術」的 `LlmAgent`。
3. **研究員代理 3：** 一個研究「碳捕獲方法」的 `LlmAgent`。

    ```py
    ParallelAgent(sub_agents=[ResearcherAgent1, ResearcherAgent2, ResearcherAgent3])
    ```

這些研究任務是獨立的。使用 `ParallelAgent` 可以讓它們同時執行，與循序執行相比，可能會大大減少總研究時間。每個代理的結果將在它們完成後單獨收集。

???+ "完整程式碼"

    === "Python"
        ```py
         --8<-- "examples/python/snippets/agents/workflow-agents/parallel_agent_web_research.py:init"
        ```
    === "Java"
        ```java
         --8<-- "examples/java/snippets/src/main/java/agents/workflow/ParallelResearchPipeline.java:full_code"
        ```
