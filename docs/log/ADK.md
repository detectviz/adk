# 正式導入 Google ADK

- 構建協調器：`sre_assistant/adapters/adk_runtime.py` 會嘗試引入 `google.adk`。
- 若可用：使用 `LoopAgent + BuiltInPlanner + FunctionTool`，並將 YAML 規格映射為 ADK 工具。
- 若不可用：回退內建 `SREAssistant`，不影響功能。
- 後續工作：按 ADK 最佳實踐補齊多代理（Diagnostic/Remediation/Postmortem）掛載。

> 注意：此儲存庫未內含 Google ADK 套件，需在部署環境安裝授權版本後方可啟用。
