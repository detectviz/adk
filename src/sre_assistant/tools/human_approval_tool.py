# src/sre_assistant/tools/human_approval_tool.py
"""
實現標準化的人類介入 (Human-in-the-Loop) 工具。
"""
import asyncio
from typing import Dict, Any, AsyncIterator
from google.adk.tools import LongRunningFunctionTool, ToolEvent

class HumanApprovalTool(LongRunningFunctionTool):
    """
    使用 ADK 的長時間運行工具實現 HITL。

    此工具會暫停工作流程，發送一個需要人工批准的請求，
    然後等待外部系統透過回調傳回批准或拒絕的結果。
    """
    async def run(self, request: Dict[str, Any]) -> AsyncIterator[ToolEvent]:
        """
        執行工具的核心邏輯。

        Args:
            request: 一個包含需要批准的操作細節的字典。
                     例如: `{'action': 'restart_deployment', 'details': '...`}`

        Yields:
            ToolEvent: 一個表示工具目前狀態的事件。
        """
        # 步驟 1: 發送審批請求
        # 在真實世界的應用中，這裡會呼叫一個通知服務 (例如 Slack, Email, PagerDuty)。
        request_id = f"req-approval-{''.join(str(ord(c)) for c in request.get('action', ''))}"
        print(f"Human approval requested for action: {request.get('action')}. Request ID: {request_id}")

        # 步驟 2: 產生一個 "pending" 事件，通知 ADK Runner 工作流程正在等待外部輸入。
        # 這個事件可以包含一個請求 ID 或一個回調 URL，以便外部系統可以回應。
        yield ToolEvent(type="pending", data={"request_id": request_id, "message": "Waiting for human approval."})

        # 步驟 3: 模擬等待外部回調。
        # 在真實應用中，Runner 會在此處暫停，直到外部呼叫 `runner.run_async` 並提供
        # 一個 `FunctionResponse`。為了演示，我們這裡模擬一個延遲後自動批准的流程。
        await asyncio.sleep(1) # 模擬網路延遲和人類反應時間
        approval_result = {"status": "approved", "approver": "system@example.com", "reason": "Auto-approved for demonstration."}

        # 步驟 4: 產生一個 "completed" 事件，並附上最終結果，以繼續工作流程。
        yield ToolEvent(type="completed", data=approval_result)
