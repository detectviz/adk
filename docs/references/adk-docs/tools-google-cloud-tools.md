# Google Cloud 工具

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前適用於 Python。Java 支援正在計劃/即將推出。"}

Google Cloud 工具讓您能更輕鬆地將代理程式連接到 Google Cloud 的產品和服務。只需幾行程式碼，您就可以使用這些工具將您的代理程式與以下項目連接：

* 開發人員在 Apigee 中託管的**任何自訂 API**。
* **數百個**預先建置的**連接器**，可連接到 Salesforce、Workday 和 SAP 等企業系統。
* 使用應用程式整合建構的**自動化工作流程**。
* 使用 MCP Toolbox for databases 連接 **Spanner、AlloyDB、Postgres 等資料庫**。

![Google Cloud 工具](../assets/google_cloud_tools.svg)

## Apigee API Hub 工具

**ApiHubToolset** 讓您只需幾行程式碼，就能將 Apigee API hub 中任何有文件記錄的 API 轉換為工具。本節將提供逐步說明，包括為您的 API 設定安全連線的驗證。

**先決條件**

1. [安裝 ADK](get-started-installation.md)
2. 安裝 [Google Cloud CLI](https://cloud.google.com/sdk/docs/install?db=bigtable-docs#installation_instructions)。
3. [Apigee API hub](https://cloud.google.com/apigee/docs/apihub/what-is-api-hub) 實例，其中包含有文件記錄 (即 OpenAPI 規格) 的 API
4. 設定您的專案結構並建立必要的檔案

```console
project_root_folder
 |
 `-- my_agent
     |-- .env
     |-- __init__.py
     |-- agent.py
     `__ tool.py
```

### 建立 API Hub 工具集

注意：本教學包含代理程式建立。如果您已經有代理程式，則只需遵循這些步驟的子集。

1. 取得您的存取權杖，以便 APIHubToolset 可以從 API Hub API 擷取規格。在您的終端機中執行以下指令

    ```shell
    gcloud auth print-access-token
    # 列印您的存取權杖，例如 'ya29....'
    ```

2. 確保所使用的帳戶具有必要的權限。您可以使用預先定義的角色 `roles/apihub.viewer` 或指派以下權限：

    1. **apihub.specs.get (必要)**
    2. apihub.apis.get (可選)
    3. apihub.apis.list (可選)
    4. apihub.versions.get (可選)
    5. apihub.versions.list (可選)
    6. apihub.specs.list (可選)

3. 使用 `APIHubToolset` 建立一個工具。將以下內容新增到 `tools.py`

    如果您的 API 需要驗證，您必須為該工具設定驗證。以下程式碼範例示範如何設定 API 金鑰。ADK 支援基於權杖的驗證 (API 金鑰、持有人權杖)、服務帳戶和 OpenID Connect。我們很快將新增對各種 OAuth2 流程的支援。

    ```python
    from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
    from google.adk.tools.apihub_tool.apihub_toolset import APIHubToolset

    # 為您的 API 提供驗證。如果您的 API 不需要驗證，則不需要。
    auth_scheme, auth_credential = token_to_scheme_credential(
        "apikey", "query", "apikey", apikey_credential_str
    )

    sample_toolset_with_auth = APIHubToolset(
        name="apihub-sample-tool",
        description="範例工具",
        access_token="...",  # 複製您在步驟 1 中產生的存取權杖
        apihub_resource_name="...", # API Hub 資源名稱
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
    )
    ```

    對於生產部署，我們建議使用服務帳戶而不是存取權杖。在上面的程式碼片段中，請使用 `service_account_json=service_account_cred_json_str` 並提供您的安全帳戶憑證，而不是權杖。

    對於 apihub_resource_name，如果您知道用於您 API 的 OpenAPI 規格的特定 ID，請使用 `` `projects/my-project-id/locations/us-west1/apis/my-api-id/versions/version-id/specs/spec-id` ``。如果您希望工具集自動從 API 中提取第一個可用的規格，請使用 `` `projects/my-project-id/locations/us-west1/apis/my-api-id` ``

4. 建立您的代理程式檔案 Agent.py 並將建立的工具新增到您的代理程式定義中：

    ```python
    from google.adk.agents.llm_agent import LlmAgent
    from .tools import sample_toolset

    root_agent = LlmAgent(
        model='gemini-2.0-flash',
        name='enterprise_assistant',
        instruction='幫助使用者，利用您有權存取的工具',
        tools=sample_toolset.get_tools(),
    )
    ```

5. 設定您的 `__init__.py` 以公開您的代理程式

    ```python
    from . import agent
    ```

6. 啟動 Google ADK Web UI 並嘗試您的代理程式：

    ```shell
    # 確保從您的 project_root_folder 執行 `adk web`
    adk web
    ```

   然後前往 [http://localhost:8000](http://localhost:8000) 從 Web UI 嘗試您的代理程式。

---

## 應用程式整合工具

透過 **ApplicationIntegrationToolset**，您可以使用 Integration Connectors 的 100 多個預建連接器，讓您的代理程式無縫地安全且受控地存取企業應用程式，例如 Salesforce、ServiceNow、JIRA、SAP 等。

它支援本地部署和 SaaS 應用程式。此外，您可以透過將應用程式整合工作流程作為工具提供給您的 ADK 代理程式，將現有的應用程式整合流程自動化轉換為代理程式工作流程。

### 先決條件


#### 1. 安裝 ADK

=== "Python"

    安裝最新版本的 [ADK](get-started-installation.md)。有關 ADK 最新版本的資訊，請參閱 [Agent Development Kit Walkthrough](https://docs.google.com/document/d/1oqXkqX9m5wjWE-rkwp-qO0CGpSEQHBTYAYQcWRf91XU/edit?tab=t.0#heading=h.7k9wrm8jpdug)。

=== "Java"

    安裝最新版本的 [ADK](get-started-installation.md)。有關 ADK 最新版本的資訊，請參閱 [Agent Development Kit Walkthrough](https://docs.google.com/document/d/1oqXkqX9m5wjWE-rkwp-qO0CGpSEQHBTYAYQcWRf91XU/edit?tab=t.0#heading=h.7k9wrm8jpdug)。


#### 2. 安裝 CLI

=== "Python"

    安裝 [Google Cloud CLI](https://cloud.google.com/sdk/docs/install#installation_instructions)。若要使用預設憑證使用該工具，請執行以下指令：
    
      ```shell
      gcloud config set project <project-id>
      gcloud auth application-default login
      gcloud auth application-default set-quota-project <project-id>
      ```
    
    將 `<project-id>` 替換為您 Google Cloud 專案的唯一 ID。
    
=== "Java"

    安裝 [Google Cloud CLI](https://cloud.google.com/sdk/docs/install#installation_instructions)。若要使用預設憑證使用該工具，請執行以下指令：
    
      ```bash
      gcloud config set project <project-id>
      gcloud auth application-default login
      gcloud auth application-default set-quota-project <project-id>
      ```
    
    將 `<project-id>` 替換為您 Google Cloud 專案的唯一 ID。


#### 3. 佈建應用程式整合工作流程並發布連線工具

=== "Python"

    使用您想與代理程式一起使用的現有 [Application Integration](https://cloud.google.com/application-integration/docs/overview) 工作流程或 [Integrations Connector](https://cloud.google.com/integration-connectors/docs/overview) 連線。您也可以建立新的 [Application Integration 工作流程](https://cloud.google.com/application-integration/docs/setup-application-integration)或[連線](https://cloud.google.com/integration-connectors/docs/connectors/neo4j/configure#configure-the-connector)。
    
    從範本庫匯入並發布[連線工具](https://pantheon.corp.google.com/integrations/templates/connection-tool/locations/us-central1)。
    
    **注意**：若要使用 Integration Connectors 的連接器，您需要在與連線相同的區域中佈建 Application Integration。

=== "Java"

    使用您想與代理程式一起使用的現有 [Application Integration](https://cloud.google.com/application-integration/docs/overview) 工作流程或 [Integrations Connector](https://cloud.google.com/integration-connectors/docs/overview) 連線。您也可以建立新的 [Application Integration 工作流程](https://cloud.google.com/application-integration/docs/setup-application-integration)或[連線](https://cloud.google.com/integration-connectors/docs/connectors/neo4j/configure#configure-the-connector)。
    
    從範本庫匯入並發布[連線工具](https://pantheon.corp.google.com/integrations/templates/connection-tool/locations/us-central1)。
    
    **注意**：若要使用 Integration Connectors 的連接器，您需要在與連線相同的區域中佈建 Application Integration，並從範本庫匯入並發布連線工具。

#### 4. 建立專案結構

=== "Python"

    設定您的專案結構並建立必要的檔案。
    
      ```console
      project_root_folder
      |-- .env
      `-- my_agent
          |-- __init__.py
          |-- agent.py
          `__ tools.py
      ```
    
    執行代理程式時，請確保在 `project_root_folder` 中執行 `adk web`。

=== "Java"

     設定您的專案結構並建立必要的檔案。
      
        ```console
          project_root_folder
          |-- my_agent
          |   |-- agent.java
          |   `-- pom.xml
        ```
        
      執行代理程式時，請確保在 `project_root_folder` 中執行指令。

#### 5. 設定角色和權限

=== "Python"

    若要取得設定 **ApplicationIntegrationToolset** 所需的權限，您必須在專案上具有以下 IAM 角色 (對於 Integration Connectors 和 Application Integration Workflows 均通用)：
    
      - `roles/integration.editor`
      - `roles/connectors.user`
      - `roles/secretmanager.secretAccessor`
    
    **注意：** 對於代理程式引擎 (AE)，請勿使用 `roles/integration.invoker`，因為這可能導致 403 錯誤。請改用 `roles/integration.editor`。

=== "Java"

    若要取得設定 **ApplicationIntegrationToolset** 所需的權限，您必須在專案上具有以下 IAM 角色 (對於 Integration Connectors 和 Application Integration Workflows 均通用)：
    
      - `roles/integration.editor`
      - `roles/connectors.user`
      - `roles/secretmanager.secretAccessor`

    **注意：** 對於代理程式引擎 (AE)，請勿使用 `roles/integration.invoker`，因為這可能導致 403 錯誤。請改用 `roles/integration.editor`。
    

### 使用 Integration Connectors

使用 [Integration Connectors](https://cloud.google.com/integration-connectors/docs/overview) 將您的代理程式連接到企業應用程式。

#### 開始之前

**注意：** 當您在給定區域中佈建 Application Integration 時，通常會自動建立 *ExecuteConnection* 整合。如果 *ExecuteConnection* 不存在於[整合清單](https://pantheon.corp.google.com/integrations/list?hl=en&inv=1&invt=Ab2u5g&project=standalone-ip-prod-testing)中，您必須按照以下步驟建立它：

1. 若要使用 Integration Connectors 的連接器，請按一下 **QUICK SETUP** 並在與您的連線相同的區域中[佈建](https://console.cloud.google.com/integrations) Application Integration。

   ![Google Cloud 工具](../assets/application-integration-overview.png)
   
   

2. 前往範本庫中的[連線工具](https://console.cloud.google.com/integrations/templates/connection-tool/locations/us-central1)範本，然後按一下 **USE TEMPLATE**。


    ![Google Cloud 工具](../assets/use-connection-tool-template.png)

3. 輸入整合名稱為 *ExecuteConnection* (必須僅使用此確切的整合名稱)。然後，選取與您的連線區域相符的區域，然後按一下 **CREATE**。

4. 按一下 **PUBLISH** 以在 <i>Application Integration</i> 編輯器中發布整合。


    ![Google Cloud 工具](../assets/publish-integration.png)
   
   
#### 建立應用程式整合工具集

Application Integration Toolset 支援 Integration Connectors 的**動態 OAuth2 驗證**的 `auth_scheme` 和 `auth_credential`。

若要為 Integration Connectors 建立 Application Integration Toolset，請按照以下步驟操作：

1.  在 `tools.py` 檔案中使用 `ApplicationIntegrationToolset` 建立一個工具：

    ```python
    from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset

    connector_tool = ApplicationIntegrationToolset(
        project="test-project", # TODO: 替換為連線的 GCP 專案
        location="us-central1", #TODO: 替換為連線的位置
        connection="test-connection", #TODO: 替換為連線名稱
        entity_operations={"Entity_One": ["LIST","CREATE"], "Entity_Two": []},#空列表表示支援實體上的所有操作。
        actions=["action1"], #TODO: 替換為動作
        service_account_json='{...}', # 可選。服務帳號金鑰的字串化 json
        tool_name_prefix="tool_prefix2",
        tool_instructions="..."
    )
    ```

    **注意：**

    * 您可以提供一個服務帳戶來代替使用預設憑證，方法是產生一個[服務帳戶金鑰](https://cloud.google.com/iam/docs/keys-create-delete#creating)，並向該服務帳戶提供正確的[應用程式整合和整合連接器 IAM 角色](#prerequisites)。
    * 若要尋找連線支援的實體和動作清單，請使用 Connectors API：[listActions](https://cloud.google.com/integration-connectors/docs/reference/rest/v1/projects.locations.connections.connectionSchemaMetadata/listActions) 或 [listEntityTypes](https://cloud.google.com/integration-connectors/docs/reference/rest/v1/projects.locations.connections.connectionSchemaMetadata/listEntityTypes)。


    `ApplicationIntegrationToolset` 也支援 Integration Connectors 的動態 OAuth2 驗證的 `auth_scheme` 和 `auth_credential`。若要使用它，請在 `tools.py` 檔案中建立一個類似以下的工具：

    ```python
    from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset
    from google.adk.tools.openapi_tool.auth.auth_helpers import dict_to_auth_scheme
    from google.adk.auth import AuthCredential
    from google.adk.auth import AuthCredentialTypes
    from google.adk.auth import OAuth2Auth

    oauth2_data_google_cloud = {
      "type": "oauth2",
      "flows": {
          "authorizationCode": {
              "authorizationUrl": "https://accounts.google.com/o/oauth2/auth",
              "tokenUrl": "https://oauth2.googleapis.com/token",
              "scopes": {
                  "https://www.googleapis.com/auth/cloud-platform": (
                      "檢視和管理您在 Google Cloud Platform 服務中的資料"
                  ),
                  "https://www.googleapis.com/auth/calendar.readonly": "檢視您的日曆"
              },
          }
      },
    }

    oauth_scheme = dict_to_auth_scheme(oauth2_data_google_cloud)

    auth_credential = AuthCredential(
      auth_type=AuthCredentialTypes.OAUTH2,
      oauth2=OAuth2Auth(
          client_id="...", #TODO: 替換為 client_id
          client_secret="...", #TODO: 替換為 client_secret
      ),
    )

    connector_tool = ApplicationIntegrationToolset(
        project="test-project", # TODO: 替換為連線的 GCP 專案
        location="us-central1", #TODO: 替換為連線的位置
        connection="test-connection", #TODO: 替換為連線名稱
        entity_operations={"Entity_One": ["LIST","CREATE"], "Entity_Two": []},#空列表表示支援實體上的所有操作。
        actions=["GET_calendars/%7BcalendarId%7D/events"], #TODO: 替換為動作。這個是列出事件。
        service_account_json='{...}', # 可選。服務帳號金鑰的字串化 json
        tool_name_prefix="tool_prefix2",
        tool_instructions="...",
        auth_scheme=oauth_scheme,
        auth_credential=auth_credential
    )
    ```


2. 更新 `agent.py` 檔案並將工具新增到您的代理程式：

    ```python
    from google.adk.agents.llm_agent import LlmAgent
    from .tools import connector_tool

    root_agent = LlmAgent(
        model='gemini-2.0-flash',
        name='connector_agent',
        instruction="幫助使用者，利用您有權存取的工具",
        tools=[connector_tool],
    )
    ```

3. 設定 `__init__.py` 以公開您的代理程式：

    ```python
    from . import agent
    ```

4. 啟動 Google ADK Web UI 並使用您的代理程式：

    ```shell
    # 確保從您的 project_root_folder 執行 `adk web`
    adk web
    ```

完成上述步驟後，前往 [http://localhost:8000](http://localhost:8000)，然後選擇 `my_agent` 代理程式 (與代理程式資料夾名稱相同)。


### 使用應用程式整合工作流程

使用現有的 [Application Integration](https://cloud.google.com/application-integration/docs/overview) 工作流程作為您代理程式的工具，或建立一個新的。


#### 1. 建立一個工具

=== "Python"

    若要在 `tools.py` 檔案中使用 `ApplicationIntegrationToolset` 建立一個工具，請使用以下程式碼：
    
      ```python
          integration_tool = ApplicationIntegrationToolset(
              project="test-project", # TODO: 替換為連線的 GCP 專案
              location="us-central1", #TODO: 替換為連線的位置
              integration="test-integration", #TODO: 替換為整合名稱
              triggers=["api_trigger/test_trigger"],#TODO: 替換為觸發器 ID。空列表表示考慮整合中的所有 api 觸發器。
              service_account_json='{...}', #可選。服務帳號金鑰的字串化 json
              tool_name_prefix="tool_prefix1",
              tool_instructions="..."
          )
      ```
      
      **注意：** 您可以提供一個服務帳戶來代替使用預設憑證。為此，請產生一個[服務帳戶金鑰](https://cloud.google.com/iam/docs/keys-create-delete#creating)並向該服務帳戶提供正確的[應用程式整合和整合連接器 IAM 角色](#prerequisites)。有關 IAM 角色的更多詳細資訊，請參閱[先決條件](#prerequisites)部分。

=== "Java"

    若要在 `tools.java` 檔案中使用 `ApplicationIntegrationToolset` 建立一個工具，請使用以下程式碼：
    
      ```java    
          import com.google.adk.tools.applicationintegrationtoolset.ApplicationIntegrationToolset;
          import com.google.common.collect.ImmutableList;
          import com.google.common.collect.ImmutableMap;
      
          public class Tools {
              private static ApplicationIntegrationToolset integrationTool;
              private static ApplicationIntegrationToolset connectionsTool;
      
              static {
                  integrationTool = new ApplicationIntegrationToolset(
                          "test-project",
                          "us-central1",
                          "test-integration",
                          ImmutableList.of("api_trigger/test-api"),
                          null,
                          null,
                          null,
                          "{...}",
                          "tool_prefix1",
                          "...");
      
                  connectionsTool = new ApplicationIntegrationToolset(
                          "test-project",
                          "us-central1",
                          null,
                          null,
                          "test-connection",
                          ImmutableMap.of("Issue", ImmutableList.of("GET")),
                          ImmutableList.of("ExecuteCustomQuery"),
                          "{...}",
                          "tool_prefix",
                          "...");
              }
          }
      ```
    
      **注意：** 您可以提供一個服務帳戶來代替使用預設憑證。為此，請產生一個[服務帳戶金鑰](https://cloud.google.com/iam/docs/keys-create-delete#creating)並向該服務帳戶提供正確的[應用程式整合和整合連接器 IAM 角色](#prerequisites)。有關 IAM 角色的更多詳細資訊，請參閱[先決條件](#prerequisites)部分。

#### 2. 將工具新增到您的代理程式

=== "Python"

    若要更新 `agent.py` 檔案並將工具新增到您的代理程式，請使用以下程式碼：
    
      ```python
          from google.adk.agents.llm_agent import LlmAgent
          from .tools import integration_tool, connector_tool
      
          root_agent = LlmAgent(
              model='gemini-2.0-flash',
              name='integration_agent',
              instruction="幫助使用者，利用您有權存取的工具",
              tools=[integration_tool],
          )
      ```

=== "Java"

    若要更新 `agent.java` 檔案並將工具新增到您的代理程式，請使用以下程式碼：
    
      ```java
           import com.google.adk.agent.LlmAgent;
           import com.google.adk.tools.BaseTool;
           import com.google.common.collect.ImmutableList;
        
            public class MyAgent {
                public static void main(String[] args) {
                    // 假設 Tools 類別如上一步驟所定義
                    ImmutableList<BaseTool> tools = ImmutableList.<BaseTool>builder()
                            .add(Tools.integrationTool)
                            .add(Tools.connectionsTool)
                            .build();
        
                    // 最後，使用自動產生的工具建立您的代理程式。
                    LlmAgent rootAgent = LlmAgent.builder()
                            .name("science-teacher")
                            .description("科學老師代理程式")
                            .model("gemini-2.0-flash")
                            .instruction(
                                    "幫助使用者，利用您有權存取的工具。"
                            )
                            .tools(tools)
                            .build();
        
                    // 您現在可以使用 rootAgent 與 LLM 互動
                    // 例如，您可以與代理程式開始對話。
                }
            }
      ```
        
    **注意：** 若要尋找連線支援的實體和動作清單，請使用這些 Connector API：`listActions`、`listEntityTypes`。
      
#### 3. 公開您的代理程式

=== "Python"

    若要設定 `__init__.py` 以公開您的代理程式，請使用以下程式碼：
    
      ```python
          from . import agent
      ```

#### 4. 使用您的代理程式

=== "Python"

    若要啟動 Google ADK Web UI 並使用您的代理程式，請使用以下指令：
    
      ```shell
          # 確保從您的 project_root_folder 執行 `adk web`
          adk web
      ```
    完成上述步驟後，前往 [http://localhost:8000](http://localhost:8000)，然後選擇 `my_agent` 代理程式 (與代理程式資料夾名稱相同)。
    
=== "Java"

    若要啟動 Google ADK Web UI 並使用您的代理程式，請使用以下指令：
    
      ```bash
          mvn install
      
          mvn exec:java \
              -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
              -Dexec.args="--adk.agents.source-dir=src/main/java" \
              -Dexec.classpathScope="compile"
      ```
    
    完成上述步驟後，前往 [http://localhost:8000](http://localhost:8000)，然後選擇 `my_agent` 代理程式 (與代理程式資料夾名稱相同)。
  
---

## 用於資料庫的工具箱工具

[MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) 是一個用於資料庫的開源 MCP 伺服器。它的設計考慮到了企業級和生產品質。它透過處理連線池、驗證等複雜性，使您能夠更輕鬆、更快速、更安全地開發工具。

Google 的代理程式開發套件 (ADK) 內建了對 Toolbox 的支援。有關[入門](https://googleapis.github.io/genai-toolbox/getting-started)或[設定](https://googleapis.github.io/genai-toolbox/getting-started/configure/) Toolbox 的更多資訊，請參閱[文件](https://googleapis.github.io/genai-toolbox/getting-started/introduction/)。

![GenAI 工具箱](../assets/mcp_db_toolbox.png)

### 設定和部署

Toolbox 是一個您可以自行部署和管理的開源伺服器。有關部署和設定的更多說明，請參閱官方 Toolbox 文件：

* [安裝伺服器](https://googleapis.github.io/genai-toolbox/getting-started/introduction/#installing-the-server)
* [設定 Toolbox](https://googleapis.github.io/genai-toolbox/getting-started/configure/)

### 安裝客戶端 SDK

ADK 依賴 `toolbox-core` python 套件來使用 Toolbox。在開始之前，請先安裝該套件：

```shell
pip install toolbox-core
```

### 載入工具箱工具

一旦您的 Toolbox 伺服器設定完成並開始執行，您就可以使用 ADK 從您的伺服器載入工具：

```python
from google.adk.agents import Agent
from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("https://127.0.0.1:5000")

# 載入一組特定的工具
tools = toolbox.load_toolset('my-toolset-name'),
# 載入單一工具
tools = toolbox.load_tool('my-tool-name'),

root_agent = Agent(
    ...,
    tools=tools # 將工具清單提供給代理程式

)
```

### 進階工具箱功能

Toolbox 具有多種功能，可讓您開發用於資料庫的 Gen AI 工具。有關更多資訊，請閱讀以下功能的更多內容：

* [已驗證的參數](https://googleapis.github.io/genai-toolbox/resources/tools/#authenticated-parameters)：自動將工具輸入綁定到來自 OIDC 權杖的值，從而可以輕鬆執行敏感查詢而不會潛在地洩漏資料
* [已授權的調用：](https://googleapis.github.io/genai-toolbox/resources/tools/#authorized-invocations)  根據使用者驗證權杖限制使用工具的存取權限
* [OpenTelemetry](https://googleapis.github.io/genai-toolbox/how-to/export_telemetry/)：使用 OpenTelemetry 從 Toolbox 取得指標和追蹤
