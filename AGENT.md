
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

## HITL 與長任務（對齊 ADK）
- `start_func`：判斷高風險操作時呼叫 `tool_context.request_credential(...)`，並在 `Session.state['lr_ops']` 建立 op 狀態。
- `poll_func`：呼叫 `tool_context.get_auth_response(function_call_id=op_id)`；若已核可則繼續操作，若拒絕則回傳失敗並結束。


## 配置鍵位（adk.yaml）
```yaml
agent:
  model: gemini-2.0-flash
  tools_allowlist: [rag_search, K8sRolloutRestartLongRunningTool, ingest_text]
  tools_require_approval: [K8sRolloutRestartLongRunningTool]

policy:
  risk_threshold: High   # Low/Medium/High/Critical
experts:
  diagnostic:
    tools_allowlist: [rag_search]
  remediation:
    tools_allowlist: [K8sRolloutRestartLongRunningTool]
  postmortem:
    tools_allowlist: [rag_search]
  config:
    tools_allowlist: [ingest_text]
```


## 專家代理標準化
- 各專家以 `LlmAgent` 實例定義於 runtime 中組裝，並以 `AgentTool` 掛載於主代理。
- 若需拆分檔案，可在 `sre_assistant/experts/` 下提供 `*_expert_agent` 實例並於 runtime 匯入。


## 模型覆蓋規則（experts.*.model）
- 解析順序：`experts.<name>.model` > `agent.model` > `ADK_MODEL` 環境變數。
- 例：
```yaml
agent:
  model: gemini-2.0-flash
experts:
  diagnostic:
    model: gemini-2.0-pro        # 僅診斷專家使用更強模型
    tools_allowlist: [rag_search]
  remediation:
    tools_allowlist: [K8sRolloutRestartLongRunningTool]
```


## 專家設定鍵位一覽
- `experts/<name>.yaml`：
  - `model`：覆蓋此專家的 LLM 模型。
  - `tools_allowlist`：此專家允許的工具。
  - `prompt`：此專家系統提示詞。
  - `slo`：此專家的 SLO 指標（供觀測/測試）。
