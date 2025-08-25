# ADK 代理 (Agent)

此範例使用代理開發套件 (Agent Development Kit, ADK) 來建立一個使用 A2A 進行通訊的簡單日曆更新代理 (Agent)。

## 先決條件

- Python 3.10 或更高版本
- [UV](https://docs.astral.sh/uv/)
- 存取 LLM 和 API 金鑰

## 執行範例

1. 導覽至範例目錄：

```shell
cd samples/python/agents/adk_cloud_run
````

2. 建立包含您的 API 金鑰的環境檔案：

```shell
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

3. 執行一個代理 (Agent)：

```shell
uv run .
```

## 設定 Google Cloud Run 組態

### 建立服務帳戶

Cloud Run 在執行服務執行個體時會使用[服務帳戶 (service accounts, SA)](https://cloud.google.com/run/docs/configuring/service-accounts)。為已部署的 A2A 服務建立一個專屬的服務帳戶。

```shell
gcloud iam service-accounts create a2a-service-account \
  --description="a2a cloud run 服務的服務帳戶" \
  --display-name="A2A cloud run 服務帳戶"
```

### 新增 IAM 存取權限

以下角色允許 Cloud Run 服務存取密鑰並在 Vertex AI 模型上叫用 `predict` API。

```shell
gcloud projects add-iam-policy-binding "{your-project-id}" \
  --member="serviceAccount:a2a-service-account@{your-project-id}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --role="roles/aiplatform.user"
```

如果使用 AlloyDb，也請新增以下 IAM 角色繫結。

```shell
gcloud projects add-iam-policy-binding "{your-project-id}" \
  --member="serviceAccount:a2a-service-account@{your-project-id}.iam.gserviceaccount.com" \
  --role="roles/alloydb.client" \
  --role="roles/serviceusage.serviceUsageConsumer" \
  --role="roles/secretmanager.secretAccessor"
```

### 設定密鑰

所有敏感憑證都應透過安全機制提供給伺服器。Cloud Run 允許將密鑰作為環境變數或動態磁碟區掛載來提供。資料庫使用者和密碼密鑰可以在 Secret Manager 中建立，如下所示：

```shell
gcloud secrets create alloy_db_user --replication-policy="automatic"
# 建立一個 user.txt 檔案，其內容為密鑰值
gcloud secrets versions add alloy_db_user --data-file="user.txt"

gcloud secrets create alloy_db_pass --replication-policy="automatic"
# 建立一個 pass.txt 檔案，其內容為密鑰值
gcloud secrets versions add alloy_db_pass --data-file="pass.txt"
```

## 部署至 Google Cloud Run

A2A Cloud Run 服務可以[公開暴露](https://cloud.google.com/run/docs/authenticating/public)或保持在僅限 GCP 客戶端的內部。

將服務部署到 Cloud Run 時，它會傳回一個 `run.app` URL，用於查詢正在執行的服務。

### 服務驗證

#### 基於 IAM 的驗證

如果客戶端在 GCP 內部，IAM 可用於[服務對服務驗證](https://cloud.google.com/run/docs/authenticating/service-to-service)。Agentspace 就是這樣一個內部客戶端的範例。客戶端可以使用服務帳戶，並且需要被授予 IAM 角色：`roles/run.invoker`

#### 公開存取

A2A 伺服器負責處理代理 (Agent) 層級的驗證。他們需要在其代理卡 (agent card) 中使用 securitySchemes 和 security 參數提供此驗證資訊。

在部署到 Cloud Run 時，請使用 `--allow-unauthenticated` 參數以允許公開存取。

### 使用 `InMemoryTaskStore`

```shell
gcloud run deploy sample-a2a-agent \
    --port=8080 \
    --source=. \
    --no-allow-unauthenticated \
    --memory "1Gi" \
    --region="us-central1" \
    --project="{your-project-id}" \
    --service-account a2a-service-account \
    --set-env-vars=GOOGLE_GENAI_USE_VERTEXAI=true,\
GOOGLE_CLOUD_PROJECT="{your-project-id}",\
GOOGLE_CLOUD_LOCATION="us-central1",\
APP_URL="TEMPORARY_URL"

```

### 使用 AlloyDb

```shell
gcloud run deploy sample-a2a-agent \
    --port=8080 \
    --source=. \
    --no-allow-unauthenticated \
    --memory "1Gi" \
    --region="us-central1" \
    --project="{your-project-id}" \
    --update-secrets=DB_USER=alloy_db_user:latest,DB_PASS=alloy_db_pass:latest \
    --service-account a2a-service-account \
    --set-env-vars=GOOGLE_GENAI_USE_VERTEXAI=true,\
GOOGLE_CLOUD_PROJECT="{your-project-id}",\
GOOGLE_CLOUD_LOCATION="us-central1",\
USE_ALLOY_DB="True",\
DB_INSTANCE="projects/{your-project-id}/locations/us-central1/clusters/{my-cluster}/instances/primary-instance",\
DB_NAME="postgres",\
APP_URL="TEMPORARY_URL"
```

### 使用服務 URL 更新服務

部署指令完成後，它將輸出服務 URL。更新正在執行的服務，以使用此新 URL 設定 `APP_URL` 環境變數。

```shell
gcloud run services update sample-a2a-agent \
  --project="{your-project-id}" \
  --region="us-central1" \
  --update-env-vars=APP_URL="{your-cloud-run-service-url}"
```

## 測試您的代理 (Agent)

您可以使用 A2A CLI 測試您的即時代理 (Agent)，該 CLI 可在 `a2a-samples/samples/python/hosts/cli` 中找到。

以下指令可讓您驗證並與您在 Cloud Run 中已啟用 A2A 的代理 (Agent) 互動。

```shell
cd /path/to/cli
uv run . --agent {your-cloud-run-service-url} --bearer-token "$(gcloud auth print-identity-token)
```

## 免責聲明

重要提示：此處提供的範例程式碼僅供示範之用，旨在說明代理對代理 (A2A) 協定的運作機制。在建構實際應用程式時，至關重要的是將任何在您直接控制範圍之外運作的代理 (Agent) 視為潛在不受信任的實體。

所有從外部代理 (Agent) 接收的資料——包括但不限於其 AgentCard、訊息、產物和任務狀態——都應作為不受信任的輸入來處理。

例如，一個惡意代理 (Agent) 可能在其 AgentCard 的欄位（例如：description、name、skills.description）中提供經過精心設計的資料。如果這些資料在未經清理的情況下被用來建構大型語言模型 (LLM) 的提示，可能會使您的應用程式遭受提示注入攻擊 (prompt injection attacks)。若未能在使用前對這些資料進行適當的驗證和清理，可能會為您的應用程式帶來安全漏洞。

開發人員有責任實施適當的安全措施，例如輸入驗證和安全處理憑證，以保護他們的系統和使用者。
