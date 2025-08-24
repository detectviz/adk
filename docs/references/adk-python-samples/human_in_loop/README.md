# 具有長時間執行工具的代理 (Agent)

此範例示範一個使用長時間執行工具 (`ask_for_approval`) 的代理 (agent)。

## 長時間執行工具的關鍵流程

1. **初始呼叫**：代理 (agent) 呼叫長時間執行的工具（例如 `ask_for_approval`）。
2. **初始工具回應**：工具會立即傳回初始回應，通常表示「待處理」狀態以及追蹤請求的方式（例如 `ticket-id`）。這會以 `types.FunctionResponse` 的形式傳回給代理 (agent)（通常由執行器在內部處理，然後影響代理 (agent) 的下一輪）。
3. **代理 (Agent) 確認**：代理 (agent) 處理此初始回應，並通常會通知使用者待處理狀態。
4. **外部程序/更新**：長時間執行的任務在外部進行（例如，人類核准請求）。
5. **❗️關鍵步驟：提供更新的工具回應❗️**：
    * 外部程序完成或更新後，您的應用程式**必須**建構一個新的 `types.FunctionResponse`。
    * 此回應應使用與對長時間執行工具的原始 `FunctionCall` **相同的 `id` 和 `name`**。
    * 此 `types.FunctionResponse` 中的 `response` 欄位應包含*更新的資料*（例如 `{'status': 'approved', ...}`）。
    * 使用 `role="user"` 將此 `types.FunctionResponse` 作為新訊息的一部分傳回給代理 (agent)。

    ```python
    # 範例：在外部核准後
    updated_tool_output_data = {
        "status": "approved",
        "ticket-id": ticket_id, # 來自原始呼叫
        # ... 其他相關的更新資料
    }

    updated_function_response_part = types.Part(
        function_response=types.FunctionResponse(
            id=long_running_function_call.id,   # 原始呼叫 ID
            name=long_running_function_call.name, # 原始呼叫名稱
            response=updated_tool_output_data,
        )
    )

    # 將此傳回給代理 (agent)
    await runner.run_async(
        # ... session_id, user_id ...
        new_message=types.Content(
            parts=[updated_function_response_part], role="user"
        ),
    )
    ```
6. **代理 (Agent) 根據更新採取行動**：代理 (agent) 收到包含 `types.FunctionResponse` 的訊息，並根據其指示繼續執行後續步驟（例如，呼叫另一個工具，如 `reimburse`）。

**為什麼這很重要？** 代理 (agent) 依賴接收此後續的 `types.FunctionResponse`（在包含特定 `Part` 且 `role="user"` 的訊息中提供）來了解長時間執行的任務已結束或其狀態已變更。若沒有它，代理 (agent) 將無法得知待處理任務的結果。
