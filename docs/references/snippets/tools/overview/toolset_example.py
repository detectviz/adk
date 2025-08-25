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

import asyncio
from typing import Optional, List, Dict, Any

from google.adk.agents import LlmAgent, ReadonlyContext
from google.adk.tools import BaseTool, FunctionTool, BaseToolset
from google.adk.tools.tool_context import ToolContext  # 用於工具實作
from google.adk.runners import Runner  # 用於概念性執行
from google.adk.sessions import InMemorySessionService  # 用於概念性執行
from google.genai.types import Content, Part

## --8<-- [start:init]


# 1. 定義個別的工具函式
def add_numbers(a: int, b: int, tool_context: ToolContext) -> Dict[str, Any]:
    """將兩個整數相加。
    Args:
        a: 第一個數字。
        b: 第二個數字。
    Returns:
        一個包含總和的字典，例如：{'status': 'success', 'result': 5}
    """
    print(f"工具：add_numbers 被呼叫，參數 a={a}, b={b}")
    result = a + b
    # 範例：在 tool_context 狀態中儲存某些內容
    tool_context.state["last_math_operation"] = "addition"
    return {"status": "success", "result": result}


def subtract_numbers(a: int, b: int) -> Dict[str, Any]:
    """從第一個數字中減去第二個數字。
    Args:
        a: 第一個數字。
        b: 第二個數字。
    Returns:
        一個包含差值的字典，例如：{'status': 'success', 'result': 1}
    """
    print(f"工具：subtract_numbers 被呼叫，參數 a={a}, b={b}")
    return {"status": "success", "result": a - b}


# 2. 透過實作 BaseToolset 建立工具集
class SimpleMathToolset(BaseToolset):
    def __init__(self, prefix: str = "math_"):
        self.prefix = prefix
        # 一次性建立 FunctionTool 實例
        self._add_tool = FunctionTool(
            func=add_numbers,
            name=f"{self.prefix}add_numbers",  # 工具集可以自訂名稱
        )
        self._subtract_tool = FunctionTool(
            func=subtract_numbers, name=f"{self.prefix}subtract_numbers"
        )
        print(f"SimpleMathToolset 已使用前綴 '{self.prefix}' 初始化")

    async def get_tools(
        self, readonly_context: Optional[ReadonlyContext] = None
    ) -> List[BaseTool]:
        print(f"SimpleMathToolset.get_tools() 被呼叫。")
        # 動態行為範例：
        # 可以使用 readonly_context.state 來決定要返回哪些工具
        # 例如，如果 readonly_context.state.get("enable_advanced_math"):
        #    return [self._add_tool, self._subtract_tool, self._multiply_tool]

        # 在這個簡單的範例中，總是返回兩個工具
        tools_to_return = [self._add_tool, self._subtract_tool]
        print(f"SimpleMathToolset 提供的工具：{[t.name for t in tools_to_return]}")
        return tools_to_return

    async def close(self) -> None:
        # 在這個簡單的範例中沒有要清理的資源
        print(f"SimpleMathToolset.close() 被呼叫，前綴為 '{self.prefix}'。")
        await asyncio.sleep(0)  # 如果需要，這是非同步清理的佔位符


# 3. 定義一個單獨的工具（不屬於工具集）
def greet_user(name: str = "User") -> Dict[str, str]:
    """向使用者打招呼。"""
    print(f"工具：greet_user 被呼叫，名稱為 {name}")
    return {"greeting": f"您好，{name}！"}


greet_tool = FunctionTool(func=greet_user)

# 4. 實例化工具集
math_toolset_instance = SimpleMathToolset(prefix="calculator_")

# 5. 定義一個同時使用單獨工具和工具集的代理
calculator_agent = LlmAgent(
    name="CalculatorAgent",
    model="gemini-2.0-flash",  # 替換為您想要的模型
    instruction="您是一個樂於助人的計算器和問候員。"
    "使用 'greet_user' 來打招呼。"
    "使用 'calculator_add_numbers' 來相加，'calculator_subtract_numbers' 來相減。"
    "如果 'last_math_operation' 已設定，請宣告其狀態。",
    tools=[greet_tool, math_toolset_instance],  # 單獨的工具  # 工具集實例
)

##  --8<-- [end:init]

# print(f"代理 '{calculator_agent.name}' 已建立。")

# async def main():
#     session_service = InMemorySessionService()
#     runner = Runner(
#         agent=calculator_agent,
#         app_name="toolset_example_app",
#         session_service=session_service
#     )
#     session = await session_service.create_session(app_name="toolset_example_app", user_id="test_user")
#
#     user_query1 = Content(parts=[Part(text="嗨！")])
#     print("\n--- 查詢 1：問候 ---")
#     async for event in runner.run_async(session_id=session.id, new_message=user_query1):
#         if event.is_final_response(): print(f"代理回應：{event.content.parts[0].text}")
#
#     user_query2 = Content(parts=[Part(text="5 加 3 是多少？")])
#     print("\n--- 查詢 2：加法 ---")
#     async for event in runner.run_async(session_id=session.id, new_message=user_query2):
#         if event.is_final_response(): print(f"代理回應：{event.content.parts[0].text}")
#
#     # 重要：如果工具集管理資源，請清理它
#     await math_toolset_instance.close()
#
# if __name__ == "__main__":
#    asyncio.run(main())
