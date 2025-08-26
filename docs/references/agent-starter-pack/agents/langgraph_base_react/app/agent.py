# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# mypy: disable-error-code="union-attr"
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

LOCATION = "global"
LLM = "gemini-2.5-flash"


# 1. 定義工具
@tool
def search(query: str) -> str:
    """模擬網路搜尋。用它來獲取天氣資訊"""
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "現在是華氏 60 度，有霧。"
    return "現在是華氏 90 度，晴天。"


tools = [search]

# 2. 設定語言模型
llm = ChatVertexAI(
    model=LLM, location=LOCATION, temperature=0, max_tokens=1024, streaming=True
).bind_tools(tools)


# 3. 定義工作流程元件
def should_continue(state: MessagesState) -> str:
    """決定是使用工具還是結束對話。"""
    last_message = state["messages"][-1]
    return "tools" if last_message.tool_calls else END


def call_model(state: MessagesState, config: RunnableConfig) -> dict[str, BaseMessage]:
    """呼叫語言模型並返回回應。"""
    system_message = "你是一個樂於助人的 AI 助理。"
    messages_with_system = [{"type": "system", "content": system_message}] + state[
        "messages"
    ]
    # 轉發 RunnableConfig 物件以確保代理能夠串流回應。
    response = llm.invoke(messages_with_system, config)
    return {"messages": response}


# 4. 建立工作流程圖
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))
workflow.set_entry_point("agent")

# 5. 定義圖的邊
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

# 6. 編譯工作流程
agent = workflow.compile()
