# 用於展示會話狀態持續性的範例代理。

## 會話狀態的生命週期

在使用上下文物件指派狀態後（例如
`tool_context.state['log_query_var'] = 'log_query_var_value'`）：

* 該狀態可在稍後的回呼中使用。
* 一旦產生的事件由執行器處理並附加到會話中，該狀態也將被持續儲存在會話中。

此範例代理旨在展示前述行為。

## 執行代理

執行以下指令：

```bash
$ adk run contributing/samples/session_state_agent --replay contributing/samples/session_state_agent/input.json
```

您應該會看到以下輸出：

```bash
[user]: hello world!
===================== In before_agent_callback ==============================
** Asserting keys are cached in context: ['before_agent_callback_state_key'] pass ✅
** Asserting keys are already persisted in session: [] pass ✅
** Asserting keys are not persisted in session yet: ['before_agent_callback_state_key'] pass ✅
============================================================
===================== In before_model_callback ==============================
** Asserting keys are cached in context: ['before_agent_callback_state_key', 'before_model_callback_state_key'] pass ✅
** Asserting keys are already persisted in session: ['before_agent_callback_state_key'] pass ✅
** Asserting keys are not persisted in session yet: ['before_model_callback_state_key'] pass ✅
============================================================
===================== In after_model_callback ==============================
** Asserting keys are cached in context: ['before_agent_callback_state_key', 'before_model_callback_state_key', 'after_model_callback_state_key'] pass ✅
** Asserting keys are already persisted in session: ['before_agent_callback_state_key'] pass ✅
** Asserting keys are not persisted in session yet: ['before_model_callback_state_key', 'after_model_callback_state_key'] pass ✅
============================================================
[root_agent]: Hello! How can I help you verify something today?

===================== In after_agent_callback ==============================
** Asserting keys are cached in context: ['before_agent_callback_state_key', 'before_model_callback_state_key', 'after_model_callback_state_key', 'after_agent_callback_state_key'] pass ✅
** Asserting keys are already persisted in session: ['before_agent_callback_state_key', 'before_model_callback_state_key', 'after_model_callback_state_key'] pass ✅
** Asserting keys are not persisted in session yet: ['after_agent_callback_state_key'] pass ✅
============================================================
```

## 詳細說明

根據經驗，要讀取和寫入會話狀態，使用者應假設狀態在透過上下文物件（`tool_context`、`callback_context` 或 `readonly_context`）寫入後即可用。

### 目前行為

目前持續儲存狀態的行為是：

* 對於 `before_agent_callback`：狀態差異將在所有回呼處理完畢後持續儲存。
* 對於 `before_model_callback`：狀態差異將與最終的 LlmResponse 一起持續儲存，即在 `after_model_callback` 處理完畢後。
* 對於 `after_model_callback`：狀態差異將與 LlmResponse 的事件一起持續儲存。
* 對於 `after_agent_callback`：狀態差異將在所有回呼處理完畢後持續儲存。

**注意**：目前的行為被視為實作細節，日後可能會變更。**請勿**依賴它。
