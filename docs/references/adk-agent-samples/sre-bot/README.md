# SRE 助理代理

一個由 Google Agent Development Kit (ADK) 驅動的助理，旨在協助網站可靠性工程師 (SRE) 處理營運任務和監控，特別是專注於 Kubernetes 的互動。

![成本報告示範](https://github.com/serkanh/static-files/blob/main/gifs/cost-reporting-demo.gif?raw=true)

![Kubernetes 示範](https://github.com/serkanh/static-files/blob/main/gifs/eks-cluster-demo.gif?raw=true)

## 總覽

本儲存庫包含一個使用 Google 的 Agent Development Kit (ADK) 建置的 SRE 助理代理。它旨在透過自動化常見任務、提供系統洞察以及透過自然語言對話簡化事件回應來協助 SRE。該代理利用 Google 的大型語言模型來理解使用者查詢，並透過定義的函式和子代理與各種監控、營運和雲端服務工具互動。

## 功能

SRE 助理包括用於與以下項目互動的工具和子代理：

- **Kubernetes 叢集：**
  - 列出所有命名空間或特定命名空間中的資源（命名空間、部署、Pod、服務、密鑰、DaemonSet、ConfigMap）。
  - 取得有關特定部署和 Pod 的詳細資訊。
  - 擴展部署。
  - 從 Pod 擷取日誌。
  - 取得資源健康資訊。
  - 擷取叢集事件。
- **AWS 服務與成本管理：**
  - **AWS Core MCP 代理**：提供與核心 AWS 服務進行一般互動的功能（具體工具的詳細資訊將在開發後新增）。
  - **AWS 成本分析 MCP 代理**：提供用於查詢和分析 AWS 成本和使用情況資料的工具和函式（具體工具的詳細資訊將在開發後新增）。
  - **AWS 成本代理**：一個專門用於深入 AWS 成本分析、報告和提供洞察的子代理。

## 先決條件

- Python 3.10+（如 `Dockerfile` 中所定義）
- Docker 和 Docker Compose
- 用於存取 Gemini 的 Google API 金鑰 (https://aistudio.google.com/apikey)
- 機器人需要與之互動的任何系統的存取憑證/設定：
    - 已設定的 `kubectl` 對您 Kubernetes 叢集的存取權 (`~/.kube/config`)。
    - *（可選）* 已設定的 AWS 憑證 (`~/.aws/credentials` 和 `~/.aws/config`)（如果使用 AWS 工具）。
- 必要的 Python 套件（請參閱 `agent_root/requirements.txt`）：
    - `google-adk`
    - `kubernetes>=28.1.0`
    - `python-dateutil>=2.8.2`
    - `litellm>=1.63.11`（專有模型整合所需）
    - `boto3==1.38.7`（AWS 服務和 Bedrock 模型所需）
    - `ruff`（用於格式化和程式碼檢查）
    - `aiohttp>=3,<4`
    *（新增其他必要的套件）*
- 開發用：
    - `pre-commit`（用於執行 pre-commit 掛鉤）

## 安裝（本地開發 - 可選）

雖然建議透過 Docker 執行，但您也可以設定本地環境：

1.  複製此儲存庫：
    ```bash
    # 以您的實際儲存庫 URL 取代
    git clone https://github.com/your-username/sre-bot.git
    cd sre-bot
    ```
2.  建立並啟動虛擬環境：
    ```bash
    python -m venv venv
    source venv/bin/activate  # 在 Windows 上使用 `venv\Scripts\activate`
    ```
3.  安裝必要的依賴項：
    ```bash
    pip install -r agent_root/requirements.txt
    ```

4.  對於開發，請安裝額外的依賴項：
    ```bash
    pip install -r requirements-dev.txt
    ```

5.  設定 pre-commit 掛鉤：
    ```bash
    pre-commit install
    ```

6.  設定您的 Google API 金鑰：
    ```bash
    export GOOGLE_API_KEY="your-api-key"
    ```

7.  確保 `kubectl` 已正確設定，且任何必要的 AWS 設定檔都已設定。

## 使用方式（建議使用 Docker）

### 使用 Docker 執行

應用程式設計為使用 Docker 和 Docker Compose 執行，以簡化依賴管理和環境設定。

1. 設定必要的環境變數：
    ```bash
    # 強制性
    export GOOGLE_API_KEY="your-api-key"
    
    # 可選：用於存取 Anthropic Claude 模型
    export ANTHROPIC_API_KEY="your-anthropic-api-key"

    # 可選：指定要使用的 Kubernetes 上下文（如果與預設不同）
    # 注意：應用程式程式碼必須明確使用此變數。
    export KUBE_CONTEXT="your-kube-context-name"

    # 可選：指定要使用的 AWS 設定檔（如果使用 AWS 工具）
    # 注意：應用程式程式碼必須明確使用此變數，否則將套用 AWS SDK 預設值。
    export AWS_PROFILE="your-aws-profile-name"
    ```

2. 建置並啟動容器：
    ```bash
    docker-compose build
    docker-compose up -d
    ```
    預設情況下，這將啟動 `sre-bot` 服務（網頁介面）。

3. 在 `http://localhost:8000` 存取網頁介面。ADK 識別的應用程式名稱可能對應於 `agent_root` 目錄。

4. `docker-compose.yml` 檔案掛載：
    - `~/.kube` 到容器內的 `/home/root/.kube`（唯讀），以允許 `kubectl` 存取。容器內的 `KUBECONFIG` 環境變數設定為 `/home/root/.kube/config`。
    - `~/.aws` 到容器內的 `/home/root/.aws`（唯讀），以允許 AWS 工具存取。

5. 若要停止容器：
    ```bash
    docker-compose down
    ```

6. 若要執行 API 伺服器而非網頁 UI：
    ```bash
    # 確保 'sre-bot-api' 服務在 docker-compose.yml 中已定義
    docker-compose up -d sre-bot-api
    ```
    API 將可在 `http://localhost:8001` 存取。有關範例 `curl` 指令，請參閱 ADK 文件或先前的「使用方式」部分（如有必要，請調整應用程式名稱路徑，例如 `/apps/agent_root/...`）。


若要以 API 模式執行代理，請使用以下指令：

```bash
adk api
```

若要以 API 模式測試代理，請先使用以下指令建立一個新會話：

```
curl -X POST http://0.0.0.0:8001/apps/agent_root/users/u_123/sessions/s_123 -H "Content-Type: application/json" -d '{"state": {"key1": "value1", "key2": 42}}'
```
然後使用以下指令向代理發送訊息：

```
curl -X POST http://0.0.0.0:8001/run \
-H "Content-Type: application/json" \
-d '{
"app_name": "agent_root",
"user_id": "u_123",
"session_id": "s_123",
"new_message": {
    "role": "user",
    "parts": [{
    "text": "預設命名空間中有多少個 pod 正在執行？"
    }]
}
}'
```

### 執行 Slack 機器人

本儲存庫還包含一個 Slack 機器人整合，允許使用者直接從 Slack 與代理互動：

1. 確保您已按照下文「建立 Slack 應用程式」一節中的說明設定 Slack 應用程式。

2. 在 `slack_bot` 目錄中使用您的 Slack 憑證設定 `.env` 檔案：
   ```
   SLACK_BOT_TOKEN=xoxb-your-token
   SLACK_SIGNING_SECRET=your-signing-secret
   BOT_PREFIX=your-bot-name
   ```

3. 啟動 Slack 機器人容器：
   ```bash
   docker-compose up -d slack-bot
   ```

4. Slack 機器人將可在 `http://localhost:8002` 存取。

5. 對於外部存取，請按照「設定」一節中的說明設定 ngrok。

### 疑難排解

如果您遇到服務之間的通訊逾時（例如，slack-bot 和 sre-bot-api 之間）：

1. 檢查所有容器是否正在執行：
   ```bash
   docker-compose ps
   ```
   
2. 驗證容器之間的網路連線：
   ```bash
   docker network inspect $(docker network ls --filter name=sre-bot --format "{{.Name}}")
   ```

3. 檢查特定容器的日誌：
   ```bash
   docker-compose logs slack-bot
   docker-compose logs sre-bot-api
   ```

4. 確保 API 端點在 Slack 機器人程式碼中已正確設定。

### 本地執行（如果已遵循安裝步驟）

您或許可以使用 ADK CLI 在本地執行代理。應用程式名稱可能衍生自目錄結構 (`agent_root`)。

```bash
# 從專案根目錄
adk web agent_root
# 或可能
adk web
```

*由於先前遇到的潛在路徑和發現問題，本地執行可能較不可靠。*

## 程式碼格式化與檢查 (Ruff)

本專案使用 Ruff 進行程式碼格式化和檢查（遵循 PEP 8）。

1. 確保已安裝 Ruff（透過 `pip install -r requirements-dev.txt`）。
2. 檢查問題：
   ```bash
   ruff check .
   ```
3. 格式化程式碼：
   ```bash
   ruff format .
   ```
4. 檢查並自動修正問題：
   ```bash
   ruff check . --fix
   ```

從專案的根目錄執行這些指令。設定在 `pyproject.toml` 中。

### Pre-commit 掛鉤

本專案使用 pre-commit 掛鉤以在提交變更前確保程式碼品質。掛鉤在 `.pre-commit-config.yaml` 中設定。

1. 如果您尚未安裝 pre-commit，請先安裝：
   ```bash
   pip install pre-commit
   ```

2. 設定掛鉤：
   ```bash
   pre-commit install
   ```

3. 當您提交變更時，掛鉤將自動執行。目前，掛鉤包括：
   - Ruff 格式化：自動格式化您的程式碼
   - Ruff 檢查：檢查程式碼問題並在可能時修正它們

4. 若要手動對所有檔案執行掛鉤：
   ```bash
   pre-commit run --all-files
   ```

5. 若要執行特定掛鉤：
   ```bash
   pre-commit run ruff-format
   ```

## 結構

- `agents/`
  - `sre_agent/`
    - `agent.py`：包含主要的 SRE 代理邏輯（ADK 應用程式定義、`root_agent`）和子代理的初始化。
    - `kube_agent.py`：定義 Kubernetes 子代理及其工具。
    - `aws_mcps.py`：（假設位置）定義 AWS Core MCP 和 AWS 成本分析 MCP 代理/工具。
    - `aws_cost_agent.py`：（假設位置）定義專門的 AWS 成本代理。
    - `settings.py`：設定（例如，`DB_URL`）。
    - `json_utils.py`：自訂 JSON 工具。
    - `__init__.py`
  - `__init__.py`
- `slack_bot/`
  - `main.py`：主要的 Slack 機器人實作。
  - `modules/`：Slack 機器人的輔助模組（例如，`health.py`）。
  - `requirements.txt`：Slack 機器人的 Python 依賴項。
  - `Dockerfile`：用於建置 Slack 機器人容器的說明。
  - `.env.example`：Slack 機器人的範例環境變數。
- `docker-compose.yml`：用於執行服務的 Docker Compose 設定。
- `Dockerfile`：用於建置 SRE Bot API Docker 映像的說明。
- `requirements-dev.txt`：開發特定的 Python 依賴項。
- `pyproject.toml`：Ruff（檢查/格式化）和其他 Python 工具的設定。
- `.pre-commit-config.yaml`：pre-commit 掛鉤的設定。
- `.gitignore`：指定 Git 應忽略的故意未追蹤的檔案。
- `README.md`：本文件檔案。

## 可用函式與功能

### Kubernetes 工具

以下函式在 `agents/sre_agent/kube_agent.py`（或類似檔案）中定義，並可透過 `kubernetes_agent` 使用：

- `list_namespaces()`
- `list_deployments_from_namespace(namespace: str)`
- `list_deployments_all_namespaces()`
- `list_pods_from_namespace(namespace: str)`
- `list_pods_all_namespaces()`
- `list_services_from_namespace(namespace: str)`
- `list_secrets_from_namespace(namespace: str)`
- `list_daemonsets_from_namespace(namespace: str)`
- `list_configmaps_from_namespace(namespace: str)`
- `list_all_resources(namespace: str)`
- `get_deployment_details(namespace: str, deployment_name: str)`
- `get_pod_details(namespace: str, pod_name: str)`
- `scale_deployment(namespace: str, deployment_name: str, replicas: int)`
- `get_pod_logs(namespace: str, pod_name: str, tail_lines: int = 50)`
- `get_resource_health(namespace: str, resource_type: str, resource_name: str)`
- `get_events(namespace: str)`
- `get_events_all_namespaces()`

### AWS Core MCP 功能（示意性）

*（由 `aws_core_mcp_agent` 提供用於與各種 AWS 服務互動的工具。具體函式將在開發和公開後在此處列出。範例可能包括與 EC2、S3、IAM 等互動。）*

### AWS 成本分析 MCP 與代理功能（示意性）

*（由 `aws_cost_analysis_mcp_agent` 和 `aws_cost_agent` 提供用於查詢 AWS 成本和使用情況、產生報告以及提供成本優化洞察的工具和功能。具體函式/功能將在此處列出，例如 `get_monthly_cost_summary`、`analyze_service_costs_by_tag`。）*

# 建立 Slack 應用程式：
1. 前往 https://api.slack.com/apps 並點擊「建立新應用程式」
2. 為其命名並選擇一個工作區
3. 新增範圍
    - 前往「OAuth 與權限」
    - 在「機器人權杖範圍」下，新增權限。對於此應用程式，我們至少需要 `app_mentions:read`，它允許我們的應用程式查看直接提及我們機器人的訊息，以及 `chat:write`，它允許我們的應用程式發送訊息
4. 滾動到「OAuth 與權限」頁面頂部，然後點擊「將應用程式安裝到工作區」
5. 應用程式需要由工作區擁有者批准。


範例應用程式清單：

```yaml
display_information:
  name: sre-bot
features:
  bot_user:
    display_name: sre-bot
    always_online: false
  slash_commands:
    - command: /sre-bot:scale
      url: http://<ngrok-url>.ngrok-free.app/slack/events
      description: "sre-bot scale "
      should_escape: false
oauth_config:
  scopes:
    user:
      - reactions:read
    bot:
      - app_mentions:read
      - channels:join
      - channels:history
      - chat:write
      - chat:write.customize
      - commands
      - groups:history
      - im:write
      - chat:write.public
      - reactions:read
      - mpim:history
      - im:history
settings:
  event_subscriptions:
    request_url: http://<ngrok-url>.ngrok-free.app/slack/events
    bot_events:
      - reaction_added
  interactivity:
    is_enabled: true
    request_url: http://<ngrok-url>.ngrok-free.app/slack/events
  org_deploy_enabled: false
  socket_mode_enabled: false
  token_rotation_enabled: false


```

# 設定

安裝 [ngrok](https://ngrok.com)

在應用程式資料夾內透過 docker-compose 啟動應用程式。
`docker compose up`

本地公開的埠是 80，所以我們將讓 ngrok 指向該埠

`ngrok http 80`

## 安全注意事項

此代理可能需要存取敏感系統和資料（Kubernetes 叢集，可能還有 AWS）。請確保：
1.  適當的憑證和 API 金鑰得到安全管理（例如，使用像 `GOOGLE_API_KEY` 這樣的環境變數，依賴掛載的 `~/.kube/config` 和 `~/.aws/credentials`）。
2.  遵循最小權限原則 – 代理應僅擁有在 Kubernetes 和/或 AWS 中執行其定義任務所必需的權限。
3.  網路存取和設定是安全的。
4.  定期審查稽核日誌。

## 會話和使用者 ID 管理

此系統根據使用者與 SRE Bot 互動的方式，以不同方式處理使用者會話和 ID。所有會話資料最終都儲存在為 `sre-agent` 設定的 PostgreSQL 資料庫中。

### 1. 透過 Slack 的互動

當使用者透過 Slack 與 SRE Bot 互動時：

1.  **初始訊息**：`slack_bot`（特別是 `slack_bot/main.py`）接收訊息。
2.  **會話建立（Slack 機器人端）**：
    *   `slack_bot/main.py` 中的 `SessionManager` 建立或擷取一個 `ConversationSession`。
    *   為 Slack 使用者唯一產生一個 `user_id`（例如，`u_{slack_user_id}`）。
    *   根據 Slack 頻道和執行緒時間戳記產生一個 `session_id`（例如，`s_{channel_id}_{thread_ts_or_timestamp}`）。這確保了 Slack 執行緒內的對話連續性。
3.  **API 會話建立（SRE 代理）**：
    *   在處理使用者查詢之前，`slack_bot` 向 `http://sre-bot-api:8000/apps/sre_agent/users/{session.user_id}/sessions/{session.session_id}` 等端點發出 `POST` 請求。
    *   此請求透過 `agents/sre_agent/agent.py` 中的 `DatabaseSessionService` 在 PostgreSQL 資料庫中明確建立一個會話記錄。酬載包括一個包含 Slack 特定上下文（頻道、執行緒、Slack 使用者）的初始狀態。
    *   如果資料庫中已存在該會話，此步驟將確認其可用性。
4.  **查詢處理**：
    *   然後 `slack_bot` 將使用者的訊息發送到 `http://sre-bot-api:8000/run` 端點。
    *   此 `/run` 端點的酬載包括：
        *   `app_name`：「sre_agent」
        *   `user_id`：由 Slack 機器人產生的 `user_id`（例如，`u_{slack_user_id}`）。
        *   `session_id`：由 Slack 機器人產生的 `session_id`（例如，`s_{channel_id}_{thread_ts_or_timestamp}`）。
        *   `new_message`：使用者的查詢。
5.  **SRE 代理處理 (ADK)**：
    *   驅動 `agents/sre_agent/agent.py` 的 ADK 框架接收這些參數。
    *   `DatabaseSessionService` 使用 API 請求中提供的 `app_name`、`user_id` 和 `session_id` 從資料庫載入此互動的相關會話資料。任何狀態變更或對話歷史更新都會儲存回此特定的會話記錄。

### 2. 透過本地 Web UI / 直接 API 呼叫的互動

在本地與 SRE Bot 互動時（例如，透過開發 Web UI 或直接 API 呼叫，而不是透過 Slack 機器人）：

1.  **API 請求**：客戶端（Web UI 或工具）預期會向 SRE Bot API（例如，`/run` 端點）發出請求。
    *   **建議**：客戶端應管理自己的使用者和會話識別碼，並在 API 酬載中包含 `app_name`、`user_id` 和 `session_id`，類似於 Slack 機器人的做法。
        *   如果提供了這些，`agents/sre_agent/agent.py` 中的 `DatabaseSessionService` 將使用它們從資料庫建立或擷取會話。如果會話不存在，客戶端也將負責初始呼叫以建立會話（例如，`/apps/{app_name}/users/{user_id}/sessions/{session_id}`）。
    *   **備用 / `agent.py` 直接執行**：
        *   如果直接執行 `agents/sre_agent/agent.py`（例如，`python agents/sre_agent/agent.py`，這會觸發 `if __name__ == "__main__":` 區塊），或者如果對 `/run` 的 API 呼叫因故未提供特定的使用者/會話 ID，且系統回退到 `get_or_create_session` 中的預設值：
            *   將使用 `agents/sre_agent/agent.py` 頂部定義的預設 `APP_NAME = "sre_agent"` 和 `USER_ID = "test_user"`。
            *   將叫用 `agents/sre_agent/agent.py` 中的 `get_or_create_session()` 函式。
            *   它將使用這些預設的 `APP_NAME` 和 `USER_ID` 與 `DatabaseSessionService`。
            *   如果資料庫中不存在此預設 `APP_NAME`/`USER_ID` 的會話，則會使用由 `DatabaseSessionService` 自動產生的新的基於 UUID 的 `session_id` 建立一個新會話。初始狀態是通用的。
            *   後續使用這些預設值的互動將重複使用此會話。

總之，API 請求酬載中的 `user_id` 和 `session_id` 優先。`agents/sre_agent/agent.py` 中的預設值主要用於腳本在不涉及帶有這些參數的傳入 API 請求的上下文中執行的情況（如直接執行腳本或某些 ADK CLI 互動）。
