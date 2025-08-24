# 事件 (Events)

事件 (Events) 是代理開發套件 (Agent Development Kit, ADK) 中資訊流的基本單位。它們代表代理互動生命週期中的每一個重要事件，從最初的使用者輸入到最終回應以及其間的所有步驟。了解事件至關重要，因為它們是元件通訊、狀態管理和控制流導向的主要方式。

## 什麼是事件及其重要性

ADK 中的 `Event` 是一個不可變的記錄，代表代理執行中的特定點。它擷取了使用者訊息、代理回覆、使用工具的請求（函式呼叫）、工具結果、狀態變更、控制信號和錯誤。

=== "Python"
    技術上，它是 `google.adk.events.Event` 類別的實例，它在基本的 `LlmResponse` 結構上增加了必要的 ADK 特定元數據和一個 `actions` 酬載。

    ```python
    # 事件的概念結構 (Python)
    # from google.adk.events import Event, EventActions
    # from google.genai import types

    # class Event(LlmResponse): # 簡化視圖
    #     # --- LlmResponse 欄位 ---
    #     content: Optional[types.Content]
    #     partial: Optional[bool]
    #     # ... 其他回應欄位 ...

    #     # --- ADK 特定新增 ---
    #     author: str          # 'user' 或代理名稱
    #     invocation_id: str   # 整個互動執行的 ID
    #     id: str              # 此特定事件的唯一 ID
    #     timestamp: float     # 建立時間
    #     actions: EventActions # 對於副作用和控制很重要
    #     branch: Optional[str] # 階層路徑
    #     # ...
    ```

=== "Java"
    在 Java 中，這是 `com.google.adk.events.Event` 類別的實例。它也在一個基本的回應結構上增加了必要的 ADK 特定元數據和一個 `actions` 酬載。

    ```java
    // 事件的概念結構 (Java - 請參閱 com.google.adk.events.Event.java)
    // 簡化視圖，基於提供的 com.google.adk.events.Event.java
    // public class Event extends JsonBaseModel {
    //     // --- 類似於 LlmResponse 的欄位 ---
    //     private Optional<Content> content;
    //     private Optional<Boolean> partial;
    //     // ... 其他回應欄位，如 errorCode, errorMessage ...

    //     // --- ADK 特定新增 ---
    //     private String author;         // 'user' 或代理名稱
    //     private String invocationId;   // 整個互動執行的 ID
    //     private String id;             // 此特定事件的唯一 ID
    //     private long timestamp;        // 建立時間 (epoch 毫秒)
    //     private EventActions actions;  // 對於副作用和控制很重要
    //     private Optional<String> branch; // 階層路徑
    //     // ... 其他欄位，如 turnComplete, longRunningToolIds 等。
    // }
    ```

事件對於 ADK 的運作至關重要，原因如下：

1.  **通訊：** 它們作為使用者介面、`Runner`、代理、大型語言模型 (LLM) 和工具之間的標準訊息格式。一切都以 `Event` 的形式流動。

2.  **發出狀態和產物變更信號：** 事件攜帶狀態修改的指令並追蹤產物更新。`SessionService` 使用這些信號來確保持久性。在 Python 中，變更是透過 `event.actions.state_delta` 和 `event.actions.artifact_delta` 發出信號的。

3.  **控制流：** 像 `event.actions.transfer_to_agent` 或 `event.actions.escalate` 這樣的特定欄位作為指導框架的信號，決定下一個執行的代理或是否應終止迴圈。

4.  **歷史和可觀察性：** `session.events` 中記錄的事件序列提供了互動的完整、按時間順序的歷史記錄，對於偵錯、稽核和逐步了解代理行為非常有價值。

從本質上講，從使用者的查詢到代理的最終答案的整個過程，都是透過 `Event` 物件的產生、解釋和處理來協調的。


## 了解和使用事件

作為開發人員，您將主要與 `Runner` 產生的事件流互動。以下是如何理解和從中提取資訊：

!!! Note
    原語的具體參數或方法名稱可能因 SDK 語言而略有不同（例如，Python 中的 `event.content()`，Java 中的 `event.content().get().parts()`）。有關詳細資訊，請參閱特定語言的 API 文件。

### 識別事件來源和類型

透過檢查以下內容快速確定事件代表什麼：

*   **誰發送的？ (`event.author`)**
    *   `'user'`：表示直接來自終端使用者的輸入。
    *   `'AgentName'`：表示來自特定代理（例如，`'WeatherAgent'`、`'SummarizerAgent'`）的輸出或動作。
*   **主要酬載是什麼？ (`event.content` 和 `event.content.parts`)**
    *   **文字：** 表示對話訊息。對於 Python，檢查 `event.content.parts[0].text` 是否存在。對於 Java，檢查 `event.content()` 是否存在，其 `parts()` 是否存在且不為空，以及第一部分的 `text()` 是否存在。
    *   **工具呼叫請求：** 檢查 `event.get_function_calls()`。如果不為空，表示 LLM 要求執行一個或多個工具。列表中的每個項目都有 `.name` 和 `.args`。
    *   **工具結果：** 檢查 `event.get_function_responses()`。如果不為空，此事件攜帶工具執行的結果。每個項目都有 `.name` 和 `.response`（工具返回的字典）。*注意：* 為了歷史結構，`content` 內的 `role` 通常是 `'user'`，但事件 `author` 通常是請求工具呼叫的代理。

*   **是串流輸出嗎？ (`event.partial`)**
    表示這是否是來自 LLM 的不完整文字區塊。
    *   `True`：後面還會有更多文字。
    *   `False` 或 `None`/`Optional.empty()`：這部分內容是完整的（儘管如果 `turn_complete` 也為 false，整個輪次可能尚未完成）。

=== "Python"
    ```python
    # 虛擬碼：基本事件識別 (Python)
    # async for event in runner.run_async(...):
    #     print(f"事件來源：{event.author}")
    #
    #     if event.content and event.content.parts:
    #         if event.get_function_calls():
    #             print("  類型：工具呼叫請求")
    #         elif event.get_function_responses():
    #             print("  類型：工具結果")
    #         elif event.content.parts[0].text:
    #             if event.partial:
    #                 print("  類型：串流文字區塊")
    #             else:
    #                 print("  類型：完整文字訊息")
    #         else:
    #             print("  類型：其他內容（例如，程式碼結果）")
    #     elif event.actions and (event.actions.state_delta or event.actions.artifact_delta):
    #         print("  類型：狀態/產物更新")
    #     else:
    #         print("  類型：控制信號或其他")
    ```

=== "Java"
    ```java
    // 虛擬碼：基本事件識別 (Java)
    // import com.google.genai.types.Content;
    // import com.google.adk.events.Event;
    // import com.google.adk.events.EventActions;

    // runner.runAsync(...).forEach(event -> { // 假設是同步流或反應式流
    //     System.out.println("事件來源：" + event.author());
    //
    //     if (event.content().isPresent()) {
    //         Content content = event.content().get();
    //         if (!event.functionCalls().isEmpty()) {
    //             System.out.println("  類型：工具呼叫請求");
    //         } else if (!event.functionResponses().isEmpty()) {
    //             System.out.println("  類型：工具結果");
    //         } else if (content.parts().isPresent() && !content.parts().get().isEmpty() &&
    //                    content.parts().get().get(0).text().isPresent()) {
    //             if (event.partial().orElse(false)) {
    //                 System.out.println("  類型：串流文字區塊");
    //             } else {
    //                 System.out.println("  類型：完整文字訊息");
    //             }
    //         } else {
    //             System.out.println("  類型：其他內容（例如，程式碼結果）");
    //         }
    //     } else if (event.actions() != null &&
    //                ((event.actions().stateDelta() != null && !event.actions().stateDelta().isEmpty()) ||
    //                 (event.actions().artifactDelta() != null && !event.actions().artifactDelta().isEmpty()))) {
    //         System.out.println("  類型：狀態/產物更新");
    //     } else {
    //         System.out.println("  類型：控制信號或其他");
    //     }
    // });
    ```

### 提取關鍵資訊

一旦知道事件類型，就可以存取相關資料：

*   **文字內容：**
    在存取文字之前，請務必檢查內容和部分是否存在。在 Python 中是 `text = event.content.parts[0].text`。

*   **函式呼叫詳細資訊：**
    
    === "Python"
        ```python
        calls = event.get_function_calls()
        if calls:
            for call in calls:
                tool_name = call.name
                arguments = call.args # 這通常是一個字典
                print(f"  工具：{tool_name}, 參數：{arguments}")
                # 應用程式可能會根據此內容分派執行
        ```
    === "Java"

        ```java
        import com.google.genai.types.FunctionCall;
        import com.google.common.collect.ImmutableList;
        import java.util.Map;
    
        ImmutableList<FunctionCall> calls = event.functionCalls(); // 來自 Event.java
        if (!calls.isEmpty()) {
          for (FunctionCall call : calls) {
            String toolName = call.name().get();
            // args 是 Optional<Map<String, Object>>
            Map<String, Object> arguments = call.args().get();
                   System.out.println("  工具：" + toolName + ", 參數：" + arguments);
            // 應用程式可能會根據此內容分派執行
          }
        }
        ```

*   **函式回應詳細資訊：**
    
    === "Python"
        ```python
        responses = event.get_function_responses()
        if responses:
            for response in responses:
                tool_name = response.name
                result_dict = response.response # 工具返回的字典
                print(f"  工具結果：{tool_name} -> {result_dict}")
        ```
    === "Java"

        ```java
        import com.google.genai.types.FunctionResponse;
        import com.google.common.collect.ImmutableList;
        import java.util.Map; 

        ImmutableList<FunctionResponse> responses = event.functionResponses(); // 來自 Event.java
        if (!responses.isEmpty()) {
            for (FunctionResponse response : responses) {
                String toolName = response.name().get();
                Map<String, String> result= response.response().get(); // 在取得回應之前檢查
                System.out.println("  工具結果：" + toolName + " -> " + result);
            }
        }
        ```

*   **識別碼：**
    *   `event.id`：此特定事件實例的唯一 ID。
    *   `event.invocation_id`：此事件所屬的整個使用者請求到最終回應週期的 ID。對於記錄和追蹤很有用。

### 偵測動作和副作用

`event.actions` 物件表示已發生或應發生的變更。在存取 `event.actions` 及其欄位/方法之前，請務必檢查其是否存在。

*   **狀態變更：** 提供在產生此事件的步驟中，會話狀態中被修改的鍵值對集合。
    
    === "Python"
        `delta = event.actions.state_delta` (一個 `{key: value}` 對的字典)。
        ```python
        if event.actions and event.actions.state_delta:
            print(f"  狀態變更：{event.actions.state_delta}")
            # 如有必要，更新本地 UI 或應用程式狀態
        ```
    === "Java"
        `ConcurrentMap<String, Object> delta = event.actions().stateDelta();`

        ```java
        import java.util.concurrent.ConcurrentMap;
        import com.google.adk.events.EventActions;

        EventActions actions = event.actions(); // 假設 event.actions() 不為 null
        if (actions != null && actions.stateDelta() != null && !actions.stateDelta().isEmpty()) {
            ConcurrentMap<String, Object> stateChanges = actions.stateDelta();
            System.out.println("  狀態變更：" + stateChanges);
            # 如有必要，更新本地 UI 或應用程式狀態
        }
        ```

*   **產物儲存：** 提供一個集合，指示儲存了哪些產物及其新版本號（或相關的 `Part` 資訊）。
    
    === "Python"
        `artifact_changes = event.actions.artifact_delta` (一個 `{filename: version}` 的字典)。
        ```python
        if event.actions and event.actions.artifact_delta:
            print(f"  已儲存的產物：{event.actions.artifact_delta}")
            # UI 可能會刷新產物列表
        ```
    === "Java"
        `ConcurrentMap<String, Part> artifactChanges = event.actions().artifactDelta();`
        
        ```java
        import java.util.concurrent.ConcurrentMap;
        import com.google.genai.types.Part;
        import com.google.adk.events.EventActions;

        EventActions actions = event.actions(); // 假設 event.actions() 不為 null
        if (actions != null && actions.artifactDelta() != null && !actions.artifactDelta().isEmpty()) {
            ConcurrentMap<String, Part> artifactChanges = actions.artifactDelta();
            System.out.println("  已儲存的產物：" + artifactChanges);
            // UI 可能會刷新產物列表
            // 迭代 artifactChanges.entrySet() 以取得檔名和 Part 詳細資訊
        }
        ```

*   **控制流信號：** 檢查布林值旗標或字串值：
    
    === "Python"
        *   `event.actions.transfer_to_agent` (string)：控制權應傳遞給指定的代理。
        *   `event.actions.escalate` (bool)：迴圈應終止。
        *   `event.actions.skip_summarization` (bool)：工具結果不應由 LLM 摘要。
        ```python
        if event.actions:
            if event.actions.transfer_to_agent:
                print(f"  信號：傳輸至 {event.actions.transfer_to_agent}")
            if event.actions.escalate:
                print("  信號：升級（終止迴圈）")
            if event.actions.skip_summarization:
                print("  信號：跳過工具結果的摘要")
        ```
    === "Java"
        *   `event.actions().transferToAgent()` (回傳 `Optional<String>`)：控制權應傳遞給指定的代理。
        *   `event.actions().escalate()` (回傳 `Optional<Boolean>`)：迴圈應終止。
        *   `event.actions().skipSummarization()` (回傳 `Optional<Boolean>`)：工具結果不應由 LLM 摘要。

        ```java
        import com.google.adk.events.EventActions;
        import java.util.Optional;

        EventActions actions = event.actions(); // 假設 event.actions() 不為 null
        if (actions != null) {
            Optional<String> transferAgent = actions.transferToAgent();
            if (transferAgent.isPresent()) {
                System.out.println("  信號：傳輸至 " + transferAgent.get());
            }

            Optional<Boolean> escalate = actions.escalate();
            if (escalate.orElse(false)) { // 或 escalate.isPresent() && escalate.get()
                System.out.println("  信號：升級（終止迴圈）");
            }

            Optional<Boolean> skipSummarization = actions.skipSummarization();
            if (skipSummarization.orElse(false)) { // 或 skipSummarization.isPresent() && skipSummarization.get()
                System.out.println("  信號：跳過工具結果的摘要");
            }
        }
        ```

### 判斷事件是否為「最終」回應

使用內建的輔助方法 `event.is_final_response()` 來識別適合顯示為代理該輪完整輸出的事件。

*   **目的：** 從最終面向使用者的訊息中過濾掉中繼步驟（如工具呼叫、部分串流文字、內部狀態更新）。
*   **何時為 `True`？**
    1.  事件包含工具結果 (`function_response`) 且 `skip_summarization` 為 `True`。
    2.  事件包含一個工具呼叫 (`function_call`)，該工具標記為 `is_long_running=True`。在 Java 中，檢查 `longRunningToolIds` 列表是否為空：
        *   `event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()` 為 `true`。
    3.  或者，**所有**以下條件都滿足：
        *   沒有函式呼叫 (`get_function_calls()` 為空)。
        *   沒有函式回應 (`get_function_responses()` 為空)。
        *   不是部分串流區塊 (`partial` 不為 `True`)。
        *   不以可能需要進一步處理/顯示的程式碼執行結果結尾。
*   **用法：** 在您的應用程式邏輯中過濾事件流。

    === "Python"
        ```python
        # 虛擬碼：在應用程式中處理最終回應 (Python)
        # full_response_text = ""
        # async for event in runner.run_async(...):
        #     # 如有需要，累積串流文字...
        #     if event.partial and event.content and event.content.parts and event.content.parts[0].text:
        #         full_response_text += event.content.parts[0].text
        #
        #     # 檢查是否為最終、可顯示的事件
        #     if event.is_final_response():
        #         print("\n--- 偵測到最終輸出 ---")
        #         if event.content and event.content.parts and event.content.parts[0].text:
        #              # 如果是串流的最後一部分，使用累積的文字
        #              final_text = full_response_text + (event.content.parts[0].text if not event.partial else "")
        #              print(f"向使用者顯示：{final_text.strip()}")
        #              full_response_text = "" # 重設累積器
        #         elif event.actions and event.actions.skip_summarization and event.get_function_responses():
        #              # 如有需要，處理顯示原始工具結果
        #              response_data = event.get_function_responses()[0].response
        #              print(f"顯示原始工具結果：{response_data}")
        #         elif hasattr(event, 'long_running_tool_ids') and event.long_running_tool_ids:
        #              print("顯示訊息：工具正在背景執行...")
        #         else:
        #              # 如適用，處理其他類型的最終回應
        #              print("顯示：最終非文字回應或信號。")
        ```
    === "Java"
        ```java
        // 虛擬碼：在應用程式中處理最終回應 (Java)
        import com.google.adk.events.Event;
        import com.google.genai.types.Content;
        import com.google.genai.types.FunctionResponse;
        import java.util.Map;

        StringBuilder fullResponseText = new StringBuilder();
        runner.run(...).forEach(event -> { // 假設是事件流
             // 如有需要，累積串流文字...
             if (event.partial().orElse(false) && event.content().isPresent()) {
                 event.content().flatMap(Content::parts).ifPresent(parts -> {
                     if (!parts.isEmpty() && parts.get(0).text().isPresent()) {
                         fullResponseText.append(parts.get(0).text().get());
                    }
                 });
             }
        
             // 檢查是否為最終、可顯示的事件
             if (event.finalResponse()) { // 使用 Event.java 中的方法
                 System.out.println("\n--- 偵測到最終輸出 ---");
                 if (event.content().isPresent() &&
                     event.content().flatMap(Content::parts).map(parts -> !parts.isEmpty() && parts.get(0).text().isPresent()).orElse(false)) {
                     // 如果是串流的最後一部分，使用累積的文字
                     String eventText = event.content().get().parts().get().get(0).text().get();
                     String finalText = fullResponseText.toString() + (event.partial().orElse(false) ? "" : eventText);
                     System.out.println("向使用者顯示：" + finalText.trim());
                     fullResponseText.setLength(0); // 重設累積器
                 } else if (event.actions() != null && event.actions().skipSummarization().orElse(false)
                            && !event.functionResponses().isEmpty()) {
                     // 如有需要，處理顯示原始工具結果，
                     // 特別是如果 finalResponse() 因其他條件為 true
                     // 或如果您想無論 finalResponse() 如何都顯示跳過的摘要結果
                     Map<String, Object> responseData = event.functionResponses().get(0).response().get();
                     System.out.println("顯示原始工具結果：" + responseData);
                 } else if (event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()) {
                     // 此情況已由 event.finalResponse() 涵蓋
                     System.out.println("顯示訊息：工具正在背景執行...");
                 } else {
                     // 如適用，處理其他類型的最終回應
                     System.out.println("顯示：最終非文字回應或信號。");
                 }
             }
         });
        ```

透過仔細檢查事件的這些方面，您可以建置健全的應用程式，以適當地回應流經 ADK 系統的豐富資訊。

## 事件如何流動：產生與處理

事件在不同時間點建立，並由框架系統地處理。了解此流程有助於釐清如何管理動作和歷史記錄。

*   **產生來源：**
    *   **使用者輸入：** `Runner` 通常會將初始使用者訊息或對話中輸入包裝成一個 `author='user'` 的 `Event`。
    *   **代理邏輯：** 代理 (`BaseAgent`, `LlmAgent`) 明確地 `yield Event(...)` 物件（設定 `author=self.name`）以通訊回應或發出動作信號。
    *   **LLM 回應：** ADK 模型整合層會將原始 LLM 輸出（文字、函式呼叫、錯誤）轉換為由呼叫代理創作的 `Event` 物件。
    *   **工具結果：** 工具執行後，框架會產生一個包含 `function_response` 的 `Event`。`author` 通常是請求該工具的代理，而 `content` 內的 `role` 則設定為 `'user'` 以供 LLM 歷史記錄使用。


*   **處理流程：**
    1.  **產生/回傳：** 事件由其來源產生並 yield (Python) 或回傳/發出 (Java)。
    2.  **Runner 接收：** 執行代理的主要 `Runner` 接收事件。
    3.  **SessionService 處理：** `Runner` 將事件傳送至設定的 `SessionService`。這是一個關鍵步驟：
        *   **應用差異：** 服務會將 `event.actions.state_delta` 合併至 `session.state`，並根據 `event.actions.artifact_delta` 更新內部記錄。（注意：實際的產物*儲存*通常在 `context.save_artifact` 被呼叫時就已發生）。
        *   **完成元數據：** 如果 `event.id` 不存在，則指派一個唯一的 `event.id`，並可能更新 `event.timestamp`。
        *   **保存至歷史記錄：** 將處理過的事件附加至 `session.events` 列表。
    4.  **外部產生：** `Runner` 將處理過的事件向外 yield (Python) 或回傳/發出 (Java) 給呼叫應用程式（例如，調用 `runner.run_async` 的程式碼）。

此流程確保狀態變更和歷史記錄與每個事件的通訊內容一致地被記錄下來。


## 常見事件範例（說明性模式）

以下是您可能會在事件流中看到的典型事件的簡潔範例：

*   **使用者輸入：**
    ```json
    {
      "author": "user",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"text": "預訂下週二飛往倫敦的航班"}]}
      // actions 通常為空
    }
    ```
*   **代理最終文字回應：** (`is_final_response() == True`)
    ```json
    {
      "author": "TravelAgent",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"text": "好的，我可以幫您處理。請問可以確認出發城市嗎？"}]},
      "partial": false,
      "turn_complete": true
      // actions 可能有 state delta 等。
    }
    ```
*   **代理串流文字回應：** (`is_final_response() == False`)
    ```json
    {
      "author": "SummaryAgent",
      "invocation_id": "e-abc...",
      "content": {"parts": [{"text": "該文件討論了三個要點："}]},
      "partial": true,
      "turn_complete": false
    }
    // ... 後面跟著更多 partial=True 的事件 ...
    ```
*   **工具呼叫請求 (由 LLM 發出)：** (`is_final_response() == False`)
    ```json
    {
      "author": "TravelAgent",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"function_call": {"name": "find_airports", "args": {"city": "London"}}}]}
      // actions 通常為空
    }
    ```
*   **提供的工具結果 (給 LLM)：** (`is_final_response()` 取決於 `skip_summarization`)
    ```json
    {
      "author": "TravelAgent", // 作者是請求呼叫的代理
      "invocation_id": "e-xyz...",
      "content": {
        "role": "user", // LLM 歷史記錄的角色
        "parts": [{"function_response": {"name": "find_airports", "response": {"result": ["LHR", "LGW", "STN"]}}}]
      }
      // actions 可能有 skip_summarization=True
    }
    ```
*   **僅狀態/產物更新：** (`is_final_response() == False`)
    ```json
    {
      "author": "InternalUpdater",
      "invocation_id": "e-def...",
      "content": null,
      "actions": {
        "state_delta": {"user_status": "verified"},
        "artifact_delta": {"verification_doc.pdf": 2}
      }
    }
    ```
*   **代理轉移信號：** (`is_final_response() == False`)
    ```json
    {
      "author": "OrchestratorAgent",
      "invocation_id": "e-789...",
      "content": {"parts": [{"function_call": {"name": "transfer_to_agent", "args": {"agent_name": "BillingAgent"}}}]},
      "actions": {"transfer_to_agent": "BillingAgent"} // 由框架新增
    }
    ```
*   **迴圈升級信號：** (`is_final_response() == False`)
    ```json
    {
      "author": "CheckerAgent",
      "invocation_id": "e-loop...",
      "content": {"parts": [{"text": "已達最大重試次數。"}]}, // 可選內容
      "actions": {"escalate": true}
    }
    ```

## 其他上下文和事件詳細資訊

除了核心概念之外，以下是一些對於特定使用案例很重要的關於上下文和事件的具體細節：

1.  **`ToolContext.function_call_id` (連結工具動作)：**
    *   當 LLM 請求一個工具 (FunctionCall) 時，該請求有一個 ID。提供給您工具函式的 `ToolContext` 包含此 `function_call_id`。
    *   **重要性：** 此 ID 對於將驗證等動作連結回發起它們的特定工具請求至關重要，特別是如果在一輪中呼叫了多個工具。框架在內部使用此 ID。

2.  **如何記錄狀態/產物變更：**
    *   當您使用 `CallbackContext` 或 `ToolContext` 修改狀態或儲存產物時，這些變更不會立即寫入持久性儲存。
    *   相反，它們會填入 `EventActions` 物件內的 `state_delta` 和 `artifact_delta` 欄位。
    *   此 `EventActions` 物件會附加到變更後產生的*下一個事件*（例如，代理的回應或工具結果事件）。
    *   `SessionService.append_event` 方法會從傳入的事件中讀取這些差異，並將其應用於會話的持久性狀態和產物記錄。這確保了變更是按時間順序與事件流綁定的。

3.  **狀態範圍前綴 (`app:`, `user:`, `temp:`)：**
    *   透過 `context.state` 管理狀態時，您可以選擇性地使用前綴：
        *   `app:my_setting`：建議與整個應用程式相關的狀態（需要持久性 `SessionService`）。
        *   `user:user_preference`：建議與特定使用者跨會話相關的狀態（需要持久性 `SessionService`）。
        *   `temp:intermediate_result` 或無前綴：通常是特定於會話或當前調用的臨時狀態。
    *   底層的 `SessionService` 決定如何處理這些前綴以實現持久性。

4.  **錯誤事件：**
    *   `Event` 可以代表一個錯誤。檢查 `event.error_code` 和 `event.error_message` 欄位（繼承自 `LlmResponse`）。
    *   錯誤可能源自 LLM（例如，安全過濾器、資源限制），也可能由框架在工具嚴重失敗時打包。檢查工具 `FunctionResponse` 內容以了解典型的工具特定錯誤。
    ```json
    // 錯誤事件範例（概念性）
    {
      "author": "LLMAgent",
      "invocation_id": "e-err...",
      "content": null,
      "error_code": "SAFETY_FILTER_TRIGGERED",
      "error_message": "由於安全設定，回應被封鎖。",
      "actions": {}
    }
    ```

這些詳細資訊為涉及工具驗證、狀態持久性範圍和事件流中錯誤處理的進階使用案例提供了更完整的畫面。

## 使用事件的最佳實踐

為了在您的 ADK 應用程式中有效使用事件：

*   **明確的作者：** 在建置自訂代理時，確保在歷史記錄中正確歸屬代理動作。框架通常會正確處理 LLM/工具事件的作者。
    
    === "Python"
        在 `BaseAgent` 子類別中使用 `yield Event(author=self.name, ...)`。
    === "Java"
        在您的自訂代理邏輯中建構 `Event` 時，請設定作者，例如：`Event.builder().author(this.getAgentName()) // ... .build();`

*   **語意內容和動作：** 使用 `event.content` 表示核心訊息/資料（文字、函式呼叫/回應）。專門使用 `event.actions` 來發出副作用（狀態/產物差異）或控制流（`transfer`、`escalate`、`skip_summarization`）的信號。
*   **冪等性意識：** 了解 `SessionService` 負責應用 `event.actions` 中發出的狀態/產物變更信號。雖然 ADK 服務旨在保持一致性，但如果您的應用程式邏輯重新處理事件，請考慮潛在的下游影響。
*   **使用 `is_final_response()`：** 在您的應用程式/UI 層中依賴此輔助方法來識別完整的、面向使用者的文字回應。避免手動複製其邏輯。
*   **利用歷史記錄：** 會話的事件列表是您的主要偵錯工具。檢查作者、內容和動作的順序以追蹤執行並診斷問題。
*   **使用元數據：** 使用 `invocation_id` 來關聯單一使用者互動中的所有事件。使用 `event.id` 來參考特定的、唯一的事件。

將事件視為具有明確內容和動作目的的結構化訊息，是建置、偵錯和管理 ADK 中複雜代理行為的關鍵。
