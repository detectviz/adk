from google.adk.tools import ToolContext, FunctionTool
from .. import config



def check_condition_and_escalate_tool(tool_context: ToolContext) -> dict:
    """檢查循環終止條件，如果滿足或達到最大計數，則提升。"""
 

    # 使用狀態增加循環迭代計數
    current_loop_count = tool_context.state.get("loop_iteration", 0)
    current_loop_count += 1
    tool_context.state["loop_iteration"] = current_loop_count

    # 定義最大迭代次數
    max_iterations = config.MAX_ITERATIONS

    # 從狀態中取得由循序代理設定的條件結果
    total_score = tool_context.state.get("total_score", 50)

    condition_met = total_score > config.SCORE_THRESHOLD

    response_message = f"檢查迭代 {current_loop_count}：循序條件滿足 = {condition_met}。"

    # 檢查條件是否滿足或是否達到最大迭代次數
    if condition_met:
        print("  條件滿足。設定 escalate=True 以停止 LoopAgent。")
        tool_context.actions.escalate = True
        response_message += "條件滿足，停止循環。"
    elif current_loop_count >= max_iterations:
        print(
            f"  已達到最大迭代次數 ({max_iterations})。設定 escalate=True 以停止 LoopAgent。"
        )
        tool_context.actions.escalate = True
        response_message += "已達到最大迭代次數，停止循環。"
    else:
        print(
            "  條件未滿足且未達到最大迭代次數。循環將繼續。"
        )
        response_message += "循環繼續。"

    return {"status": "已評估評分條件", "message": response_message}




check_tool_condition = FunctionTool(func=check_condition_and_escalate_tool)
