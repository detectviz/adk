# 插件 (Plugins)

## 什麼是插件？

在代理程式開發套件 (ADK) 中，插件 (Plugin) 是一個自訂的程式碼模組，可以使用回呼掛鉤 (callback hooks) 在代理程式工作流程生命週期的各個階段執行。您可以使用插件來實現適用於整個代理程式工作流程的功能。插件的一些典型應用如下：

-   **日誌記錄與追蹤**：建立代理程式、工具和生成式 AI 模型活動的詳細日誌，以進行偵錯和效能分析。
-   **策略強制執行**：實作安全護欄，例如一個檢查使用者是否有權限使用特定工具的函式，如果沒有權限則阻止其執行。
-   **監控與指標**：收集並匯出關於權杖使用量、執行時間和調用次數的指標到監控系統，例如 Prometheus 或 [Google Cloud Observability](https://cloud.google.com/stackdriver/docs) (前身為 Stackdriver)。
-   **回應快取**：檢查請求是否之前已經發出過，以便您可以傳回快取的回應，從而跳過昂貴或耗時的 AI 模型或工具呼叫。
-   **請求或回應修改**：動態地將資訊新增到 AI 模型提示中，或標準化工具輸出回應。

**注意：** [ADK Web 介面](../evaluate/#1-adk-web-run-evaluations-via-the-web-ui)不支援插件。如果您的 ADK 工作流程使用插件，您必須在沒有 Web 介面的情況下執行您的工作流程。

## 插件如何運作？

ADK 插件擴充了 `BasePlugin` 類別，並包含一個或多個 `callback` 方法，指出插件應在代理程式生命週期的哪個位置執行。您可以透過在代理程式的 `Runner` 類別中註冊插件，將其整合到代理程式中。有關如何在您的代理程式應用程式中以及在何處觸發插件的更多資訊，請參閱[插件回呼掛鉤](#plugin-callback-hooks)。

插件功能建立在[回呼 (Callbacks)](../callbacks/) 的基礎之上，這是 ADK 可擴充架構的一個關鍵設計元素。雖然典型的代理程式回呼是針對*單一代理程式、單一工具*的*特定任務*進行設定的，但插件是在 `Runner` 上*註冊一次*，其回呼會*全域*應用於該執行器管理下的每個代理程式、工具和 LLM 呼叫。插件讓您可以將相關的回呼函式打包在一起，以便在整個工作流程中使用。這使得插件成為實作橫跨整個代理程式應用程式的功能的理想解決方案。

## 定義和註冊插件

本節說明如何定義插件類別並將其註冊為代理程式工作流程的一部分。如需完整的程式碼範例，請參閱儲存庫中的 [Plugin Basic](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_basic)。

### 建立插件類別

首先擴充 `BasePlugin` 類別並新增一個或多個 `callback` 方法，如下列程式碼範例所示：

```python
# count_plugin.py
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.plugins.base_plugin import BasePlugin

class CountInvocationPlugin(BasePlugin):
  """一個計算代理程式和工具調用次數的自訂插件。"""

  def __init__(self) -> None:
    """用計數器初始化插件。"""
    super().__init__(name="count_invocation")
    self.agent_count: int = 0
    self.tool_count: int = 0
    self.llm_request_count: int = 0

  async def before_agent_callback(
      self, *, agent: BaseAgent, callback_context: CallbackContext
  ) -> None:
    """計算代理程式執行次數。"""
    self.agent_count += 1
    print(f"[Plugin] 代理程式執行次數：{self.agent_count}")

  async def before_model_callback(
      self, *, callback_context: CallbackContext, llm_request: LlmRequest
  ) -> None:
    """計算 LLM 請求次數。"""
    self.llm_request_count += 1
    print(f"[Plugin] LLM 請求次數：{self.llm_request_count}")
```

此範例程式碼實作了 `before_agent_callback` 和 `before_model_callback` 的回呼，以計算這些任務在代理程式生命週期中的執行次數。

### 註冊插件類別

在代理程式初始化期間，使用 `plugins` 參數將您的插件類別註冊為 `Runner` 類別的一部分，以整合您的插件類別。您可以使用此參數指定多個插件。以下程式碼範例示範如何將上一節中定義的 `CountInvocationPlugin` 插件註冊到一個簡單的 ADK 代理程式中。


```python
from google.adk.runners import InMemoryRunner
from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import asyncio

# 匯入插件。
from .count_plugin import CountInvocationPlugin

async def hello_world(tool_context: ToolContext, query: str):
  print(f'Hello world: 查詢是 [{query}]')

root_agent = Agent(
    model='gemini-2.0-flash',
    name='hello_world',
    description='印出 hello world 與使用者查詢。',
    instruction="""使用 hello_world 工具印出 hello world 和使用者查詢。
    """,
    tools=[hello_world],
)

async def main():
  """代理程式的主要進入點。"""
  prompt = 'hello world'
  runner = InMemoryRunner(
      agent=root_agent,
      app_name='test_app_with_plugin',

      # 在此處新增您的插件。您可以新增多個插件。
      plugins=[CountInvocationPlugin()],
  )

  # 其餘部分與啟動常規 ADK 執行器相同。
  session = await runner.session_service.create_session(
      user_id='user',
      app_name='test_app_with_plugin',
  )

  async for event in runner.run_async(
      user_id='user',
      session_id=session.id,
      new_message=types.Content(
        role='user', parts=[types.Part.from_text(text=prompt)]
      )
  ):
    print(f'** 從 {event.author} 收到事件')

if __name__ == "__main__":
  asyncio.run(main())
```

### 使用插件執行代理程式

像平常一樣執行插件。以下顯示如何執行命令列：

```
> python3 -m path.to.main
```

[ADK Web 介面](../evaluate/#1-adk-web-run-evaluations-via-the-web-ui)不支援插件。如果您的 ADK 工作流程使用插件，您必須在沒有 Web 介面的情況下執行您的工作流程。

先前描述的代理程式的輸出應類似於以下內容：

```
[Plugin] 代理程式執行次數：1
[Plugin] LLM 請求次數：1
** 從 hello_world 收到事件
Hello world: 查詢是 [hello world]
** 從 hello_world 收到事件
[Plugin] LLM 請求次數：2
** 從 hello_world 收到事件
```


有關執行 ADK 代理程式的更多資訊，請參閱[快速入門](/get-started/quickstart/#run-your-agent)指南。

## 使用插件建立工作流程

插件回呼掛鉤是一種實作邏輯的機制，可以攔截、修改甚至控制代理程式的執行生命週期。每個掛鉤都是您插件類別中的一個特定方法，您可以在關鍵時刻實作它來執行程式碼。根據您的掛鉤的傳回值，您可以選擇兩種操作模式：

-   **觀察：** 實作一個沒有傳回值 (`None`) 的掛鉤。這種方法適用於記錄或收集指標等任務，因為它允許代理程式的工作流程在不中斷的情況下繼續到下一步。例如，您可以在插件中使用 `after_tool_callback` 來記錄每個工具的結果以進行偵錯。
-   **介入：** 實作一個掛鉤並傳回一個值。這種方法會使工作流程短路。`Runner` 會停止處理，跳過任何後續的插件和原始預期的操作（如模型呼叫），並使用插件回呼的傳回值作為結果。一個常見的用例是實作 `before_model_callback` 以傳回快取的 `LlmResponse`，從而防止多餘且昂貴的 API 呼叫。
-   **修正：** 實作一個掛鉤並修改 Context 物件。這種方法允許您修改要執行的模組的上下文資料，而不會以其他方式中斷該模組的執行。例如，為模型物件執行新增額外的、標準化的提示文字。

**注意：** 插件回呼函式的優先級高於在物件層級實作的回呼。此行為表示任何插件回呼程式碼都會在任何代理程式、模型或工具物件回呼執行*之前*執行。此外，如果插件層級的代理程式回呼傳回任何值，而不是空 (`None`) 回應，則代理程式、模型或工具層級的回呼*不會執行*（被跳過）。

插件設計建立了一個程式碼執行的階層，並將全域關注點與本地代理程式邏輯分開。插件是您建立的狀態化*模組*，例如 `PerformanceMonitoringPlugin`，而回呼掛鉤是該模組內執行的特定*函式*。這種架構在以下關鍵方面與標準代理程式回呼有根本的不同：

-   **範圍：** 插件掛鉤是*全域*的。您在 `Runner` 上註冊一次插件，其掛鉤會普遍應用於它管理下的每個代理程式、模型和工具。相比之下，代理程式回呼是*本地*的，在特定的代理程式實例上單獨設定。
-   **執行順序：** 插件具有*優先級*。對於任何給定的事件，插件掛鉤總是在任何對應的代理程式回呼之前執行。這種系統行為使得插件成為實作跨領域功能（如安全策略、通用快取和整個應用程式的一致性日誌記錄）的正確架構選擇。

### 代理程式回呼與插件

如前一節所述，插件和代理程式回呼之間存在一些功能上的相似之處。下表更詳細地比較了插件和代理程式回呼之間的差異。

<table>
  <thead>
    <tr>
      <th></th>
      <th><strong>插件</strong></th>
      <th><strong>代理程式回呼</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>範圍</strong></td>
      <td><strong>全域</strong>：應用於 <code>Runner</code> 中的所有代理程式/工具/LLM。</td>
      <td><strong>本地</strong>：僅應用於設定它們的特定代理程式實例。</td>
    </tr>
    <tr>
      <td><strong>主要使用案例</strong></td>
      <td><strong>水平功能</strong>：日誌記錄、策略、監控、全域快取。</td>
      <td><strong>特定代理程式邏輯</strong>：修改單一代理程式的行為或狀態。</td>
    </tr>
    <tr>
      <td><strong>設定</strong></td>
      <td>在 <code>Runner</code> 上設定一次。</td>
      <td>在每個 <code>BaseAgent</code> 實例上單獨設定。</td>
    </tr>
    <tr>
      <td><strong>執行順序</strong></td>
      <td>插件回呼在代理程式回呼<strong>之前</strong>執行。</td>
      <td>代理程式回呼在插件回呼<strong>之後</strong>執行。</td>
    </tr>
  </tbody>
</table>

## 插件回呼掛鉤

您透過在插件類別中定義的回呼函式來定義插件的呼叫時機。當收到使用者訊息、在呼叫 `Runner`、`Agent`、`Model` 或 `Tool` 之前和之後、對於 `Events` 以及當 `Model` 或 `Tool` 發生錯誤時，都可以使用回呼。這些回呼包括並優先於您代理程式、模型和工具類別中定義的任何回呼。

下圖說明了在代理程式工作流程期間可以附加和執行插件功能的回呼點：

![ADK 插件回呼掛鉤](../assets/workflow-plugin-hooks.svg)
**圖 1.** 具有插件回呼掛鉤位置的 ADK 代理程式工作流程圖。

以下各節更詳細地描述了插件可用的回呼掛鉤。

-   [使用者訊息回呼](#user-message-callbacks)
-   [執行器啟動回呼](#runner-start-callbacks)
-   [代理程式執行回呼](#agent-execution-callbacks)
-   [模型回呼](#model-callbacks)
-   [工具回呼](#tool-callbacks)
-   [執行器結束回呼](#runner-end-callbacks)

### 使用者訊息回呼

*使用者訊息回呼* (`on_user_message_callback`) 在使用者傳送訊息時發生。`on_user_message_callback` 是最先執行的掛鉤，讓您有機會檢查或修改初始輸入。\

-   **執行時機：** 此回呼在 `runner.run()` 之後，在任何其他處理之前立即發生。
-   **目的：** 檢查或修改使用者原始輸入的第一次機會。
-   **流程控制：** 傳回一個 `types.Content` 物件以**取代**使用者的原始訊息。

以下程式碼範例顯示了此回呼的基本語法：

```python
async def on_user_message_callback(
    self,
    *,
    invocation_context: InvocationContext,
    user_message: types.Content,
) -> Optional[types.Content]:
```

### 執行器啟動回呼

*執行器啟動*回呼 (`before_run_callback`) 在 `Runner` 物件取得可能已修改的使用者訊息並準備執行時發生。`before_run_callback` 在此處觸發，允許在任何代理程式邏輯開始之前進行全域設定。

-   **執行時機：** 在 `runner.run()` 被呼叫後，在任何其他處理之前立即發生。
-   **目的：** 檢查或修改使用者原始輸入的第一次機會。
-   **流程控制：** 傳回一個 `types.Content` 物件以**取代**使用者的原始訊息。

以下程式碼範例顯示了此回呼的基本語法：

```python
async def before_run_callback(
    self, *, invocation_context: InvocationContext
) -> Optional[types.Content]:
```

### 代理程式執行回呼

*代理程式執行*回呼 (`before_agent`, `after_agent`) 在 `Runner` 物件調用代理程式時發生。`before_agent_callback` 在代理程式的主要工作開始之前立即執行。主要工作包含代理程式處理請求的整個過程，其中可能涉及呼叫模型或工具。在代理程式完成所有步驟並準備好結果後，`after_agent_callback` 會執行。

**注意：** 實作這些回呼的插件會在代理程式層級的回呼執行*之前*執行。此外，如果插件層級的代理程式回呼傳回 `None` 或 null 回應以外的任何內容，則代理程式層級的回呼*不會執行*（被跳過）。

有關作為代理程式物件一部分定義的代理程式回呼的更多資訊，請參閱[回呼類型](../callbacks/types-of-callbacks/#agent-lifecycle-callbacks)。

### 模型回呼

模型回呼 **(`before_model`, `after_model`, `on_model_error`)** 在模型物件執行之前和之後發生。插件功能還支援在發生錯誤時的回呼，詳述如下：

-   如果代理程式需要呼叫 AI 模型，`before_model_callback` 會先執行。
-   如果模型呼叫成功，`after_model_callback` 會接著執行。
-   如果模型呼叫失敗並引發例外，則會觸發 `on_model_error_callback`，從而可以優雅地進行復原。

**注意：** 實作 **`before_model`** 和 `**after_model`** 回呼方法的插件會在模型層級的回呼執行*之前*執行。此外，如果插件層級的模型回呼傳回 `None` 或 null 回應以外的任何內容，則模型層級的回呼*不會執行*（被跳過）。

#### 模型錯誤回呼詳細資訊

模型物件的錯誤回呼僅受插件功能支援，其運作方式如下：

-   **執行時機：** 在模型呼叫期間引發例外時。
-   **常見使用案例：** 優雅的錯誤處理、記錄特定錯誤，或傳回備援回應，例如「AI 服務目前無法使用」。
-   **流程控制：**
    -   傳回一個 `LlmResponse` 物件以**抑制例外**並提供備援結果。
    -   傳回 `None` 以允許引發原始例外。

**注意**：如果模型物件的執行傳回 `LlmResponse`，系統將恢復執行流程，並且 `after_model_callback` 將正常觸發。****

以下程式碼範例顯示了此回呼的基本語法：

```python
async def on_model_error_callback(
    self,
    *,
    callback_context: CallbackContext,
    llm_request: LlmRequest,
    error: Exception,
) -> Optional[LlmResponse]:
```

### 工具回呼

插件的工具回呼 **(`before_tool`, `after_tool`, `on_tool_error`)** 在工具執行之前或之後，或發生錯誤時發生。插件功能還支援在發生錯誤時的回呼，詳述如下：\

-   當代理程式執行工具時，`before_tool_callback` 會先執行。
-   如果工具執行成功，`after_tool_callback` 會接著執行。
-   如果工具引發例外，則會觸發 `on_tool_error_callback`，讓您有機會處理失敗。如果 `on_tool_error_callback` 傳回一個 dict，`after_tool_callback` 將正常觸發。

**注意：** 實作這些回呼的插件會在工具層級的回呼執行*之前*執行。此外，如果插件層級的工具回呼傳回 `None` 或 null 回應以外的任何內容，則工具層級的回呼*不會執行*（被跳過）。

#### 工具錯誤回呼詳細資訊

工具物件的錯誤回呼僅受插件功能支援，其運作方式如下：

-   **執行時機：** 在執行工具的 `run` 方法期間引發例外時。
-   **目的：** 捕捉特定的工具例外（如 `APIError`）、記錄失敗，並向 LLM 提供使用者友善的錯誤訊息。
-   **流程控制：** 傳回一個 `dict` 以**抑制例外**，提供備援結果。傳回 `None` 以允許引發原始例外。

**注意**：透過傳回一個 `dict`，這會恢復執行流程，並且 `after_tool_callback` 將正常觸發。

以下程式碼範例顯示了此回呼的基本語法：

```python
async def on_tool_error_callback(
    self,
    *,
    tool: BaseTool,
    tool_args: dict[str, Any],
    tool_context: ToolContext,
    error: Exception,
) -> Optional[dict]:
```

### 事件回呼

*事件回呼* (`on_event_callback`) 在代理程式產生輸出（例如文字回應或工具呼叫結果）時發生，它會將它們作為 `Event` 物件產生。`on_event_callback` 會為每個事件觸發，讓您可以在將其串流到客戶端之前對其進行修改。

-   **執行時機：** 在代理程式產生 `Event` 之後，但在將其傳送給使用者之前。代理程式的執行可能會產生多個事件。
-   **目的：** 用於修改或豐富事件（例如，新增元數據）或根據特定事件觸發副作用。
-   **流程控制：** 傳回一個 `Event` 物件以**取代**原始事件。

以下程式碼範例顯示了此回呼的基本語法：

```python
async def on_event_callback(
    self, *, invocation_context: InvocationContext, event: Event
) -> Optional[Event]:
```

### 執行器結束回呼

*執行器結束*回呼 **(`after_run_callback`)** 在代理程式完成其整個過程且所有事件都已處理完畢後，`Runner` 會完成其執行。`after_run_callback` 是最後一個掛鉤，非常適合進行清理和最終報告。

-   **執行時機：** 在 `Runner` 完全完成請求的執行之後。
-   **目的：** 非常適合全域清理任務，例如關閉連線或完成日誌和指標資料。
-   **流程控制：** 此回呼僅用於拆卸，無法更改最終結果。

以下程式碼範例顯示了此回呼的基本語法：

```python
async def after_run_callback(
    self, *, invocation_context: InvocationContext
) -> Optional[None]:
```