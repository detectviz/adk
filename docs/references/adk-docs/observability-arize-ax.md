# 使用 Arize AX 實現代理程式可觀測性

[Arize AX](https://arize.com/docs/ax) 是一個生產級的可觀測性平台，用於大規模監控、偵錯和改善大型語言模型 (LLM) 應用程式和 AI 代理程式。它為您的 Google ADK 應用程式提供全面的追蹤、評估和監控功能。若要開始，請註冊一個[免費帳戶](https://app.arize.com/auth/join)。

若想尋找開源、可自行託管的替代方案，請查看 [Phoenix](https://arize.com/docs/phoenix)。

## 總覽

Arize AX 可以使用 [OpenInference instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk) 自動從 Google ADK 收集追蹤資料，讓您能夠：

- **追蹤代理程式互動** - 自動捕捉每個代理程式的執行、工具呼叫、模型請求和回應，以及相關的上下文和元數據
- **評估效能** - 使用自訂或預先建立的評估器評估代理程式行為，並執行實驗以測試代理程式設定
- **在生產環境中監控** - 設定即時儀表板和警報以追蹤效能
- **偵錯問題** - 分析詳細的追蹤資料，以快速識別瓶頸、失敗的工具呼叫和任何非預期的代理程式行為

![代理程式追蹤](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-traces.png)

## 安裝

安裝所需的套件：

```bash
pip install openinference-instrumentation-google-adk google-adk arize-otel
```

## 設定

### 1. 設定環境變數

設定您的 Google API 金鑰：

```bash
export GOOGLE_API_KEY=[此處填入您的金鑰]
```

### 2. 將您的應用程式連接到 Arize AX

```python
from arize.otel import register

# 註冊 Arize AX
tracer_provider = register(
    space_id="您的空間ID",      # 在應用程式空間設定頁面中找到
    api_key="您的API金鑰",        # 在應用程式空間設定頁面中找到
    project_name="您的專案名稱"  # 可自行命名
)

# 從 OpenInference 匯入並設定自動檢測器
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

# 完成自動檢測
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)
```

## 觀察

現在您已設定追蹤，所有 Google ADK SDK 的請求都將串流至 Arize AX 進行可觀測性和評估。

```python
import nest_asyncio
nest_asyncio.apply()

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# 定義一個工具函式
def get_weather(city: str) -> dict:
    """擷取指定城市的目前天氣報告。

    Args:
        city (str): 要擷取天氣報告的城市名稱。

    Returns:
        dict: 狀態和結果或錯誤訊息。
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "紐約天氣晴朗，溫度為攝氏 25 度"
                " (華氏 77 度)。"
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"無法提供 '{city}' 的天氣資訊。",
        }

# 建立一個帶有工具的代理程式
agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash-exp",
    description="使用天氣工具回答問題的代理程式。",
    instruction="您必須使用可用的工具來尋找答案。",
    tools=[get_weather]
)

app_name = "weather_app"
user_id = "test_user"
session_id = "test_session"
runner = InMemoryRunner(agent=agent, app_name=app_name)
session_service = runner.session_service

await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id
)

# 執行代理程式 (所有互動都將被追蹤)
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(role="user", parts=[
        types.Part(text="紐約現在天氣如何？")]
    )
):
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```
## 在 Arize AX 中查看結果
![Arize AX 中的追蹤](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-dashboard.png)
![代理程式視覺化](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-agent.png)
![代理程式實驗](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-experiments.png)

## 支援與資源
- [Arize AX 文件](https://arize.com/docs/ax/observe/tracing-integrations-auto/google-adk)
- [Arize 社群 Slack](https://arize-ai.slack.com/join/shared_invite/zt-11t1vbu4x-xkBIHmOREQnYnYDH1GDfCg#/shared-invite/email)
- [OpenInference 套件](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
