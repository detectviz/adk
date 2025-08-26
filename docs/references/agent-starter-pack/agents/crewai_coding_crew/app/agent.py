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

from .crew.crew import DevCrew

LOCATION = "global"
LLM = "gemini-2.5-flash"


@tool
def coding_tool(code_instructions: str) -> str:
    """根據一組需求或指令，使用此工具來編寫一個 python 程式。"""
    inputs = {"code_instructions": code_instructions}
    return DevCrew().crew().kickoff(inputs=inputs)


tools = [coding_tool]

# 2. 設定語言模型
llm = ChatVertexAI(
    model=LLM, location=LOCATION, temperature=0, max_tokens=4096, streaming=True
).bind_tools(tools)


# 3. 定義工作流程元件
def should_continue(state: MessagesState) -> str:
    """決定是使用團隊還是結束對話。"""
    last_message = state["messages"][-1]
    return "dev_crew" if last_message.tool_calls else END


def call_model(state: MessagesState, config: RunnableConfig) -> dict[str, BaseMessage]:
    """呼叫語言模型並返回回應。"""
    system_message = (
        "你是一位資深的軟體工程經理專家。\n"
        "你的角色是與使用者交談，並理解他們需要建構什麼樣的程式碼。\n"
        "因此，你的部分任務是收集需求並透過提出後續問題來澄清模糊之處。不要一次問完所有問題，因為使用者的注意力持續時間很短，而是每次問一個問題。\n"
        "一旦要解決的問題明確了，你將呼叫你的工具來編寫解決方案。\n"
        "記住，你是理解需求的專家，但你不能編寫程式碼，請使用你的編碼工具來產生解決方案。如果有的話，保留測試案例，它們對使用者很有用。"
    )

    messages_with_system = [{"type": "system", "content": system_message}] + state[
        "messages"
    ]
    # 轉發 RunnableConfig 物件以確保代理能夠串流回應。
    response = llm.invoke(messages_with_system, config)
    return {"messages": response}


# 4. 建立工作流程圖
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("dev_crew", ToolNode(tools))
workflow.set_entry_point("agent")

# 5. 定義圖的邊
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("dev_crew", "agent")

# 6. 編譯工作流程
agent = workflow.compile()
