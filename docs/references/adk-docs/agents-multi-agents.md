# ADK 中的多代理系統

隨著代理應用程式的複雜性增加，將其建構成單一、龐大的代理在開發、維護和推理方面可能會變得具有挑戰性。代理開發套件 (ADK) 支援透過將多個不同的 `BaseAgent` 實例組合成一個**多代理系統 (MAS)** 來建構複雜的應用程式。

在 ADK 中，多代理系統是一個應用程式，其中不同的代理 (通常形成一個層級結構) 協作或協調以實現一個更大的目標。以這種方式建構您的應用程式具有顯著的優勢，包括增強的模組化、專業化、可重複使用性、可維護性，以及使用專用工作流程代理定義結構化控制流程的能力。

您可以組合衍生自 `BaseAgent` 的各種類型的代理來建構這些系統：

* **LLM 代理：** 由大型語言模型驅動的代理。(請參閱 [LLM 代理](agents-llm-agents.md))
* **工作流程代理：** 專門的代理 (`SequentialAgent`、`ParallelAgent`、`LoopAgent`)，旨在管理其子代理的執行流程。(請參閱[工作流程代理](agents-workflow-agents.md))
* **自訂代理：** 您自己的代理，繼承自 `BaseAgent`，具有專門的、非 LLM 的邏輯。(請參閱[自訂代理](agents-custom-agents.md))

以下各節詳細介紹了核心的 ADK 原語——例如代理層級、工作流程代理和互動機制——使您能夠有效地建構和管理這些多代理系統。

## 1. 用於代理組合的 ADK 原語

ADK 提供了核心建構區塊——原語——使您能夠在多代理系統中建構和管理互動。

!!! Note
    原語的特定參數或方法名稱可能會因 SDK 語言而略有不同 (例如，Python 中的 `sub_agents`，Java 中的 `subAgents`)。有關詳細資訊，請參閱特定語言的 API 文件。

### 1.1. 代理層級 (父代理、子代理)

建構多代理系統的基礎是在 `BaseAgent` 中定義的父子關係。

* **建立層級：** 您可以透過在初始化父代理時將代理實例列表傳遞給 `sub_agents` 引數來建立一個樹狀結構。ADK 會在初始化期間自動設定每個子代理的 `parent_agent` 屬性。
* **單一父級規則：** 一個代理實例只能作為子代理新增一次。嘗試指派第二個父級將導致 `ValueError`。
* **重要性：** 此層級定義了[工作流程代理](#12-workflow-agents-as-orchestrators)的範圍，並影響了 LLM 驅動委派的潛在目標。您可以使用 `agent.parent_agent` 導覽層級或使用 `agent.find_agent(name)` 尋找後代。

=== "Python"

    ```python
    # 概念範例：定義層級
    from google.adk.agents import LlmAgent, BaseAgent
    
    # 定義個別代理
    greeter = LlmAgent(name="Greeter", model="gemini-2.0-flash")
    task_doer = BaseAgent(name="TaskExecutor") # 自訂非 LLM 代理
    
    # 建立父代理並透過 sub_agents 指派子代理
    coordinator = LlmAgent(
        name="Coordinator",
        model="gemini-2.0-flash",
        description="我協調問候和任務。",
        sub_agents=[ # 在此處指派子代理
            greeter,
            task_doer
        ]
    )
    
    # 框架自動設定：
    # assert greeter.parent_agent == coordinator
    # assert task_doer.parent_agent == coordinator
    ```

=== "Java"

    ```java
    // 概念範例：定義層級
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.agents.LlmAgent;
    
    // 定義個別代理
    LlmAgent greeter = LlmAgent.builder().name("Greeter").model("gemini-2.0-flash").build();
    SequentialAgent taskDoer = SequentialAgent.builder().name("TaskExecutor").subAgents(...).build(); // 循序代理
    
    // 建立父代理並指派子代理
    LlmAgent coordinator = LlmAgent.builder()
        .name("Coordinator")
        .model("gemini-2.0-flash")
        .description("我協調問候和任務")
        .subAgents(greeter, taskDoer) // 在此處指派子代理
        .build();
    
    // 框架自動設定：
    // assert greeter.parentAgent().equals(coordinator);
    // assert taskDoer.parentAgent().equals(coordinator);
    ```

### 1.2. 作為協調器的工作流程代理

ADK 包括衍生自 `BaseAgent` 的專門代理，它們本身不執行任務，而是協調其 `sub_agents` 的執行流程。

* **[`SequentialAgent`](agents-workflow-agents-sequential-agents.md)：** 按照列出的順序一個接一個地執行其 `sub_agents`。
    * **上下文：** 循序傳遞*相同*的 [`InvocationContext`](runtime.md)，允許代理透過共用狀態輕鬆傳遞結果。

=== "Python"

    ```python
    # 概念範例：循序管線
    from google.adk.agents import SequentialAgent, LlmAgent

    step1 = LlmAgent(name="Step1_Fetch", output_key="data") # 將輸出儲存到 state['data']
    step2 = LlmAgent(name="Step2_Process", instruction="處理來自 {data} 的資料。")

    pipeline = SequentialAgent(name="MyPipeline", sub_agents=[step1, step2])
    # 當 pipeline 執行時，Step2 可以存取由 Step1 設定的 state['data']。
    ```

=== "Java"

    ```java
    // 概念範例：循序管線
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.agents.LlmAgent;

    LlmAgent step1 = LlmAgent.builder().name("Step1_Fetch").outputKey("data").build(); // 將輸出儲存到 state.get("data")
    LlmAgent step2 = LlmAgent.builder().name("Step2_Process").instruction("處理來自 {data} 的資料。").build();

    SequentialAgent pipeline = SequentialAgent.builder().name("MyPipeline").subAgents(step1, step2).build();
    // 當 pipeline 執行時，Step2 可以存取由 Step1 設定的 state.get("data")。
    ```

* **[`ParallelAgent`](agents-workflow-agents-parallel-agents.md)：** 平行執行其 `sub_agents`。來自子代理的事件可能會交錯。
    * **上下文：** 為每個子代理修改 `InvocationContext.branch` (例如 `ParentBranch.ChildName`)，提供一個不同的上下文路徑，這對於在某些記憶體實作中隔離歷史記錄很有用。
    * **狀態：** 儘管分支不同，所有平行的子代理都存取*相同共用*的 `session.state`，使它們能夠讀取初始狀態並寫入結果 (使用不同的鍵以避免競爭條件)。

=== "Python"

    ```python
    # 概念範例：平行執行
    from google.adk.agents import ParallelAgent, LlmAgent

    fetch_weather = LlmAgent(name="WeatherFetcher", output_key="weather")
    fetch_news = LlmAgent(name="NewsFetcher", output_key="news")

    gatherer = ParallelAgent(name="InfoGatherer", sub_agents=[fetch_weather, fetch_news])
    # 當 gatherer 執行時，WeatherFetcher 和 NewsFetcher 會同時執行。
    # 後續的代理可以讀取 state['weather'] 和 state['news']。
    ```
  
=== "Java"

    ```java
    // 概念範例：平行執行
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.ParallelAgent;
   
    LlmAgent fetchWeather = LlmAgent.builder()
        .name("WeatherFetcher")
        .outputKey("weather")
        .build();
    
    LlmAgent fetchNews = LlmAgent.builder()
        .name("NewsFetcher")
        .instruction("news")
        .build();
    
    ParallelAgent gatherer = ParallelAgent.builder()
        .name("InfoGatherer")
        .subAgents(fetchWeather, fetchNews)
        .build();
    
    // 當 gatherer 執行時，WeatherFetcher 和 NewsFetcher 會同時執行。
    // 後續的代理可以讀取 state['weather'] 和 state['news']。
    ```

  * **[`LoopAgent`](agents-workflow-agents-loop-agents.md)：** 在一個循環中循序執行其 `sub_agents`。
      * **終止：** 如果達到可選的 `max_iterations`，或者任何子代理在其事件動作中傳回 `escalate=True` 的 [`Event`](events.md)，則循環停止。
      * **上下文和狀態：** 在每次迭代中傳遞*相同*的 `InvocationContext`，允許狀態變更 (例如計數器、旗標) 在循環之間持續存在。

=== "Python"

      ```python
      # 概念範例：帶條件的循環
      from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
      from google.adk.events import Event, EventActions
      from google.adk.agents.invocation_context import InvocationContext
      from typing import AsyncGenerator

      class CheckCondition(BaseAgent): # 檢查狀態的自訂代理
          async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
              status = ctx.session.state.get("status", "pending")
              is_done = (status == "completed")
              yield Event(author=self.name, actions=EventActions(escalate=is_done)) # 如果完成則提升

      process_step = LlmAgent(name="ProcessingStep") # 可能更新 state['status'] 的代理

      poller = LoopAgent(
          name="StatusPoller",
          max_iterations=10,
          sub_agents=[process_step, CheckCondition(name="Checker")]
      )
      # 當 poller 執行時，它會重複執行 process_step 然後 Checker
      # 直到 Checker 提升 (state['status'] == 'completed') 或 10 次迭代結束。
      ```
    
=== "Java"

    ```java
    // 概念範例：帶條件的循環
    // 檢查狀態並可能提升的自訂代理
    public static class CheckConditionAgent extends BaseAgent {
      public CheckConditionAgent(String name, String description) {
        super(name, description, List.of(), null, null);
      }
  
      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext ctx) {
        String status = (String) ctx.session().state().getOrDefault("status", "pending");
        boolean isDone = "completed".equalsIgnoreCase(status);

        // 如果符合條件，則發出一個表示要提升 (退出循環) 的事件。
        // 如果未完成，提升旗標將為 false 或不存在，循環將繼續。
        Event checkEvent = Event.builder()
                .author(name())
                .id(Event.generateEventId()) // 為事件提供唯一 ID 很重要
                .actions(EventActions.builder().escalate(isDone).build()) // 如果完成則提升
                .build();
        return Flowable.just(checkEvent);
      }
    }
  
    // 可能更新 state.put("status") 的代理
    LlmAgent processingStepAgent = LlmAgent.builder().name("ProcessingStep").build();
    // 用於檢查條件的自訂代理實例
    CheckConditionAgent conditionCheckerAgent = new CheckConditionAgent(
        "ConditionChecker",
        "檢查狀態是否為 'completed'。"
    );
    LoopAgent poller = LoopAgent.builder().name("StatusPoller").maxIterations(10).subAgents(processingStepAgent, conditionCheckerAgent).build();
    // 當 poller 執行時，它會重複執行 processingStepAgent 然後 conditionCheckerAgent
    // 直到 Checker 提升 (state.get("status") == "completed") 或 10 次迭代結束。
    ```

### 1.3. 互動與通訊機制

系統中的代理通常需要交換資料或在彼此之間觸發動作。ADK 透過以下方式促進這一點：

#### a) 共用會話狀態 (`session.state`)

在同一個調用中操作 (並因此透過 `InvocationContext` 共用同一個 [`Session`](sessions-session.md) 物件) 的代理之間進行被動通訊的最基本方式。

* **機制：** 一個代理 (或其工具/回呼) 寫入一個值 (`context.state['data_key'] = processed_data`)，後續的代理讀取它 (`data = context.state.get('data_key')`)。狀態變更是透過 [`CallbackContext`](callbacks.md) 追蹤的。
* **便利性：** [`LlmAgent`](agents-llm-agents.md) 上的 `output_key` 屬性會自動將代理的最終回應文字 (或結構化輸出) 儲存到指定的狀態鍵。
* **性質：** 非同步、被動通訊。非常適合由 `SequentialAgent` 協調的管線或在 `LoopAgent` 迭代之間傳遞資料。
* **另請參閱：** [狀態管理](sessions-state.md)

=== "Python"

    ```python
    # 概念範例：使用 output_key 和讀取狀態
    from google.adk.agents import LlmAgent, SequentialAgent
    
    agent_A = LlmAgent(name="AgentA", instruction="尋找法國的首都。", output_key="capital_city")
    agent_B = LlmAgent(name="AgentB", instruction="告訴我關於儲存在 {capital_city} 中的城市的資訊。")
    
    pipeline = SequentialAgent(name="CityInfo", sub_agents=[agent_A, agent_B])
    # AgentA 執行，將「巴黎」儲存到 state['capital_city']。
    # AgentB 執行，其指令處理器讀取 state['capital_city'] 以取得「巴黎」。
    ```

=== "Java"

    ```java
    // 概念範例：使用 outputKey 和讀取狀態
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;
    
    LlmAgent agentA = LlmAgent.builder()
        .name("AgentA")
        .instruction("尋找法國的首都。")
        .outputKey("capital_city")
        .build();
    
    LlmAgent agentB = LlmAgent.builder()
        .name("AgentB")
        .instruction("告訴我關於儲存在 {capital_city} 中的城市的資訊。")
        .outputKey("capital_city")
        .build();
    
    SequentialAgent pipeline = SequentialAgent.builder().name("CityInfo").subAgents(agentA, agentB).build();
    // AgentA 執行，將「巴黎」儲存到 state('capital_city')。
    // AgentB 執行，其指令處理器讀取 state.get("capital_city") 以取得「巴黎」。
    ```

#### b) LLM 驅動的委派 (代理轉移)

利用 [`LlmAgent`](agents-llm-agents.md) 的理解能力，動態地將任務路由到層級結構中的其他合適代理。

* **機制：** 代理的 LLM 產生一個特定的函式呼叫：`transfer_to_agent(agent_name='target_agent_name')`。
* **處理：** 當存在子代理或未禁止轉移時，預設使用的 `AutoFlow` 會攔截此呼叫。它使用 `root_agent.find_agent()` 識別目標代理，並更新 `InvocationContext` 以切換執行焦點。
* **要求：** 呼叫的 `LlmAgent` 需要關於何時轉移的明確 `instructions`，潛在的目標代理需要有不同的 `description`s，以便 LLM 做出明智的決策。轉移範圍 (父級、子代理、同級) 可以在 `LlmAgent` 上設定。
* **性質：** 基於 LLM 解釋的動態、靈活路由。

=== "Python"

    ```python
    # 概念設定：LLM 轉移
    from google.adk.agents import LlmAgent
    
    booking_agent = LlmAgent(name="Booker", description="處理航班和飯店預訂。")
    info_agent = LlmAgent(name="Info", description="提供一般資訊並回答問題。")
    
    coordinator = LlmAgent(
        name="Coordinator",
        model="gemini-2.0-flash",
        instruction="你是一個助理。將預訂任務委派給 Booker，將資訊請求委派給 Info。",
        description="主要協調器。",
        # AutoFlow 在此通常是隱式使用的
        sub_agents=[booking_agent, info_agent]
    )
    # 如果協調器收到「預訂航班」，其 LLM 應該產生：
    # FunctionCall(name='transfer_to_agent', args={'agent_name': 'Booker'})
    # ADK 框架然後將執行路由到 booking_agent。
    ```

=== "Java"

    ```java
    // 概念設定：LLM 轉移
    import com.google.adk.agents.LlmAgent;
    
    LlmAgent bookingAgent = LlmAgent.builder()
        .name("Booker")
        .description("處理航班和飯店預訂。")
        .build();
    
    LlmAgent infoAgent = LlmAgent.builder()
        .name("Info")
        .description("提供一般資訊並回答問題。")
        .build();
    
    // 定義協調器代理
    LlmAgent coordinator = LlmAgent.builder()
        .name("Coordinator")
        .model("gemini-2.0-flash") // 或您想要的模型
        .instruction("你是一個助理。將預訂任務委派給 Booker，將資訊請求委派給 Info。")
        .description("主要協調器。")
        // AutoFlow 將預設使用 (隱式)，因為存在 subAgents
        // 且未禁止轉移。
        .subAgents(bookingAgent, infoAgent)
        .build();

    // 如果協調器收到「預訂航班」，其 LLM 應該產生：
    // FunctionCall.builder.name("transferToAgent").args(ImmutableMap.of("agent_name", "Booker")).build()
    // ADK 框架然後將執行路由到 bookingAgent。
    ```

#### c) 明確調用 (`AgentTool`)

允許 [`LlmAgent`](agents-llm-agents.md) 將另一個 `BaseAgent` 實例視為可呼叫的函式或[工具](tools.md)。

* **機制：** 將目標代理實例包裝在 `AgentTool` 中，並將其包含在父 `LlmAgent` 的 `tools` 列表中。`AgentTool` 會為 LLM 產生一個對應的函式宣告。
* **處理：** 當父 LLM 產生一個以 `AgentTool` 為目標的函式呼叫時，框架會執行 `AgentTool.run_async`。此方法會執行目標代理，擷取其最終回應，將任何狀態/產物變更轉發回父級的上下文，並將回應作為工具的結果傳回。
* **性質：** 同步 (在父級的流程中)、明確、受控的調用，就像任何其他工具一樣。
* **(注意：** `AgentTool` 需要明確匯入和使用)。

=== "Python"

    ```python
    # 概念設定：代理即工具
    from google.adk.agents import LlmAgent, BaseAgent
    from google.adk.tools import agent_tool
    from pydantic import BaseModel
    
    # 定義一個目標代理 (可以是 LlmAgent 或自訂 BaseAgent)
    class ImageGeneratorAgent(BaseAgent): # 範例自訂代理
        name: str = "ImageGen"
        description: str = "根據提示產生影像。"
        # ... 內部邏輯 ...
        async def _run_async_impl(self, ctx): # 簡化的執行邏輯
            prompt = ctx.session.state.get("image_prompt", "default prompt")
            # ... 產生影像位元組 ...
            image_bytes = b"..."
            yield Event(author=self.name, content=types.Content(parts=[types.Part.from_bytes(image_bytes, "image/png")]))
    
    image_agent = ImageGeneratorAgent()
    image_tool = agent_tool.AgentTool(agent=image_agent) # 包裝代理
    
    # 父代理使用 AgentTool
    artist_agent = LlmAgent(
        name="Artist",
        model="gemini-2.0-flash",
        instruction="建立一個提示並使用 ImageGen 工具產生影像。",
        tools=[image_tool] # 包含 AgentTool
    )
    # Artist LLM 產生一個提示，然後呼叫：
    # FunctionCall(name='ImageGen', args={'image_prompt': '一隻戴著帽子的貓'})
    # 框架呼叫 image_tool.run_async(...)，它會執行 ImageGeneratorAgent。
    # 產生的影像部分作為工具結果傳回給 Artist 代理。
    ```

=== "Java"

    ```java
    // 概念設定：代理即工具
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;

    // 範例自訂代理 (可以是 LlmAgent 或自訂 BaseAgent)
    public class ImageGeneratorAgent extends BaseAgent  {
    
      public ImageGeneratorAgent(String name, String description) {
        super(name, description, List.of(), null, null);
      }
    
      // ... 內部邏輯 ...
      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) { // 簡化的執行邏輯
        invocationContext.session().state().get("image_prompt");
        // 產生影像位元組
        // ...
    
        Event responseEvent = Event.builder()
            .author(this.name())
            .content(Content.fromParts(Part.fromText("\b...")))
            .build();
    
        return Flowable.just(responseEvent);
      }
    
      @Override
      protected Flowable<Event> runLiveImpl(InvocationContext invocationContext) {
        return null;
      }
    }

    // 使用 AgentTool 包裝代理
    ImageGeneratorAgent imageAgent = new ImageGeneratorAgent("image_agent", "產生影像");
    AgentTool imageTool = AgentTool.create(imageAgent);
    
    // 父代理使用 AgentTool
    LlmAgent artistAgent = LlmAgent.builder()
            .name("Artist")
            .model("gemini-2.0-flash")
            .instruction(
                    "你是一位藝術家。為影像建立一個詳細的提示，然後 " +
                            "使用 'ImageGen' 工具產生影像。 " +
                            "'ImageGen' 工具需要一個名為 'request' 的單一字串引數 " +
                            "包含影像提示。此工具將在其 " +
                            "'result' 欄位中傳回一個 JSON 字串，其中包含 'image_base64'、'mime_type' 和 'status'。"
            )
            .description("一個可以使用生成工具建立影像的代理。")
            .tools(imageTool) // 包含 AgentTool
            .build();
    
    // Artist LLM 產生一個提示，然後呼叫：
    // FunctionCall(name='ImageGen', args={'imagePrompt': '一隻戴著帽子的貓'})
    // 框架呼叫 imageTool.runAsync(...)，它會執行 ImageGeneratorAgent。
    // 產生的影像部分作為工具結果傳回給 Artist 代理。
    ```

這些原語提供了設計從緊密耦合的循序工作流程到動態、LLM 驅動的委派網路的多代理互動的靈活性。

## 2. 使用 ADK 原語的常見多代理模式

透過結合 ADK 的組合原語，您可以實作各種已建立的多代理協作模式。

### 協調器/分派器模式

* **結構：** 一個中央的 [`LlmAgent`](agents-llm-agents.md) (協調器) 管理多個專門的 `sub_agents`。
* **目標：** 將傳入的請求路由到適當的專家代理。
* **使用的 ADK 原語：**
    * **層級：** 協調器在其 `sub_agents` 中列出了專家。
    * **互動：** 主要使用**LLM 驅動的委派** (需要在子代理上有明確的 `description`s 和在協調器上有適當的 `instruction`) 或**明確調用 (`AgentTool`)** (協調器在其 `tools` 中包含 `AgentTool` 包裝的專家)。

=== "Python"

    ```python
    # 概念程式碼：使用 LLM 轉移的協調器
    from google.adk.agents import LlmAgent
    
    billing_agent = LlmAgent(name="Billing", description="處理帳務查詢。")
    support_agent = LlmAgent(name="Support", description="處理技術支援請求。")
    
    coordinator = LlmAgent(
        name="HelpDeskCoordinator",
        model="gemini-2.0-flash",
        instruction="路由使用者請求：對付款問題使用 Billing 代理，對技術問題使用 Support 代理。",
        description="主要服務台路由器。",
        # allow_transfer=True 在 AutoFlow 中通常與 sub_agents 隱含
        sub_agents=[billing_agent, support_agent]
    )
    # 使用者詢問「我的付款失敗」 -> 協調器的 LLM 應該呼叫 transfer_to_agent(agent_name='Billing')
    # 使用者詢問「我無法登入」 -> 協調器的 LLM 應該呼叫 transfer_to_agent(agent_name='Support')
    ```

=== "Java"

    ```java
    // 概念程式碼：使用 LLM 轉移的協調器
    import com.google.adk.agents.LlmAgent;

    LlmAgent billingAgent = LlmAgent.builder()
        .name("Billing")
        .description("處理帳務查詢和付款問題。")
        .build();

    LlmAgent supportAgent = LlmAgent.builder()
        .name("Support")
        .description("處理技術支援請求和登入問題。")
        .build();

    LlmAgent coordinator = LlmAgent.builder()
        .name("HelpDeskCoordinator")
        .model("gemini-2.0-flash")
        .instruction("路由使用者請求：對付款問題使用 Billing 代理，對技術問題使用 Support 代理。")
        .description("主要服務台路由器。")
        .subAgents(billingAgent, supportAgent)
        // 代理轉移在 Autoflow 中與子代理是隱含的，除非指定
        // 使用 .disallowTransferToParent 或 disallowTransferToPeers
        .build();

    // 使用者詢問「我的付款失敗」 -> 協調器的 LLM 應該呼叫
    // transferToAgent(agentName='Billing')
    // 使用者詢問「我無法登入」 -> 協調器的 LLM 應該呼叫
    // transferToAgent(agentName='Support')
    ```

### 循序管線模式

* **結構：** 一個 [`SequentialAgent`](agents-workflow-agents-sequential-agents.md) 包含按固定順序執行的 `sub_agents`。
* **目標：** 實作一個多步驟的流程，其中一個步驟的輸出饋送到下一個步驟。
* **使用的 ADK 原語：**
    * **工作流程：** `SequentialAgent` 定義順序。
    * **通訊：** 主要使用**共用會話狀態**。較早的代理寫入結果 (通常透過 `output_key`)，較晚的代理從 `context.state` 讀取這些結果。

=== "Python"

    ```python
    # 概念程式碼：循序資料管線
    from google.adk.agents import SequentialAgent, LlmAgent
    
    validator = LlmAgent(name="ValidateInput", instruction="驗證輸入。", output_key="validation_status")
    processor = LlmAgent(name="ProcessData", instruction="如果 {validation_status} 為 'valid'，則處理資料。", output_key="result")
    reporter = LlmAgent(name="ReportResult", instruction="報告來自 {result} 的結果。")
    
    data_pipeline = SequentialAgent(
        name="DataPipeline",
        sub_agents=[validator, processor, reporter]
    )
    # validator 執行 -> 儲存到 state['validation_status']
    # processor 執行 -> 讀取 state['validation_status']，儲存到 state['result']
    # reporter 執行 -> 讀取 state['result']
    ```

=== "Java"

    ```java
    // 概念程式碼：循序資料管線
    import com.google.adk.agents.SequentialAgent;
    
    LlmAgent validator = LlmAgent.builder()
        .name("ValidateInput")
        .instruction("驗證輸入")
        .outputKey("validation_status") // 將其主要文字輸出儲存到 session.state["validation_status"]
        .build();
    
    LlmAgent processor = LlmAgent.builder()
        .name("ProcessData")
        .instruction("如果 {validation_status} 為 'valid'，則處理資料")
        .outputKey("result") // 將其主要文字輸出儲存到 session.state["result"]
        .build();
    
    LlmAgent reporter = LlmAgent.builder()
        .name("ReportResult")
        .instruction("報告來自 {result} 的結果")
        .build();
    
    SequentialAgent dataPipeline = SequentialAgent.builder()
        .name("DataPipeline")
        .subAgents(validator, processor, reporter)
        .build();
    
    // validator 執行 -> 儲存到 state['validation_status']
    // processor 執行 -> 讀取 state['validation_status']，儲存到 state['result']
    // reporter 執行 -> 讀取 state['result']
    ```

### 平行扇出/收集模式

* **結構：** 一個 [`ParallelAgent`](agents-workflow-agents-parallel-agents.md) 同時執行多個 `sub_agents`，通常後面跟著一個聚合結果的後續代理 (在 `SequentialAgent` 中)。
* **目標：** 同時執行獨立的任務以減少延遲，然後組合它們的輸出。
* **使用的 ADK 原語：**
    * **工作流程：** `ParallelAgent` 用於並行執行 (扇出)。通常巢狀在 `SequentialAgent` 中以處理後續的聚合步驟 (收集)。
    * **通訊：** 子代理將結果寫入**共用會話狀態**中的不同鍵。後續的「收集」代理讀取多個狀態鍵。

=== "Python"

    ```python
    # 概念程式碼：平行資訊收集
    from google.adk.agents import SequentialAgent, ParallelAgent, LlmAgent
    
    fetch_api1 = LlmAgent(name="API1Fetcher", instruction="從 API 1 擷取資料。", output_key="api1_data")
    fetch_api2 = LlmAgent(name="API2Fetcher", instruction="從 API 2 擷取資料。", output_key="api2_data")
    
    gather_concurrently = ParallelAgent(
        name="ConcurrentFetch",
        sub_agents=[fetch_api1, fetch_api2]
    )
    
    synthesizer = LlmAgent(
        name="Synthesizer",
        instruction="組合來自 {api1_data} 和 {api2_data} 的結果。"
    )
    
    overall_workflow = SequentialAgent(
        name="FetchAndSynthesize",
        sub_agents=[gather_concurrently, synthesizer] # 執行平行擷取，然後合成
    )
    # fetch_api1 和 fetch_api2 同時執行，並儲存到狀態。
    # synthesizer 之後執行，讀取 state['api1_data'] 和 state['api2_data']。
    ```
=== "Java"

    ```java
    // 概念程式碼：平行資訊收集
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.ParallelAgent;
    import com.google.adk.agents.SequentialAgent;

    LlmAgent fetchApi1 = LlmAgent.builder()
        .name("API1Fetcher")
        .instruction("從 API 1 擷取資料。")
        .outputKey("api1_data")
        .build();

    LlmAgent fetchApi2 = LlmAgent.builder()
        .name("API2Fetcher")
        .instruction("從 API 2 擷取資料。")
        .outputKey("api2_data")
        .build();

    ParallelAgent gatherConcurrently = ParallelAgent.builder()
        .name("ConcurrentFetcher")
        .subAgents(fetchApi2, fetchApi1)
        .build();

    LlmAgent synthesizer = LlmAgent.builder()
        .name("Synthesizer")
        .instruction("組合來自 {api1_data} 和 {api2_data} 的結果。")
        .build();

    SequentialAgent overallWorfklow = SequentialAgent.builder()
        .name("FetchAndSynthesize") // 執行平行擷取，然後合成
        .subAgents(gatherConcurrently, synthesizer)
        .build();

    // fetch_api1 和 fetch_api2 同時執行，並儲存到狀態。
    // synthesizer 之後執行，讀取 state['api1_data'] 和 state['api2_data']。
    ```


### 層級任務分解

* **結構：** 一個多層級的代理樹，其中較高層級的代理分解複雜的目標並將子任務委派給較低層級的代理。
* **目標：** 透過遞迴地將複雜問題分解為更簡單、可執行的步驟來解決它們。
* **使用的 ADK 原語：**
    * **層級：** 多層級的 `parent_agent`/`sub_agents` 結構。
    * **互動：** 主要由父代理使用**LLM 驅動的委派**或**明確調用 (`AgentTool`)** 將任務指派給子代理。結果會透過階層結構向上傳回 (透過工具回應或狀態)。

=== "Python"

    ```python
    # 概念程式碼：層級研究任務
    from google.adk.agents import LlmAgent
    from google.adk.tools import agent_tool
    
    # 低階類似工具的代理
    web_searcher = LlmAgent(name="WebSearch", description="執行網路搜尋以尋找事實。")
    summarizer = LlmAgent(name="Summarizer", description="總結文字。")
    
    # 結合工具的中階代理
    research_assistant = LlmAgent(
        name="ResearchAssistant",
        model="gemini-2.0-flash",
        description="尋找並總結關於一個主題的資訊。",
        tools=[agent_tool.AgentTool(agent=web_searcher), agent_tool.AgentTool(agent=summarizer)]
    )
    
    # 委派研究的高階代理
    report_writer = LlmAgent(
        name="ReportWriter",
        model="gemini-2.0-flash",
        instruction="撰寫關於主題 X 的報告。使用 ResearchAssistant 收集資訊。",
        tools=[agent_tool.AgentTool(agent=research_assistant)]
        # 或者，如果 research_assistant 是一個子代理，可以使用 LLM 轉移
    )
    # 使用者與 ReportWriter 互動。
    # ReportWriter 呼叫 ResearchAssistant 工具。
    # ResearchAssistant 呼叫 WebSearch 和 Summarizer 工具。
    # 結果向上流動。
    ```

=== "Java"

    ```java
    // 概念程式碼：層級研究任務
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;
    
    // 低階類似工具的代理
    LlmAgent webSearcher = LlmAgent.builder()
        .name("WebSearch")
        .description("執行網路搜尋以尋找事實。")
        .build();
    
    LlmAgent summarizer = LlmAgent.builder()
        .name("Summarizer")
        .description("總結文字。")
        .build();
    
    // 結合工具的中階代理
    LlmAgent researchAssistant = LlmAgent.builder()
        .name("ResearchAssistant")
        .model("gemini-2.0-flash")
        .description("尋找並總結關於一個主題的資訊。")
        .tools(AgentTool.create(webSearcher), AgentTool.create(summarizer))
        .build();
    
    // 委派研究的高階代理
    LlmAgent reportWriter = LlmAgent.builder()
        .name("ReportWriter")
        .model("gemini-2.0-flash")
        .instruction("撰寫關於主題 X 的報告。使用 ResearchAssistant 收集資訊。")
        .tools(AgentTool.create(researchAssistant))
        // 或者，如果 research_assistant 是一個子代理，可以使用 LLM 轉移
        .build();
    
    // 使用者與 ReportWriter 互動。
    // ReportWriter 呼叫 ResearchAssistant 工具。
    // ResearchAssistant 呼叫 WebSearch 和 Summarizer 工具。
    // 結果向上流動。
    ```

### 審查/評論模式 (產生器-評論家)

* **結構：** 通常在 [`SequentialAgent`](agents-workflow-agents-sequential-agents.md) 中包含兩個代理：一個產生器和一個評論家/審查員。
* **目標：** 透過讓專門的代理審查產生的輸出來提高其品質或有效性。
* **使用的 ADK 原語：**
    * **工作流程：** `SequentialAgent` 確保在審查之前進行生成。
    * **通訊：** **共用會話狀態** (產生器使用 `output_key` 儲存輸出；審查員讀取該狀態鍵)。審查員可能會將其回饋儲存到另一個狀態鍵以供後續步驟使用。

=== "Python"

    ```python
    # 概念程式碼：產生器-評論家
    from google.adk.agents import SequentialAgent, LlmAgent
    
    generator = LlmAgent(
        name="DraftWriter",
        instruction="撰寫一段關於主題 X 的短文。",
        output_key="draft_text"
    )
    
    reviewer = LlmAgent(
        name="FactChecker",
        instruction="審查 {draft_text} 中的文字以確保事實準確性。輸出 'valid' 或 'invalid' 並附上原因。",
        output_key="review_status"
    )
    
    # 可選：根據 review_status 採取進一步步驟
    
    review_pipeline = SequentialAgent(
        name="WriteAndReview",
        sub_agents=[generator, reviewer]
    )
    # generator 執行 -> 將草稿儲存到 state['draft_text']
    # reviewer 執行 -> 讀取 state['draft_text']，將狀態儲存到 state['review_status']
    ```

=== "Java"

    ```java
    // 概念程式碼：產生器-評論家
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;
    
    LlmAgent generator = LlmAgent.builder()
        .name("DraftWriter")
        .instruction("撰寫一段關於主題 X 的短文。")
        .outputKey("draft_text")
        .build();
    
    LlmAgent reviewer = LlmAgent.builder()
        .name("FactChecker")
        .instruction("審查 {draft_text} 中的文字以確保事實準確性。輸出 'valid' 或 'invalid' 並附上原因。")
        .outputKey("review_status")
        .build();
    
    // 可選：根據 review_status 採取進一步步驟
    
    SequentialAgent reviewPipeline = SequentialAgent.builder()
        .name("WriteAndReview")
        .subAgents(generator, reviewer)
        .build();
    
    // generator 執行 -> 將草稿儲存到 state['draft_text']
    // reviewer 執行 -> 讀取 state['draft_text']，將狀態儲存到 state['review_status']
    ```

### 迭代改進模式

* **結構：** 使用一個 [`LoopAgent`](agents-workflow-agents-loop-agents.md)，其中包含一個或多個在多次迭代中處理任務的代理。
* **目標：** 逐步改進儲存在會話狀態中的結果 (例如，程式碼、文字、計劃)，直到達到品質閾值或達到最大迭代次數。
* **使用的 ADK 原語：**
    * **工作流程：** `LoopAgent` 管理重複。
    * **通訊：** **共用會話狀態**對於代理讀取上一次迭代的輸出並儲存改進後的版本至關重要。
    * **終止：** 循環通常根據 `max_iterations` 或一個專門的檢查代理在結果滿意時在 `Event Actions` 中設定 `escalate=True` 來結束。

=== "Python"

    ```python
    # 概念程式碼：迭代式程式碼改進
    from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
    from google.adk.events import Event, EventActions
    from google.adk.agents.invocation_context import InvocationContext
    from typing import AsyncGenerator
    
    # 根據 state['current_code'] 和 state['requirements'] 產生/改進程式碼的代理
    code_refiner = LlmAgent(
        name="CodeRefiner",
        instruction="讀取 state['current_code'] (如果存在) 和 state['requirements']。產生/改進 Python 程式碼以滿足需求。儲存到 state['current_code']。",
        output_key="current_code" # 覆寫狀態中的先前程式碼
    )
    
    # 檢查程式碼是否符合品質標準的代理
    quality_checker = LlmAgent(
        name="QualityChecker",
        instruction="根據 state['requirements'] 評估 state['current_code'] 中的程式碼。輸出 'pass' 或 'fail'。",
        output_key="quality_status"
    )
    
    # 檢查狀態並在 'pass' 時提升的自訂代理
    class CheckStatusAndEscalate(BaseAgent):
        async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
            status = ctx.session.state.get("quality_status", "fail")
            should_stop = (status == "pass")
            yield Event(author=self.name, actions=EventActions(escalate=should_stop))
    
    refinement_loop = LoopAgent(
        name="CodeRefinementLoop",
        max_iterations=5,
        sub_agents=[code_refiner, quality_checker, CheckStatusAndEscalate(name="StopChecker")]
    )
    # 循環執行：Refiner -> Checker -> StopChecker
    # 每次迭代都會更新 State['current_code']。
    # 如果 QualityChecker 輸出 'pass' (導致 StopChecker 提升) 或 5 次迭代後，循環停止。
    ```

=== "Java"

    ```java
    // 概念程式碼：迭代式程式碼改進
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.LoopAgent;
    import com.google.adk.events.Event;
    import com.google.adk.events.EventActions;
    import com.google.adk.agents.InvocationContext;
    import io.reactivex.rxjava3.core.Flowable;
    import java.util.List;
    
    // 根據 state['current_code'] 和 state['requirements'] 產生/改進程式碼的代理
    LlmAgent codeRefiner = LlmAgent.builder()
        .name("CodeRefiner")
        .instruction("讀取 state['current_code'] (如果存在) 和 state['requirements']。產生/改進 Java 程式碼以滿足需求。儲存到 state['current_code']。")
        .outputKey("current_code") // 覆寫狀態中的先前程式碼
        .build();
    
    // 檢查程式碼是否符合品質標準的代理
    LlmAgent qualityChecker = LlmAgent.builder()
        .name("QualityChecker")
        .instruction("根據 state['requirements'] 評估 state['current_code'] 中的程式碼。輸出 'pass' 或 'fail'。")
        .outputKey("quality_status")
        .build();
    
    BaseAgent checkStatusAndEscalate = new BaseAgent(
        "StopChecker","檢查 quality_status 並在 'pass' 時提升。", List.of(), null, null) {
    
      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
        String status = (String) invocationContext.session().state().getOrDefault("quality_status", "fail");
        boolean shouldStop = "pass".equals(status);
    
        EventActions actions = EventActions.builder().escalate(shouldStop).build();
        Event event = Event.builder()
            .author(this.name())
            .actions(actions)
            .build();
        return Flowable.just(event);
      }
    };
    
    LoopAgent refinementLoop = LoopAgent.builder()
        .name("CodeRefinementLoop")
        .maxIterations(5)
        .subAgents(codeRefiner, qualityChecker, checkStatusAndEscalate)
        .build();
    
    // 循環執行：Refiner -> Checker -> StopChecker
    // 每次迭代都會更新 State['current_code']。
    // 如果 QualityChecker 輸出 'pass' (導致 StopChecker 提升) 或 5 次
    // 迭代後，循環停止。
    ```

### 人在迴路模式

* **結構：** 在代理工作流程中整合人工干預點。
* **目標：** 允許人工監督、批准、更正或執行 AI 無法執行的任務。
* **使用的 ADK 原語 (概念性)：**
    * **互動：** 可以使用一個自訂的**工具**來實作，該工具會暫停執行並向外部系統 (例如 UI、票務系統) 傳送請求，等待人工輸入。然後，該工具會將人工的回應傳回給代理。
    * **工作流程：** 可以使用**LLM 驅動的委派** (`transfer_to_agent`)，以一個觸發外部工作流程的概念性「人類代理」為目標，或在 `LlmAgent` 中使用自訂工具。
    * **狀態/回呼：** 狀態可以保存人類的任務詳細資訊；回呼可以管理互動流程。
    * **注意：** ADK 沒有內建的「人類代理」類型，因此這需要自訂整合。

=== "Python"

    ```python
    # 概念程式碼：使用工具進行人工批准
    from google.adk.agents import LlmAgent, SequentialAgent
    from google.adk.tools import FunctionTool
    
    # --- 假設存在 external_approval_tool ---
    # 此工具將：
    # 1. 取得詳細資訊 (例如 request_id、金額、原因)。
    # 2. 將這些詳細資訊傳送到人工審查系統 (例如透過 API)。
    # 3. 輪詢或等待人工回應 (批准/拒絕)。
    # 4. 傳回人工的決定。
    # async def external_approval_tool(amount: float, reason: str) -> str: ...
    approval_tool = FunctionTool(func=external_approval_tool)
    
    # 準備請求的代理
    prepare_request = LlmAgent(
        name="PrepareApproval",
        instruction="根據使用者輸入準備批准請求詳細資訊。將金額和原因儲存在狀態中。",
        # ... 可能會設定 state['approval_amount'] 和 state['approval_reason'] ...
    )
    
    # 呼叫人工批准工具的代理
    request_approval = LlmAgent(
        name="RequestHumanApproval",
        instruction="使用來自 state['approval_amount'] 的金額和來自 state['approval_reason'] 的原因來使用 external_approval_tool。",
        tools=[approval_tool],
        output_key="human_decision"
    )
    
    # 根據人工決定繼續執行的代理
    process_decision = LlmAgent(
        name="ProcessDecision",
        instruction="檢查 {human_decision}。如果 'approved'，則繼續。如果 'rejected'，則通知使用者。"
    )
    
    approval_workflow = SequentialAgent(
        name="HumanApprovalWorkflow",
        sub_agents=[prepare_request, request_approval, process_decision]
    )
    ```

=== "Java"

    ```java
    // 概念程式碼：使用工具進行人工批准
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.tools.FunctionTool;
    
    // --- 假設存在 external_approval_tool ---
    // 此工具將：
    // 1. 取得詳細資訊 (例如 request_id、金額、原因)。
    // 2. 將這些詳細資訊傳送到人工審查系統 (例如透過 API)。
    // 3. 輪詢或等待人工回應 (批准/拒絕)。
    // 4. 傳回人工的決定。
    // public boolean externalApprovalTool(float amount, String reason) { ... }
    FunctionTool approvalTool = FunctionTool.create(externalApprovalTool);
    
    // 準備請求的代理
    LlmAgent prepareRequest = LlmAgent.builder()
        .name("PrepareApproval")
        .instruction("根據使用者輸入準備批准請求詳細資訊。將金額和原因儲存在狀態中。")
        // ... 可能會設定 state['approval_amount'] 和 state['approval_reason'] ...
        .build();
    
    // 呼叫人工批准工具的代理
    LlmAgent requestApproval = LlmAgent.builder()
        .name("RequestHumanApproval")
        .instruction("使用來自 state['approval_amount'] 的金額和來自 state['approval_reason'] 的原因來使用 external_approval_tool。")
        .tools(approvalTool)
        .outputKey("human_decision")
        .build();
    
    // 根據人工決定繼續執行的代理
    LlmAgent processDecision = LlmAgent.builder()
        .name("ProcessDecision")
        .instruction("檢查 {human_decision}。如果 'approved'，則繼續。如果 'rejected'，則通知使用者。")
        .build();
    
    SequentialAgent approvalWorkflow = SequentialAgent.builder()
        .name("HumanApprovalWorkflow")
        .subAgents(prepareRequest, requestApproval, processDecision)
        .build();
    ```

這些模式為建構您的多代理系統提供了起點。您可以根據需要混合和匹配它們，以建立最適合您特定應用程式的架構。
