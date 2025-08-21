
# AGENT 設計說明（對齊 ADK）

> 本文件以範例導向闡述代理與工具的組裝，參考 [agents.md/examples](https://agents.md/#examples)。

## 主協調器
```python
from google.adk.agents import LoopAgent, LlmAgent
from google.adk.planners import BuiltInPlanner
from google.adk.tools.agent_tool import AgentTool
from sre_assistant.adk_app.coordinator import main_llm, diagnostic_expert, remediation_expert, postmortem_expert

coordinator = LoopAgent(
    agents=[main_llm],
    planner=BuiltInPlanner(),
    max_iterations=10
)
```
- 單一 `LoopAgent`，僅掛 `main_llm`。子專家以 `AgentTool` 被 `main_llm` 使用（避免重複掛載）。

## 子專家
```python
DiagnosticExpert  # PromQL + RAG → 初診結論與建議
RemediationExpert # K8s LongRunningTool → 支援 HITL（request_credential）
PostmortemExpert  # 文件/RAG → 覆盤報告
```

## 工具
- `FunctionTool`：PromQL、Grafana、RAG、知識匯入。
- `LongRunningFunctionTool`：`K8sRolloutRestartLongRunningTool(start/poll)`。

## HITL（人機在迴圈）
1. 工具在 `start_func` 以 `tool_context.request_credential(auth_config)` 觸發事件。  
2. 前端從 SSE 收到 `adk_request_credential(function_call_id)`，引導使用者完成核可。  
3. 前端以 `FunctionResponse(name='adk_request_credential', id=function_call_id, response=auth_config)` 回傳。  
4. 工具在 `poll_func` 以 `tool_context.get_auth_response(auth_config)` 取得核可再繼續。

## Sessions
- 以 ADK Runner `run_async(...)` 串流事件；`SESSION_BACKEND` 控制 `InMemorySessionService|DatabaseSessionService`。
