# 循序代理

## `SequentialAgent`

`SequentialAgent` 是一個[工作流程代理](index.md)，它按照列表中指定的順序執行其子代理。

當您希望執行以固定的、嚴格的順序進行時，請使用 `SequentialAgent`。

### 範例

* 您想要建立一個可以摘要任何網頁的代理，使用兩個工具：`Get Page Contents` 和 `Summarize Page`。因為代理必須始終在呼叫 `Summarize Page` 之前呼叫 `Get Page Contents` (您不能無中生有地進行摘要！)，您應該使用 `SequentialAgent` 來建構您的代理。

與其他[工作流程代理](index.md)一樣，`SequentialAgent` 不由 LLM 驅動，因此其執行方式是確定性的。也就是說，工作流程代理只關心其執行 (即按順序)，而不關心其內部邏輯；工作流程代理的工具或子代理可能會或可能不會利用 LLM。

### 運作方式

當呼叫 `SequentialAgent` 的 `Run Async` 方法時，它會執行以下操作：

1. **迭代：** 它會按照提供的順序迭代子代理列表。
2. **子代理執行：** 對於列表中的每個子代理，它會呼叫子代理的 `Run Async` 方法。

![Sequential Agent](../../assets/sequential-agent.png){: width="600"}

### 完整範例：程式碼開發管線

考慮一個簡化的程式碼開發管線：

* **程式碼撰寫代理：** 一個根據規格產生初始程式碼的 LLM 代理。
* **程式碼審查代理：** 一個審查產生的程式碼是否有錯誤、樣式問題以及是否遵循最佳實踐的 LLM 代理。它會接收程式碼撰寫代理的輸出。
* **程式碼重構代理：** 一個接收審查過的程式碼 (以及審查員的評論) 並對其進行重構以提高品質和解決問題的 LLM 代理。

`SequentialAgent` 非常適合這種情況：

```py
SequentialAgent(sub_agents=[CodeWriterAgent, CodeReviewerAgent, CodeRefactorerAgent])
```

這確保了程式碼以嚴格、可靠的順序被撰寫、*然後*審查，以及*最後*重構。**每個子代理的輸出都透過[輸出鍵](../llm-agents.md#structuring-data-input_schema-output_schema-output_key)儲存在狀態中，然後傳遞給下一個**。

???+ "程式碼"

    === "Python"
        ```py
        --8<-- "examples/python/snippets/agents/workflow-agents/sequential_agent_code_development_agent.py:init"
        ```

    === "Java"
        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/workflow/SequentialAgentExample.java:init"
        ```
