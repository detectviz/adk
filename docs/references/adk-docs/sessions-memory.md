# 記憶體：使用 `MemoryService` 的長期知識

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前適用於 Python。Java 支援正在計劃/即將推出。"}

我們已經看過 `Session` 如何追蹤*單一、進行中對話*的歷史 (`events`) 和臨時資料 (`state`)。但如果代理程式需要回憶*過去*對話的資訊或存取外部知識庫該怎麼辦？這就是**長期知識 (Long-Term Knowledge)** 和 **`MemoryService`** 發揮作用的地方。

可以這樣想：

* **`Session` / `State`：** 就像您在一次特定聊天中的短期記憶。
* **長期知識 (`MemoryService`)**：就像一個可搜尋的存檔或知識庫，代理程式可以查閱，可能包含許多過去聊天或其他來源的資訊。

## `MemoryService` 的角色

`BaseMemoryService` 定義了管理這個可搜尋的長期知識儲存庫的介面。其主要職責是：

1. **擷取資訊 (`add_session_to_memory`)：** 取得一個（通常是已完成的）`Session` 的內容，並將相關資訊新增到長期知識儲存庫中。
2. **搜尋資訊 (`search_memory`)：** 允許代理程式（通常透過 `Tool`）查詢知識儲存庫，並根據搜尋查詢檢索相關的片段或上下文。

## 選擇正確的記憶體服務

ADK 提供了兩種不同的 `MemoryService` 實作，每種都針對不同的使用案例量身訂做。請使用下表來決定哪種最適合您的代理程式。

| **功能** | **InMemoryMemoryService** | **[新功能!] VertexAiMemoryBankService** |
| :--- | :--- | :--- |
| **持久性** | 無 (資料在重新啟動時會遺失) | 是 (由 Vertex AI 管理) |
| **主要使用案例** | 原型設計、本地開發和簡單測試。 | 從使用者對話中建立有意義、不斷演進的記憶。 |
| **記憶體提取** | 儲存完整對話 | 從對話中提取[有意義的資訊](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/generate-memories)並與現有記憶體合併 (由 LLM 提供支援) |
| **搜尋能力** | 基本關鍵字比對。 | 進階語意搜尋。 |
| **設定複雜度** | 無。它是預設值。 | 低。需要在 Vertex AI 中建立一個[代理程式引擎 (Agent Engine)](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)。 |
| **相依性** | 無。 | Google Cloud 專案、Vertex AI API |
| **使用時機** | 當您想在多個會話的聊天歷史記錄中進行搜尋以進行原型設計時。 | 當您希望您的代理程式記住並從過去的互動中學習時。 |

## 記憶體內記憶體 (In-Memory Memory)

`InMemoryMemoryService` 將會話資訊儲存在應用程式的記憶體中，並對搜尋執行基本的關鍵字比對。它不需要任何設定，最適合不需要持久性的原型設計和簡單測試場景。

```python
from google.adk.memory import InMemoryMemoryService
memory_service = InMemoryMemoryService()
```

**範例：新增和搜尋記憶體**

此範例為了簡單起見，使用 `InMemoryMemoryService` 來示範基本流程。

??? "完整程式碼"

    ```python
    import asyncio
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.memory import InMemoryMemoryService # 匯入 MemoryService
    from google.adk.runners import Runner
    from google.adk.tools import load_memory # 查詢記憶體的工具
    from google.genai.types import Content, Part

    # --- 常數 ---
    APP_NAME = "memory_example_app"
    USER_ID = "mem_user"
    MODEL = "gemini-2.0-flash" # 使用一個有效的模型

    # --- 代理程式定義 ---
    # 代理程式 1：用於擷取資訊的簡單代理程式
    info_capture_agent = LlmAgent(
        model=MODEL,
        name="InfoCaptureAgent",
        instruction="確認使用者的陳述。",
    )

    # 代理程式 2：可以使用記憶體的代理程式
    memory_recall_agent = LlmAgent(
        model=MODEL,
        name="MemoryRecallAgent",
        instruction="回答使用者的問題。如果答案可能在過去的對話中，請使用 'load_memory' 工具。",
        tools=[load_memory] # 將工具提供給代理程式
    )

    # --- 服務 ---
    # 服務必須在執行器之間共享，以共享狀態和記憶體
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService() # 為了示範使用記憶體內記憶體

    async def run_scenario():
        # --- 情境 ---

        # 第 1 輪：在一個會話中擷取一些資訊
        print("--- 第 1 輪：擷取資訊 ---")
        runner1 = Runner(
            # 從資訊擷取代理程式開始
            agent=info_capture_agent,
            app_name=APP_NAME,
            session_service=session_service,
            memory_service=memory_service # 將記憶體服務提供給 Runner
        )
        session1_id = "session_info"
        await runner1.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)
        user_input1 = Content(parts=[Part(text="我最喜歡的專案是 Alpha 專案。")], role="user")

        # 執行代理程式
        final_response_text = "(沒有最終回應)"
        async for event in runner1.run_async(user_id=USER_ID, session_id=session1_id, new_message=user_input1):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
        print(f"代理程式 1 回應：{final_response_text}")

        # 取得已完成的會話
        completed_session1 = await runner1.session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)

        # 將此會話的內容新增到記憶體服務中
        print("\n--- 將會話 1 新增到記憶體 ---")
        await memory_service.add_session_to_memory(completed_session1)
        print("會話已新增到記憶體。")

        # 第 2 輪：在一個新會話中回憶資訊
        print("\n--- 第 2 輪：回憶資訊 ---")
        runner2 = Runner(
            # 使用第二個代理程式，它有記憶體工具
            agent=memory_recall_agent,
            app_name=APP_NAME,
            session_service=session_service, # 重複使用相同的服務
            memory_service=memory_service   # 重複使用相同的服務
        )
        session2_id = "session_recall"
        await runner2.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session2_id)
        user_input2 = Content(parts=[Part(text="我最喜歡的專案是什麼？")], role="user")

        # 執行第二個代理程式
        final_response_text_2 = "(沒有最終回應)"
        async for event in runner2.run_async(user_id=USER_ID, session_id=session2_id, new_message=user_input2):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text_2 = event.content.parts[0].text
        print(f"代理程式 2 回應：{final_response_text_2}")

    # 若要執行此範例，您可以使用以下程式碼片段：
    # asyncio.run(run_scenario())

    # await run_scenario()
    ```

## Vertex AI 記憶庫 (Memory Bank)

`VertexAiMemoryBankService` 將您的代理程式連接到 [Vertex AI 記憶庫](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)，這是一個完全託管的 Google Cloud 服務，為對話式代理程式提供複雜、持久的記憶體功能。

### 運作方式

該服務會自動處理兩個關鍵操作：

*   **產生記憶：** 在對話結束時，ADK 會將會話的事件傳送到記憶庫，後者會智慧地處理資訊並將其儲存為「記憶」。
*   **檢索記憶：** 您的代理程式程式碼可以對記憶庫發出搜尋查詢，以從過去的對話中檢索相關的記憶。

### 先決條件

在您可以使用此功能之前，您必須具備：

1.  **一個 Google Cloud 專案：** 並已啟用 Vertex AI API。
2.  **一個代理程式引擎：** 您需要在 Vertex AI 中建立一個代理程式引擎。這將為您提供設定所需的**代理程式引擎 ID**。
3.  **驗證：** 確保您的本地環境已通過驗證，可以存取 Google Cloud 服務。最簡單的方法是執行：
    ```bash
    gcloud auth application-default login
    ```
4.  **環境變數：** 該服務需要您的 Google Cloud 專案 ID 和位置。請將它們設定為環境變數：
    ```bash
    export GOOGLE_CLOUD_PROJECT="您的-gcp-專案-id"
    export GOOGLE_CLOUD_LOCATION="您的-gcp-位置"
    ```

### 設定

若要將您的代理程式連接到記憶庫，您可以在啟動 ADK 伺服器（`adk web` 或 `adk api_server`）時使用 `--memory_service_uri` 旗標。URI 的格式必須為 `agentengine://<agent_engine_id>`。

```bash title="bash"
adk web path/to/your/agents_dir --memory_service_uri="agentengine://1234567890"
```

或者，您可以透過手動實例化 `VertexAiMemoryBankService` 並將其傳遞給 `Runner` 來設定您的代理程式使用記憶庫。

```python
from google.adk.memory import VertexAiMemoryBankService

agent_engine_id = agent_engine.api_resource.name.split("/")[-1]

memory_service = VertexAiMemoryBankService(
    project="專案ID",
    location="位置",
    agent_engine_id=agent_engine_id
)

runner = adk.Runner(
    ...
    memory_service=memory_service
)
``` 

### 在您的代理程式中使用記憶體

設定服務後，ADK 會自動將會話資料儲存到記憶庫中。若要讓您的代理程式使用此記憶體，您需要從代理程式的程式碼中呼叫 `search_memory` 方法。

這通常在輪次開始時完成，以在產生回應之前擷取相關的上下文。

**範例：**

```python
from google.adk.agents import Agent
from google.genai import types

class MyAgent(Agent):
    async def run(self, request: types.Content, **kwargs) -> types.Content:
        # 取得使用者的最新訊息
        user_query = request.parts[0].text

        # 在記憶體中搜尋與使用者查詢相關的上下文
        search_result = await self.search_memory(query=user_query)

        # 建立一個包含檢索到的記憶的提示
        prompt = f"根據我的記憶，這是我對您查詢的回憶：{search_result.memories}\n\n現在，請回答：{user_query}"

        # 使用增強的提示呼叫 LLM
        return await self.llm.generate_content_async(prompt)
```

## 進階概念

### 記憶體在實務中如何運作

記憶體工作流程在內部涉及以下步驟：

1. **會話互動：** 使用者透過 `SessionService` 管理的 `Session` 與代理程式互動。事件被新增，狀態可能會更新。
2. **擷取到記憶體中：** 在某個時間點（通常是當會話被視為完成或已產生重要資訊時），您的應用程式會呼叫 `memory_service.add_session_to_memory(session)`。這會從會話的事件中提取相關資訊，並將其新增到長期知識儲存庫（記憶體內字典或 RAG 語料庫）。
3. **稍後的查詢：** 在一個*不同*（或相同）的會話中，使用者可能會問一個需要過去上下文的問題（例如，「我們上週討論了關於 X 專案的什麼？」）。
4. **代理程式使用記憶體工具：** 配備了記憶體檢索工具（如內建的 `load_memory` 工具）的代理程式會識別出需要過去的上下文。它會呼叫該工具，提供一個搜尋查詢（例如，「上週討論 X 專案」）。
5. **搜尋執行：** 該工具在內部呼叫 `memory_service.search_memory(app_name, user_id, query)`。
6. **傳回結果：** `MemoryService` 會搜尋其儲存庫（使用關鍵字比對或語意搜尋），並將相關的片段作為包含 `MemoryResult` 物件列表的 `SearchMemoryResponse` 傳回（每個物件可能包含來自相關過去會話的事件）。
7. **代理程式使用結果：** 該工具將這些結果傳回給代理程式，通常作為上下文或函式回應的一部分。然後，代理程式可以使用此檢索到的資訊來制定對使用者的最終答案。

### 一個代理程式可以存取多個記憶體服務嗎？

*   **透過標準設定：否。** 該框架（`adk web`、`adk api_server`）被設計為一次只能透過 `--memory_service_uri` 旗標設定一個記憶體服務。然後，這個單一服務會被提供給代理程式，並透過內建的 `self.search_memory()` 方法存取。從設定的角度來看，您只能為該程序服務的所有代理程式選擇一個後端（`InMemory`、`VertexAiMemoryBankService`）。

*   **在您的代理程式程式碼中：是的，絕對可以。** 沒有什麼能阻止您直接在代理程式的程式碼中手動匯入和實例化另一個記憶體服務。這允許您在單一代理程式輪次中存取多個記憶體來源。

例如，您的代理程式可以使用框架設定的 `VertexAiMemoryBankService` 來回憶對話歷史，也可以手動實例化一個 `InMemoryMemoryService` 來查詢技術手冊中的資訊。

#### 範例：使用兩個記憶體服務

以下是您可以在代理程式程式碼中實作的方法：

```python
from google.adk.agents import Agent
from google.adk.memory import InMemoryMemoryService, VertexAiMemoryBankService
from google.genai import types

class MultiMemoryAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.memory_service = InMemoryMemoryService()
        # 手動實例化第二個記憶體服務以進行文件查詢
        self.vertexai_memorybank_service = VertexAiMemoryBankService(
            project="專案ID",
            location="位置",
            agent_engine_id="代理程式引擎ID"
        )

    async def run(self, request: types.Content, **kwargs) -> types.Content:
        user_query = request.parts[0].text

        # 1. 使用框架提供的記憶體搜尋對話歷史
        #    (如果已設定，這將是 InMemoryMemoryService)
        conversation_context = await self.search_memory(query=user_query)

        # 2. 使用手動建立的服務搜尋文件知識庫
        document_context = await self.vertexai_memorybank_service.search_memory(query=user_query)

        # 結合兩個來源的上下文以產生更好的回應
        prompt = "從我們過去的對話中，我記得：\n"
        prompt += f"{conversation_context.memories}\n\n"
        prompt += "從技術手冊中，我發現：\n"
        prompt += f"{document_context.memories}\n\n"
        prompt += f"基於所有這些，這是我對 '{user_query}' 的回答："

        return await self.llm.generate_content_async(prompt)
```
