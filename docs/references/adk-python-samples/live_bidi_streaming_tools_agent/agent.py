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
from typing import AsyncGenerator

from google.adk.agents import LiveRequestQueue
from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool
from google.genai import Client
from google.genai import types as genai_types


async def monitor_stock_price(stock_symbol: str) -> AsyncGenerator[str, None]:
  """此函式將以連續、串流和非同步的方式監控給定 stock_symbol 的價格。"""
  print(f"開始監控 {stock_symbol} 的股價！")

  # 讓我們模擬股價變化。
  await asyncio.sleep(4)
  price_alert1 = f"{stock_symbol} 的價格是 300"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(4)
  price_alert1 = f"{stock_symbol} 的價格是 400"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(20)
  price_alert1 = f"{stock_symbol} 的價格是 900"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(20)
  price_alert1 = f"{stock_symbol} 的價格是 500"
  yield price_alert1
  print(price_alert1)


# 對於視訊串流，`input_stream: LiveRequestQueue` 是 ADK 傳入視訊串流所需的保留關鍵字參數。
async def monitor_video_stream(
    input_stream: LiveRequestQueue,
) -> AsyncGenerator[str, None]:
  """監控視訊串流中有多少人。"""
  print("開始 monitor_video_stream！")
  client = Client(vertexai=False)
  prompt_text = (
      "計算此影像中的人數。僅回應一個數值。"
  )
  last_count = None
  while True:
    last_valid_req = None
    print("開始監控迴圈")

    # 使用此迴圈來提取最新影像並捨棄舊影像
    while input_stream._queue.qsize() != 0:
      live_req = await input_stream.get()

      if live_req.blob is not None and live_req.blob.mime_type == "image/jpeg":
        last_valid_req = live_req

    # 如果我們找到有效的影像，就處理它
    if last_valid_req is not None:
      print("正在處理佇列中最新的影格")

      # 使用 blob 的資料和 mime 類型建立影像部分
      image_part = genai_types.Part.from_bytes(
          data=last_valid_req.blob.data, mime_type=last_valid_req.blob.mime_type
      )

      contents = genai_types.Content(
          role="user",
          parts=[image_part, genai_types.Part.from_text(text=prompt_text)],
      )

      # 呼叫模型以根據提供的影像和提示產生內容
      response = client.models.generate_content(
          model="gemini-2.0-flash-exp",
          contents=contents,
          config=genai_types.GenerateContentConfig(
              system_instruction=(
                  "您是一位樂於助人的視訊分析助理。您可以計算此影像或視訊中的人數。僅回應一個數值。"
              )
          ),
      )
      if not last_count:
        last_count = response.candidates[0].content.parts[0].text
      elif last_count != response.candidates[0].content.parts[0].text:
        last_count = response.candidates[0].content.parts[0].text
        yield response
        print("回應:", response)

    # 等待一下再檢查新影像
    await asyncio.sleep(0.5)


# 使用此確切函式來協助 ADK 在收到請求時停止您的串流工具。
# 例如，如果我們想要停止 `monitor_stock_price`，那麼代理 (agent) 將
# 使用 stop_streaming(function_name=monitor_stock_price) 叫用此函式。
def stop_streaming(function_name: str):
  """停止串流

  參數：
    function_name：要停止的串流函式的名稱。
  """
  pass


root_agent = Agent(
    # 在此處尋找支援的模型：https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/
    model="gemini-2.0-flash-live-preview-04-09",  # 適用於 Vertex 專案
    # model="gemini-live-2.5-flash-preview",  # 適用於 AI studio 金鑰
    name="video_streaming_agent",
    instruction="""
      您是一個監控代理 (agent)。您可以使用提供的工具/函式進行視訊監控和股價監控。
      當使用者想要監控視訊串流時，
      您可以使用 monitor_video_stream 函式來執行此操作。當 monitor_video_stream
      傳回警示時，您應該告知使用者。
      當使用者想要監控股價時，您可以使用 monitor_stock_price。
      不要問太多問題。不要太健談。
    """,
    tools=[
        monitor_video_stream,
        monitor_stock_price,
        FunctionTool(stop_streaming),
    ],
)
