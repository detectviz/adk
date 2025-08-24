# 快速入門

本快速入門將引導您安裝代理開發套件 (Agent Development Kit, ADK)，設定一個包含多個工具的基本代理，並在終端機或互動式、基於瀏覽器的開發者介面中於本機執行它。


本快速入門假設您擁有一個本地 IDE (VS Code、PyCharm、IntelliJ IDEA 等)，並已安裝 Python 3.9+ 或 Java 17+ 且具有終端機存取權限。此方法會將應用程式完全在您的機器上執行，建議用於內部開發。

## 1. 設定環境並安裝 ADK {#venv-install}

=== "Python"

    建立並啟用虛擬環境 (建議)：

    ```bash
    # 建立
    python -m venv .venv
    # 啟用 (每個新終端機)
    # macOS/Linux: source .venv/bin/activate
    # Windows CMD: .venv\Scripts\activate.bat
    # Windows PowerShell: .venv\Scripts\Activate.ps1
    ```

    安裝 ADK：

    ```bash
    pip install google-adk
    ```

=== "Java"

    要安裝 ADK 並設定環境，請執行以下步驟。

## 2. 建立代理專案 {#create-agent-project}

### 專案結構

=== "Python"

    您需要建立以下專案結構：

    ```console
    parent_folder/
        multi_tool_agent/
            __init__.py
            agent.py
            .env
    ```

    建立資料夾 `multi_tool_agent`：

    ```bash
    mkdir multi_tool_agent/
    ```

    !!! info "Windows 使用者注意事項"

        在 Windows 上使用 ADK 執行接下來的幾個步驟時，我們建議使用檔案總管或 IDE 建立 Python 檔案，因為以下指令 (`mkdir`、`echo`) 通常會產生包含空位元組和/或不正確編碼的檔案。

    ### `__init__.py`

    現在在資料夾中建立一個 `__init__.py` 檔案：

    ```shell
    echo "from . import agent" > multi_tool_agent/__init__.py
    ```

    您的 `__init__.py` 現在應該如下所示：

    ```python title="multi_tool_agent/__init__.py"
    --8<-- "examples/python/snippets/get-started/multi_tool_agent/__init__.py"
    ```

    ### `agent.py`

    在同一個資料夾中建立一個 `agent.py` 檔案：

    ```shell
    touch multi_tool_agent/agent.py
    ```

    複製並貼上以下程式碼到 `agent.py`：

    ```python title="multi_tool_agent/agent.py"
    --8<-- "examples/python/snippets/get-started/multi_tool_agent/agent.py"
    ```

    ### `.env`

    在同一個資料夾中建立一個 `.env` 檔案：

    ```shell
    touch multi_tool_agent/.env
    ```

    有關此檔案的更多說明，請參閱下一節 [設定模型](#set-up-the-model)。

=== "Java"

    Java 專案通常具有以下專案結構：

    ```console
    project_folder/
    ├── pom.xml (or build.gradle)
    ├── src/
    ├── └── main/
    │       └── java/
    │           └── agents/
    │               └── multitool/
    └── test/
    ```

    ### 建立 `MultiToolAgent.java`

    在 `src/main/java/agents/multitool/` 目錄的 `agents.multitool` 套件中建立一個 `MultiToolAgent.java` 原始檔。

    複製並貼上以下程式碼到 `MultiToolAgent.java`：

    ```java title="agents/multitool/MultiToolAgent.java"
    --8<-- "examples/java/cloud-run/src/main/java/agents/multitool/MultiToolAgent.java:full_code"
    ```

![intro_components.png](../assets/quickstart-flow-tool.png)

## 3. 設定模型 {#set-up-the-model}

您的代理理解使用者請求和生成回應的能力由大型語言模型 (LLM) 提供支援。您的代理需要對此外部 LLM 服務進行安全呼叫，這**需要身份驗證憑證**。如果沒有有效的身份驗證，LLM 服務將拒絕代理的請求，代理將無法運作。

!!!tip "模型驗證指南"
    有關向不同模型進行身份驗證的詳細指南，請參閱 [身份驗證指南](../agents/models.md#google-ai-studio)。這是確保您的代理可以呼叫 LLM 服務的關鍵步驟。

=== "Gemini - Google AI Studio"
    1. 從 [Google AI Studio](https://aistudio.google.com/apikey) 取得 API 金鑰。
    2. 使用 Python 時，開啟位於 (`multi_tool_agent/`) 內的 **`.env`** 檔案，並複製貼上以下程式碼。

        ```env title="multi_tool_agent/.env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

        使用 Java 時，定義環境變數：

        ```console title="terminal"
        export GOOGLE_GENAI_USE_VERTEXAI=FALSE
        export GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3. 將 `PASTE_YOUR_ACTUAL_API_KEY_HERE` 替換為您實際的 `API KEY`。

=== "Gemini - Google Cloud Vertex AI"
    1. 設定 [Google Cloud 專案](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp) 並 [啟用 Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)。
    2. 設定 [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)。
    3. 透過執行 `gcloud auth login` 從終端機向 Google Cloud 進行身份驗證。
    4. 使用 Python 時，開啟位於 (`multi_tool_agent/`) 內的 **`.env`** 檔案。複製貼上以下程式碼並更新專案 ID 和位置。

        ```env title="multi_tool_agent/.env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=LOCATION
        ```

        使用 Java 時，定義環境變數：

        ```console title="terminal"
        export GOOGLE_GENAI_USE_VERTEXAI=TRUE
        export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
        export GOOGLE_CLOUD_LOCATION=LOCATION
        ```

=== "Gemini - Google Cloud Vertex AI with Express Mode"
    1. 您可以註冊一個免費的 Google Cloud 專案，並使用符合條件的帳戶免費使用 Gemini！
        * 設定一個 [使用 Vertex AI Express 模式的 Google Cloud 專案](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)
        * 從您的 Express 模式專案取得 API 金鑰。此金鑰可用於 ADK，以免費使用 Gemini 模型，並存取代理引擎服務。
    2. 使用 Python 時，開啟位於 (`multi_tool_agent/`) 內的 **`.env`** 檔案。複製貼上以下程式碼並更新專案 ID 和位置。

        ```env title="multi_tool_agent/.env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
        ```

        使用 Java 時，定義環境變數：

        ```console title="terminal"
        export GOOGLE_GENAI_USE_VERTEXAI=TRUE
        export GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
        ```

## 4. 執行您的代理 {#run-your-agent}

=== "Python"

    使用終端機，導覽至您代理專案的父目錄 (例如使用 `cd ..`)：

    ```console
    parent_folder/      <-- navigate to this directory
        multi_tool_agent/
            __init__.py
            agent.py
            .env
    ```

    有多种方式可以與您的代理互動：

    === "開發者介面 (adk web)"

        !!! success "Vertex AI 使用者驗證設定"
            如果您在上一步中選擇了 **"Gemini - Google Cloud Vertex AI"**，則必須在啟動開發者介面前向 Google Cloud 進行身份驗證。
            
            執行此指令並依照提示操作：
            ```bash
            gcloud auth application-default login
            ```
            
            **注意：** 如果您使用的是「Gemini - Google AI Studio」，請跳過此步驟。

        執行以下指令以啟動 **開發者介面**。

        ```shell
        adk web
        ```
        
        !!!info "Windows 使用者注意事項"

            當遇到 `_make_subprocess_transport NotImplementedError` 時，請考慮改用 `adk web --no-reload`。


        **步驟 1：** 在瀏覽器中直接開啟提供的 URL (通常是 `http://localhost:8000` 或 `http://127.0.0.1:8000`)。

        **步驟 2.** 在 UI 的左上角，您可以在下拉式選單中選擇您的代理。選擇 "multi_tool_agent"。

        !!!note "疑難排解"

            如果您在下拉式選單中沒有看到 "multi_tool_agent"，請確保您正在代理資料夾的 **父資料夾** (即 multi_tool_agent 的父資料夾) 中執行 `adk web`。

        **步驟 3.** 現在您可以使用文字方塊與您的代理聊天：

        ![adk-web-dev-ui-chat.png](../assets/adk-web-dev-ui-chat.png)


        **步驟 4.** 透過使用左側的 `Events` 標籤，您可以透過點擊動作來檢查個別的函式呼叫、回應和模型回應：

        ![adk-web-dev-ui-function-call.png](../assets/adk-web-dev-ui-function-call.png)

        在 `Events` 標籤上，您也可以點擊 `Trace` 按鈕來查看每個事件的追蹤日誌，其中顯示了每個函式呼叫的延遲：

        ![adk-web-dev-ui-trace.png](../assets/adk-web-dev-ui-trace.png)

        **步驟 5.** 您也可以啟用麥克風與您的代理交談：

        !!!note "語音/視訊串流的模型支援"

            為了在 ADK 中使用語音/視訊串流，您需要使用支援 Live API 的 Gemini 模型。您可以在文件中找到支援 Gemini Live API 的 **模型 ID**：

            - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
            - [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

            然後，您可以將您先前建立的 `agent.py` 檔案中 `root_agent` 的 `model` 字串替換掉 ([跳至章節](#agentpy))。您的程式碼應該如下所示：

            ```py
            root_agent = Agent(
                name="weather_time_agent",
                model="replace-me-with-model-id", #e.g. gemini-2.0-flash-live-001
                ...
            ```

        ![adk-web-dev-ui-audio.png](../assets/adk-web-dev-ui-audio.png)

    === "終端機 (adk run)"

        執行以下指令，與您的天氣代理聊天。

        ```
        adk run multi_tool_agent
        ```

        ![adk-run.png](../assets/adk-run.png)

        若要結束，請使用 Cmd/Ctrl+C。

    === "API 伺服器 (adk api_server)"

        `adk api_server` 可讓您透過單一指令建立本地 FastAPI 伺服器，讓您在部署代理前測試本地 cURL 請求。

        ![adk-api-server.png](../assets/adk-api-server.png)

        要了解如何使用 `adk api_server` 進行測試，請參閱[關於測試的文件](get-started-testing.md)。

=== "Java"

    使用終端機，導覽至您代理專案的父目錄 (例如使用 `cd ..`)：

    ```console
    project_folder/                <-- navigate to this directory
    ├── pom.xml (or build.gradle)
    ├── src/
    ├── └── main/
    │       └── java/
    │           └── agents/
    │               └── multitool/
    │                   └── MultiToolAgent.java
    └── test/
    ```

    === "開發者介面"

        從終端機執行以下指令以啟動開發者介面。

        **請勿變更開發者介面伺服器的主類別名稱。**

        ```console title="terminal"
        mvn exec:java \
            -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
            -Dexec.args="--adk.agents.source-dir=src/main/java" \
            -Dexec.classpathScope="compile"
        ```

        **步驟 1：** 在瀏覽器中直接開啟提供的 URL (通常是 `http://localhost:8080` 或 `http://127.0.0.1:8080`)。

        **步驟 2.** 在 UI 的左上角，您可以在下拉式選單中選擇您的代理。選擇 "multi_tool_agent"。

        !!!note "疑難排解"

            如果您在下拉式選單中沒有看到 "multi_tool_agent"，請確保您在 Java 原始碼所在的位置 (通常是 `src/main/java`) 執行 `mvn` 指令。

        **步驟 3.** 現在您可以使用文字方塊與您的代理聊天：

        ![adk-web-dev-ui-chat.png](../assets/adk-web-dev-ui-chat.png)

        **步驟 4.** 您也可以透過點擊動作來檢查個別的函式呼叫、回應和模型回應：

        ![adk-web-dev-ui-function-call.png](../assets/adk-web-dev-ui-function-call.png)

    === "Maven"

        使用 Maven，透過以下指令執行您 Java 類別的 `main()` 方法：

        ```console title="terminal"
        mvn compile exec:java -Dexec.mainClass="agents.multitool.MultiToolAgent"
        ```

    === "Gradle"

        使用 Gradle，`build.gradle` 或 `build.gradle.kts` 建置檔案應在其 `plugins` 區段中包含以下 Java 外掛程式：

        ```groovy
        plugins {
            id("java")
            // other plugins
        }
        ```

        然後，在建置檔案的其他地方，在最上層，建立一個新任務來執行您代理的 `main()` 方法：

        ```groovy
        task runAgent(type: JavaExec) {
            classpath = sourceSets.main.runtimeClasspath
            mainClass = "agents.multitool.MultiToolAgent"
        }
        ```

        最後，在命令列上，執行以下指令：

        ```console
        gradle runAgent
        ```



### 📝 可嘗試的範例提示

* 紐約的天氣如何？
* 紐約現在幾點？
* 巴黎的天氣如何？
* 巴黎現在幾點？

## 🎉 恭喜！

您已成功使用 ADK 建立並與您的第一個代理互動！

---

## 🛣️ 後續步驟

* **前往教學**：了解如何為您的代理新增記憶體、會話、狀態：[教學](tutorials.md)。
* **深入了解進階組態：** 探索 [設定](get-started-installation.md) 部分，深入了解專案結構、組態和其他介面。
* **了解核心概念：** 了解[代理概念](agents.md)。
