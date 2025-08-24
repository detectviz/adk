# 執行階段 (Runtime)

## 什麼是執行階段？

ADK 執行階段 (Runtime) 是在使用者互動期間為您的代理程式應用程式提供動力的底層引擎。它是一個系統，負責接收您定義的代理程式、工具和回呼，並根據使用者輸入協調它們的執行，管理資訊流、狀態變更以及與外部服務（如大型語言模型 (LLM) 或儲存）的互動。

您可以將執行階段視為您代理程式應用程式的**「引擎」**。您定義各個部分（代理程式、工具），而執行階段則處理它們如何連接和協同運作以滿足使用者的請求。

## 核心理念：事件迴圈 (Event Loop)

ADK 執行階段的核心是一個**事件迴圈 (Event Loop)**。這個迴圈促進了 `Runner` 元件和您定義的「執行邏輯」(Execution Logic)（包括您的代理程式、它們所做的 LLM 呼叫、回呼和工具）之間的來回通訊。

![intro_components.png](../assets/event-loop.png)

簡單來說：

1. `Runner` 接收使用者查詢，並要求主 `Agent` 開始處理。
2. `Agent`（及其相關邏輯）執行，直到有東西要報告（例如回應、使用工具的請求或狀態變更）——然後它會**產生 (yield)** 或 **發出 (emit)** 一個 `Event`。
3. `Runner` 接收這個 `Event`，處理任何相關的動作（例如透過 `Services` 儲存狀態變更），並將事件轉發出去（例如，到使用者介面）。
4. 只有在 `Runner` 處理完事件*之後*，`Agent` 的邏輯才會從暫停的地方**恢復 (resume)**，此時它可能會看到 `Runner` 所提交變更的效果。
5. 這個循環會重複進行，直到代理程式對於目前的使用者查詢沒有更多事件可以產生為止。

這個事件驅動的迴圈是管理 ADK 如何執行您代理程式程式碼的基本模式。

## 心跳：事件迴圈 - 內部運作

事件迴圈是定義 `Runner` 與您的自訂程式碼（代理程式、工具、回呼，在設計文件中統稱為「執行邏輯」或「邏輯元件」）之間互動的核心操作模式。它建立了明確的責任分工：

!!! Note
    具體的方法名稱和參數名稱可能會因 SDK 語言而略有不同（例如，Java 中的 `agent_to_run.runAsync(...)`，Python 中的 `agent_to_run.run_async(...)`）。有關詳細資訊，請參閱特定語言的 API 文件。

### `Runner` 的角色（協調器）

`Runner` 作為單一使用者調用的中央協調器。它在迴圈中的職責是：

1. **啟動：** 接收終端使用者的查詢 (`new_message`)，並通常透過 `SessionService` 將其附加到會話歷史記錄中。
2. **開始：** 透過呼叫主代理程式的執行方法（例如，`agent_to_run.run_async(...)`）來啟動事件產生過程。
3. **接收與處理：** 等待代理程式邏輯 `yield` 或 `emit` 一個 `Event`。收到事件後，`Runner` 會**立即處理**它。這包括：
      * 使用設定的 `Services` (`SessionService`、`ArtifactService`、`MemoryService`) 來提交 `event.actions` 中指示的變更（如 `state_delta`、`artifact_delta`）。
      * 執行其他內部記錄。
4. **向上產生：** 將處理過的事件轉發出去（例如，到呼叫的應用程式或 UI 進行渲染）。
5. **迭代：** 通知代理程式邏輯，已產生事件的處理已完成，允許其恢復並產生*下一個*事件。

*概念性 `Runner` 迴圈：*

=== "Python"

    ```python
    # Runner 主迴圈邏輯的簡化視圖
    def run(new_query, ...) -> Generator[Event]:
        # 1. 將 new_query 附加到會話事件歷史記錄 (透過 SessionService)
        session_service.append_event(session, Event(author='user', content=new_query))
    
        # 2. 透過呼叫代理程式來啟動事件迴圈
        agent_event_generator = agent_to_run.run_async(context)
    
        async for event in agent_event_generator:
            # 3. 處理產生的事件並提交變更
            session_service.append_event(session, event) # 提交狀態/產物差異等。
            # memory_service.update_memory(...) # 如果適用
            # artifact_service 可能已在代理程式執行期間透過 context 呼叫
    
            # 4. 向上產生事件以進行上游處理 (例如，UI 渲染)
            yield event
            # Runner 在產生後隱式地通知代理程式產生器可以繼續
    ```

=== "Java"

    ```java
    // Java 中 Runner 主迴圈邏輯的簡化概念視圖。
    public Flowable<Event> runConceptual(
        Session session,                  
        InvocationContext invocationContext, 
        Content newQuery                
        ) {
    
        // 1. 將 new_query 附加到會話事件歷史記錄 (透過 SessionService)
        // ...
        sessionService.appendEvent(session, userEvent).blockingGet();
    
        // 2. 透過呼叫代理程式來啟動事件流
        Flowable<Event> agentEventStream = agentToRun.runAsync(invocationContext);
    
        // 3. 處理每個產生的事件，提交變更，並「產生」或「發出」
        return agentEventStream.map(event -> {
            // 這會改變會話物件 (新增事件，應用 stateDelta)。
            // appendEvent 的傳回值 (一個 Single<Event>) 在概念上
            // 只是處理後的事件本身。
            sessionService.appendEvent(session, event).blockingGet(); // 簡化的阻塞呼叫
    
            // memory_service.update_memory(...) // 如果適用 - 概念性的
            // artifact_service 可能已在代理程式執行期間透過 context 呼叫
    
            // 4. 「產生」事件以進行上游處理
            //    在 RxJava 中，在 map 中傳回事件有效地將其產生給下一個運算子或訂閱者。
            return event;
        });
    }
    ```

### 執行邏輯的角色（代理程式、工具、回呼）

您在代理程式、工具和回呼中的程式碼負責實際的計算和決策。它與迴圈的互動包括：

1. **執行：** 根據目前的 `InvocationContext` 執行其邏輯，包括在執行恢復時的會話狀態。
2. **產生：** 當邏輯需要通訊（傳送訊息、呼叫工具、報告狀態變更）時，它會建構一個包含相關內容和動作的 `Event`，然後將此事件 `yield` 回 `Runner`。
3. **暫停：** 關鍵的是，代理程式邏輯的執行在 `yield` 陳述式（或 RxJava 中的 `return`）之後**立即暫停**。它會等待 `Runner` 完成步驟 3（處理和提交）。
4. **恢復：** *只有在* `Runner` 處理完已產生的事件後，代理程式邏輯才會從緊接在 `yield` 之後的陳述式恢復執行。
5. **查看更新後的狀態：** 恢復後，代理程式邏輯現在可以可靠地存取會話狀態 (`ctx.session.state`)，該狀態反映了由 `Runner` 從*先前產生的*事件中提交的變更。

*概念性執行邏輯：*

=== "Python"

    ```python
    # Agent.run_async、回呼或工具內部邏輯的簡化視圖
    
    # ... 先前的程式碼根據目前狀態執行 ...
    
    # 1. 確定需要變更或輸出，建構事件
    # 範例：更新狀態
    update_data = {'field_1': 'value_2'}
    event_with_state_change = Event(
        author=self.name,
        actions=EventActions(state_delta=update_data),
        content=types.Content(parts=[types.Part(text="狀態已更新。")])
        # ... 其他事件欄位 ...
    )
    
    # 2. 將事件產生給 Runner 進行處理和提交
    yield event_with_state_change
    # <<<<<<<<<<<< 執行在此處暫停 >>>>>>>>>>>>
    
    # <<<<<<<<<<<< RUNNER 處理並提交事件 >>>>>>>>>>>>
    
    # 3. 僅在 Runner 完成處理上述事件後才恢復執行。
    # 現在，Runner 提交的狀態已可靠地反映出來。
    # 後續程式碼可以安全地假設已產生的事件所做的變更已發生。
    val = ctx.session.state['field_1']
    # 此處 `val` 保證為 "value_2" (假設 Runner 成功提交)
    print(f"恢復執行。field_1 的值現在是：{val}")
    
    # ... 後續程式碼繼續 ...
    # 稍後可能會產生另一個事件...
    ```

=== "Java"

    ```java
    // Agent.runAsync、回呼或工具內部邏輯的簡化視圖
    // ... 先前的程式碼根據目前狀態執行 ...
    
    // 1. 確定需要變更或輸出，建構事件
    # 範例：更新狀態
    ConcurrentMap<String, Object> updateData = new ConcurrentHashMap<>();
    updateData.put("field_1", "value_2");
    
    EventActions actions = EventActions.builder().stateDelta(updateData).build();
    Content eventContent = Content.builder().parts(Part.fromText("狀態已更新。")).build();
    
    Event eventWithStateChange = Event.builder()
        .author(self.name())
        .actions(actions)
        .content(Optional.of(eventContent))
        // ... 其他事件欄位 ...
        .build();
    
    // 2. 「產生」事件。在 RxJava 中，這意味著將其發射到流中。
    //    Runner (或上游消費者) 將訂閱此 Flowable。
    //    當 Runner 收到此事件時，它將處理它 (例如，呼叫 sessionService.appendEvent)。
    //    Java ADK 中的 'appendEvent' 會改變 'ctx' (InvocationContext) 中持有的 'Session' 物件。
    
    // <<<<<<<<<<<< 概念性暫停點 >>>>>>>>>>>>
    // 在 RxJava 中，'eventWithStateChange' 的發射會發生，然後流
    // 可能會繼續使用 'flatMap' 或 'concatMap' 運算子，代表
    // 在 Runner 處理此事件*之後*的邏輯。
    
    // 為了模擬「僅在 Runner 完成處理後才恢復執行」：
    // Runner 的 `appendEvent` 本身通常是一個非同步操作 (傳回 Single<Event>)。
    // 代理程式的流程需要被建構，使得依賴於已提交狀態的後續邏輯
    // 在該 `appendEvent` 完成*之後*執行。
    
    // 這就是 Runner 通常協調它的方式：
    // Runner:
    //   agent.runAsync(ctx)
    //     .concatMapEager(eventFromAgent ->
    //         sessionService.appendEvent(ctx.session(), eventFromAgent) // 這會更新 ctx.session().state()
    //             .toFlowable() // 在處理後發出事件
    //     )
    //     .subscribe(processedEvent -> { /* UI 渲染 processedEvent */ });
    
    // 因此，在代理程式自己的邏輯中，如果它需要在它產生的事件
    // 被處理並且其狀態變更反映在 ctx.session().state() 中*之後*做某事，
    // 該後續邏輯通常會在其反應式鏈的另一步中。
    
    // 對於這個概念性範例，我們將發出事件，然後模擬「恢復」
    // 作為 Flowable 鏈中的後續操作。
    
    return Flowable.just(eventWithStateChange) // 步驟 2：產生事件
        .concatMap(yieldedEvent -> {
            // <<<<<<<<<<<< RUNNER 概念性地處理並提交事件 >>>>>>>>>>>>
            // 此時，在一個真正的 runner 中，ctx.session().appendEvent(yieldedEvent) 會被
            // Runner 呼叫，並且 ctx.session().state() 會被更新。
            // 因為我們在代理程式的概念性邏輯*內部*試圖模擬這個，
            // 我們假設 Runner 的動作已經隱式地更新了我們的 'ctx.session()'。
    
            // 3. 恢復執行。
            // 現在，Runner 提交的狀態 (透過 sessionService.appendEvent)
            // 已可靠地反映在 ctx.session().state() 中。
            Object val = ctx.session().state().get("field_1");
            // 此處 `val` 保證為 "value_2"，因為 Runner 呼叫的 `sessionService.appendEvent`
            // 會更新 `ctx` 物件內的會話狀態。
    
            System.out.println("恢復執行。field_1 的值現在是：" + val);
    
            // ... 後續程式碼繼續 ...
            // 如果這個後續程式碼需要產生另一個事件，它會在這裡這麼做。
    ```

`Runner` 和您的執行邏輯之間這種合作性的產生/暫停/恢復循環，由 `Event` 物件所媒介，構成了 ADK 執行階段的核心。

## 執行階段的主要元件

在 ADK 執行階段中，有幾個元件協同運作以執行代理程式的調用。了解它們的角色有助於闡明事件迴圈的功能：

1. ### `Runner`

      * **角色：** 單一使用者查詢 (`run_async`) 的主要進入點和協調器。
      * **功能：** 管理整個事件迴圈，接收執行邏輯產生的事件，與服務協調以處理和提交事件動作（狀態/產物變更），並將處理過的事件向上游轉發（例如，到 UI）。它基本上是根據產生的事件逐輪驅動對話。(定義於 `google.adk.runners.runner`)。

2. ### 執行邏輯元件

      * **角色：** 包含您的自訂程式碼和核心代理程式功能的部分。
      * **元件：**
      * `Agent` (`BaseAgent`, `LlmAgent` 等)：您的主要邏輯單元，處理資訊並決定動作。它們實作了產生事件的 `_run_async_impl` 方法。
      * `Tools` (`BaseTool`, `FunctionTool`, `AgentTool` 等)：代理程式（通常是 `LlmAgent`）用來與外部世界互動或執行特定任務的外部函式或功能。它們執行並傳回結果，然後將結果包裝在事件中。
      * `Callbacks` (函式)：附加到代理程式的使用者定義函式（例如 `before_agent_callback`、`after_model_callback`），它們掛鉤到執行流程中的特定點，可能會修改行為或狀態，其效果會被捕捉在事件中。
      * **功能：** 執行實際的思考、計算或外部互動。它們透過**產生 `Event` 物件**並暫停直到 `Runner` 處理它們來傳達其結果或需求。

3. ### `Event`

      * **角色：** 在 `Runner` 和執行邏輯之間來回傳遞的訊息。
      * **功能：** 代表一個原子性的發生（使用者輸入、代理程式文字、工具呼叫/結果、狀態變更請求、控制信號）。它既攜帶了發生的內容，也攜帶了預期的副作用（`actions`，如 `state_delta`）。

4. ### `Services`

      * **角色：** 負責管理持久性或共享資源的後端元件。主要由 `Runner` 在事件處理期間使用。
      * **元件：**
      * `SessionService` (`BaseSessionService`, `InMemorySessionService` 等)：管理 `Session` 物件，包括儲存/載入它們、將 `state_delta` 應用於會話狀態，以及將事件附加到 `event history`。
      * `ArtifactService` (`BaseArtifactService`, `InMemoryArtifactService`, `GcsArtifactService` 等)：管理二進位產物資料的儲存和檢索。雖然 `save_artifact` 是在執行邏輯期間透過上下文呼叫的，但事件中的 `artifact_delta` 確認了 `Runner/SessionService` 的動作。
      * `MemoryService` (`BaseMemoryService` 等)：(可選) 管理使用者跨會話的長期語義記憶。
      * **功能：** 提供持久層。`Runner` 與它們互動，以確保在執行邏輯恢復*之前*，`event.actions` 所指示的變更已可靠地儲存。

5. ### `Session`

      * **角色：** 一個資料容器，保存使用者和應用程式之間*一個特定對話*的狀態和歷史記錄。
      * **功能：** 儲存目前的 `state` 字典、所有過去 `events` (`event history`) 的列表，以及對相關產物的引用。它是互動的主要記錄，由 `SessionService` 管理。

6. ### `Invocation`

      * **角色：** 一個概念性術語，代表從 `Runner` 收到*單一*使用者查詢的那一刻起，直到代理程式邏輯完成為該查詢產生事件為止所發生的一切。
      * **功能：** 一次調用可能涉及多次代理程式執行（如果使用代理程式轉移或 `AgentTool`）、多次 LLM 呼叫、工具執行和回呼執行，所有這些都由 `InvocationContext` 中的單一 `invocation_id` 聯繫在一起。

這些參與者透過事件迴圈持續互動，以處理使用者的請求。

## 運作方式：簡化的調用

讓我們追蹤一個涉及 LLM 代理程式呼叫工具的典型使用者查詢的簡化流程：

![intro_components.png](../assets/invocation-flow.png)

### 逐步分解

1. **使用者輸入：** 使用者傳送一個查詢（例如，「法國的首都是什麼？」）。
2. **`Runner` 啟動：** `Runner.run_async` 開始。它與 `SessionService` 互動以載入相關的 `Session`，並將使用者查詢作為第一個 `Event` 新增到會話歷史記錄中。準備好一個 `InvocationContext` (`ctx`)。
3. **代理程式執行：** `Runner` 在指定的根代理程式（例如，一個 `LlmAgent`）上呼叫 `agent.run_async(ctx)`。
4. **LLM 呼叫（範例）：** `Agent_Llm` 確定它需要資訊，也許是透過呼叫一個工具。它為 `LLM` 準備一個請求。讓我們假設 LLM 決定呼叫 `MyTool`。
5. **產生 FunctionCall 事件：** `Agent_Llm` 從 LLM 收到 `FunctionCall` 回應，將其包裝在一個 `Event(author='Agent_Llm', content=Content(parts=[Part(function_call=...)]))` 中，並 `yields` 或 `emits` 這個事件。
6. **代理程式暫停：** `Agent_Llm` 的執行在 `yield` 之後立即暫停。
7. **`Runner` 處理：** `Runner` 收到 FunctionCall 事件。它將其傳遞給 `SessionService` 以記錄在歷史記錄中。然後 `Runner` 將事件向上游產生給 `User`（或應用程式）。
8. **代理程式恢復：** `Runner` 通知事件已處理，`Agent_Llm` 恢復執行。
9. **工具執行：** `Agent_Llm` 的內部流程現在繼續執行請求的 `MyTool`。它呼叫 `tool.run_async(...)`。
10. **工具傳回結果：** `MyTool` 執行並傳回其結果（例如，`{'result': 'Paris'}`）。
11. **產生 FunctionResponse 事件：** 代理程式 (`Agent_Llm`) 將工具結果包裝到一個包含 `FunctionResponse` 部分的 `Event` 中（例如，`Event(author='Agent_Llm', content=Content(role='user', parts=[Part(function_response=...)]))`）。如果工具修改了狀態 (`state_delta`) 或儲存了產物 (`artifact_delta`)，此事件也可能包含 `actions`。代理程式 `yield`s 這個事件。
12. **代理程式暫停：** `Agent_Llm` 再次暫停。
13. **`Runner` 處理：** `Runner` 收到 FunctionResponse 事件。它將其傳遞給 `SessionService`，後者會應用任何 `state_delta`/`artifact_delta` 並將事件新增到歷史記錄中。`Runner` 將事件向上游產生。
14. **代理程式恢復：** `Agent_Llm` 恢復，現在知道工具結果和任何狀態變更都已提交。
15. **最終 LLM 呼叫（範例）：** `Agent_Llm` 將工具結果傳回給 `LLM` 以產生自然語言回應。
16. **產生最終文字事件：** `Agent_Llm` 從 `LLM` 收到最終文字，將其包裝在一個 `Event(author='Agent_Llm', content=Content(parts=[Part(text=...)]))` 中，並 `yield`s 它。
17. **代理程式暫停：** `Agent_Llm` 暫停。
18. **`Runner` 處理：** `Runner` 收到最終文字事件，將其傳遞給 `SessionService` 以記錄歷史，並將其向上游產生給 `User`。這很可能被標記為 `is_final_response()`。
19. **代理程式恢復並完成：** `Agent_Llm` 恢復。完成此次調用的任務後，其 `run_async` 產生器結束。
20. **`Runner` 完成：** `Runner` 看到代理程式的產生器已耗盡，並完成此次調用的迴圈。

這種產生/暫停/處理/恢復的循環確保了狀態變更的一致應用，並且執行邏輯在產生事件後始終操作在最近提交的狀態上。

## 重要的執行階段行為

了解 ADK 執行階段如何處理狀態、串流和非同步操作的幾個關鍵方面，對於建立可預測和高效的代理程式至關重要。

### 狀態更新與提交時機

* **規則：** 當您的程式碼（在代理程式、工具或回呼中）修改會話狀態時（例如，`context.state['my_key'] = 'new_value'`），此變更最初會被本地記錄在目前的 `InvocationContext` 中。只有在攜帶相應 `state_delta` 的 `Event` 在其 `actions` 中被您的程式碼 `yield` 並隨後由 `Runner` 處理*之後*，該變更才**保證被持久化**（由 `SessionService` 儲存）。

* **含義：** 在從 `yield` 恢復後執行的程式碼可以可靠地假設在*已產生的事件*中發出的狀態變更已被提交。

=== "Python"

    ```python
    # 代理程式邏輯內部 (概念性)
    
    # 1. 修改狀態
    ctx.session.state['status'] = 'processing'
    event1 = Event(..., actions=EventActions(state_delta={'status': 'processing'}))
    
    # 2. 產生帶有 delta 的事件
    yield event1
    # --- 暫停 --- Runner 處理 event1，SessionService 提交 'status' = 'processing' ---
    
    # 3. 恢復執行
    # 現在可以安全地依賴已提交的狀態
    current_status = ctx.session.state['status'] # 保證為 'processing'
    print(f"恢復後的狀態：{current_status}")
    ```

=== "Java"

    ```java
    // 代理程式邏輯內部 (概念性)
    // ... 先前的程式碼根據目前狀態執行 ...
    
    // 1. 準備狀態修改並建構事件
    ConcurrentHashMap<String, Object> stateChanges = new ConcurrentHashMap<>();
    stateChanges.put("status", "processing");
    
    EventActions actions = EventActions.builder().stateDelta(stateChanges).build();
    Content content = Content.builder().parts(Part.fromText("狀態更新：處理中")).build();
    
    Event event1 = Event.builder()
        .actions(actions)
        // ...
        .build();
    
    // 2. 產生帶有 delta 的事件
    return Flowable.just(event1)
        .map(
            emittedEvent -> {
                // --- 概念性暫停與 RUNNER 處理 ---
                // 3. 恢復執行 (概念性)
                // 現在可以安全地依賴已提交的狀態。
                String currentStatus = (String) ctx.session().state().get("status");
                System.out.println("恢復後的狀態 (在代理程式邏輯內部)：" + currentStatus); // 保證為 'processing'
    
                // 事件本身 (event1) 被傳遞下去。
                // 如果此代理程式步驟中的後續邏輯產生了*另一個*事件，
                // 您將使用 concatMap 來發出該新事件。
                return emittedEvent;
            });
    
    // ... 後續代理程式邏輯可能涉及進一步的反應式運算子
    // 或根據現在更新的 `ctx.session().state()` 發出更多事件。
    ```

### 會話狀態的「髒讀」

* **定義：** 雖然提交發生在 `yield` *之後*，但在同一次調用中稍後執行，但在狀態變更事件實際被產生和處理*之前*執行的程式碼，**通常可以看到本地的、未提交的變更**。這有時被稱為「髒讀」(dirty read)。
* **範例：**

=== "Python"

    ```python
    # before_agent_callback 中的程式碼
    callback_context.state['field_1'] = 'value_1'
    # 狀態在本地設定為 'value_1'，但尚未由 Runner 提交
    
    # ... 代理程式執行 ...
    
    # 在同一次調用中稍後呼叫的工具中的程式碼
    # 可讀 (髒讀)，但 'value_1' 尚未保證持久化。
    val = tool_context.state['field_1'] # 此處 'val' 很可能是 'value_1'
    print(f"工具中的髒讀值：{val}")
    
    # 假設攜帶 state_delta={'field_1': 'value_1'} 的事件
    # 在此工具執行後被產生並由 Runner 處理。
    ```

=== "Java"

    ```java
    // 修改狀態 - BeforeAgentCallback 中的程式碼
    // 並將此變更暫存在 callbackContext.eventActions().stateDelta() 中。
    callbackContext.state().put("field_1", "value_1");

    // --- 代理程式執行 ... ---

    // --- 在同一次調用中稍後呼叫的工具中的程式碼 ---
    // 可讀 (髒讀)，但 'value_1' 尚未保證持久化。
    Object val = toolContext.state().get("field_1"); // 此處 'val' 很可能是 'value_1'
    System.out.println("工具中的髒讀值：" + val);
    // 假設攜帶 state_delta={'field_1': 'value_1'} 的事件
    // 在此工具執行後被產生並由 Runner 處理。
    ```

* **含義：**
  * **好處：** 允許您邏輯中單一複雜步驟內的不同部分（例如，在下一次 LLM 輪次之前的多個回呼或工具呼叫）使用狀態進行協調，而無需等待完整的產生/提交循環。
  * **警告：** 過度依賴髒讀來處理關鍵邏輯可能存在風險。如果調用在攜帶 `state_delta` 的事件被產生並由 `Runner` 處理*之前*失敗，未提交的狀態變更將會遺失。對於關鍵的狀態轉換，請確保它們與成功處理的事件相關聯。

### 串流與非串流輸出 (`partial=True`)

這主要涉及如何處理來自 LLM 的回應，尤其是在使用串流生成 API 時。

* **串流：** LLM 逐個權杖或以小區塊的形式產生其回應。
  * 框架（通常在 `BaseLlmFlow` 內）為單一概念性回應產生多個 `Event` 物件。這些事件中的大多數都將具有 `partial=True`。
  * `Runner` 在收到具有 `partial=True` 的事件時，通常會**立即將其向上游轉發**（用於 UI 顯示），但會**跳過處理其 `actions`**（如 `state_delta`）。
  * 最終，框架會為該回應產生一個最終事件，標記為非部分（`partial=False` 或透過 `turn_complete=True` 隱式表示）。
  * `Runner` **僅完全處理此最終事件**，提交任何相關的 `state_delta` 或 `artifact_delta`。
* **非串流：** LLM 一次產生整個回應。框架會產生一個標記為非部分的單一事件，`Runner` 會完全處理該事件。
* **重要性：** 確保狀態變更基於來自 LLM 的*完整*回應以原子方式且僅應用一次，同時仍允許 UI 在生成文字時逐步顯示。

## 非同步是主要的 (`run_async`)

* **核心設計：** ADK 執行階段基本上是建立在非同步函式庫（如 Python 的 `asyncio` 和 Java 的 `RxJava`）之上，以有效地處理並行操作（如等待 LLM 回應或工具執行）而不會阻塞。
* **主要進入點：** `Runner.run_async` 是執行代理程式調用的主要方法。所有核心可執行元件（代理程式、特定流程）都在內部使用 `非同步` 方法。
* **同步便利性 (`run`)：** 同步的 `Runner.run` 方法主要為方便起見而存在（例如，在簡單的腳本或測試環境中）。然而，在內部，`Runner.run` 通常只是呼叫 `Runner.run_async` 並為您管理非同步事件迴圈的執行。
* **開發人員體驗：** 我們建議將您的應用程式（例如，使用 ADK 的 Web 伺服器）設計為非同步的，以獲得最佳效能。在 Python 中，這意味著使用 `asyncio`；在 Java 中，利用 `RxJava` 的反應式程式設計模型。
* **同步回呼/工具：** ADK 框架支援工具和回呼的非同步和同步函式。
    * **阻塞 I/O：** 對於長時間執行的同步 I/O 操作，框架會嘗試防止停頓。Python ADK 可能會使用 `asyncio.to_thread`，而 Java ADK 通常依賴適當的 RxJava 調度器或包裝器來進行阻塞呼叫。
    * **CPU 密集型工作：** 純粹的 CPU 密集型同步任務在這兩種環境中仍會阻塞其執行緒。

了解這些行為有助於您編寫更穩健的 ADK 應用程式，並偵錯與狀態一致性、串流更新和非同步執行相關的問題。
