
# 營運手冊（HITL 與事件流程）

## HITL 互動新流程（對齊程式碼）
1. 後端工具在需要人工核可時，呼叫 `tool_context.request_credential(...)`。
2. ADK 事件流產生 `RequestCredential`，在 SSE 轉換為 `type=adk_request_credential` 後送往前端。
3. 前端顯示核可表單（可依 `sre_assistant/hitl/providers.yaml` 動態渲染欄位）。
4. 使用者核可：`POST /api/v1/hitl/approve`，或拒絕：`POST /api/v1/hitl/reject`。
5. 後端將核可/拒絕寫入 `Session.state['lr_ops'][op_id]`，長任務繼續或終止。
6. 事件、決策持續經由 SSE 推送，便於即時追蹤與回放。

> 已淘汰：舊的 `approval_id` 模式與非事件化流程。

## 端點摘要
- `POST /api/v1/hitl/approve`：核可長任務。欄位：`session_id, op_id, approver, ticket_id?`  
- `POST /api/v1/hitl/reject`：拒絕長任務。欄位：`session_id, op_id, reason`  
- `GET /api/v1/sse/{session_id}`：SSE 事件流，含 `adk_request_credential`。

## 回放與審計
- 事件回放：`GET /api/v1/sessions/{session_id}/events` 或 `/events_range`  
- 決策回放：`GET /api/v1/sessions/{session_id}/decisions` 或 `/decisions_range`
