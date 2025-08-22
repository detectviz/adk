# 前端 HITL 操作說明
- 從 SSE 監聽 `type=adk_request_credential` 事件，讀取其中 `function_call_id` 或 `op_id`。
- 提交核可：POST `/api/v1/hitl/approve`；拒絕：POST `/api/v1/hitl/reject`。
- 之後使用長任務的 poll 端點（或現有 SSE）觀察進度變化。
