

### v15.7.6
- 架構精簡：刪除 Non-ADK 協調器、ToolRegistry、自訂 agents、otel_grpc。
- 政策與安全：移除 policy.py；HITL 完全由工具端 `request_credential` 觸發。
- 工作流：移除 k8s_long_running 全域狀態，統一 session.state；修正 HITL 條件。
- 品質：移除 coding header 與自動產生註解字樣；新增 HITL 條件測試。
