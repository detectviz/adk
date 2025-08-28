# file: src/sre_assistant/workflow.py
import asyncio
import time
from typing import Any
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import LongRunningFunctionTool, FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.events import Event

APP_NAME = "detectviz_sre"
USER_ID = "sre_bot"
SESSION_ID = "sre_session_1"

# 1) domain functions / tools
def ask_for_approval(action: str, reason: str) -> dict[str, Any]:
    """建立審批 ticket 並通知決策者。回傳初始狀態（pending 與 ticket id）。"""
    ticket_id = f"ticket-{int(time.time())}"
    # 在此可呼叫外部 ticket 系統 / webhook / slack
    return {"status": "pending", "ticket-id": ticket_id, "approver": "oncall@example.com", "action": action, "reason": reason}

def perform_remediation(action: str) -> dict[str, Any]:
    """實際 remediation 的同步函式範例。"""
    # 這邊放真正執行 remediation 邏輯或呼叫 orchestration 平台
    return {"status": "ok", "action": action}

# 2) 工具包裝
approval_tool = LongRunningFunctionTool(func=ask_for_approval)
remediate_tool = FunctionTool(func=perform_remediation)

# 3) SREWorkflow builder
class SREWorkflowFactory:
    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model = model

    def build(self) -> SequentialAgent:
        """
        建立一個 SequentialAgent：
         - Step A: 用 LlmAgent 呼叫 LongRunningFunctionTool(ask_for_approval)
         - Step B: 用 LlmAgent 根據 approval 結果決定是否呼叫 perform_remediation
        """
        approver = LlmAgent(
            name="SRE_ApprovalRequester",
            model=self.model,
            instruction=(
                "判斷是否需要人工審批。若需，呼叫 ask_for_approval(action, reason)。"
                "將工具回傳的物件儲存為 output key 'approval'."
            ),
            tools=[approval_tool],
            output_key="approval"
        )

        executor = LlmAgent(
            name="SRE_RemediationExecutor",
            model=self.model,
            instruction=(
                "讀取上一步的 {approval}。若 approval.status == 'approved'，呼叫 perform_remediation(action)。"
                "否則回報已中止。"
            ),
            tools=[remediate_tool],
            output_key="remediation_result"
        )

        return SequentialAgent(name="SRE_HITL_Workflow", sub_agents=[approver, executor])

# 4) Runner 端範例：執行、偵測 long-running 呼叫、並回填人工審批結果
async def run_sre_workflow_and_simulate_human(action: str, reason: str):
    factory = SREWorkflowFactory()
    workflow_agent = factory.build()

    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=workflow_agent, app_name=APP_NAME, session_service=session_service)

    def get_long_running_function_call(event: Event) -> types.FunctionCall | None:
        if not event.long_running_tool_ids or not event.content or not event.content.parts:
            return None
        for part in event.content.parts:
            if part and part.function_call and part.function_call.id in event.long_running_tool_ids:
                return part.function_call
        return None

    def get_function_response(event: Event, function_call_id: str) -> types.FunctionResponse | None:
        if not event.content or not event.content.parts:
            return None
        for part in event.content.parts:
            if part and part.function_response and part.function_response.id == function_call_id:
                return part.function_response
        return None

    user_content = types.Content(role="user", parts=[types.Part(text=f"請執行 action={action}，原因={reason}")])
    events_async = runner.run_async(user_id=USER_ID, session_id=session.id, new_message=user_content)

    long_running_call = None
    long_running_function_response = None

    async for event in events_async:
        # 印出 agent 回應（簡化）
        if event.content and event.content.parts:
            text = "".join(part.text or "" for part in event.content.parts)
            if text:
                print(f"[{event.author}] {text}")

        if not long_running_call:
            long_running_call = get_long_running_function_call(event)
            if long_running_call:
                print("Detected long running function call:", long_running_call.name, long_running_call.id)
        else:
            # 嘗試抓取 tool 的初始回應（包含 ticket-id）
            fr = get_function_response(event, long_running_call.id)
            if fr:
                long_running_function_response = fr
                print("Received initial FunctionResponse:", fr.response)

    # 模擬人工審批（可改成呼叫 UI / webhook 等）
    if long_running_function_response:
        updated = long_running_function_response.model_copy(deep=True)
        # 實際情境會查 ticket 狀態，這裡直接模擬 approve
        updated.response = {"status": "approved", "ticket-id": long_running_function_response.response.get("ticket-id")}
        # 將人工決策回填給 runner，讓 agent 繼續執行後續步驟
        async for event in runner.run_async(session_id=session.id, user_id=USER_ID,
                                            new_message=types.Content(parts=[types.Part(function_response=updated)], role="user")):
            if event.content and event.content.parts:
                text = "".join(part.text or "" for part in event.content.parts)
                if text:
                    print(f"[{event.author}] {text}")

# Helper for sync run convenience
def run_demo():
    asyncio.run(run_sre_workflow_and_simulate_human(action="restart-service", reason="OOM spike"))
