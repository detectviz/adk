from google.adk.tools import ToolContext, FunctionTool

def update_user_preference(preference: str, value: str, tool_context: ToolContext):
    """更新使用者特定的偏好設定。"""
    user_prefs_key = "user:preferences"
    # 取得目前的偏好設定，如果不存在則初始化
    preferences = tool_context.state.get(user_prefs_key, {})
    preferences[preference] = value
    # 將更新後的字典寫回狀態
    tool_context.state[user_prefs_key] = preferences
    print(f"工具：已將使用者偏好 '{preference}' 更新為 '{value}'")
    return {"status": "success", "updated_preference": preference}

pref_tool = FunctionTool(func=update_user_preference)

# 在代理中：
# my_agent = Agent(..., tools=[pref_tool])

# 當大型語言模型（LLM）呼叫 update_user_preference(preference='theme', value='dark', ...) 時：
# tool_context.state 將會更新，且變更將成為
# 產生的工具回應事件的 actions.state_delta 的一部分。
