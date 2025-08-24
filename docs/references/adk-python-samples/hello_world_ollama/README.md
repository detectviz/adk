# 將 ollama 模型與 ADK 搭配使用

## 模型選擇

如果您的代理 (agent) 依賴工具，請確保您從 [ollama 網站](https://ollama.com/search?c=tools) 中選擇支援工具的模型。

為獲得可靠的結果，我們建議使用具有工具支援且大小適中的模型。

可以使用以下指令檢查模型是否支援工具：

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

您應該會在 capabilities 下看到 `tools`。

您還可以查看模型正在使用的範本，並根據您的需求進行調整。

```bash
ollama show --modelfile llama3.1 > model_file_to_modify
```

然後您可以使用以下指令建立模型：

```bash
ollama create llama3.1-modified -f model_file_to_modify
```

## 使用 ollama_chat 提供者

我們的 LiteLlm 包裝函式可用於建立具有 ollama 模型的代理 (agent)。

```py
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral-small3.1"),
    name="dice_agent",
    description=(
        "一個可以擲八面骰並檢查質數的 hello world 代理 (agent)。"
    ),
    instruction="""
      您擲骰子並回答有關擲骰結果的問題。
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

**重要的是將提供者設定為 `ollama_chat` 而非 `ollama`。使用 `ollama` 會導致非預期的行為，例如無限的工具呼叫迴圈和忽略先前的上下文 (context)。**

雖然可以在 litellm 內部提供 `api_base` 進行生成，但 litellm 函式庫在 v1.65.5 版之後的完成後，會呼叫其他依賴環境變數的 API。因此，目前我們建議設定環境變數 `OLLAMA_API_BASE` 以指向 ollama 伺服器。

```bash
export OLLAMA_API_BASE="http://localhost:11434"
adk web
```

## 使用 openai 提供者

或者，可以使用 `openai` 作為提供者名稱。但這也需要設定 `OPENAI_API_BASE=http://localhost:11434/v1` 和 `OPENAI_API_KEY=anything` 環境變數，而不是 `OLLAMA_API_BASE`。**請注意，api base 現在結尾有 `/v1`。**

```py
root_agent = Agent(
    model=LiteLlm(model="openai/mistral-small3.1"),
    name="dice_agent",
    description=(
        "一個可以擲八面骰並檢查質數的 hello world 代理 (agent)。"
    ),
    instruction="""
      您擲骰子並回答有關擲骰結果的問題。
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

## 偵錯

您可以在代理 (agent) 程式碼中緊接在匯入之後新增以下內容，以查看傳送到 ollama 伺服器的請求。

```py
import litellm
litellm._turn_on_debug()
```

尋找類似下面的一行：

```bash
quest Sent from LiteLLM:
curl -X POST \
http://localhost:11434/api/chat \
-d '{'model': 'mistral-small3.1', 'messages': [{'role': 'system', 'content': ...
```
