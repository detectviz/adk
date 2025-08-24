# 使用 Cloud Trace 實現代理程式可觀測性

透過 ADK，您已經能夠利用[此處](https://google.github.io/adk-docs/evaluate/#debugging-with-the-trace-view)討論的強大 Web 開發 UI，在本地端檢查和觀察您的代理程式互動。然而，如果我們的目標是雲端部署，我們將需要一個集中式的儀表板來觀察真實流量。

Cloud Trace 是 Google Cloud Observability 的一個元件。它是一個強大的工具，專注於追蹤功能，用於監控、偵錯和改善您應用程式的效能。對於代理程式開發套件 (ADK) 應用程式，Cloud Trace 可實現全面的追蹤，幫助您了解請求如何在您的代理程式互動中流動，並識別 AI 代理程式中的效能瓶頸或錯誤。

## 總覽

Cloud Trace 建立在 [OpenTelemetry](https://opentelemetry.io/) 之上，這是一個開源標準，支援多種語言和擷取方法以產生追蹤資料。這與 ADK 應用程式的可觀測性實踐一致，後者也利用與 OpenTelemetry 相容的檢測工具，讓您能夠：

- **追蹤代理程式互動**：Cloud Trace 持續收集和分析您專案的追蹤資料，使您能夠快速診斷 ADK 應用程式中的延遲問題和錯誤。這種自動化的資料收集簡化了在複雜代理程式工作流程中識別問題的過程。
- **偵錯問題**：透過分析詳細的追蹤資料，快速診斷延遲問題和錯誤。這對於理解以跨不同服務或在特定代理程式操作（如工具呼叫）期間增加的通訊延遲形式出現的問題至關重要。
- **深入分析與視覺化**：Trace Explorer 是分析追蹤的主要工具，提供視覺輔助工具，如跨度持續時間的熱圖和請求/錯誤率的折線圖。它還提供一個跨度表，可按服務和操作分組，提供對代表性追蹤的一鍵式存取和瀑布式視圖，以輕鬆識別代理程式執行路徑中的瓶頸和錯誤來源。

以下範例將假設使用以下代理程式目錄結構：

```
working_dir/
├── weather_agent/
│   ├── agent.py
│   └── __init__.py
└── deploy_agent_engine.py
└── deploy_fast_api_app.py
└── agent_runner.py
```

```python
# weather_agent/agent.py

import os
from google.adk.agents import Agent

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "{您的專案 ID}")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


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
root_agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    description="使用天氣工具回答問題的代理程式。",
    instruction="您必須使用可用的工具來尋找答案。",
    tools=[get_weather],
)
```

## Cloud Trace 設定

### 代理程式引擎部署設定

#### 代理程式引擎部署 - 從 ADK CLI

您可以在使用 `adk deploy agent_engine` 指令部署代理程式引擎時，透過新增 `--trace_to_cloud` 旗標來啟用雲端追蹤。

```bash
adk deploy agent_engine \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --staging_bucket=$STAGING_BUCKET \
    --trace_to_cloud \
    $AGENT_PATH
```

#### 代理程式引擎部署 - 從 Python SDK

如果您偏好使用 Python SDK，可以在初始化 `AdkApp` 物件時，透過新增 `enable_tracing=True` 來啟用雲端追蹤。

```python
# deploy_agent_engine.py

from vertexai.preview import reasoning_engines
from vertexai import agent_engines
from weather_agent.agent import root_agent

import vertexai

PROJECT_ID = "{您的專案 ID}"
LOCATION = "{您偏好的位置}"
STAGING_BUCKET = "{您的暫存值區}"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

adk_app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)


remote_app = agent_engines.create(
    agent_engine=adk_app,
    extra_packages=[
        "./weather_agent",
    ],
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
    ],
)
```

### Cloud Run 部署設定

#### Cloud Run 部署 - 從 ADK CLI

您可以在使用 `adk deploy cloud_run` 指令部署 Cloud Run 時，透過新增 `--trace_to_cloud` 旗標來啟用雲端追蹤。

```bash
adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --trace_to_cloud \
    $AGENT_PATH
```

如果您想啟用雲端追蹤並在 Cloud Run 上使用自訂的代理程式服務部署，可以參考下面的[自訂部署設定](#setup-for-customized-deployment)部分。

### 自訂部署設定

#### 從內建的 `get_fast_api_app` 模組

如果您想自訂自己的代理程式服務，可以使用內建的 `get_fast_api_app` 模組初始化 FastAPI 應用程式，並設定 `trace_to_cloud=True` 來啟用雲端追蹤。

```python
# deploy_fast_api_app.py

import os
from google.adk.cli.fast_api import get_fast_api_app
from fastapi import FastAPI

# 為雲端追蹤設定 GOOGLE_CLOUD_PROJECT 環境變數
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "alvin-exploratory-2")

# 在目前工作目錄中尋找 `weather_agent` 目錄
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 建立已啟用雲端追蹤的 FastAPI 應用程式
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    trace_to_cloud=True,
)

app.title = "weather-agent"
app.description = "用於與 weather-agent 代理程式互動的 API"


# 主要執行
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
```


#### 從自訂的代理程式執行器

如果您想完全自訂您的 ADK 代理程式執行階段，可以使用 Opentelemetry 的 `CloudTraceSpanExporter` 模組來啟用雲端追蹤。

```python
# agent_runner.py

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from weather_agent.agent import root_agent as weather_agent
from google.genai.types import Content, Part
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import export
from opentelemetry.sdk.trace import TracerProvider

APP_NAME = "weather_agent"
USER_ID = "u_123"
SESSION_ID = "s_123"

provider = TracerProvider()
processor = export.BatchSpanProcessor(
    CloudTraceSpanExporter(project_id="{您的專案 ID}")
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

session_service = InMemorySessionService()
runner = Runner(agent=weather_agent, app_name=APP_NAME, session_service=session_service)


async def main():
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    if session is None:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )

    user_content = Content(
        role="user", parts=[Part(text="巴黎天氣如何？")]
    )

    final_response_content = "沒有回應"
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=user_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_content = event.content.parts[0].text

    print(final_response_content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
```

## 檢查雲端追蹤

設定完成後，每當您與代理程式互動時，它都會自動將追蹤資料傳送到 Cloud Trace。您可以前往 [console.cloud.google.com](https://console.cloud.google.com) 並在設定的 Google Cloud 專案中造訪 Trace Explorer 來檢查追蹤。

![cloud-trace](../assets/cloud-trace1.png)

然後您會看到由 ADK 代理程式產生的所有可用追蹤，這些追蹤被設定在多個跨度名稱中，例如 `invocation`、`agent_run`、`call_llm` 和 `execute_tool`。

![cloud-trace](../assets/cloud-trace2.png)

如果您點擊其中一個追蹤，您將看到詳細流程的瀑布式視圖，類似於我們在 Web 開發 UI 中使用 `adk web` 指令所看到的。

![cloud-trace](../assets/cloud-trace3.png)

## 資源

- [Google Cloud Trace 文件](https://cloud.google.com/trace)
