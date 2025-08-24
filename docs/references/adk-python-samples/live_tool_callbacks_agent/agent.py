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

from datetime import datetime
import random
import time
from typing import Any
from typing import Dict
from typing import Optional

from google.adk.agents.llm_agent import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types


def get_weather(location: str, tool_context: ToolContext) -> Dict[str, Any]:
  """取得某個地點的天氣資訊。
  參數：
    location：要取得天氣資訊的城市或地點。
  傳回：
    包含天氣資訊的字典。
  """
  # 模擬天氣資料
  temperatures = [-10, -5, 0, 5, 10, 15, 20, 25, 30, 35]
  conditions = ["晴天", "多雲", "雨天", "下雪", "有風"]

  return {
      "location": location,
      "temperature": random.choice(temperatures),
      "condition": random.choice(conditions),
      "humidity": random.randint(30, 90),
      "timestamp": datetime.now().isoformat(),
  }


async def calculate_async(operation: str, x: float, y: float) -> Dict[str, Any]:
  """以非同步方式執行數學計算。
  參數：
    operation：要執行的運算（加、減、乘、除）。
    x：第一個數字。
    y：第二個數字。
  傳回：
    包含計算結果的字典。
  """
  # 模擬一些非同步工作
  await asyncio.sleep(0.1)

  operations = {
      "add": x + y,
      "subtract": x - y,
      "multiply": x * y,
      "divide": x / y if y != 0 else float("inf"),
  }

  result = operations.get(operation.lower(), "未知的運算")

  return {
      "operation": operation,
      "x": x,
      "y": y,
      "result": result,
      "timestamp": datetime.now().isoformat(),
  }


def log_activity(message: str, tool_context: ToolContext) -> Dict[str, str]:
  """記錄帶有時間戳記的活動訊息。
  參數：
    message：要記錄的訊息。
  傳回：
    確認記錄項目的字典。
  """
  if "activity_log" not in tool_context.state:
    tool_context.state["activity_log"] = []

  log_entry = {"timestamp": datetime.now().isoformat(), "message": message}
  tool_context.state["activity_log"].append(log_entry)

  return {
      "status": "logged",
      "entry": log_entry,
      "total_entries": len(tool_context.state["activity_log"]),
  }


# 工具前回呼
def before_tool_audit_callback(
    tool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
  """稽核回呼，在執行前記錄所有工具呼叫。"""
  print(f"🔍 AUDIT: 即將使用參數呼叫工具 '{tool.name}'：{args}")

  # 將稽核資訊新增至工具內容狀態
  if "audit_log" not in tool_context.state:
    tool_context.state["audit_log"] = []

  tool_context.state["audit_log"].append({
      "type": "before_call",
      "tool_name": tool.name,
      "args": args,
      "timestamp": datetime.now().isoformat(),
  })

  # 傳回 None 以允許正常工具執行
  return None


def before_tool_security_callback(
    tool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
  """安全性回呼，可封鎖某些工具呼叫。"""
  # 範例：封鎖限制地點的天氣要求
  if tool.name == "get_weather" and args.get("location", "").lower() in [
      "classified",
      "secret",
  ]:
    print(
        "🚫 SECURITY: 已封鎖限制地點的天氣要求："
        f" {args.get('location')}"
    )
    return {
        "error": "存取遭拒",
        "reason": "地點存取受到限制",
        "requested_location": args.get("location"),
    }

  # 允許其他呼叫繼續
  return None


async def before_tool_async_callback(
    tool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
  """非同步前回呼，可新增前置處理。"""
  print(f"⚡ ASYNC BEFORE: 以非同步方式處理工具 '{tool.name}'")

  # 模擬一些非同步前置處理
  await asyncio.sleep(0.05)

  # 對於計算工具，我們可以新增驗證
  if (
      tool.name == "calculate_async"
      and args.get("operation") == "divide"
      and args.get("y") == 0
  ):
    print("🚫 VALIDATION: 已防止除以零")
    return {
        "error": "除以零",
        "operation": args.get("operation"),
        "x": args.get("x"),
        "y": args.get("y"),
    }

  return None


# 工具後回呼
def after_tool_enhancement_callback(
    tool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    tool_response: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
  """使用其他中繼資料增強工具回應。"""
  print(f"✨ ENHANCE: 正在將中繼資料新增至 '{tool.name}' 的回應")

  # 新增增強中繼資料
  enhanced_response = tool_response.copy()
  enhanced_response.update({
      "enhanced": True,
      "enhancement_timestamp": datetime.now().isoformat(),
      "tool_name": tool.name,
      "execution_context": "live_streaming",
  })

  return enhanced_response


async def after_tool_async_callback(
    tool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    tool_response: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
  """用於後處理的非同步後回呼。"""
  print(
      f"🔄 ASYNC AFTER: 以非同步方式後處理來自 '{tool.name}' 的回應"
  )

  # 模擬非同步後處理
  await asyncio.sleep(0.05)

  # 新增非同步處理中繼資料
  processed_response = tool_response.copy()
  processed_response.update({
      "async_processed": True,
      "processing_time": "0.05s",
      "processor": "async_after_callback",
  })

  return processed_response


import asyncio

# 使用工具回呼建立代理 (agent)
root_agent = Agent(
    # 在此處尋找支援的模型：https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/
    model="gemini-2.0-flash-live-preview-04-09",  # 適用於 Vertex 專案
    # model="gemini-live-2.5-flash-preview",  # 適用於 AI studio 金鑰
    name="tool_callbacks_agent",
    description=(
        "展示工具回呼功能的即時串流代理 (agent)。"
        "它可以取得天氣、執行計算和記錄活動，同時"
        "展示工具前回呼和工具後回呼在即時模式下的運作方式。"
    ),
    instruction="""
      您是一位樂於助人的助理，可以：
      1. 使用 get_weather 工具取得任何地點的天氣資訊
      2. 使用 calculate_async 工具執行數學計算
      3. 使用 log_activity 工具記錄活動

      重要的行為注意事項：
      - 您有數個回呼，會在工具呼叫前後觸發
      - 工具前回呼可以稽核、驗證甚至封鎖工具呼叫
      - 工具後回呼可以增強或修改工具回應
      - 某些地點（如「classified」或「secret」）的天氣要求受到限制
      - 驗證回呼將防止除以零
      - 您所有的工具回應都將使用其他中繼資料進行增強

      當使用者要求您測試回呼時，請說明回呼系統的運作方式。
      請以對話方式並說明您觀察到的回呼行為。
    """,
    tools=[
        get_weather,
        calculate_async,
        log_activity,
    ],
    # 多個工具前回呼（將按順序處理，直到其中一個傳回回應）
    before_tool_callback=[
        before_tool_audit_callback,
        before_tool_security_callback,
        before_tool_async_callback,
    ],
    # 多個工具後回呼（將按順序處理，直到其中一個傳回回應）
    after_tool_callback=[
        after_tool_enhancement_callback,
        after_tool_async_callback,
    ],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
