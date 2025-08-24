# 使用 Phoenix 實現代理程式可觀測性

[Phoenix](https://arize.com/docs/phoenix) 是一個開源、可自行託管的可觀測性平台，用於大規模監控、偵錯和改善大型語言模型 (LLM) 應用程式和 AI 代理程式。它為您的 Google ADK 應用程式提供全面的追蹤和評估功能。若要開始，請註冊一個[免費帳戶](https://phoenix.arize.com/)。


## 總覽

Phoenix 可以使用 [OpenInference instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk) 自動從 Google ADK 收集追蹤資料，讓您能夠：

- **追蹤代理程式互動** - 自動捕捉每個代理程式的執行、工具呼叫、模型請求和回應，以及完整的上下文和元數據
- **評估效能** - 使用自訂或預先建立的評估器評估代理程式行為，並執行實驗以測試代理程式設定
- **偵錯問題** - 分析詳細的追蹤資料，以快速識別瓶頸、失敗的工具呼叫和非預期的代理程式行為
- **自行託管控制** - 將您的資料保留在您自己的基礎設施上

## 安裝

### 1. 安裝所需的套件

```bash
pip install openinference-instrumentation-google-adk google-adk arize-phoenix-otel
```

## 設定

### 1. 啟動 Phoenix

這些說明將教您如何使用 Phoenix Cloud。您也可以在筆記本、終端機中[啟動 Phoenix](https://arize.com/docs/phoenix/integrations/llm-providers/google-gen-ai/google-adk-tracing)，或使用容器自行託管。

1. 註冊一個[免費的 Phoenix 帳戶](https://phoenix.arize.com/)。
2. 從您新的 Phoenix 空間的「設定」頁面建立您的 API 金鑰。
3. 複製您的端點，其格式應如下：https://app.phoenix.arize.com/s/[您的空間名稱]

**設定您的 Phoenix 端點和 API 金鑰：**

```python
import os

os.environ["PHOENIX_API_KEY"] = "新增您的 PHOENIX API 金鑰"
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "新增您的 PHOENIX 收集器端點"

# 如果您在 2025 年 6 月 24 日之前建立了 Phoenix Cloud 實例，請將 API 金鑰設定為標頭：
# os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={os.getenv('PHOENIX_API_KEY')}"
```

### 2.  將您的應用程式連接到 Phoenix

```python
from phoenix.otel import register

# 設定 Phoenix 追蹤器
tracer_provider = register(
    project_name="my-llm-app",  # 預設為 'default'
    auto_instrument=True        # 根據已安裝的 OI 相依性自動檢測您的應用程式
)
```

## 觀察

現在您已設定追蹤，所有 Google ADK SDK 的請求都將串流至 Phoenix 進行可觀測性和評估。

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

## 支援與資源
- [Phoenix 文件](https://arize.com/docs/phoenix/integrations/llm-providers/google-gen-ai/google-adk-tracing)
- [社群 Slack](https://arize-ai.slack.com/join/shared_invite/zt-11t1vbu4x-xkBIHmOREQnYnYDH1GDfCg#/shared-invite/email)
- [OpenInference 套件](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
