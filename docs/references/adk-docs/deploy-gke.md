# 部署至 GKE

[GKE](https://cloud.google.com/gke) 是 Google Cloud 的代管 Kubernetes 服務。它可讓您使用 Kubernetes 部署和管理容器化應用程式。

若要部署您的代理，您需要在 GKE 上執行一個 Kubernetes 叢集。您可以使用 Google Cloud Console 或 `gcloud` 命令列工具建立叢集。

在此範例中，我們將部署一個簡單的代理至 GKE。此代理將是一個 FastAPI 應用程式，使用 `Gemini 2.0 Flash` 作為大型語言模型 (LLM)。我們可以使用環境變數 `GOOGLE_GENAI_USE_VERTEXAI` 來將 Vertex AI 或 AI Studio 作為 LLM 提供者。

## 環境變數

如 [設定與安裝](get-started-installation.md) 指南中所述，設定您的環境變數。您還需要安裝 `kubectl` 命令列工具。您可以在 [Google Kubernetes Engine 文件](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl) 中找到相關說明。

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id # 您的 GCP 專案 ID
export GOOGLE_CLOUD_LOCATION=us-central1 # 或您偏好的地區
export GOOGLE_GENAI_USE_VERTEXAI=true # 如果使用 Vertex AI，請設為 true
export GOOGLE_CLOUD_PROJECT_NUMBER=$(gcloud projects describe --format json $GOOGLE_CLOUD_PROJECT | jq -r ".projectNumber")
```

如果您未安裝 `jq`，可以使用以下指令取得專案編號：

```bash
gcloud projects describe $GOOGLE_CLOUD_PROJECT
```

並從輸出中複製專案編號。

```bash
export GOOGLE_CLOUD_PROJECT_NUMBER=YOUR_PROJECT_NUMBER
```



## 啟用 API 和權限

請確保您已向 Google Cloud 進行驗證（`gcloud auth login` 和 `gcloud config set project <your-project-id>`）。

為您的專案啟用必要的 API。您可以使用 `gcloud` 命令列工具來執行此操作。

```bash
gcloud services enable \
    container.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com
```

將 `gcloud builds submit` 指令所需的必要角色授予預設的運算引擎服務帳戶。



```bash
ROLES_TO_ASSIGN=(
    "roles/artifactregistry.writer"
    "roles/storage.objectViewer"
    "roles/logging.viewer"
    "roles/logging.logWriter"
)

for ROLE in "${ROLES_TO_ASSIGN[@]}"; do
    gcloud projects add-iam-policy-binding "${GOOGLE_CLOUD_PROJECT}" \
        --member="serviceAccount:${GOOGLE_CLOUD_PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="${ROLE}"
done
```

## 部署選項

您可以選擇**手動使用 Kubernetes 清單**或**自動使用 `adk deploy gke` 指令**將您的代理部署到 GKE。請選擇最適合您工作流程的方法。


## 選項 1：使用 gcloud 和 kubectl 手動部署

### 建立 GKE 叢集

您可以使用 `gcloud` 命令列工具建立 GKE 叢集。此範例會在 `us-central1` 地區建立一個名為 `adk-cluster` 的 Autopilot 叢集。

> 如果建立 GKE Standard 叢集，請確保已啟用 [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)。Workload Identity 在 AutoPilot 叢集中預設為啟用。

```bash
gcloud container clusters create-auto adk-cluster \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

建立叢集後，您需要使用 `kubectl` 連接到它。此指令會設定 `kubectl` 以使用您新叢集的憑證。

```bash
gcloud container clusters get-credentials adk-cluster \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

### 建立您的代理

我們將參考 [LLM 代理](agents-llm-agents.md) 頁面上定義的 `capital_agent` 範例。

若要繼續，請將您的專案檔案組織如下：

```txt
your-project-directory/
├── capital_agent/
│   ├── __init__.py
│   └── agent.py       # 您的代理程式碼（請參閱下方的「Capital Agent 範例」）
├── main.py            # FastAPI 應用程式進入點
├── requirements.txt   # Python 相依性
└── Dockerfile         # 容器建置說明
```



### 程式碼檔案

在 `your-project-directory/` 的根目錄中建立以下檔案（`main.py`、`requirements.txt`、`Dockerfile`、`capital_agent/agent.py`、`capital_agent/__init__.py`）。

1. 這是 `capital_agent` 目錄中的 Capital Agent 範例

    ```python title="capital_agent/agent.py"
    from google.adk.agents import LlmAgent 

    # 定義一個工具函式
    def get_capital_city(country: str) -> str:
      """擷取指定國家的首都。"""
      # 以實際邏輯取代（例如，API 呼叫、資料庫查詢）
      capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
      return capitals.get(country.lower(), f"抱歉，我不知道 {country} 的首都。")

    # 將工具新增至代理
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent", #您的代理名稱
        description="回答使用者關於指定國家首都的問題。",
        instruction="""您是一個提供國家首都的代理...（先前的指令文字）""",
        tools=[get_capital_city] # 直接提供函式
    )

    # ADK 將會發現 root_agent 實例
    root_agent = capital_agent
    ```
    
    將您的目錄標記為 python 套件

    ```python title="capital_agent/__init__.py"

    from . import agent
    ```

2. 此檔案使用 ADK 的 `get_fast_api_app()` 設定 FastAPI 應用程式：

    ```python title="main.py"
    import os

    import uvicorn
    from fastapi import FastAPI
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
    app: FastAPI = get_fast_api_app(
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

3. 列出必要的 Python 套件：

    ```txt title="requirements.txt"
    google_adk
    # 新增您的代理所需的任何其他相依性
    ```

4. 定義容器映像檔：

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

### 建置容器映像檔

您需要建立一個 Google Artifact Registry 儲存庫來儲存您的容器映像檔。您可以使用 `gcloud` 命令列工具來執行此操作。

```bash
gcloud artifacts repositories create adk-repo \
    --repository-format=docker \
    --location=$GOOGLE_CLOUD_LOCATION \
    --description="ADK repository"
```

使用 `gcloud` 命令列工具建置容器映像檔。此範例會建置映像檔並將其標記為 `adk-repo/adk-agent:latest`。

```bash
gcloud builds submit \
    --tag $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-repo/adk-agent:latest \
    --project=$GOOGLE_CLOUD_PROJECT \
    .
```

驗證映像檔已建置並推送至 Artifact Registry：

```bash
gcloud artifacts docker images list \
  $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-repo \
  --project=$GOOGLE_CLOUD_PROJECT
```

### 為 Vertex AI 設定 Kubernetes 服務帳戶

如果您的代理使用 Vertex AI，您需要建立一個具有必要權限的 Kubernetes 服務帳戶。此範例會建立一個名為 `adk-agent-sa` 的服務帳戶，並將其繫結至 `Vertex AI User` 角色。

> 如果您使用 AI Studio 並使用 API 金鑰存取模型，則可以略過此步驟。

```bash
kubectl create serviceaccount adk-agent-sa
```

```bash
gcloud projects add-iam-policy-binding projects/${GOOGLE_CLOUD_PROJECT} \
    --role=roles/aiplatform.user \
    --member=principal://iam.googleapis.com/projects/${GOOGLE_CLOUD_PROJECT_NUMBER}/locations/global/workloadIdentityPools/${GOOGLE_CLOUD_PROJECT}.svc.id.goog/subject/ns/default/sa/adk-agent-sa \
    --condition=None
```

### 建立 Kubernetes 清單檔案

在您的專案目錄中建立一個名為 `deployment.yaml` 的 Kubernetes 部署清單檔案。此檔案定義如何在 GKE 上部署您的應用程式。

```yaml title="deployment.yaml"
cat <<  EOF > deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: adk-agent
  template:
    metadata:
      labels:
        app: adk-agent
    spec:
      serviceAccount: adk-agent-sa
      containers:
      - name: adk-agent
        imagePullPolicy: Always
        image: $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-repo/adk-agent:latest
        resources:
          limits:
            memory: "128Mi"
            cpu: "500m"
            ephemeral-storage: "128Mi"
          requests:
            memory: "128Mi"
            cpu: "500m"
            ephemeral-storage: "128Mi"
        ports:
        - containerPort: 8080
        env:
          - name: PORT
            value: "8080"
          - name: GOOGLE_CLOUD_PROJECT
            value: $GOOGLE_CLOUD_PROJECT
          - name: GOOGLE_CLOUD_LOCATION
            value: $GOOGLE_CLOUD_LOCATION
          - name: GOOGLE_GENAI_USE_VERTEXAI
            value: "$GOOGLE_GENAI_USE_VERTEXAI"
          # 如果使用 AI Studio，請將 GOOGLE_GENAI_USE_VERTEXAI 設為 false 並設定以下內容：
          # - name: GOOGLE_API_KEY
          #   value: $GOOGLE_API_KEY
          # 新增您的代理可能需要的任何其他必要環境變數
---
apiVersion: v1
kind: Service
metadata:
  name: adk-agent
spec:       
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8080
  selector:
    app: adk-agent
EOF
```

### 部署應用程式

使用 `kubectl` 命令列工具部署應用程式。此指令會將部署和服務清單檔案套用至您的 GKE 叢集。

```bash
kubectl apply -f deployment.yaml
```

幾分鐘後，您可以使用以下指令檢查部署狀態：

```bash
kubectl get pods -l=app=adk-agent
```

此指令會列出與您部署相關的 pod。您應該會看到一個狀態為 `Running` 的 pod。

一旦 pod 開始執行，您可以使用以下指令檢查服務狀態：

```bash
kubectl get service adk-agent
```

如果輸出顯示 `External IP`，表示您的服務可從網際網路存取。可能需要幾分鐘才能指派外部 IP。

您可以使用以下指令取得服務的外部 IP 位址：

```bash
kubectl get svc adk-agent -o=jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

## 選項 2：使用 `adk deploy gke` 自動部署

ADK 提供了一個 CLI 指令來簡化 GKE 部署。這避免了手動建置映像檔、編寫 Kubernetes 清單或推送到 Artifact Registry 的需要。

#### 先決條件

在開始之前，請確保您已完成以下設定：

1. **一個正在執行的 GKE 叢集：** 您需要在 Google Cloud 上有一個作用中的 Kubernetes 叢集。

2. **`gcloud` CLI：** 必須安裝、驗證 Google Cloud CLI，並將其設定為使用您的目標專案。執行 `gcloud auth login` 和 `gcloud config set project [YOUR_PROJECT_ID]`。

3. **必要的 IAM 權限：** 執行此指令的使用者或服務帳戶至少需要以下角色：

   * **Kubernetes Engine 開發人員** (`roles/container.developer`)：與 GKE 叢集互動。

   * **Artifact Registry 寫入者** (`roles/artifactregistry.writer`)：推送代理的容器映像檔。

4. **Docker：** Docker 精靈必須在您的本機電腦上執行，才能建置容器映像檔。

### `deploy gke` 指令

此指令會取得您代理的路徑和指定目標 GKE 叢集的參數。

#### 語法

```bash
adk deploy gke [OPTIONS] AGENT_PATH
```

### 引數和選項

| 引數 | 說明 | 必要 |
| -------- | ------- | ------  |
| AGENT_PATH | 您代理根目錄的本機檔案路徑。 | 是 |
| --project | 您 GKE 叢集所在的 Google Cloud 專案 ID。 | 是 |
| --cluster_name | 您 GKE 叢集的名稱。 | 是 |
| --region | 您叢集的 Google Cloud 地區（例如，us-central1）。 | 是 |
| --with_ui | 同時部署代理的後端 API 和一個配套的前端使用者介面。 | 否 |
| --verbosity | 設定部署過程的記錄層級。選項：debug、info、warning、error。 | 否 |


### 運作方式
當您執行 `adk deploy gke` 指令時，ADK 會自動執行以下步驟：

- 容器化：它會從您代理的原始碼建置一個 Docker 容器映像檔。

- 映像檔推送：它會標記容器映像檔並將其推送到您專案的 Artifact Registry。

- 清單產生：它會動態產生必要的 Kubernetes 清單檔案（一個 `Deployment` 和一個 `Service`）。

- 叢集部署：它會將這些清單套用至您指定的 GKE 叢集，這會觸發以下操作：

`Deployment` 會指示 GKE 從 Artifact Registry 拉取容器映像檔，並在一個或多個 Pod 中執行它。

`Service` 會為您的代理建立一個穩定的網路端點。預設情況下，這是一個 LoadBalancer 服務，它會佈建一個公開 IP 位址，以將您的代理公開到網際網路。


### 使用範例
這是一個將位於 `~/agents/multi_tool_agent/` 的代理部署到名為 test 的 GKE 叢集的實際範例。

```bash
adk deploy gke \
    --project myproject \
    --cluster_name test \
    --region us-central1 \
    --with_ui \
    --verbosity info \
    ~/agents/multi_tool_agent/
```

### 驗證您的部署
如果您使用 `adk deploy gke`，請使用 `kubectl` 驗證部署：

1. 檢查 Pod：確保您代理的 pod 處於執行中狀態。

```bash
kubectl get pods
```
您應該會在預設命名空間中看到類似 `adk-default-service-name-xxxx-xxxx ... 1/1 Running` 的輸出。

2. 尋找外部 IP：取得您代理服務的公開 IP 位址。

```bash
kubectl get service
NAME                       TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)        AGE
adk-default-service-name   LoadBalancer   34.118.228.70   34.63.153.253   80:32581/TCP   5d20h
```

我們可以導覽至外部 IP 並透過 UI 與代理互動
![GKE Deployment](../assets/agent-gke-deployment.png)

## 測試您的代理

一旦您的代理部署到 GKE，您可以透過已部署的 UI（如果已啟用）或直接使用 `curl` 等工具與其 API 端點互動。您需要部署後提供的服務 URL。

=== "UI 測試"

    ### UI 測試

    如果您部署的代理啟用了 UI：

    您可以透過在網頁瀏覽器中導覽至 kubernetes 服務 URL 來測試您的代理。

    ADK 開發 UI 可讓您直接在瀏覽器中與您的代理互動、管理會話並檢視執行詳細資訊。

    若要驗證您的代理是否如預期般運作，您可以：

    1. 從下拉式選單中選取您的代理。
    2. 輸入訊息並驗證您是否收到代理的預期回應。

    如果您遇到任何非預期行為，請使用以下指令檢查您代理的 pod 日誌：

    ```bash
    kubectl logs -l app=adk-agent
    ```

=== "API 測試 (curl)"

    ### API 測試 (curl)

    您可以使用 `curl` 等工具與代理的 API 端點互動。這對於程式化互動或如果您部署時未包含 UI 很有用。

    #### 設定應用程式 URL

    請將範例 URL 取代為您已部署的 Cloud Run 服務的實際 URL。

    ```bash
    export APP_URL=$(kubectl get service adk-agent -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    ```

    #### 列出可用的應用程式

    驗證已部署的應用程式名稱。

    ```bash
    curl -X GET $APP_URL/list-apps
    ```

    *（如果需要，請根據此輸出調整以下指令中的 `app_name`。預設值通常是代理目錄名稱，例如 `capital_agent`）*。

    #### 建立或更新會話

    為特定使用者和會話初始化或更新狀態。如果不同，請將 `capital_agent` 取代為您實際的應用程式名稱。值 `user_123` 和 `session_abc` 是範例識別碼；您可以將它們取代為您想要的使用者和會話 ID。

    ```bash
    curl -X POST \
        $APP_URL/apps/capital_agent/users/user_123/sessions/session_abc \
        -H "Content-Type: application/json" \
        -d '{"state": {"preferred_language": "English", "visit_count": 5}}'
    ```

    #### 執行代理

    向您的代理傳送提示。請將 `capital_agent` 取代為您的應用程式名稱，並根據需要調整使用者/會話 ID 和提示。

    ```bash
    curl -X POST $APP_URL/run_sse \
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

## 疑難排解

以下是您在將代理部署到 GKE 時可能遇到的一些常見問題：

### 403 `Gemini 2.0 Flash` 的權限遭拒

這通常表示 Kubernetes 服務帳戶沒有存取 Vertex AI API 的必要權限。請確保您已建立服務帳戶並將其繫結至 `Vertex AI User` 角色，如 [為 Vertex AI 設定 Kubernetes 服務帳戶](#configure-kubernetes-service-account-for-vertex-ai) 一節中所述。如果您使用 AI Studio，請確保您已在部署清單中設定 `GOOGLE_API_KEY` 環境變數且其有效。

### 404 或找不到回應

這通常表示您的請求中有錯誤。請檢查應用程式日誌以診斷問題。

```bash

export POD_NAME=$(kubectl get pod -l app=adk-agent -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD_NAME
```

### 嘗試寫入唯讀資料庫

您可能會發現在 UI 中沒有建立會話 ID，且代理對任何訊息都沒有回應。這通常是由於 SQLite 資料庫是唯讀的所致。如果您在本機執行代理，然後建立將 SQLite 資料庫複製到容器中的容器映像檔，就可能發生這種情況。然後資料庫在容器中是唯讀的。

```bash
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) attempt to write a readonly database
[SQL: UPDATE app_states SET state=?, update_time=CURRENT_TIMESTAMP WHERE app_states.app_name = ?]
```

若要修正此問題，您可以：

在建置容器映像檔之前，從您的本機電腦刪除 SQLite 資料庫檔案。這會在容器啟動時建立一個新的 SQLite 資料庫。

```bash
rm -f sessions.db
```

或者（建議）您可以在專案目錄中新增一個 `.dockerignore` 檔案，以排除將 SQLite 資料庫複製到容器映像檔中。

```txt title=".dockerignore"
sessions.db
```

再次建置容器映像檔並部署應用程式。

### 串流日誌權限不足 `ERROR: (gcloud.builds.submit)`

當您沒有足夠的權限來串流建置日誌，或您的 VPC-SC 安全性原則限制存取預設日誌儲存貯體時，可能會發生此錯誤。

若要檢查建置進度，請依照錯誤訊息中提供的連結，或導覽至 Google Cloud Console 中的 Cloud Build 頁面。

您也可以使用 [建置容器映像檔](#build-the-container-image) 一節下的指令來驗證映像檔已建置並推送至 Artifact Registry。

### Gemini-2.0-Flash 在 Live Api 中不受支援

在使用已部署代理的 ADK 開發 UI 時，文字型聊天可以運作，但語音（例如，按一下麥克風按鈕）會失敗。您可能會在 pod 日誌中看到 `websockets.exceptions.ConnectionClosedError`，表示您的模型「在 live api 中不受支援」。

發生此錯誤的原因是代理設定的模型（如此範例中的 `gemini-2.0-flash`）不支援 Gemini Live API。即時、雙向串流音訊和視訊需要 Live API。

## 清理

若要刪除 GKE 叢集和所有相關資源，請執行：

```bash
gcloud container clusters delete adk-cluster \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

若要刪除 Artifact Registry 儲存庫，請執行：

```bash
gcloud artifacts repositories delete adk-repo \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

如果您不再需要該專案，也可以刪除它。這將刪除與該專案相關的所有資源，包括 GKE 叢集、Artifact Registry 儲存庫以及您建立的任何其他資源。

```bash
gcloud projects delete $GOOGLE_CLOUD_PROJECT
```
