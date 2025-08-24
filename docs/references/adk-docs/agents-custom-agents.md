!!! warning "進階概念"

    透過直接實作 `_run_async_impl` (或其在其他語言中的等效方法) 來建構自訂代理提供了強大的控制權，但比使用預先定義的 `LlmAgent` 或標準 `WorkflowAgent` 類型更複雜。我們建議您在處理自訂協調邏輯之前，先了解那些基礎的代理類型。

# 自訂代理

自訂代理在 ADK 中提供了極致的靈活性，允許您透過直接繼承 `BaseAgent` 並實作您自己的控制流程來定義**任意的協調邏輯**。這超越了 `SequentialAgent`、`LoopAgent` 和 `ParallelAgent` 的預先定義模式，使您能夠建構高度特定和複雜的代理工作流程。

## 簡介：超越預先定義的工作流程

### 什麼是自訂代理？

自訂代理基本上是您建立的任何繼承自 `google.adk.agents.BaseAgent` 的類別，並在其 `_run_async_impl` 非同步方法中實作其核心執行邏輯。您可以完全控制此方法如何呼叫其他代理 (子代理)、管理狀態和處理事件。

!!! Note
    用於實作代理核心非同步邏輯的特定方法名稱可能會因 SDK 語言而略有不同 (例如，Java 中的 `runAsyncImpl`，Python 中的 `_run_async_impl`)。有關詳細資訊，請參閱特定語言的 API 文件。

### 為什麼要使用它們？

雖然標準的[工作流程代理](agents-workflow-agents.md) (`SequentialAgent`、`LoopAgent`、`ParallelAgent`) 涵蓋了常見的協調模式，但當您的需求包括以下內容時，您將需要一個自訂代理：

* **條件邏輯：** 根據執行階段條件或先前步驟的結果執行不同的子代理或採取不同的路徑。
* **複雜的狀態管理：** 實作複雜的邏輯來維護和更新整個工作流程中的狀態，超越簡單的循序傳遞。
* **外部整合：** 在協調流程控制中直接整合對外部 API、資料庫或自訂函式庫的呼叫。
* **動態代理選擇：** 根據對情況或輸入的動態評估來選擇接下來要執行的子代理。
* **獨特的工作流程模式：** 實作不符合標準順序、平行或循環結構的協調邏輯。


![intro_components.png](../assets/custom-agent-flow.png)


## 實作自訂邏輯：

任何自訂代理的核心都是您定義其獨特非同步行為的方法。此方法可讓您協調子代理並管理執行流程。

=== "Python"

      任何自訂代理的核心都是 `_run_async_impl` 方法。這就是您定義其獨特行為的地方。
      
      * **簽章：** `async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:`
      * **非同步產生器：** 它必須是一個 `async def` 函式並傳回一個 `AsyncGenerator`。這允許它將子代理或其自身邏輯產生的事件 `yield` 回執行器。
      * **`ctx` (InvocationContext)：** 提供對關鍵執行階段資訊的存取，最重要的是 `ctx.session.state`，這是由您的自訂代理協調的步驟之間共用資料的主要方式。

=== "Java"

    任何自訂代理的核心都是您從 `BaseAgent` 覆寫的 `runAsyncImpl` 方法。

    *   **簽章：** `protected Flowable<Event> runAsyncImpl(InvocationContext ctx)`
    *   **反應式串流 (`Flowable`)：** 它必須傳回一個 `io.reactivex.rxjava3.core.Flowable<Event>`。此 `Flowable` 表示將由自訂代理的邏輯產生的事件串流，通常是透過組合或轉換來自子代理的多個 `Flowable`。
    *   **`ctx` (InvocationContext)：** 提供對關鍵執行階段資訊的存取，最重要的是 `ctx.session().state()`，它是一個 `java.util.concurrent.ConcurrentMap<String, Object>`。這是由您的自訂代理協調的步驟之間共用資料的主要方式。

**核心非同步方法中的主要功能：**

=== "Python"

    1. **呼叫子代理：** 您使用其 `run_async` 方法呼叫子代理 (通常儲存為實例屬性，如 `self.my_llm_agent`) 並產生其事件：

          ```python
          async for event in self.some_sub_agent.run_async(ctx):
              # 可選地檢查或記錄事件
              yield event # 將事件向上传遞
          ```

    2. **管理狀態：** 從會話狀態字典 (`ctx.session.state`) 讀取和寫入，以在子代理呼叫之間傳遞資料或做出決策：
          ```python
          # 讀取先前代理設定的資料
          previous_result = ctx.session.state.get("some_key")
      
          # 根據狀態做出決策
          if previous_result == "some_value":
              # ... 呼叫特定的子代理 ...
          else:
              # ... 呼叫另一個子代理 ...
      
          # 為後續步驟儲存結果 (通常透過子代理的 output_key 完成)
          # ctx.session.state["my_custom_result"] = "calculated_value"
          ```

    3. **實作控制流程：** 使用標準的 Python 結構 (`if`/`elif`/`else`、`for`/`while` 迴圈、`try`/`except`) 來建立涉及您的子代理的複雜、條件式或迭代式工作流程。

=== "Java"

    1. **呼叫子代理：** 您使用其非同步執行方法呼叫子代理 (通常儲存為實例屬性或物件) 並傳回其事件串流：

           您通常使用 RxJava 運算子 (如 `concatWith`、`flatMapPublisher` 或 `concatArray`) 將來自子代理的 `Flowable` 鏈結起來。

           ```java
           // 範例：執行一個子代理
           // return someSubAgent.runAsync(ctx);
      
           // 範例：循序執行子代理
           Flowable<Event> firstAgentEvents = someSubAgent1.runAsync(ctx)
               .doOnNext(event -> System.out.println("來自代理 1 的事件：" + event.id()));
      
           Flowable<Event> secondAgentEvents = Flowable.defer(() ->
               someSubAgent2.runAsync(ctx)
                   .doOnNext(event -> System.out.println("來自代理 2 的事件：" + event.id()))
           );
      
           return firstAgentEvents.concatWith(secondAgentEvents);
           ```
           如果後續階段的執行取決於先前階段的完成或狀態，則通常使用 `Flowable.defer()`。

    2. **管理狀態：** 從會話狀態讀取和寫入，以在子代理呼叫之間傳遞資料或做出決策。會話狀態是透過 `ctx.session().state()` 取得的 `java.util.concurrent.ConcurrentMap<String, Object>`。
        
        ```java
        // 讀取先前代理設定的資料
        Object previousResult = ctx.session().state().get("some_key");

        // 根據狀態做出決策
        if ("some_value".equals(previousResult)) {
            // ... 包含特定子代理 Flowable 的邏輯 ...
        } else {
            // ... 包含另一個子代理 Flowable 的邏輯 ...
        }

        // 為後續步驟儲存結果 (通常透過子代理的 output_key 完成)
        // ctx.session().state().put("my_custom_result", "calculated_value");
        ```

    3. **實作控制流程：** 使用標準語言結構 (`if`/`else`、迴圈、`try`/`catch`) 結合反應式運算子 (RxJava) 來建立複雜的工作流程。

          *   **條件式：** `Flowable.defer()` 根據條件選擇要訂閱哪個 `Flowable`，或者如果您正在過濾串流中的事件，則使用 `filter()`。
          *   **迭代式：** `repeat()`、`retry()` 等運算子，或透過建構您的 `Flowable` 鏈以根據條件遞歸地呼叫其自身的部分 (通常使用 `flatMapPublisher` 或 `concatMap` 管理)。

## 管理子代理和狀態

通常，一個自訂代理會協調其他代理 (如 `LlmAgent`、`LoopAgent` 等)。

* **初始化：** 您通常將這些子代理的實例傳遞到您的自訂代理的建構函式中，並將它們儲存為實例欄位/屬性 (例如，`this.story_generator = story_generator_instance` 或 `self.story_generator = story_generator_instance`)。這使得它們可以在自訂代理的核心非同步執行邏輯中存取 (例如：`_run_async_impl` 方法)。
* **子代理列表：** 使用其 `super()` 建構函式初始化 `BaseAgent` 時，您應該傳遞一個 `sub agents` 列表。此列表會告知 ADK 框架哪些代理是此自訂代理的直接層次結構的一部分。即使您的核心執行邏輯 (`_run_async_impl`) 透過 `self.xxx_agent` 直接呼叫代理，這對於生命週期管理、內省以及潛在的未來路由功能等框架功能也很重要。請包含您的自訂邏輯在最上層直接呼叫的代理。
* **狀態：** 如前所述，`ctx.session.state` 是子代理 (特別是使用 `output key` 的 `LlmAgent`) 將結果傳回協調器以及協調器將必要輸入向下傳遞的標準方式。

## 設計模式範例：`StoryFlowAgent`

讓我們用一個範例模式來說明自訂代理的強大功能：一個具有條件邏輯的多階段內容生成工作流程。

**目標：** 建立一個系統，該系統可以生成一個故事，透過批判和修訂反覆地完善它，執行最終檢查，並且至關重要的是，*如果最終的語氣檢查失敗，則重新生成故事*。

**為什麼要自訂？** 這裡需要自訂代理的核心要求是**基於語氣檢查的條件式重新生成**。標準工作流程代理沒有根據子代理任務結果進行內建條件分支的功能。我們需要在協調器中加入自訂邏輯 (`if tone == "negative": ...`)。

---

### 第 1 部分：簡化的自訂代理初始化

=== "Python"

    我們定義繼承自 `BaseAgent` 的 `StoryFlowAgent`。在 `__init__` 中，我們將必要的子代理 (傳入) 儲存為實例屬性，並告知 `BaseAgent` 框架此自訂代理將直接協調的最上層代理。
    
    ```python
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:init"
    ```

=== "Java"

    我們透過擴充 `BaseAgent` 來定義 `StoryFlowAgentExample`。在其**建構函式**中，我們將必要的子代理實例 (作為參數傳遞) 儲存為實例欄位。這些最上層的子代理，此自訂代理將直接協調，也作為列表傳遞給 `BaseAgent` 的 `super` 建構函式。

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:init"
    ```
---

### 第 2 部分：定義自訂執行邏輯

=== "Python"

    此方法使用標準的 Python async/await 和控制流程來協調子代理。
    
    ```python
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:executionlogic"
    ```
    **邏輯說明：**

    1. 初始的 `story_generator` 執行。其輸出預期在 `ctx.session.state["current_story"]` 中。
    2. `loop_agent` 執行，它在內部循序呼叫 `critic` 和 `reviser` `max_iterations` 次。它們從/向狀態讀取/寫入 `current_story` 和 `criticism`。
    3. `sequential_agent` 執行，呼叫 `grammar_check` 然後 `tone_check`，讀取 `current_story` 並將 `grammar_suggestions` 和 `tone_check_result` 寫入狀態。
    4. **自訂部分：** `if` 陳述式檢查來自狀態的 `tone_check_result`。如果它是「negative」，則會*再次*呼叫 `story_generator`，覆寫狀態中的 `current_story`。否則，流程結束。


=== "Java"
    
    `runAsyncImpl` 方法使用 RxJava 的 Flowable 串流和運算子來協調子代理的非同步控制流程。

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:executionlogic"
    ```
    **邏輯說明：**

    1. 初始的 `storyGenerator.runAsync(invocationContext)` Flowable 被執行。其輸出預期在 `invocationContext.session().state().get("current_story")` 中。
    2. `loopAgent` 的 Flowable 接下來執行 (由於 `Flowable.concatArray` 和 `Flowable.defer`)。LoopAgent 在內部循序呼叫 `critic` 和 `reviser` 子代理，最多 `maxIterations` 次。它們從/向狀態讀取/寫入 `current_story` 和 `criticism`。
    3. 然後，`sequentialAgent` 的 Flowable 執行。它呼叫 `grammar_check` 然後 `tone_check`，讀取 `current_story` 並將 `grammar_suggestions` 和 `tone_check_result` 寫入狀態。
    4. **自訂部分：** 在 sequentialAgent 完成後，`Flowable.defer` 中的邏輯會檢查來自 `invocationContext.session().state()` 的 "tone_check_result"。如果它是「negative」，`storyGenerator` Flowable 會被*有條件地串連*並再次執行，覆寫 "current_story"。否則，將使用一個空的 Flowable，整個工作流程將繼續完成。

---

### 第 3 部分：定義 LLM 子代理

這些是標準的 `LlmAgent` 定義，負責特定的任務。它們的 `output key` 參數對於將結果放置到 `session.state` 中至關重要，以便其他代理或自訂協調器可以存取它們。

!!! tip "在說明中直接注入狀態"
    請注意 `story_generator` 的說明。`{var}` 語法是一個佔位符。在將說明傳送給 LLM 之前，ADK 框架會自動將 (範例：`{topic}`) 替換為 `session.state['topic']` 的值。這是使用說明中的範本為代理提供上下文的建議方法。有關更多詳細資訊，請參閱[狀態文件](../sessions/state.md#accessing-session-state-in-agent-instructions)。

=== "Python"

    ```python
    GEMINI_2_FLASH = "gemini-2.0-flash" # 定義模型常數
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:llmagents"
    ```
=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:llmagents"
    ```

---

### 第 4 部分：實例化並執行自訂代理

最後，您像往常一樣實例化您的 `StoryFlowAgent` 並使用 `Runner`。

=== "Python"

    ```python
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:story_flow_agent"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:story_flow_agent"
    ```

*(注意：完整的可執行程式碼，包括匯入和執行邏輯，可以在下面連結中找到。)*

---

## 完整程式碼範例

???+ "故事流程代理"

    === "Python"
    
        ```python
        # StoryFlowAgent 範例的完整可執行程式碼
        --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py"
        ```
    
    === "Java"
    
        ```java
        # StoryFlowAgent 範例的完整可執行程式碼
        --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:full_code"
        ```
