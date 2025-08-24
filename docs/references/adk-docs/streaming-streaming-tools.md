# 串流工具

!!! info

    這僅在串流（即時）代理程式/API 中受支援。

串流工具允許工具（函式）將中間結果串流回代理程式，代理程式可以對這些中間結果做出回應。
例如，我們可以使用串流工具來監控股價的變化，並讓代理程式對其做出反應。另一個例子是，我們可以讓代理程式監控視訊串流，當視訊串流發生變化時，代理程式可以報告這些變化。

要定義串流工具，您必須遵守以下規定：

1.  **非同步函式：** 該工具必須是一個 `async` Python 函式。
2.  **AsyncGenerator 傳回類型：** 該函式必須被類型化以傳回一個 `AsyncGenerator`。`AsyncGenerator` 的第一個類型參數是您 `yield` 的資料類型（例如，`str` 用於文字訊息，或自訂物件用於結構化資料）。如果產生器不透過 `send()` 接收值，則第二個類型參數通常是 `None`。


我們支援兩種串流工具：
- 簡單類型。這是一種只接受非視訊/音訊串流（您饋送給 adk web 或 adk runner 的串流）作為輸入的串流工具。
- 視訊串流工具。這僅適用於視訊串流，視訊串流（您饋送給 adk web 或 adk runner 的串流）將被傳遞到此函式中。

現在讓我們定義一個可以監控股價變化和監控視訊串流變化的代理程式。

```python
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


# 對於視訊串流，`input_stream: LiveRequestQueue` 是 ADK 傳入視訊串流所必需的保留關鍵字參數。
async def monitor_video_stream(
    input_stream: LiveRequestQueue,
) -> AsyncGenerator[str, None]:
  """監控視訊串流中有多少人。"""
  print("開始 monitor_video_stream！")
  client = Client(vertexai=False)
  prompt_text = (
      "計算此影像中的人數。只需回應一個數字。"
  )
  last_count = None
  while True:
    last_valid_req = None
    print("開始監控迴圈")

    # 使用此迴圈來拉取最新的影像並捨棄舊的影像
    while input_stream._queue.qsize() != 0:
      live_req = await input_stream.get()

      if live_req.blob is not None and live_req.blob.mime_type == "image/jpeg":
        last_valid_req = live_req

    # 如果我們找到一個有效的影像，就處理它
    if last_valid_req is not None:
      print("正在處理佇列中最新的影格")

      # 使用 blob 的資料和 mime 類型建立一個影像部分
      image_part = genai_types.Part.from_bytes(
          data=last_valid_req.blob.data, mime_type=last_valid_req.blob.mime_type
      )

      contents = genai_types.Content(
          role="user",
          parts=[image_part, genai_types.Part.from_text(prompt_text)],
      )

      # 呼叫模型以根據提供的影像和提示產生內容
      response = client.models.generate_content(
          model="gemini-2.0-flash-exp",
          contents=contents,
          config=genai_types.GenerateContentConfig(
              system_instruction=(
                  "您是一個樂於助人的視訊分析助理。您可以計算此影像或視訊中的人數。只需回應一個數字。"
              )
          ),
      )
      if not last_count:
        last_count = response.candidates[0].content.parts[0].text
      elif last_count != response.candidates[0].content.parts[0].text:
        last_count = response.candidates[0].content.parts[0].text
        yield response
        print("回應：", response)

    # 在檢查新影像之前等待
    await asyncio.sleep(0.5)


# 使用此確切函式來幫助 ADK 在請求時停止您的串流工具。
# 例如，如果我們想停止 `monitor_stock_price`，那麼代理程式將
# 使用 stop_streaming(function_name=monitor_stock_price) 調用此函式。
def stop_streaming(function_name: str):
  """停止串流

  Args:
    function_name: 要停止的串流函式的名稱。
  """
  pass


root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="video_streaming_agent",
    instruction="""
      您是一個監控代理程式。您可以使用提供的工具/函式進行視訊監控和股價監控。
      當使用者想要監控視訊串流時，
      您可以使用 monitor_video_stream 函式來執行此操作。當 monitor_video_stream
      傳回警報時，您應該告訴使用者。
      當使用者想要監控股價時，您可以使用 monitor_stock_price。
      不要問太多問題。不要太健談。
    """,
    tools=[
        monitor_video_stream,
        monitor_stock_price,
        FunctionTool(stop_streaming),
    ]
)
```

以下是一些可供測試的範例查詢：
- 幫我監控 $XYZ 股票的股價。
- 幫我監控視訊串流中有多少人。
