# 部署至 Vertex AI Agent Engine

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="Vertex AI Agent Engine 目前僅支援 Python。" }

[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
是一項全代管的 Google Cloud 服務，可讓開發人員在生產環境中部署、管理和擴展 AI 代理。Agent Engine 會處理基礎架構以在生產環境中擴展代理，讓您可以專注於建立智慧且具影響力的應用程式。

```python
from vertexai import agent_engines

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
    ]
)
```

## 安裝 Vertex AI SDK

Agent Engine 是 Vertex AI SDK for Python 的一部分。如需更多資訊，您可以查看 [Agent Engine 快速入門文件](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/quickstart)。

### 安裝 Vertex AI SDK

```shell
pip install "google-cloud-aiplatform[adk,agent_engines]" cloudpickle
```

!!!info
    Agent Engine 僅支援 Python 版本 >=3.9 和 <=3.13。

### 初始化

```py
import vertexai

PROJECT_ID = "您的專案 ID"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://您的-google-cloud-storage-bucket"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)
```

關於 `LOCATION`，您可以查看 [Agent Engine 支援的地區](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview#supported-regions) 列表。

### 建立您的代理

您可以使用下方的範例代理，它有兩個工具（取得天氣或擷取指定城市的時間）：

```python
--8<-- "examples/python/snippets/get-started/multi_tool_agent/agent.py"
```

### 準備您的代理以用於 Agent Engine

使用 `reasoning_engines.AdkApp()` 來包裝您的代理，使其可部署至 Agent Engine。

```py
from vertexai.preview import reasoning_engines

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)
```

!!!info
    當 AdkApp 部署到 Agent Engine 時，它會自動使用 `VertexAiSessionService` 來實現持久化、代管的會話狀態。這提供了多輪對話記憶體，無需任何額外設定。對於本機測試，應用程式預設使用暫時的記憶體內會話服務。

### 在本機測試您的代理

您可以在部署至 Agent Engine 之前，先在本機進行測試。

#### 建立會話（本機）

```py
session = app.create_session(user_id="u_123")
session
```

`create_session`（本機）的預期輸出：

```console
Session(id='c6a33dae-26ef-410c-9135-b434a528291f', app_name='default-app-name', user_id='u_123', state={}, events=[], last_update_time=1743440392.8689594)
```

#### 列出會話（本機）

```py
app.list_sessions(user_id="u_123")
```

`list_sessions`（本機）的預期輸出：

```console
ListSessionsResponse(session_ids=['c6a33dae-26ef-410c-9135-b434a528291f'])
```

#### 取得特定會話（本機）

```py
session = app.get_session(user_id="u_123", session_id=session.id)
session
```

`get_session`（本機）的預期輸出：

```console
Session(id='c6a33dae-26ef-410c-9135-b434a528291f', app_name='default-app-name', user_id='u_123', state={}, events=[], last_update_time=1743681991.95696)
```

#### 向您的代理傳送查詢（本機）

```py
for event in app.stream_query(
    user_id="u_123",
    session_id=session.id,
    message="紐約的天氣如何",
):
print(event)
```

`stream_query`（本機）的預期輸出：

```console
{'parts': [{'function_call': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'name': 'get_weather', 'response': {'status': 'success', 'report': '紐約天氣晴朗，溫度為攝氏 25 度（華氏 41 度）。'}}}], 'role': 'user'}
{'parts': [{'text': '紐約天氣晴朗，溫度為攝氏 25 度（華氏 41 度）。'}], 'role': 'model'}
```

### 將您的代理部署至 Agent Engine

```python
from vertexai import agent_engines

remote_app = agent_engines.create(
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]"   
    ]
)
```

此步驟可能需要幾分鐘才能完成。

您可以在 Google Cloud 的 [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines) 上檢查並監控您的 ADK 代理部署情況。

每個已部署的代理都有一個唯一的識別碼。您可以執行以下指令來取得已部署代理的 `resource_name` 識別碼：

```python
remote_app.resource_name
```

回應應如下列字串所示：

```shell
f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"
```

如需其他詳細資訊，您可以造訪 Agent Engine 文件中的[部署代理](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy)和[管理已部署的代理](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)。

### 在 Agent Engine 上測試您的代理

#### 建立會話（遠端）

```py
remote_session = remote_app.create_session(user_id="u_456")
remote_session
```

`create_session`（遠端）的預期輸出：

```console
{'events': [],
'user_id': 'u_456',
'state': {},
'id': '7543472750996750336',
'app_name': '7917477678498709504',
'last_update_time': 1743683353.030133}
```

`id` 是會話 ID，`app_name` 是 Agent Engine 上已部署代理的資源 ID。

#### 列出會話（遠端）

```py
remote_app.list_sessions(user_id="u_456")
```

#### 取得特定會話（遠端）

```py
remote_app.get_session(user_id="u_456", session_id=remote_session["id"])
```

!!!note
    在本機使用您的代理時，會話 ID 儲存在 `session.id` 中；在 Agent Engine 遠端使用您的代理時，會話 ID 儲存在 `remote_session["id"]` 中。

#### 向您的代理傳送查詢（遠端）

```py
for event in remote_app.stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message="紐約的天氣如何",
):
    print(event)
```

`stream_query`（遠端）的預期輸出：

```console
{'parts': [{'function_call': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'name': 'get_weather', 'response': {'status': 'success', 'report': '紐約天氣晴朗，溫度為攝氏 25 度（華氏 41 度）。'}}}], 'role': 'user'}
{'parts': [{'text': '紐約天氣晴朗，溫度為攝氏 25 度（華氏 41 度）。'}], 'role': 'model'}
```

## 使用 Agent Engine UI

## 清理

完成後，最好清理您的雲端資源。
您可以刪除已部署的 Agent Engine 實例，以避免您的 Google Cloud 帳戶產生任何非預期費用。

```python
remote_app.delete(force=True)
```

`force=True` 也會刪除從已部署代理產生的任何子資源，例如會話。

您也可以透過 Google Cloud 上的 [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines) 刪除已部署的代理。
