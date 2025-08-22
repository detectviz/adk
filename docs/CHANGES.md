

### v15.7.6
- 架構精簡：刪除 Non-ADK 協調器、ToolRegistry、自訂 agents、otel_grpc。
- 政策與安全：移除 policy.py；HITL 完全由工具端 `request_credential` 觸發。
- 工作流：移除 k8s_long_running 全域狀態，統一 session.state；修正 HITL 條件。
- 品質：移除 coding header 與字樣；新增 HITL 條件測試。


### v15.7.8
- 樣板註解清理：全域清除『自動產生註解』文字以提升可讀性。
- 移除硬編碼：K8s 高風險命名空間改為可配置，並提供稽核報告 `docs/HARDCODE_AUDIT.md`。
- 移除殘留檔案：再度清理已棄用目錄，避免雙模式維護。
