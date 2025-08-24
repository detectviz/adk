# LLM 代理

`LlmAgent` (通常簡稱為 `Agent`) 是 ADK 中的一個核心元件，
充當您應用程式的「思考」部分。它利用
大型語言模型 (LLM) 的強大功能進行推理、理解自然語言、做出
決策、產生回應以及與工具互動。

與遵循預先定義執行路徑的確定性[工作流程代理](agents-workflow-agents.md)不同，`LlmAgent` 的行為是非確定性的。它使用
LLM 來解釋指令和上下文，動態決定如何
進行、使用哪些工具 (如果有的話)，或者是否將控制權轉移給另一個
代理。

建立一個有效的 `LlmAgent` 需要定義其身份，透過指令明確指導
其行為，並為其配備必要的工具和
功能。

## 定義代理的身份和目的

首先，您需要確定代理「是」什麼以及它的「用途」是什麼。

* **`name` (必要)：** 每個代理都需要一個唯一的字串識別碼。此
  `name` 對於內部操作至關重要，尤其是在多代理系統中，
  代理需要互相參照或委派任務。選擇一個
  能反映代理功能的描述性名稱 (例如，
  `customer_support_router`、`billing_inquiry_agent`)。避免使用
  `user` 等保留名稱。

* **`description` (可選，建議用於多代理)：** 提供代理
  功能的簡潔摘要。此描述主要由
  *其他* LLM 代理用來決定是否應將任務路由到此代理。
  使其足夠具體以與同級代理區分開來 (例如，「處理
  有關目前帳單的查詢」，而不僅僅是「帳務代理」)。

* **`model` (必要)：** 指定將為此
  代理的推理提供支援的底層 LLM。這是一個字串識別碼，例如 `"gemini-2.0-flash"`。
  模型的選擇會影響代理的功能、成本和效能。請參閱
  [模型](agents-models.md) 頁面以了解可用的選項和考量因素。

=== "Python"

    ```python
    # 範例：定義基本身份
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="回答使用者關於給定國家首都的問題。"
        # 接下來將新增 instruction 和 tools
    )
    ```

=== "Java"

    ```java
    // 範例：定義基本身份
    LlmAgent capitalAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("capital_agent")
            .description("回答使用者關於給定國家首都的問題。")
            // 接下來將新增 instruction 和 tools
            .build();
    ```


## 指導代理：指令 (`instruction`)

`instruction` 參數可以說是塑造 `LlmAgent` 行為最關鍵的因素。它是一個字串 (或傳回字串的函式)，用於告知代理：

* 其核心任務或目標。
* 其個性或角色 (例如，「你是一個樂於助人的助理」，「你是一個機智的海盜」)。
* 其行為的限制 (例如，「只回答關於 X 的問題」，「絕不透露 Y」)。
* 如何以及何時使用其 `tools`。您應該解釋每個工具的用途以及應在何種情況下呼叫它，以補充工具本身的任何描述。
* 其輸出的期望格式 (例如，「以 JSON 格式回應」，「提供項目符號列表」)。

**有效指令的提示：**

* **清晰具體：** 避免模稜兩可。清楚地陳述期望的動作和結果。
* **使用 Markdown：** 使用標題、列表等提高複雜指令的可讀性。
* **提供範例 (Few-Shot)：** 對於複雜的任務或特定的輸出格式，請直接在指令中包含範例。
* **指導工具使用：** 不要只列出工具；解釋代理「何時」以及「為何」應該使用它們。

**狀態：**

* 指令是一個字串範本，您可以使用 `{var}` 語法將動態值插入指令中。
* `{var}` 用於插入名為 var 的狀態變數的值。
* `{artifact.var}` 用於插入名為 var 的產物的文字內容。
* 如果狀態變數或產物不存在，代理將引發錯誤。如果您想忽略錯誤，可以在變數名稱後面附加一個 `?`，如 `{var?}`。

=== "Python"

    ```python
    # 範例：新增指令
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="回答使用者關於給定國家首都的問題。",
        instruction="""您是一個提供國家首都資訊的代理。
    當使用者詢問一個國家的首都時：
    1. 從使用者的查詢中識別國家名稱。
    2. 使用 `get_capital_city` 工具尋找首都。
    3. 清楚地向使用者回應，說明首都城市。
    範例查詢：「{country}的首都是什麼？」
    範例回應：「法國的首都是巴黎。」
    """,
        # 接下來將新增 tools
    )
    ```

=== "Java"

    ```java
    // 範例：新增指令
    LlmAgent capitalAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("capital_agent")
            .description("回答使用者關於給定國家首都的問題。")
            .instruction(
                """
                您是一個提供國家首都資訊的代理。
                當使用者詢問一個國家的首都時：
                1. 從使用者的查詢中識別國家名稱。
                2. 使用 `get_capital_city` 工具尋找首都。
                3. 清楚地向使用者回應，說明首都城市。
                範例查詢：「{country}的首都是什麼？」
                範例回應：「法國的首都是巴黎。」
                """)
            // 接下來將新增 tools
            .build();
    ```

*(注意：對於適用於系統中*所有*代理的指令，請考慮在根代理上使用
`global_instruction`，詳情請參閱
[多代理](agents-multi-agents.md)部分。)*

## 為代理配備工具 (`tools`)

工具賦予您的 `LlmAgent` 超越 LLM 內建知識或
推理的能力。它們允許代理與外部世界互動、執行
計算、擷取即時資料或執行特定動作。

* **`tools` (可選)：** 提供代理可以使用的工具列表。列表中的每個項目可以是：
    * 一個原生函式或方法 (包裝為 `FunctionTool`)。Python ADK 會自動將原生函式包裝到 `FuntionTool` 中，而您必須使用 `FunctionTool.create(...)` 明確包裝您的 Java 方法
    * 一個繼承自 `BaseTool` 的類別的實例。
    * 另一個代理的實例 (`AgentTool`，啟用代理對代理的委派 - 請參閱[多代理](agents-multi-agents.md))。

LLM 使用函式/工具名稱、描述 (來自 docstrings 或
`description` 欄位) 和參數結構來決定根據對話和其指令呼叫哪個工具。

=== "Python"

    ```python
    # 定義一個工具函式
    def get_capital_city(country: str) -> str:
      """擷取給定國家的首都。"""
      # 用實際邏輯取代 (例如，API 呼叫、資料庫查詢)
      capitals = {"france": "巴黎", "japan": "東京", "canada": "渥太華"}
      return capitals.get(country.lower(), f"抱歉，我不知道 {country} 的首都。")
    
    # 將工具新增至代理
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="回答使用者關於給定國家首都的問題。",
        instruction="""您是一個提供國家首都資訊的代理... (先前的指令文字)""",
        tools=[get_capital_city] # 直接提供函式
    )
    ```

=== "Java"

    ```java
    
    // 定義一個工具函式
    // 擷取給定國家的首都。
    public static Map<String, Object> getCapitalCity(
            @Schema(name = "country", description = "要取得首都的國家")
            String country) {
      // 用實際邏輯取代 (例如，API 呼叫、資料庫查詢)
      Map<String, String> countryCapitals = new HashMap<>();
      countryCapitals.put("canada", "渥太華");
      countryCapitals.put("france", "巴黎");
      countryCapitals.put("japan", "東京");
    
      String result =
              countryCapitals.getOrDefault(
                      country.toLowerCase(), "抱歉，我找不到 " + country + " 的首都。");
      return Map.of("result", result); // 工具必須傳回一個 Map
    }
    
    // 將工具新增至代理
    FunctionTool capitalTool = FunctionTool.create(experiment.getClass(), "getCapitalCity");
    LlmAgent capitalAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("capital_agent")
            .description("回答使用者關於給定國家首都的問題。")
            .instruction("您是一個提供國家首都資訊的代理... (先前的指令文字)")
            .tools(capitalTool) // 提供包裝為 FunctionTool 的函式
            .build();
    ```

在[工具](tools.md)部分了解更多關於工具的資訊。

## 進階組態與控制

除了核心參數，`LlmAgent` 還提供了幾個用於更精細控制的選項：

### 微調 LLM 生成 (`generate_content_config`)

您可以使用 `generate_content_config` 調整底層 LLM 如何產生回應。

* **`generate_content_config` (可選)：** 傳遞一個 `google.genai.types.GenerateContentConfig` 的實例來控制參數，例如 `temperature` (隨機性)、`max_output_tokens` (回應長度)、`top_p`、`top_k` 和安全設定。

=== "Python"

    ```python
    from google.genai import types

    agent = LlmAgent(
        # ... 其他參數
        generate_content_config=types.GenerateContentConfig(
            temperature=0.2, # 更具確定性的輸出
            max_output_tokens=250
        )
    )
    ```

=== "Java"

    ```java
    import com.google.genai.types.GenerateContentConfig;

    LlmAgent agent =
        LlmAgent.builder()
            // ... 其他參數
            .generateContentConfig(GenerateContentConfig.builder()
                .temperature(0.2F) // 更具確定性的輸出
                .maxOutputTokens(250)
                .build())
            .build();
    ```

### 結構化資料 (`input_schema`, `output_schema`, `output_key`)

對於需要與 `LLM 代理` 進行結構化資料交換的場景，ADK 提供了使用結構定義來定義預期輸入和期望輸出格式的機制。

* **`input_schema` (可選)：** 定義表示預期輸入結構的結構。如果設定，傳遞給此代理的使用者訊息內容*必須*是符合此結構的 JSON 字串。您的指令應相應地指導使用者或前一個代理。

* **`output_schema` (可選)：** 定義表示期望輸出結構的結構。如果設定，代理的最終回應*必須*是符合此結構的 JSON 字串。
    * **限制：** 使用 `output_schema` 可在 LLM 中啟用受控生成，但**會停用代理使用工具或將控制權轉移給其他代理的能力**。您的指令必須直接指導 LLM 產生符合結構的 JSON。

* **`output_key` (可選)：** 提供一個字串鍵。如果設定，代理的*最終*回應的文字內容將自動儲存到會話的狀態字典中，並以此鍵為名。這對於在代理或工作流程中的步驟之間傳遞結果很有用。
    * 在 Python 中，可能如下所示：`session.state[output_key] = agent_response_text`
    * 在 Java 中：`session.state().put(outputKey, agentResponseText)`

=== "Python"

    輸入和輸出結構通常是一個 `Pydantic` BaseModel。

    ```python
    from pydantic import BaseModel, Field
    
    class CapitalOutput(BaseModel):
        capital: str = Field(description="國家的首都。")
    
    structured_capital_agent = LlmAgent(
        # ... name, model, description
        instruction="""您是一個首都資訊代理。給定一個国家，只用包含首都的 JSON 物件回應。格式：{"capital": "capital_name"}""",
        output_schema=CapitalOutput, # 強制 JSON 輸出
        output_key="found_capital"  # 將結果儲存在 state['found_capital'] 中
        # 此處無法有效使用 tools=[get_capital_city]
    )
    ```

=== "Java"

     輸入和輸出結構是一個 `google.genai.types.Schema` 物件。

    ```java
    private static final Schema CAPITAL_OUTPUT =
        Schema.builder()
            .type("OBJECT")
            .description("首都資訊的結構。")
            .properties(
                Map.of(
                    "capital",
                    Schema.builder()
                        .type("STRING")
                        .description("國家的首都。")
                        .build()))
            .build();
    
    LlmAgent structuredCapitalAgent =
        LlmAgent.builder()
            // ... name, model, description
            .instruction(
                    "您是一個首都資訊代理。給定一個国家，只用包含首都的 JSON 物件回應。格式：{\"capital\": \"capital_name\"}")
            .outputSchema(capitalOutput) // 強制 JSON 輸出
            .outputKey("found_capital") // 將結果儲存在 state.get("found_capital") 中
            // 此處無法有效使用 tools(getCapitalCity)
            .build();
    ```

### 管理上下文 (`include_contents`)

控制代理是否接收先前的對話歷史記錄。

* **`include_contents` (可選，預設：`'default'`)：** 決定是否將 `contents` (歷史記錄) 傳送給 LLM。
    * `'default'`: 代理接收相關的對話歷史記錄。
    * `'none'`: 代理不接收任何先前的 `contents`。它僅根據其目前的指令和在*目前*回合中提供的任何輸入進行操作 (對於無狀態任務或強制執行特定上下文很有用)。

=== "Python"

    ```python
    stateless_agent = LlmAgent(
        # ... 其他參數
        include_contents='none'
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent.IncludeContents;
    
    LlmAgent statelessAgent =
        LlmAgent.builder()
            // ... 其他參數
            .includeContents(IncludeContents.NONE)
            .build();
    ```

### 規劃器

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前適用於 Python。Java 支援計畫中/即將推出。" }

**`planner` (可選)：** 指派一個 `BasePlanner` 實例以在執行前啟用多步驟推理和規劃。有兩個主要規劃器：

* **`BuiltInPlanner`：** 利用模型的內建規劃功能 (例如，Gemini 的思考功能)。有關詳細資訊和範例，請參閱 [Gemini 思考](https://ai.google.dev/gemini-api/docs/thinking)。

    此處，`thinking_budget` 參數指導模型在產生回應時要使用的思考權杖數量。`include_thoughts` 參數控制模型是否應在其回應中包含其原始思考和內部推理過程。

    ```python
    from google.adk import Agent
    from google.adk.planners import BuiltInPlanner
    from google.genai import types

    my_agent = Agent(
        model="gemini-2.5-flash",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            )
        ),
        # ... 您的工具在此
    )
    ```
    
* **`PlanReActPlanner`：** 此規劃器指示模型在其輸出中遵循特定結構：首先建立一個計劃，然後執行動作 (如呼叫工具)，並為其步驟提供推理。*對於沒有內建「思考」功能的模型特別有用*。

    ```python
    from google.adk import Agent
    from google.adk.planners import PlanReActPlanner

    my_agent = Agent(
        model="gemini-2.0-flash",
        planner=PlanReActPlanner(),
        # ... 您的工具在此
    )
    ```

    代理的回應將遵循結構化格式：

    ```
    [user]: ai news
    [google_search_agent]: /*PLANNING*/
    1. 對「最新 AI 新聞」進行 Google 搜尋，以取得有關人工智慧的最新更新和頭條新聞。
    2. 綜合搜尋結果中的資訊，以提供近期 AI 新聞的摘要。

    /*ACTION*/
    /*REASONING*/
    搜尋結果提供了近期 AI 新聞的全面概覽，涵蓋了公司發展、研究突破和應用等各個方面。我有足夠的資訊來回答使用者的要求。

    /*FINAL_ANSWER*/
    以下是近期 AI 新聞的摘要：
    ....
    ```

### 程式碼執行

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前適用於 Python。Java 支援計畫中/即將推出。" }

* **`code_executor` (可選)：** 提供一個 `BaseCodeExecutor` 實例，以允許代理執行在 LLM 回應中找到的程式碼區塊。([請參閱工具/內建工具](tools-built-in-tools.md))。

## 總結：範例

??? "程式碼"
    這是完整的基礎 `capital_agent`：

    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/agents/llm-agent/capital_agent.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/LlmAgentExample.java:full_code"
        ```

_(此範例展示了核心概念。更複雜的代理可能會結合結構、上下文控制、規劃等。)_

## 相關概念 (延後主題)

雖然本頁涵蓋了 `LlmAgent` 的核心組態，但其他地方詳細介紹了幾個提供更進階控制的相關概念：

* **回呼：** 使用 `before_model_callback`、`after_model_callback` 等攔截執行點 (模型呼叫之前/之後、工具呼叫之前/之後)。請參閱[回呼](callbacks-types-of-callbacks.md)。
* **多代理控制：** 代理互動的進階策略，包括規劃 (`planner`)、控制代理轉移 (`disallow_transfer_to_parent`、`disallow_transfer_to_peers`) 和全系統指令 (`global_instruction`)。請參閱[多代理](agents-multi-agents.md)。
