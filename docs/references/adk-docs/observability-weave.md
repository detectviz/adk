# 使用 Weave by WandB 實現 Agent 可觀察性

[Weave by Weights & Biases (WandB)](https://weave-docs.wandb.ai/) 提供了一個強大的平台，用於記錄和視覺化模型呼叫。透過將 Google ADK 與 Weave 整合，您可以使用 OpenTelemetry (OTEL) 追蹤來監控和分析您 Agent 的性能和行為。

## 先決條件

1. 在 [WandB](https://wandb.ai) 註冊一個帳戶。

2. 從 [WandB Authorize](https://wandb.ai/authorize) 獲取您的 API 金鑰。

3. 使用所需的 API 金鑰配置您的環境：

   ```bash
   export WANDB_API_KEY=<your-wandb-api-key>
   export GOOGLE_API_KEY=<your-google-api-key>
   ```

## 安裝依賴套件

確保您已安裝必要的套件：

```bash
pip install google-adk opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

## 將追蹤發送到 Weave

此範例示範如何設定 OpenTelemetry 以將 Google ADK 追蹤發送到 Weave。

```python
# math_agent/agent.py

import base64
import os
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry import trace

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from dotenv import load_dotenv

load_dotenv()

# 設定 Weave 端點和身份驗證
WANDB_BASE_URL = "https://trace.wandb.ai"
PROJECT_ID = "your-entity/your-project"  # 例如 "teamid/projectid"
OTEL_EXPORTER_OTLP_ENDPOINT = f"{WANDB_BASE_URL}/otel/v1/traces"

# 設定身份驗證
WANDB_API_KEY = os.getenv("WANDB_API_KEY")
AUTH = base64.b64encode(f"api:{WANDB_API_KEY}".encode()).decode()

OTEL_EXPORTER_OTLP_HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "project_id": PROJECT_ID,
}

# 建立帶有端點和標頭的 OTLP span 匯出器
exporter = OTLPSpanExporter(
    endpoint=OTEL_EXPORTER_OTLP_ENDPOINT,
    headers=OTEL_EXPORTER_OTLP_HEADERS,
)

# 建立一個追蹤提供者並添加匯出器
tracer_provider = trace_sdk.TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))

# 在匯入/使用 ADK 之前設定全域追蹤提供者
trace.set_tracer_provider(tracer_provider)

# 定義一個簡單的工具以供示範
def calculator(a: float, b: float) -> str:
    """將兩個數字相加並返回結果。

    Args:
        a: 第一個數字
        b: 第二個數字

    Returns:
        a 和 b 的總和
    """
    return str(a + b)

calculator_tool = FunctionTool(func=calculator)

# 建立一個 LLM Agent
root_agent = LlmAgent(
    name="MathAgent",
    model="gemini-2.0-flash-exp",
    instruction=(
        "你是一個樂於助人的助理，可以進行數學運算。"
        "當被問到數學問題時，請使用計算器工具來解決。"
    ),
    tools=[calculator_tool],
)
```

## 在 Weave 儀表板中查看追蹤

一旦 Agent 運行，其所有追蹤都會記錄到 [Weave 儀表板](https://wandb.ai/home) 上對應的專案中。

![Weave 中的追蹤](https://wandb.github.io/weave-public-assets/google-adk/traces-overview.png)

您可以在執行期間查看 ADK Agent 進行的呼叫時間軸 -

![時間軸視圖](https://wandb.github.io/weave-public-assets/google-adk/adk-weave-timeline.gif)


## 注意事項

- **環境變數**：確保您的 WandB 和 Google API 金鑰的環境變數都已正確設定。
- **專案配置**：請將 `<your-entity>/<your-project>` 替換為您實際的 WandB 實體和專案名稱。
- **實體名稱**：您可以訪問您的 [WandB 儀表板](https://wandb.ai/home) 並在左側邊欄中查看 **Teams** 欄位來找到您的實體名稱。
- **追蹤提供者**：在​​使用任何 ADK 元件之前設定全域追蹤提供者至關重要，以確保正確的追蹤。

透過遵循這些步驟，您可以有效地將 Google ADK 與 Weave 整合，從而實現對您的 AI Agent 的模型呼叫、工具調用和推理過程的全面記錄和視覺化。

## 資源

- **[將 OpenTelemetry 追蹤發送到 Weave](https://weave-docs.wandb.ai/guides/tracking/otel)** - 關於使用 Weave 設定 OTEL 的綜合指南，包括身份驗證和進階配置選項。

- **[導覽追蹤視圖](https://weave-docs.wandb.ai/guides/tracking/trace-tree)** - 了解如何在 Weave UI 中有效地分析和偵錯您的追蹤，包括理解追蹤層次結構和 span 詳細資訊。

- **[Weave 整合](https://weave-docs.wandb.ai/guides/integrations/)** - 探索其他框架整合，了解 Weave 如何與您的整個 AI 堆疊協同工作。