# 部署至 Cloud Run

[Cloud Run](https://cloud.google.com/run)
是一個全代管平台，可讓您直接在 Google 的可擴展基礎架構上執行程式碼。

若要部署您的代理，您可以使用 `adk deploy cloud_run` 指令*（建議 Python 使用）*，或透過 Cloud Run 使用 `gcloud run deploy` 指令。

## 代理範例

對於每個指令，我們將參考 [LLM 代理](agents-llm-agents.md) 頁面上定義的 `Capital Agent` 範例。我們將假設它位於一個目錄中（例如：`capital_agent`）。

若要繼續，請確認您的代理程式碼設定如下：

=== "Python"

    1. 代理程式碼位於代理目錄中的 `agent.py` 檔案內。
    2. 您的代理變數名稱為 `root_agent`。
    3. `__init__.py` 位於您的代理目錄中，並包含 `from . import agent`。
    4. 您的 `requirements.txt` 檔案存在於代理目錄中。

=== "Java"

    1. 代理程式碼位於代理目錄中的 `CapitalAgent.java` 檔案內。
    2. 您的代理變數是全域的，並遵循 `public static BaseAgent ROOT_AGENT` 格式。
    3. 您的代理定義存在於靜態類別方法中。

    如需更多詳細資訊，請參閱以下部分。您也可以在 Github 儲存庫中找到[範例應用程式](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run)。

## 環境變數

如 [設定與安裝](get-started-installation.md) 指南中所述，設定您的環境變數。

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1 # 或您偏好的地區
export GOOGLE_GENAI_USE_VERTEXAI=True
```

*（請將 `your-project-id` 取代為您實際的 GCP 專案 ID）*

或者，您也可以使用來自 AI Studio 的 API 金鑰

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1 # 或您偏好的地區
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY=your-api-key
```
*（請將 `your-project-id` 取代為您實際的 GCP 專案 ID，並將 `your-api-key` 取代為您來自 AI Studio 的實際 API 金鑰）*

## 部署指令

=== "Python - adk CLI"

    ### adk CLI

    `adk deploy cloud_run` 指令會將您的代理程式碼部署至 Google Cloud Run。

    請確保您已向 Google Cloud 進行驗證（`gcloud auth login` 和 `gcloud config set project <your-project-id>`）。

    #### 設定環境變數

    可選但建議：設定環境變數可以讓部署指令更簡潔。

    ```bash
    # 設定您的 Google Cloud 專案 ID
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

    # 設定您想要的 Google Cloud 地區
    export GOOGLE_CLOUD_LOCATION="us-central1" # 範例地區

    # 設定您的代理程式碼目錄路徑
    export AGENT_PATH="./capital_agent" # 假設 capital_agent 在目前目錄中

    # 為您的 Cloud Run 服務設定名稱（可選）
    export SERVICE_NAME="capital-agent-service"

    # 設定應用程式名稱（可選）
    export APP_NAME="capital-agent-app"
    ```

    #### 指令用法

    ##### 最小指令

    ```bash
    adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    $AGENT_PATH
    ```

    ##### 包含可選旗標的完整指令

    ```bash
    adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --service_name=$SERVICE_NAME \
    --app_name=$APP_NAME \
    --with_ui \
    $AGENT_PATH
    ```

    ##### 引數

    * `AGENT_PATH`：（必要）指定包含您代理原始碼的目錄路徑的位置引數（例如，範例中的 `$AGENT_PATH`，或 `capital_agent/`）。此目錄必須至少包含一個 `__init__.py` 和您的主要代理檔案（例如，`agent.py`）。

    ##### 選項

    * `--project TEXT`：（必要）您的 Google Cloud 專案 ID（例如，`$GOOGLE_CLOUD_PROJECT`）。
    * `--region TEXT`：（必要）部署的 Google Cloud 地區（例如，`$GOOGLE_CLOUD_LOCATION`、`us-central1`）。
    * `--service_name TEXT`：（可選）Cloud Run 服務的名稱（例如，`$SERVICE_NAME`）。預設為 `adk-default-service-name`。
    * `--app_name TEXT`：（可選）ADK API 伺服器的應用程式名稱（例如，`$APP_NAME`）。預設為 `AGENT_PATH` 指定的目錄名稱（例如，如果 `AGENT_PATH` 是 `./capital_agent`，則為 `capital_agent`）。
    * `--agent_engine_id TEXT`：（可選）如果您正在透過 Vertex AI Agent Engine 使用代管的會話服務，請在此提供其資源 ID。
    * `--port INTEGER`：（可選）ADK API 伺服器在容器內監聽的埠號。預設為 8000。
    * `--with_ui`：（可選）如果包含此旗標，則會將 ADK 開發 UI 與代理 API 伺服器一起部署。預設情況下，僅部署 API 伺服器。
    * `--temp_folder TEXT`：（可選）指定用於儲存部署過程中產生的中繼檔案的目錄。預設為系統暫存目錄中帶有時間戳記的資料夾。*（注意：除非進行疑難排解，否則通常不需要此選項）。*
    * `--help`：顯示說明訊息並結束。

    ##### 已驗證的存取
    在部署過程中，系統可能會提示您：`允許對 [your-service-name] 進行未經驗證的調用 (y/N)？`。

    * 輸入 `y` 以允許公開存取您的代理 API 端點，無需驗證。
    * 輸入 `N`（或按 Enter 使用預設值）以要求驗證（例如，使用「測試您的代理」部分中顯示的身分權杖）。

    成功執行後，該指令會將您的代理部署到 Cloud Run，並提供已部署服務的 URL。

=== "Python - gcloud CLI"

    ### gcloud CLI

    或者，您可以使用標準的 `gcloud run deploy` 指令搭配 `Dockerfile` 進行部署。與 `adk` 指令相比，此方法需要更多手動設定，但提供了靈活性，特別是如果您想將代理嵌入自訂的 [FastAPI](https://fastapi.tiangolo.com/) 應用程式中。

    請確保您已向 Google Cloud 進行驗證（`gcloud auth login` 和 `gcloud config set project <your-project-id>`）。

    #### 專案結構

    將您的專案檔案組織如下：

    ```txt
    your-project-directory/
    ├── capital_agent/
    │   ├── __init__.py
    │   └── agent.py       # 您的代理程式碼（請參閱「代理範例」分頁）
    ├── main.py            # FastAPI 應用程式進入點
    ├── requirements.txt   # Python 相依性
    └── Dockerfile         # 容器建置說明
    ```

    在 `your-project-directory/` 的根目錄中建立以下檔案（`main.py`、`requirements.txt`、`Dockerfile`）。

    #### 程式碼檔案

    1. 此檔案使用 ADK 的 `get_fast_api_app()` 設定 FastAPI 應用程式：

        ```python title="main.py"
        import os

        import uvicorn
        from google.adk.cli.fast_api import get_fast_api_app

        # 取得 main.py 所在的目錄
        AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
        # 範例會話服務 URI（例如，SQLite）
        SESSION_SERVICE_URI = "sqlite:///./sessions.db"
        # 範例 CORS 允許的來源
        ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
        # 如果您打算提供網頁介面，請設定 web=True，否則設定為 False
        SERVE_WEB_INTERFACE = True

        # 呼叫函式以取得 FastAPI 應用程式實例
        # 確保代理目錄名稱（'capital_agent'）與您的代理資料夾相符
        app = get_fast_api_app(
            agents_dir=AGENT_DIR,
            session_service_uri=SESSION_SERVICE_URI,
            allow_origins=ALLOWED_ORIGINS,
            web=SERVE_WEB_INTERFACE,
        )

        # 您可以在下方新增更多 FastAPI 路由或設定
        # 範例：
        # @app.get("/hello")
        # async def read_root():
        #     return {"Hello": "World"}

        if __name__ == "__main__":
            # 使用 Cloud Run 提供的 PORT 環境變數，預設為 8080
            uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
        ```

        *注意：我們將 `agent_dir` 指定為 `main.py` 所在的目錄，並使用 `os.environ.get("PORT", 8080)` 以與 Cloud Run 相容。*

    2. 列出必要的 Python 套件：

        ```txt title="requirements.txt"
        google_adk
        # 新增您的代理所需的任何其他相依性
        ```

    3. 定義容器映像檔：

        ```dockerfile title="Dockerfile"
        FROM python:3.13-slim
        WORKDIR /app

        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        RUN adduser --disabled-password --gecos "" myuser && \
            chown -R myuser:myuser /app

        COPY . .

        USER myuser

        ENV PATH="/home/myuser/.local/bin:$PATH"

        CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
        ```

    #### 定義多個代理

    您可以在同一個 Cloud Run 實例中定義和部署多個代理，方法是在 `your-project-directory/` 的根目錄中建立不同的資料夾。每個資料夾代表一個代理，且必須在其設定中定義一個 `root_agent`。

    範例結構：

    ```txt
    your-project-directory/
    ├── capital_agent/
    │   ├── __init__.py
    │   └── agent.py       # 包含 `root_agent` 定義
    ├── population_agent/
    │   ├── __init__.py
    │   └── agent.py       # 包含 `root_agent` 定義
    └── ...
    ```

    #### 使用 `gcloud` 部署

    在您的終端機中，導覽至 `your-project-directory`。

    ```bash
    gcloud run deploy capital-agent-service \
    --source . \
    --region $GOOGLE_CLOUD_LOCATION \
    --project $GOOGLE_CLOUD_PROJECT \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
    # 新增您的代理可能需要的任何其他必要環境變數
    ```

    * `capital-agent-service`：您想為 Cloud Run 服務指定的名稱。
    * `--source .`：告訴 gcloud 從目前目錄中的 Dockerfile 建置容器映像檔。
    * `--region`：指定部署地區。
    * `--project`：指定 GCP 專案。
    * `--allow-unauthenticated`：允許公開存取服務。對於私有服務，請移除此旗標。
    * `--set-env-vars`：將必要的環境變數傳遞給正在執行的容器。請確保您包含 ADK 和您的代理所需的所有變數（例如，如果未使用應用程式預設憑證，則為 API 金鑰）。

    `gcloud` 會建置 Docker 映像檔，將其推送到 Google Artifact Registry，然後部署到 Cloud Run。完成後，它會輸出您已部署服務的 URL。

    如需完整的部署選項列表，請參閱 [`gcloud run deploy` 參考文件](https://cloud.google.com/sdk/gcloud/reference/run/deploy)。


=== "Java - gcloud CLI"

    ### gcloud CLI

    您可以使用標準的 `gcloud run deploy` 指令和 `Dockerfile` 來部署 Java 代理。這是目前建議將 Java 代理部署到 Google Cloud Run 的方法。

    請確保您已向 Google Cloud [進行驗證](https://cloud.google.com/docs/authentication/gcloud)。
    具體來說，請在您的終端機中執行 `gcloud auth login` 和 `gcloud config set project <your-project-id>` 指令。

    #### 專案結構

    將您的專案檔案組織如下：

    ```txt
    your-project-directory/
    ├── src/
    │   └── main/
    │       └── java/
    │             └── agents/
    │                 ├── capitalagent/
    │                     └── CapitalAgent.java    # 您的代理程式碼
    ├── pom.xml                                    # Java adk 和 adk-dev 相依性
    └── Dockerfile                                 # 容器建置說明
    ```

    在您專案的根目錄中建立 `pom.xml` 和 `Dockerfile`。您的代理程式碼檔案（`CapitalAgent.java`）如上所示，放在目錄中。

    #### 程式碼檔案

    1. 這是我們的代理定義。此程式碼與 [LLM 代理](agents-llm-agents.md) 中的程式碼相同，但有兩個注意事項：
       
           * 代理現在被初始化為**全域公共靜態變數**。
    
           * 代理的定義可以在靜態方法中公開，或在宣告時內嵌。

        ```java title="CapitalAgent.java"
        --8<-- "examples/java/cloud-run/src/main/java/demo/agents/capitalagent/CapitalAgent.java:full_code"
        ```

    2. 將以下相依性和外掛程式新增至 pom.xml 檔案。

        ```xml title="pom.xml"
        <dependencies>
          <dependency>
             <groupId>com.google.adk</groupId>
             <artifactId>google-adk</artifactId>
             <version>0.1.0</version>
          </dependency>
          <dependency>
             <groupId>com.google.adk</groupId>
             <artifactId>google-adk-dev</artifactId>
             <version>0.1.0</version>
          </dependency>
        </dependencies>
        
        <plugin>
          <groupId>org.codehaus.mojo</groupId>
          <artifactId>exec-maven-plugin</artifactId>
          <version>3.2.0</version>
          <configuration>
            <mainClass>com.google.adk.web.AdkWebServer</mainClass>
            <classpathScope>compile</classpathScope>
          </configuration>
        </plugin>
        ```

    3.  定義容器映像檔：

        ```dockerfile title="Dockerfile"
        --8<-- "examples/java/cloud-run/Dockerfile"
        ```

    #### 使用 `gcloud` 部署

    在您的終端機中，導覽至 `your-project-directory`。

    ```bash
    gcloud run deploy capital-agent-service \
    --source . \
    --region $GOOGLE_CLOUD_LOCATION \
    --project $GOOGLE_CLOUD_PROJECT \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
    # 新增您的代理可能需要的任何其他必要環境變數
    ```

    * `capital-agent-service`：您想為 Cloud Run 服務指定的名稱。
    * `--source .`：告訴 gcloud 從目前目錄中的 Dockerfile 建置容器映像檔。
    * `--region`：指定部署地區。
    * `--project`：指定 GCP 專案。
    * `--allow-unauthenticated`：允許公開存取服務。對於私有服務，請移除此旗標。
    * `--set-env-vars`：將必要的環境變數傳遞給正在執行的容器。請確保您包含 ADK 和您的代理所需的所有變數（例如，如果未使用應用程式預設憑證，則為 API 金鑰）。

    `gcloud` 會建置 Docker 映像檔，將其推送到 Google Artifact Registry，然後部署到 Cloud Run。完成後，它會輸出您已部署服務的 URL。

    如需完整的部署選項列表，請參閱 [`gcloud run deploy` 參考文件](https://cloud.google.com/sdk/gcloud/reference/run/deploy)。



## 測試您的代理

一旦您的代理部署到 Cloud Run，您可以透過已部署的 UI（如果已啟用）或直接使用 `curl` 等工具與其 API 端點互動。您需要部署後提供的服務 URL。

=== "UI 測試"

    ### UI 測試

    如果您部署的代理啟用了 UI：

    *   **adk CLI：** 您在部署期間包含了 `--with_ui` 旗標。
    *   **gcloud CLI：** 您在 `main.py` 中設定了 `SERVE_WEB_INTERFACE = True`。

    您可以透過在網頁瀏覽器中導覽至部署後提供的 Cloud Run 服務 URL 來測試您的代理。

    ```bash
    # 範例 URL 格式
    # https://your-service-name-abc123xyz.a.run.app
    ```

    ADK 開發 UI 可讓您直接在瀏覽器中與您的代理互動、管理會話並檢視執行詳細資訊。

    若要驗證您的代理是否如預期般運作，您可以：

    1. 從下拉式選單中選取您的代理。
    2. 輸入訊息並驗證您是否收到代理的預期回應。

    如果您遇到任何非預期行為，請檢查 [Cloud Run](https://console.cloud.google.com/run) 主控台日誌。

=== "API 測試 (curl)"

    ### API 測試 (curl)

    您可以使用 `curl` 等工具與代理的 API 端點互動。這對於程式化互動或如果您部署時未包含 UI 很有用。

    您需要部署後提供的服務 URL，如果您的服務未設定為允許未經驗證的存取，則可能還需要身分權杖以進行驗證。

    #### 設定應用程式 URL

    請將範例 URL 取代為您已部署的 Cloud Run 服務的實際 URL。

    ```bash
    export APP_URL="YOUR_CLOUD_RUN_SERVICE_URL"
    # 範例：export APP_URL="https://adk-default-service-name-abc123xyz.a.run.app"
    ```

    #### 取得身分權杖（如果需要）

    如果您的服務需要驗證（即您未使用 `gcloud` 的 `--allow-unauthenticated` 或對 `adk` 的提示回答 'N'），請取得身分權杖。

    ```bash
    export TOKEN=$(gcloud auth print-identity-token)
    ```

    *如果您的服務允許未經驗證的存取，您可以從下方的 `curl` 指令中省略 `-H "Authorization: Bearer $TOKEN"` 標頭。*

    #### 列出可用的應用程式

    驗證已部署的應用程式名稱。

    ```bash
    curl -X GET -H "Authorization: Bearer $TOKEN" $APP_URL/list-apps
    ```

    *（如果需要，請根據此輸出調整以下指令中的 `app_name`。預設值通常是代理目錄名稱，例如 `capital_agent`）*。

    #### 建立或更新會話

    為特定使用者和會話初始化或更新狀態。如果不同，請將 `capital_agent` 取代為您實際的應用程式名稱。值 `user_123` 和 `session_abc` 是範例識別碼；您可以將它們取代為您想要的使用者和會話 ID。

    ```bash
    curl -X POST -H "Authorization: Bearer $TOKEN" \
        $APP_URL/apps/capital_agent/users/user_123/sessions/session_abc \
        -H "Content-Type: application/json" \
        -d '{"state": {"preferred_language": "English", "visit_count": 5}}'
    ```

    #### 執行代理

    向您的代理傳送提示。請將 `capital_agent` 取代為您的應用程式名稱，並根據需要調整使用者/會話 ID 和提示。

    ```bash
    curl -X POST -H "Authorization: Bearer $TOKEN" \
        $APP_URL/run_sse \
        -H "Content-Type: application/json" \
        -d '{
        "app_name": "capital_agent",
        "user_id": "user_123",
        "session_id": "session_abc",
        "new_message": {
            "role": "user",
            "parts": [{
            "text": "What is the capital of Canada?"
            }]
        },
        "streaming": false
        }'
    ```

    * 如果您想接收伺服器發送事件 (SSE)，請設定 `"streaming": true`。
    * 回應將包含代理的執行事件，包括最終答案。
