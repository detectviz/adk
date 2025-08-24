# 在 ADK 中使用不同的模型

!!! Note
    Java ADK 目前支援 Gemini 和 Anthropic 模型。更多模型支援即將推出。

代理開發套件 (ADK) 的設計旨在提供靈活性，讓您能夠將各種大型語言模型 (LLM) 整合到您的代理中。雖然
[設定基礎模型](get-started-installation.md)指南中涵蓋了 Google Gemini 模型的設定，但本頁面詳細介紹了如何有效地利用 Gemini 並整合其他流行的模型，包括那些外部託管或在本機執行的模型。

ADK 主要使用兩種機制進行模型整合：

1. **直接字串/註冊表：** 對於與 Google Cloud 緊密整合的模型 (例如透過 Google AI Studio 或 Vertex AI 存取的 Gemini 模型) 或託管在 Vertex AI 端點上的模型。您通常直接將模型名稱或端點資源字串提供給 `LlmAgent`。ADK 的內部註冊表會將此字串解析為適當的後端用戶端，通常利用 `google-genai` 函式庫。
2. **包裝類別：** 為了更廣泛的相容性，特別是對於 Google 生態系統之外的模型或需要特定用戶端組態的模型 (例如透過 LiteLLM 存取的模型)。您實例化一個特定的包裝類別 (例如 `LiteLlm`)，並將此物件作為 `model` 參數傳遞給您的 `LlmAgent`。

以下各節將根據您的需求引導您使用這些方法。

## 使用 Google Gemini 模型

本節介紹如何透過 Google AI Studio (用於快速開發) 或 Google Cloud Vertex AI (用於企業應用程式) 對 Google 的 Gemini 模型進行身份驗證。這是將 Google 的旗艦模型用於 ADK 的最直接方法。

**整合方法：** 使用以下方法之一進行身份驗證後，您可以將模型的識別碼字串直接傳遞給
`LlmAgent` 的 `model` 參數。


!!!tip 

    `google-genai` 函式庫由 ADK 內部用於 Gemini 模型，可以透過 Google AI Studio 或 Vertex AI 進行連接。

    **語音/視訊串流的模型支援**

    為了在 ADK 中使用語音/視訊串流，您需要使用支援 Live API 的 Gemini
    模型。您可以在文件中找到支援 Gemini Live API 的 **模型 ID**：

    - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
    - [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

### Google AI Studio

這是最簡單的方法，建議用於快速入門。

*   **身份驗證方法：** API 金鑰
*   **設定：**
    1.  **取得 API 金鑰：** 從 [Google AI Studio](https://aistudio.google.com/apikey) 取得您的金鑰。
    2.  **設定環境變數：** 在您專案的根目錄中建立一個 `.env` 檔案 (Python) 或 `.properties` (Java)，並新增以下幾行。ADK 將自動載入此檔案。

        ```shell
        export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
        export GOOGLE_GENAI_USE_VERTEXAI=FALSE
        ```

        (或)
        
        在模型初始化期間透過 `Client` 傳遞這些變數 (請參閱下面的範例)。

* **模型：** 在
  [Google AI for Developers 網站](https://ai.google.dev/gemini-api/docs/models)上尋找所有可用的模型。

### Google Cloud Vertex AI

對於可擴展和以生產為導向的使用案例，Vertex AI 是建議的平台。Vertex AI 上的 Gemini 支援企業級功能、安全性和合規性控制。根據您的開發環境和使用案例，*請選擇以下其中一種方法進行身份驗證*。

**先決條件：** 已[啟用 Vertex AI](https://console.cloud.google.com/apis/enableflow;apiid=aiplatform.googleapis.com) 的 Google Cloud 專案。

### **方法 A：使用者憑證 (用於本機開發)**

1.  **安裝 gcloud CLI：** 遵循官方[安裝說明](https://cloud.google.com/sdk/docs/install)。
2.  **使用 ADC 登入：** 此指令會開啟一個瀏覽器，以驗證您的使用者帳戶以進行本機開發。
    ```bash
    gcloud auth application-default login
    ```
3.  **設定環境變數：**
    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # 例如 us-central1
    ```     
    
    明確告知函式庫使用 Vertex AI：

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

4. **模型：** 在
  [Vertex AI 文件](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)中尋找可用的模型 ID。

### **方法 B：Vertex AI Express 模式**
[Vertex AI Express 模式](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview) 提供簡化的、基於 API 金鑰的設定，可快速進行原型設計。

1.  **註冊 Express 模式**以取得您的 API 金鑰。
2.  **設定環境變數：**
    ```shell
    export GOOGLE_API_KEY="PASTE_YOUR_EXPRESS_MODE_API_KEY_HERE"
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### **方法 C：服務帳戶 (用於生產和自動化)**

對於已部署的應用程式，服務帳戶是標準方法。

1.  [**建立服務帳戶**](https://cloud.google.com/iam/docs/service-accounts-create#console) 並授予其 `Vertex AI User` 角色。
2.  **向您的應用程式提供憑證：**
    *   **在 Google Cloud 上：** 如果您在 Cloud Run、GKE、VM 或其他 Google Cloud 服務中執行代理，環境可以自動提供服務帳戶憑證。您不必建立金鑰檔案。
    *   **在其他地方：** 建立一個[服務帳戶金鑰檔案](https://cloud.google.com/iam/docs/keys-create-delete#console) 並使用環境變數指向它：
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
        ```
    除了金鑰檔案，您還可以使用 Workload Identity 對服務帳戶進行身份驗證。但這超出了本指南的範圍。

**範例：**

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    
    # --- 使用穩定的 Gemini Flash 模型的範例 ---
    agent_gemini_flash = LlmAgent(
        # 使用最新的穩定 Flash 模型識別碼
        model="gemini-2.0-flash",
        name="gemini_flash_agent",
        instruction="你是一個快速且樂於助人的 Gemini 助理。",
        # ... 其他代理參數
    )
    
    # --- 使用功能強大的 Gemini Pro 模型的範例 ---
    # 注意：請務必查看 Gemini 官方文件以取得最新的模型名稱，
    # 如有需要，也包括特定的預覽版本。預覽模型可能有
    # 不同的可用性或配額限制。
    agent_gemini_pro = LlmAgent(
        # 使用最新的正式版 Pro 模型識別碼
        model="gemini-2.5-pro-preview-03-25",
        name="gemini_pro_agent",
        instruction="你是一個功能強大且知識淵博的 Gemini 助理。",
        # ... 其他代理參數
    )
    ```

=== "Java"

    ```java
    // --- 範例 #1：使用帶有環境變數的穩定 Gemini Flash 模型 ---
    LlmAgent agentGeminiFlash =
        LlmAgent.builder()
            // 使用最新的穩定 Flash 模型識別碼
            .model("gemini-2.0-flash") // 設定環境變數以使用此模型
            .name("gemini_flash_agent")
            .instruction("你是一個快速且樂於助人的 Gemini 助理。")
            // ... 其他代理參數
            .build();

    // --- 範例 #2：在模型中使用 API 金鑰的功能強大的 Gemini Pro 模型 ---
    LlmAgent agentGeminiPro =
        LlmAgent.builder()
            // 使用最新的正式版 Pro 模型識別碼
            .model(new Gemini("gemini-2.5-pro-preview-03-25",
                Client.builder()
                    .vertexAI(false)
                    .apiKey("API_KEY") // 設定 API 金鑰 (或) 專案/位置
                    .build()))
            // 或者，您也可以直接傳遞 API_KEY
            // .model(new Gemini("gemini-2.5-pro-preview-03-25", "API_KEY"))
            .name("gemini_pro_agent")
            .instruction("你是一個功能強大且知識淵博的 Gemini 助理。")
            // ... 其他代理參數
            .build();

    // 注意：請務必查看 Gemini 官方文件以取得最新的模型名稱，
    // 如有需要，也包括特定的預覽版本。預覽模型可能有
    // 不同的可用性或配額限制。
    ```

!!!warning "保護您的憑證"
    服務帳戶憑證或 API 金鑰是功能強大的憑證。切勿公開它們。使用像 [Google Secret Manager](https://cloud.google.com/secret-manager) 這樣的秘密管理器來安全地儲存和存取它們。

## 使用 Anthropic 模型

![java_only](https://img.shields.io/badge/Supported_in-Java-orange){ title="此功能目前適用於 Java。Python 對直接 Anthropic API (非 Vertex) 的支援是透過 LiteLLM。" }

您可以使用其 API 金鑰或從 Vertex AI 後端將 Anthropic 的 Claude 模型直接整合到您的 Java ADK 應用程式中，方法是使用 ADK 的 `Claude` 包裝類別。

對於 Vertex AI 後端，請參閱[Vertex AI 上的第三方模型](#third-party-models-on-vertex-ai-eg-anthropic-claude)部分。

**先決條件：**

1.  **相依性：**
    *   **Anthropic SDK 類別 (傳遞)：** Java ADK 的 `com.google.adk.models.Claude` 包裝函式依賴於 Anthropic 官方 Java SDK 中的類別。這些通常作為**傳遞相依性**包含在內。

2.  **Anthropic API 金鑰：**
    *   從 Anthropic 取得 API 金鑰。使用秘密管理器安全地管理此金鑰。

**整合：**

實例化 `com.google.adk.models.Claude`，提供所需的 Claude 模型名稱和使用您的 API 金鑰設定的 `AnthropicOkHttpClient`。然後，將此 `Claude` 實例傳遞給您的 `LlmAgent`。

**範例：**

```java
import com.anthropic.client.AnthropicClient;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Claude;
import com.anthropic.client.okhttp.AnthropicOkHttpClient; // 來自 Anthropic 的 SDK

public class DirectAnthropicAgent {
  
  private static final String CLAUDE_MODEL_ID = "claude-3-7-sonnet-latest"; // 或您偏好的 Claude 模型

  public static LlmAgent createAgent() {

    // 建議從安全的組態中載入敏感金鑰
    AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
        .apiKey("ANTHROPIC_API_KEY")
        .build();

    Claude claudeModel = new Claude(
        CLAUDE_MODEL_ID,
        anthropicClient
    );

    return LlmAgent.builder()
        .name("claude_direct_agent")
        .model(claudeModel)
        .instruction("你是一個由 Anthropic Claude 驅動的樂於助人的 AI 助理。")
        // ... 其他 LlmAgent 組態
        .build();
  }

  public static void main(String[] args) {
    try {
      LlmAgent agent = createAgent();
      System.out.println("成功建立直接的 Anthropic 代理：" + agent.name());
    } catch (IllegalStateException e) {
      System.err.println("建立代理時出錯：" + e.getMessage());
    }
  }
}
```



## 透過 LiteLLM 使用雲端和專有模型

![python_only](https://img.shields.io/badge/Supported_in-Python-blue)

為了存取來自 OpenAI、Anthropic (非 Vertex
AI)、Cohere 等眾多提供商的大量 LLM，ADK 透過 LiteLLM
函式庫提供整合。

**整合方法：** 實例化 `LiteLlm` 包裝類別並將其傳遞給
`LlmAgent` 的 `model` 參數。

**LiteLLM 總覽：** [LiteLLM](https://docs.litellm.ai/) 充當一個翻譯
層，為 100 多個 LLM 提供標準化的、與 OpenAI 相容的介面。

**設定：**

1. **安裝 LiteLLM：**
        ```shell
        pip install litellm
        ```
2. **設定提供商 API 金鑰：** 將您打算使用的特定提供商的 API 金鑰設定為環境變數。

    * *OpenAI 範例：*

        ```shell
        export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
        ```

    * *Anthropic (非 Vertex AI) 範例：*

        ```shell
        export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
        ```

    * *有關其他提供商的正確環境變數名稱，請參閱
      [LiteLLM 提供商文件](https://docs.litellm.ai/docs/providers)。*

        **範例：**

        ```python
        from google.adk.agents import LlmAgent
        from google.adk.models.lite_llm import LiteLlm

        # --- 使用 OpenAI 的 GPT-4o 的範例代理 ---
        # (需要 OPENAI_API_KEY)
        agent_openai = LlmAgent(
            model=LiteLlm(model="openai/gpt-4o"), # LiteLLM 模型字串格式
            name="openai_agent",
            instruction="你是一個由 GPT-4o 驅動的樂於助人的助理。",
            # ... 其他代理參數
        )

        # --- 使用 Anthropic 的 Claude Haiku (非 Vertex) 的範例代理 ---
        # (需要 ANTHROPIC_API_KEY)
        agent_claude_direct = LlmAgent(
            model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
            name="claude_direct_agent",
            instruction="你是一個由 Claude Haiku 驅動的助理。",
            # ... 其他代理參數
        )
        ```

!!!info "Windows 使用者注意事項"

    ### 避免在 Windows 上出現 LiteLLM UnicodeDecodeError
    在 Windows 上將 ADK 代理與 LiteLlm 搭配使用時，使用者可能會遇到以下錯誤：
    ```
    UnicodeDecodeError: 'charmap' codec can't decode byte...
    ```
    發生此問題的原因是 `litellm` (由 LiteLlm 使用) 使用預設的 Windows 編碼 (`cp1252`) 而非 UTF-8 讀取快取檔案 (例如模型定價資訊)。
    Windows 使用者可以透過將 `PYTHONUTF8` 環境變數設定為 `1` 來防止此問題。這會強制 Python 全域使用 UTF-8。
    **範例 (PowerShell)：**
    ```powershell
    # 為目前會話設定
    $env:PYTHONUTF8 = "1"
    # 為使用者永久設定
    [System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', [System.EnvironmentVariableTarget]::User)
    套用此設定可確保 Python 使用 UTF-8 讀取快取檔案，從而避免解碼錯誤。
    ```


## 透過 LiteLLM 使用開放和本地模型

![python_only](https://img.shields.io/badge/Supported_in-Python-blue)

為了最大程度地控制、節省成本、保護隱私或離線使用案例，您可以
在本機執行開源模型或自行託管它們，並使用 LiteLLM 將其整合。

**整合方法：** 實例化 `LiteLlm` 包裝類別，並將其設定為
指向您的本地模型伺服器。

### Ollama 整合

[Ollama](https://ollama.com/) 可讓您輕鬆地在本機執行開源模型。

#### 模型選擇

如果您的代理依賴工具，請確保您從 [Ollama 網站](https://ollama.com/search?c=tools) 中選擇具有工具支援的模型。

為了獲得可靠的結果，我們建議使用具有工具支援的相當規模的模型。

可以使用以下指令檢查模型的工具支援：

```bash
ollama show mistral-small3.1
  Model
    architecture        mistral3
    parameters          24.0B
    context length      131072
    embedding length    5120
    quantization        Q4_K_M

  Capabilities
    completion
    vision
    tools
```

您應該會在功能下看到 `tools`。

您還可以查看模型正在使用的範本，並根據您的
需求進行調整。

```bash
ollama show --modelfile llama3.2 > model_file_to_modify
```

例如，上述模型的預設範本固有地建議
模型應始終呼叫一個函式。這可能會導致函式呼叫的無限
循環。

```
給定以下函式，請以 JSON 格式回應一個函式呼叫
及其適當的參數，以最好地回答給定的提示。

以 {"name": function name, "parameters": dictionary of
argument name and its value} 的格式回應。不要使用變數。
```

您可以將此類提示替換為更具描述性的提示，以防止無限工具
呼叫循環。

例如：

```
檢閱使用者的提示和下面列出的可用函式。
首先，確定呼叫其中一個函式是否是回應的最合適方式。如果提示要求特定動作、需要外部資料查詢或涉及函式處理的計算，則很可能需要函式呼叫。如果提示是一個一般性問題或可以直接回答，則很可能不需要函式呼叫。

如果您確定需要函式呼叫：僅以 {"name": "function_name", "parameters": {"argument_name": "value"}} 格式的 JSON 物件回應。確保參數值是具體的，而不是變數。

如果您確定不需要函式呼叫：直接以純文字回應使用者的提示，提供所要求的答案或資訊。不要輸出任何 JSON。
```

然後，您可以使用以下指令建立一個新模型：

```bash
ollama create llama3.2-modified -f model_file_to_modify
```

#### 使用 ollama_chat 提供商

我們的 LiteLLM 包裝函式可用於建立具有 Ollama 模型的代理。

```py
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral-small3.1"),
    name="dice_agent",
    description=(
        "一個可以擲 8 面骰子並檢查質數的 hello world 代理。"
    ),
    instruction="""
      你擲骰子並回答有關骰子擲出結果的問題。
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

**重要的是要將提供商設定為 `ollama_chat` 而不是 `ollama`。使用
`ollama` 會導致意外行為，例如無限工具呼叫循環
和忽略先前的上下文。**

雖然可以在 LiteLLM 中提供 `api_base` 以進行生成，但 LiteLLM 函式庫
在完成後會呼叫依賴環境變數的其他 API (截至 v1.65.5)。因此，目前我們建議將環境變數
`OLLAMA_API_BASE` 設定為指向 ollama 伺服器。

```bash
export OLLAMA_API_BASE="http://localhost:11434"
adk web
```

#### 使用 openai 提供商

或者，`openai` 可以用作提供商名稱。但這也
需要設定 `OPENAI_API_BASE=http://localhost:11434/v1` 和
`OPENAI_API_KEY=anything` 環境變數，而不是 `OLLAMA_API_BASE`。**請
注意，api base 現在結尾有 `/v1`。**

```py
root_agent = Agent(
    model=LiteLlm(model="openai/mistral-small3.1"),
    name="dice_agent",
    description=(
        "一個可以擲 8 面骰子並檢查質數的 hello world 代理。"
    ),
    instruction="""
      你擲骰子並回答有關骰子擲出結果的問題。
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

```bash
export OPENAI_API_BASE=http://localhost:11434/v1
export OPENAI_API_KEY=anything
adk web
```

#### 除錯

您可以透過在
您的代理程式碼中緊接在匯入之後新增以下內容來查看傳送給 Ollama 伺服器的請求。

```py
import litellm
litellm._turn_on_debug()
```

尋找類似以下的一行：

```bash
Request Sent from LiteLLM:
curl -X POST \
http://localhost:11434/api/chat \
-d '{'model': 'mistral-small3.1', 'messages': [{'role': 'system', 'content': ...
```

### 自行託管的端點 (例如 vLLM)

![python_only](https://img.shields.io/badge/Supported_in-Python-blue)

諸如 [vLLM](https://github.com/vllm-project/vllm) 之類的工具可讓您高效地託管
模型，並通常公開與 OpenAI 相容的 API 端點。

**設定：**

1. **部署模型：** 使用 vLLM (或類似工具) 部署您選擇的模型。
   記下 API 基礎 URL (例如 `https://your-vllm-endpoint.run.app/v1`)。
    * *對 ADK 工具很重要：* 部署時，請確保服務工具
      支援並啟用與 OpenAI 相容的工具/函式呼叫。對於 vLLM，
      這可能涉及 `--enable-auto-tool-choice` 之類的旗標，並可能
      需要一個特定的 `--tool-call-parser`，具體取決於模型。請參閱 vLLM
      關於工具使用的文件。
2. **身份驗證：** 確定您的端點如何處理身份驗證 (例如，
   API 金鑰、持有者權杖)。

    **整合範例：**

    ```python
    import subprocess
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm

    # --- 使用 vLLM 端點上託管的模型的範例代理 ---

    # 您的 vLLM 部署提供的端點 URL
    api_base_url = "https://your-vllm-endpoint.run.app/v1"

    # *您的* vLLM 端點組態識別的模型名稱
    model_name_at_endpoint = "hosted_vllm/google/gemma-3-4b-it" # 來自 vllm_test.py 的範例

    # 身份驗證 (範例：對 Cloud Run 部署使用 gcloud 身份權杖)
    # 根據您的端點安全性進行調整
    try:
        gcloud_token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token", "-q"]
        ).decode().strip()
        auth_headers = {"Authorization": f"Bearer {gcloud_token}"}
    except Exception as e:
        print(f"警告：無法取得 gcloud 權杖 - {e}。端點可能不安全或需要不同的身份驗證。")
        auth_headers = None # 或適當地處理錯誤

    agent_vllm = LlmAgent(
        model=LiteLlm(
            model=model_name_at_endpoint,
            api_base=api_base_url,
            # 如有需要，傳遞身份驗證標頭
            extra_headers=auth_headers
            # 或者，如果端點使用 API 金鑰：
            # api_key="YOUR_ENDPOINT_API_KEY"
        ),
        name="vllm_agent",
        instruction="你是一個在自行託管的 vLLM 端點上執行的樂於助人的助理。",
        # ... 其他代理參數
    )
    ```

## 在 Vertex AI 上使用託管和微調的模型

對於企業級的可擴展性、可靠性以及與 Google
Cloud 的 MLOps 生態系統的整合，您可以使用部署到 Vertex AI 端點的模型。
這包括來自 Model Garden 或您自己的微調模型。

**整合方法：** 將完整的 Vertex AI 端點資源字串
(`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`) 直接傳遞給
`LlmAgent` 的 `model` 參數。

**Vertex AI 設定 (合併)：**

確保您的環境已為 Vertex AI 設定：

1. **身份驗證：** 使用應用程式預設憑證 (ADC)：

    ```shell
    gcloud auth application-default login
    ```

2. **環境變數：** 設定您的專案和位置：

    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # 例如 us-central1
    ```

3. **啟用 Vertex 後端：** 至關重要的是，確保 `google-genai` 函式庫
   以 Vertex AI 為目標：

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### Model Garden 部署

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前適用於 Python。Java 支援計畫中/即將推出。" }

您可以將來自
[Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) 的各種開放和專有模型部署
到一個端點。

**範例：**

```python
from google.adk.agents import LlmAgent
from google.genai import types # 用於組態物件

# --- 使用從 Model Garden 部署的 Llama 3 模型的範例代理 ---

# 用您實際的 Vertex AI 端點資源名稱取代
llama3_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID"

agent_llama3_vertex = LlmAgent(
    model=llama3_endpoint,
    name="llama3_vertex_agent",
    instruction="你是一個基於 Llama 3 的樂於助人的助理，託管在 Vertex AI 上。",
    generate_content_config=types.GenerateContentConfig(max_output_tokens=2048),
    # ... 其他代理參數
)
```

### 微調模型端點

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前適用於 Python。Java 支援計畫中/即將推出。" }

部署您的微調模型 (無論是基於 Gemini 還是 Vertex AI 支援的其他架構
) 都會產生一個可以直接使用的端點。

**範例：**

```python
from google.adk.agents import LlmAgent

# --- 使用微調的 Gemini 模型端點的範例代理 ---

# 用您微調模型的端點資源名稱取代
finetuned_gemini_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID"

agent_finetuned_gemini = LlmAgent(
    model=finetuned_gemini_endpoint,
    name="finetuned_gemini_agent",
    instruction="你是一個在特定資料上訓練過的專門助理。",
    # ... 其他代理參數
)
```

### Vertex AI 上的第三方模型 (例如 Anthropic Claude)

一些提供商，如 Anthropic，使其模型可直接透過
Vertex AI 使用。

=== "Python"

    **整合方法：** 使用直接模型字串 (例如，
    `"claude-3-sonnet@20240229"`)，*但需要在 ADK 中手動註冊*。
    
    **為何需要註冊？** ADK 的註冊表會自動識別 `gemini-*` 字串
    和標準 Vertex AI 端點字串 (`projects/.../endpoints/...`) 並
    透過 `google-genai` 函式庫路由它們。對於直接
    透過 Vertex AI 使用的其他模型類型 (如 Claude)，您必須明確告知 ADK 註冊表哪個
    特定的包裝類別 (`Claude` 在此情況下) 知道如何使用 Vertex AI 後端處理該模型
    識別碼字串。
    
    **設定：**
    
    1. **Vertex AI 環境：** 確保合併的 Vertex AI 設定 (ADC, Env
       Vars, `GOOGLE_GENAI_USE_VERTEXAI=TRUE`) 已完成。
    
    2. **安裝提供商函式庫：** 安裝為
       Vertex AI 設定的必要用戶端函式庫。
    
        ```shell
        pip install "anthropic[vertex]"
        ```
    
    3. **註冊模型類別：** 在您的應用程式啟動附近新增此程式碼，
       *在*使用 Claude 模型字串建立代理之前：
    
        ```python
        # 直接透過 Vertex AI 與 LlmAgent 使用 Claude 模型字串所需
        from google.adk.models.anthropic_llm import Claude
        from google.adk.models.registry import LLMRegistry
    
        LLMRegistry.register(Claude)
        ```
    
       **範例：**

       ```python
       from google.adk.agents import LlmAgent
       from google.adk.models.anthropic_llm import Claude # 註冊所需匯入
       from google.adk.models.registry import LLMRegistry # 註冊所需匯入
       from google.genai import types
        
       # --- 註冊 Claude 類別 (在啟動時執行一次) ---
       LLMRegistry.register(Claude)
        
       # --- 使用 Vertex AI 上的 Claude 3 Sonnet 的範例代理 ---
        
       # Vertex AI 上 Claude 3 Sonnet 的標準模型名稱
       claude_model_vertexai = "claude-3-sonnet@20240229"
        
       agent_claude_vertexai = LlmAgent(
           model=claude_model_vertexai, # 註冊後傳遞直接字串
           name="claude_vertexai_agent",
           instruction="你是一個由 Vertex AI 上的 Claude 3 Sonnet 驅動的助理。",
           generate_content_config=types.GenerateContentConfig(max_output_tokens=4096),
           # ... 其他代理參數
       )
       ```

=== "Java"

    **整合方法：** 直接實例化特定於提供商的模型類別 (例如 `com.google.adk.models.Claude`) 並使用 Vertex AI 後端對其進行設定。
    
    **為何直接實例化？** Java ADK 的 `LlmRegistry` 預設主要處理 Gemini 模型。對於像 Vertex AI 上的 Claude 這樣的第三方模型，您直接向 `LlmAgent` 提供 ADK 的包裝類別 (例如 `Claude`) 的實例。此包裝類別負責透過其為 Vertex AI 設定的特定用戶端函式庫與模型互動。
    
    **設定：**
    
    1.  **Vertex AI 環境：**
        *   確保您的 Google Cloud 專案和區域已正確設定。
        *   **應用程式預設憑證 (ADC)：** 確保 ADC 在您的環境中已正確設定。這通常是透過執行 `gcloud auth application-default login` 來完成的。Java 用戶端函式庫將使用這些憑證向 Vertex AI 進行身份驗證。有關詳細設定，請遵循 [Google Cloud Java ADC 文件](https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault__)。
    
    2.  **提供商函式庫相依性：**
        *   **第三方用戶端函式庫 (通常是傳遞的)：** ADK 核心函式庫通常包含 Vertex AI 上常見第三方模型 (如 Anthropic 所需的類別) 所需的用戶端函式庫作為**傳遞相依性**。這意味著您可能不需要在 `pom.xml` 或 `build.gradle` 中明確為 Anthropic Vertex SDK 新增單獨的相依性。

    3.  **實例化和設定模型：**
        建立 `LlmAgent` 時，實例化 `Claude` 類別 (或另一個提供商的等效類別) 並設定其 `VertexBackend`。
    
    **範例：**

    ```java
    import com.anthropic.client.AnthropicClient;
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.anthropic.vertex.backends.VertexBackend;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Claude; // ADK 的 Claude 包裝函式
    import com.google.auth.oauth2.GoogleCredentials;
    import java.io.IOException;

    // ... 其他匯入

    public class ClaudeVertexAiAgent {

        public static LlmAgent createAgent() throws IOException {
            // Vertex AI 上 Claude 3 Sonnet 的模型名稱 (或其他版本)
            String claudeModelVertexAi = "claude-3-7-sonnet"; // 或任何其他 Claude 模型

            // 使用 VertexBackend 設定 AnthropicOkHttpClient
            AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
                .backend(
                    VertexBackend.builder()
                        .region("us-east5") // 指定您的 Vertex AI 區域
                        .project("your-gcp-project-id") // 指定您的 GCP 專案 ID
                        .googleCredentials(GoogleCredentials.getApplicationDefault())
                        .build())
                .build();

            // 使用 ADK Claude 包裝函式實例化 LlmAgent
            LlmAgent agentClaudeVertexAi = LlmAgent.builder()
                .model(new Claude(claudeModelVertexAi, anthropicClient)) // 傳遞 Claude 實例
                .name("claude_vertexai_agent")
                .instruction("你是一個由 Vertex AI 上的 Claude 3 Sonnet 驅動的助理。")
                // .generateContentConfig(...) // 可選：如有需要，新增生成組態
                // ... 其他代理參數
                .build();
            
            return agentClaudeVertexAi;
        }

        public static void main(String[] args) {
            try {
                LlmAgent agent = createAgent();
                System.out.println("成功建立代理：" + agent.name());
                // 在這裡，您通常會設定一個 Runner 和 Session 來與代理互動
            } catch (IOException e) {
                System.err.println("建立代理失敗：" + e.getMessage());
                e.printStackTrace();
            }
        }
    }
    ```
