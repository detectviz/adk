# 快速入門：透過 A2A 公開遠端代理

本快速入門涵蓋了任何開發人員最常見的起點：**「我有一個代理。我如何將其公開以便其他代理可以透過 A2A 使用我的代理？」**。這對於建構需要不同代理協作和互動的複雜多代理系統至關重要。

## 總覽

此範例示範如何輕鬆地公開 ADK 代理，以便其他代理可以使用 A2A 協定取用它。

有兩種主要方式可以透過 A2A 公開 ADK 代理。

* **使用 `to_a2a(root_agent)` 函式**：如果您只想將現有代理轉換為可與 A2A 協作，並能夠透過 `uvicorn` 而非 `adk deploy api_server` 透過伺服器公開它，請使用此函式。這意味著當您想要將代理產品化時，您可以更嚴格地控制要透過 `uvicorn` 公開的內容。此外，`to_a2a()` 函式會根據您的代理程式碼自動產生代理卡。
* **建立您自己的代理卡 (`agent.json`) 並使用 `adk api_server --a2a` 託管它**：使用此方法有兩個主要優點。首先，`adk api_server --a2a` 可與 `adk web` 搭配使用，使其易於使用、除錯和測試您的代理。其次，使用 `adk api_server`，您可以指定一個包含多個獨立代理的父資料夾。那些擁有代理卡 (`agent.json`) 的代理將自動可以透過同一個伺服器供其他代理透過 A2A 使用。但是，您需要建立自己的代理卡。要建立代理卡，您可以遵循 [A2A Python 教學](https://a2aprotocol.ai/docs/guide/python-a2a-tutorial)。

本快速入門將著重於 `to_a2a()`，因為這是公開您的代理最簡單的方法，並且還會在幕後自動產生代理卡。如果您想使用 `adk api_server` 方法，您可以在 [A2A 快速入門 (取用) 文件](a2a-quickstart-consuming.md) 中看到它的使用方式。

```text
之前：
                                                ┌────────────────────┐
                                                │ Hello World 代理   │
                                                │  (Python 物件)     │
                                                | 沒有代理卡         │
                                                └────────────────────┘

                                                          │
                                                          │ to_a2a()
                                                          ▼

之後：
┌────────────────┐                             ┌───────────────────────────────┐
│   根代理       │       A2A 協定              │ A2A 公開的 Hello World 代理   │
│(RemoteA2aAgent)│────────────────────────────▶│      (localhost: 8001)         │
│(localhost:8000)│                             └───────────────────────────────┘
└────────────────┘
```

此範例包含：

- **遠端 Hello World 代理** (`remote_a2a/hello_world/agent.py`)：這是您想要公開以便其他代理可以透過 A2A 使用的代理。它是一個處理擲骰子和質數檢查的代理。它使用 `to_a2a()` 函式公開，並使用 `uvicorn` 提供服務。
- **根代理** (`agent.py`)：一個只是呼叫遠端 Hello World 代理的簡單代理。

## 使用 `to_a2a(root_agent)` 函式公開遠端代理

您可以將使用 ADK 建置的現有代理透過 `to_a2a()` 函式簡單地包裝起來，使其與 A2A 相容。例如，如果您在 `root_agent` 中定義了如下代理：

```python
# 您的代理程式碼在此
root_agent = Agent(
    model='gemini-2.0-flash',
    name='hello_world_agent',
    
    <...您的代理程式碼...>
)
```

然後，您可以透過使用 `to_a2a(root_agent)` 簡單地使其與 A2A 相容：

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# 使您的代理與 A2A 相容
a2a_app = to_a2a(root_agent, port=8001)
```

`to_a2a()` 函式甚至會在幕後透過[從 ADK 代理中提取技能、能力和元資料](https://github.com/google/adk-python/blob/main/src/google/adk/a2a/utils/agent_card_builder.py) 在記憶體中自動產生代理卡，以便在使用 `uvicorn` 提供代理端點時，可以使用眾所周知的代理卡。

現在讓我們深入了解範例程式碼。

### 1. 取得範例程式碼

您可以在此處複製並導覽至 [**a2a_root** 範例](https://github.com/google/adk-python/tree/main/contributing/samples/a2a_root)：

```bash
git clone https://github.com/google/adk-python.git
cd adk-python/contributing/samples/a2a_root
```

您將看到資料夾結構如下：

```text
a2a_root/
├── remote_a2a/
│   └── hello_world/    
│       ├── __init__.py
│       └── agent.py    # 遠端 Hello World 代理
├── README.md
└── agent.py            # 根代理
```

#### 根代理 (`a2a_root/agent.py`)

- **`root_agent`**：連接到遠端 A2A 服務的 `RemoteA2aAgent`
- **代理卡 URL**：指向遠端伺服器上眾所周知的代理卡端點

#### 遠端 Hello World 代理 (`a2a_root/remote_a2a/hello_world/agent.py`)

- **`roll_die(sides: int)`**：用於擲骰子並具有狀態管理的函式工具
- **`check_prime(nums: list[int])`**：用於質數檢查的非同步函式
- **`root_agent`**：具有全面說明的主要代理
- **`a2a_app`**：使用 `to_a2a()` 公用程式建立的 A2A 應用程式

### 2. 啟動遠端 A2A 代理伺服器

您現在可以啟動遠端代理伺服器，它將在 hello_world 代理中託管 `a2a_app`：

```bash
# 確保目前工作目錄為 adk-python/
# 使用 uvicorn 啟動遠端代理
uvicorn contributing.samples.a2a_root.remote_a2a.hello_world.agent:a2a_app --host localhost --port 8001
```

??? note "為什麼使用埠 8001？"
    在本快速入門中，於本地測試時，您的代理將使用 localhost，因此公開代理 (遠端質數代理) 的 A2A 伺服器的 `port` 必須與取用代理的埠不同。您將與取用代理互動的 `adk web` 的預設埠是 `8000`，這就是為什麼使用一個單獨的埠 `8001` 建立 A2A 伺服器的原因。

執行後，您應該會看到類似以下的內容：

```shell
INFO:     Started server process [10615]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8001 (Press CTRL+C to quit)
```

### 3. 檢查您的遠端代理是否正在執行

您可以透過造訪您在 `a2a_root/remote_a2a/hello_world/agent.py` 中的 `to_a2a()` 函式中先前自動產生的代理卡來檢查您的代理是否已啟動並正在執行：

[http://localhost:8001/.well-known/agent.json](http://localhost:8001/.well-known/agent.json)

您應該會看到代理卡的內容，它應該如下所示：

```json
{"capabilities":{},"defaultInputModes":["text/plain"],"defaultOutputModes":["text/plain"],"description":"hello world agent that can roll a dice of 8 sides and check prime numbers.","name":"hello_world_agent","protocolVersion":"0.2.6","skills":[{"description":"hello world agent that can roll a dice of 8 sides and check prime numbers. \n      I roll dice and answer questions about the outcome of the dice rolls.\n      I can roll dice of different sizes.\n      I can use multiple tools in parallel by calling functions in parallel(in one request and in one round).\n      It is ok to discuss previous dice roles, and comment on the dice rolls.\n      When I are asked to roll a die, I must call the roll_die tool with the number of sides. Be sure to pass in an integer. Do not pass in a string.\n      I should never roll a die on my own.\n      When checking prime numbers, call the check_prime tool with a list of integers. Be sure to pass in a list of integers. I should never pass in a string.\n      I should not check prime numbers before calling the tool.\n      When I are asked to roll a die and check prime numbers, I should always make the following two function calls:\n      1. I should first call the roll_die tool to get a roll. Wait for the function response before calling the check_prime tool.\n      2. After I get the function response from roll_die tool, I should call the check_prime tool with the roll_die result.\n        2.1 If user asks I to check primes based on previous rolls, make sure I include the previous rolls in the list.\n      3. When I respond, I must include the roll_die result from step 1.\n      I should always perform the previous 3 steps when asking for a roll and checking prime numbers.\n      I should not rely on the previous history on prime results.\n    ","id":"hello_world_agent","name":"model","tags":["llm"]},{"description":"Roll a die and return the rolled result.\n\nArgs:\n  sides: The integer number of sides the die has.\n  tool_context: the tool context\nReturns:\n  An integer of the result of rolling the die.","id":"hello_world_agent-roll_die","name":"roll_die","tags":["llm","tools"]},{"description":"Check if a given list of numbers are prime.\n\nArgs:\n  nums: The list of numbers to check.\n\nReturns:\n  A str indicating which number is prime.","id":"hello_world_agent-check_prime","name":"check_prime","tags":["llm","tools"]}],"supportsAuthenticatedExtendedCard":false,"url":"http://localhost:8001","version":"0.0.1"}
```

### 4. 執行主 (取用) 代理

現在您的遠端代理正在執行，您可以啟動開發者介面並選擇「a2a_root」作為您的代理。

```bash
# 在一個單獨的終端機中，執行 adk 網頁伺服器
adk web contributing/samples/
```

要開啟 adk 網頁伺服器，請前往：[http://localhost:8000](http://localhost:8000)。

## 互動範例

一旦兩個服務都在執行，您就可以與根代理互動，看看它如何透過 A2A 呼叫遠端代理：

**簡單擲骰子：**
此互動使用本地代理，即擲骰子代理：

```text
使用者：擲一個 6 面的骰子
機器人：我為您擲出了一個 4。
```

**質數檢查：**

此互動透過 A2A 使用遠端代理，即質數代理：

```text
使用者：7 是質數嗎？
機器人：是的，7 是質數。
```

**組合操作：**

此互動同時使用本地擲骰子代理和遠端質數代理：

```text
使用者：擲一個 10 面的骰子並檢查它是否是質數
機器人：我為您擲出了一個 8。
機器人：8 不是質數。
```

## 後續步驟

現在您已經建立了一個透過 A2A 伺服器公開遠端代理的代理，下一步是學習如何從另一個代理取用它。

- [**A2A 快速入門 (取用)**](a2a-quickstart-consuming.md)：了解您的代理如何使用 A2A 協定使用其他代理。
