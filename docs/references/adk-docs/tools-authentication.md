# 使用工具進行驗證

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前適用於 Python。Java 支援正在計劃/即將推出。"}

## 核心概念

許多工具需要存取受保護的資源（例如 Google 日曆中的使用者資料、Salesforce 記錄等），因此需要進行驗證。ADK 提供了一個系統來安全地處理各種驗證方法。

涉及的關鍵元件包括：

1. **`AuthScheme`**：定義 API *如何*期望驗證憑證（例如，作為標頭中的 API 金鑰、OAuth 2.0 持有人權杖）。ADK 支援與 OpenAPI 3.0 相同類型的驗證方案。若要了解每種類型憑證的更多資訊，請參閱 [OpenAPI 文件：驗證](https://swagger.io/docs/specification/v3_0/authentication/)。ADK 使用特定的類別，如 `APIKey`、`HTTPBearer`、`OAuth2`、`OpenIdConnectWithConfig`。
2. **`AuthCredential`**：保存*開始*驗證過程所需的*初始*資訊（例如，您應用程式的 OAuth 用戶端 ID/密鑰、API 金鑰值）。它包含一個 `auth_type`（如 `API_KEY`、`OAUTH2`、`SERVICE_ACCOUNT`），用於指定憑證類型。

一般流程是在設定工具時提供這些詳細資訊。然後，在工具進行 API 呼叫之前，ADK 會嘗試自動將初始憑證交換為可用的憑證（如存取權杖）。對於需要使用者互動的流程（如 OAuth 同意），會觸發一個涉及代理程式用戶端應用程式的特定互動過程。

## 支援的初始憑證類型

* **API_KEY：** 用於簡單的鍵/值驗證。通常不需要交換。
* **HTTP：** 可以代表基本驗證（不建議/不支援交換）或已取得的持有人權杖。如果是持有人權杖，則無需交換。
* **OAUTH2：** 用於標準的 OAuth 2.0 流程。需要設定（用戶端 ID、密鑰、範圍），並且通常會觸發使用者同意的互動流程。
* **OPEN_ID_CONNECT：** 用於基於 OpenID Connect 的驗證。與 OAuth2 類似，通常需要設定和使用者互動。
* **SERVICE_ACCOUNT：** 用於 Google Cloud 服務帳號憑證（JSON 金鑰或應用程式預設憑證）。通常會交換為持有人權杖。

## 在工具上設定驗證

您在定義工具時設定驗證：

* **RestApiTool / OpenAPIToolset**：在初始化期間傳遞 `auth_scheme` 和 `auth_credential`。

* **GoogleApiToolSet 工具**：ADK 具有內建的第一方工具，如 Google 日曆、BigQuery 等。請使用工具集的特定方法。

* **APIHubToolset / ApplicationIntegrationToolset**：如果在 API Hub 中管理的 API / 由 Application Integration 提供的 API 需要驗證，請在初始化期間傳遞 `auth_scheme` 和 `auth_credential`。

!!! tip "警告"
    將存取權杖等敏感憑證，尤其是重新整理權杖，直接儲存在會話狀態中，可能會帶來安全風險，具體取決於您的會話儲存後端 (`SessionService`) 和整體應用程式安全狀況。

    *   **`InMemorySessionService`：** 適用於測試和開發，但當程序結束時資料會遺失。風險較小，因為它是暫時的。
    *   **資料庫/持久性儲存：** **強烈考慮**在使用強大的加密函式庫（如 `cryptography`）將權杖資料儲存到資料庫之前對其進行加密，並安全地管理加密金鑰（例如，使用金鑰管理服務）。
    *   **安全密鑰儲存：** 對於生產環境，將敏感憑證儲存在專用的密鑰管理器（如 Google Cloud Secret Manager 或 HashiCorp Vault）中是**最推薦的方法**。您的工具可能只在會話狀態中儲存短期的存取權杖或安全引用（而不是重新整理權杖本身），並在需要時從安全儲存中擷取必要的密鑰。

---

## 旅程 1：使用經過驗證的工具建構代理程式應用程式

本節重點介紹如何在您的代理程式應用程式中使用需要驗證的現有工具（例如來自 `RestApiTool/ OpenAPIToolset`、`APIHubToolset`、`GoogleApiToolSet` 的工具）。您的主要職責是設定工具並處理互動式驗證流程的客戶端部分（如果工具需要）。

### 1. 使用驗證設定工具

在將經過驗證的工具新增到您的代理程式時，您需要提供其所需的 `AuthScheme` 和您應用程式的初始 `AuthCredential`。

**A. 使用基於 OpenAPI 的工具集 (`OpenAPIToolset`、`APIHubToolset` 等)**

在工具集初始化期間傳遞方案和憑證。工具集會將它們應用於所有產生的工具。以下是在 ADK 中使用驗證建立工具的幾種方法。

=== "API 金鑰"

      建立一個需要 API 金鑰的工具。

      ```python
      from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
      from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

      auth_scheme, auth_credential = token_to_scheme_credential(
          "apikey", "query", "apikey", "您的_API_金鑰_字串"
      )
      sample_api_toolset = OpenAPIToolset(
          spec_str="...",  # 在此處填入 OpenAPI 規格字串
          spec_str_type="yaml",
          auth_scheme=auth_scheme,
          auth_credential=auth_credential,
      )
      ```

=== "OAuth2"

      建立一個需要 OAuth2 的工具。

      ```python
      from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset
      from fastapi.openapi.models import OAuth2
      from fastapi.openapi.models import OAuthFlowAuthorizationCode
      from fastapi.openapi.models import OAuthFlows
      from google.adk.auth import AuthCredential
      from google.adk.auth import AuthCredentialTypes
      from google.adk.auth import OAuth2Auth

      auth_scheme = OAuth2(
          flows=OAuthFlows(
              authorizationCode=OAuthFlowAuthorizationCode(
                  authorizationUrl="https://accounts.google.com/o/oauth2/auth",
                  tokenUrl="https://oauth2.googleapis.com/token",
                  scopes={
                      "https://www.googleapis.com/auth/calendar": "日曆範圍"
                  },
              )
          )
      )
      auth_credential = AuthCredential(
          auth_type=AuthCredentialTypes.OAUTH2,
          oauth2=OAuth2Auth(
              client_id=您的_OAUTH_用戶端_ID,
              client_secret=您的_OAUTH_用戶端_密鑰
          ),
      )

      calendar_api_toolset = OpenAPIToolset(
          spec_str=google_calendar_openapi_spec_str, # 在此處填入 openapi 規格
          spec_str_type='yaml',
          auth_scheme=auth_scheme,
          auth_credential=auth_credential,
      )
      ```

=== "服務帳號"

      建立一個需要服務帳號的工具。

      ```python
      from google.adk.tools.openapi_tool.auth.auth_helpers import service_account_dict_to_scheme_credential
      from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

      service_account_cred = json.loads(service_account_json_str)
      auth_scheme, auth_credential = service_account_dict_to_scheme_credential(
          config=service_account_cred,
          scopes=["https://www.googleapis.com/auth/cloud-platform"],
      )
      sample_toolset = OpenAPIToolset(
          spec_str=sa_openapi_spec_str, # 在此處填入 openapi 規格
          spec_str_type='json',
          auth_scheme=auth_scheme,
          auth_credential=auth_credential,
      )
      ```

=== "OpenID connect"

      建立一個需要 OpenID connect 的工具。

      ```python
      from google.adk.auth.auth_schemes import OpenIdConnectWithConfig
      from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth
      from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

      auth_scheme = OpenIdConnectWithConfig(
          authorization_endpoint=OAUTH2_AUTH_ENDPOINT_URL,
          token_endpoint=OAUTH2_TOKEN_ENDPOINT_URL,
          scopes=['openid', '您的_OAUTH_範圍"]
      )
      auth_credential = AuthCredential(
          auth_type=AuthCredentialTypes.OPEN_ID_CONNECT,
          oauth2=OAuth2Auth(
              client_id="...",
              client_secret="...",
          )
      )

      userinfo_toolset = OpenAPIToolset(
          spec_str=content, # 填入實際的規格
          spec_str_type='yaml',
          auth_scheme=auth_scheme,
          auth_credential=auth_credential,
      )
      ```

**B. 使用 Google API 工具集 (例如 `calendar_tool_set`)**

這些工具集通常具有專用的設定方法。

提示：有關如何建立 Google OAuth 用戶端 ID 和密鑰的資訊，請參閱本指南：[取得您的 Google API 用戶端 ID](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid#get_your_google_api_client_id)

```python
# 範例：設定 Google 日曆工具
from google.adk.tools.google_api_tool import calendar_tool_set

client_id = "您的_GOOGLE_OAUTH_用戶端_ID.apps.googleusercontent.com"
client_secret = "您的_GOOGLE_OAUTH_用戶端_密鑰"

# 使用此工具集類型的特定設定方法
calendar_tool_set.configure_auth(
    client_id=oauth_client_id, client_secret=oauth_client_secret
)

# agent = LlmAgent(..., tools=calendar_tool_set.get_tool('calendar_tool_set'))
```

驗證請求流程（其中工具正在請求驗證憑證）的序列圖如下所示：

![驗證](../assets/auth_part1.svg)


### 2. 處理互動式 OAuth/OIDC 流程 (客戶端)

如果工具需要使用者登入/同意（通常是 OAuth 2.0 或 OIDC），ADK 框架會暫停執行並通知您的**代理程式用戶端**應用程式。有兩種情況：

* **代理程式用戶端**應用程式在同一進程中直接執行代理程式（透過 `runner.run_async`）。例如 UI 後端、CLI 應用程式或 Spark 作業等。
* **代理程式用戶端**應用程式透過 `/run` 或 `/run_sse` 端點與 ADK 的 fastapi 伺服器互動。雖然 ADK 的 fastapi 伺服器可以與**代理程式用戶端**應用程式設定在同一台伺服器或不同的伺服器上。

第二種情況是第一種情況的特例，因為 `/run` 或 `/run_sse` 端點也會調用 `runner.run_async`。唯一的區別是：

* 是呼叫 python 函式來執行代理程式（第一種情況）還是呼叫服務端點來執行代理程式（第二種情況）。
* 結果事件是記憶體中的物件（第一種情況）還是 http 回應中的序列化 json 字串（第二種情況）。

以下各節重點介紹第一種情況，您應該能夠非常直接地將其對應到第二種情況。如果需要，我們還將描述第二種情況需要處理的一些差異。

以下是您的客戶端應用程式的逐步流程：

**步驟 1：執行代理程式並偵測驗證請求**

* 使用 `runner.run_async` 啟動代理程式互動。
* 迭代產生的事件。
* 尋找一個特定的函式呼叫事件，其函式呼叫具有一個特殊的名稱：`adk_request_credential`。此事件表示需要使用者互動。您可以使用輔助函式來識別此事件並提取必要的資訊。（對於第二種情況，邏輯類似。您從 http 回應中反序列化事件）。

```python

# runner = Runner(...)
# session = await session_service.create_session(...)
# content = types.Content(...) # 使用者的初始查詢

print("\n執行代理程式中...")
events_async = runner.run_async(
    session_id=session.id, user_id='user', new_message=content
)

auth_request_function_call_id, auth_config = None, None

async for event in events_async:
    # 使用輔助函式檢查特定的驗證請求事件
    if (auth_request_function_call := get_auth_request_function_call(event)):
        print("--> 代理程式需要驗證。")
        # 儲存稍後回應所需的 ID
        if not (auth_request_function_call_id := auth_request_function_call.id):
            raise ValueError(f'無法從函式呼叫中取得函式呼叫 ID：{auth_request_function_call}')
        # 取得包含 auth_uri 等的 AuthConfig
        auth_config = get_auth_config(auth_request_function_call)
        break # 暫時停止處理事件，需要使用者互動

if not auth_request_function_call_id:
    print("\n不需要驗證或代理程式已完成。")
    # return # 或處理收到的最終回應

```

*輔助函式 `helpers.py`：*

```python
from google.adk.events import Event
from google.adk.auth import AuthConfig # 匯入必要的類型
from google.genai import types

def get_auth_request_function_call(event: Event) -> types.FunctionCall:
    # 從事件中取得特殊的驗證請求函式呼叫
    if not event.content or not event.content.parts:
        return
    for part in event.content.parts:
        if (
            part 
            and part.function_call 
            and part.function_call.name == 'adk_request_credential'
            and event.long_running_tool_ids 
            and part.function_call.id in event.long_running_tool_ids
        ):

            return part.function_call

def get_auth_config(auth_request_function_call: types.FunctionCall) -> AuthConfig:
    # 從驗證請求函式呼叫的參數中提取 AuthConfig 物件
    if not auth_request_function_call.args or not (auth_config := auth_request_function_call.args.get('auth_config')):
        raise ValueError(f'無法從函式呼叫中取得驗證設定：{auth_request_function_call}')
    if not isinstance(auth_config, AuthConfig):
        raise ValueError(f'無法取得驗證設定 {auth_config} 不是 AuthConfig 的實例。')
    return auth_config
```

**步驟 2：重新導向使用者進行授權**

* 從上一步中提取的 `auth_config` 中取得授權 URL (`auth_uri`)。
* **至關重要的是，將您應用程式的** `redirect_uri` 作為查詢參數附加到此 `auth_uri`。此 `redirect_uri` 必須已在您的 OAuth 提供者處預先註冊（例如，[Google Cloud Console](https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred)、[Okta 管理員控制台](https://developer.okta.com/docs/guides/sign-into-web-app-redirect/spring-boot/main/#create-an-app-integration-in-the-admin-console)）。
* 將使用者導向到此完整的 URL（例如，在他們的瀏覽器中開啟它）。

```python
# (偵測到需要驗證後繼續)

if auth_request_function_call_id and auth_config:
    # 從 AuthConfig 中取得基本授權 URL
    base_auth_uri = auth_config.exchanged_auth_credential.oauth2.auth_uri

    if base_auth_uri:
        redirect_uri = 'http://localhost:8000/callback' # 必須與您的 OAuth 用戶端應用程式設定相符
        # 附加 redirect_uri (在生產環境中使用 urlencode)
        auth_request_uri = base_auth_uri + f'&redirect_uri={redirect_uri}'
        # 現在您需要將您的終端使用者重新導向到此 auth_request_uri 或要求他們在瀏覽器中開啟此 auth_request_uri
        # 此 auth_request_uri 應由對應的驗證提供者提供服務，終端使用者應登入並授權您的應用程式存取其資料
        # 然後驗證提供者會將終端使用者重新導向到您提供的 redirect_uri
        # 下一步：從使用者（或您的 Web 伺服器處理常式）取得此回呼 URL
    else:
         print("錯誤：在 auth_config 中找不到 Auth URI。")
         # 處理錯誤

```

**步驟 3. 處理重新導向回呼 (客戶端)：**

* 您的應用程式必須有一個機制（例如，在 `redirect_uri` 處的 Web 伺服器路由）來在使用者向提供者授權應用程式後接收使用者。
* 提供者將使用者重新導向到您的 `redirect_uri`，並將 `authorization_code`（以及可能的 `state`、`scope`）作為查詢參數附加到 URL。
* 從此傳入請求中擷取**完整的**回呼 URL。
* （此步驟發生在主代理程式執行迴圈之外，在您的 Web 伺服器或等效的回呼處理常式中。）

**步驟 4. 將驗證結果傳回 ADK (客戶端)：**

* 一旦您有了完整的**回呼** URL（包含授權碼），請檢索在客戶端步驟 1 中儲存的 `auth_request_function_call_id` 和 `auth_config` 物件。
* 將擷取到的回呼 URL 設定到 `exchanged_auth_credential.oauth2.auth_response_uri` 欄位中。同時確保 `exchanged_auth_credential.oauth2.redirect_uri` 包含您使用的重新導向 URI。
* 建立一個包含帶有 `types.FunctionResponse` 的 `types.Part` 的 `types.Content` 物件。
      * 將 `name` 設定為 `"adk_request_credential"`。（注意：這是 ADK 繼續進行驗證的特殊名稱。請勿使用其他名稱。）
      * 將 `id` 設定為您儲存的 `auth_request_function_call_id`。
      * 將 `response` 設定為*序列化*（例如，`.model_dump()`）的更新後的 `AuthConfig` 物件。
* **再次**為同一個會話呼叫 `runner.run_async`，將此 `FunctionResponse` 內容作為 `new_message` 傳遞。

```python
# (使用者互動後繼續)

    # 模擬取得回呼 URL (例如，從使用者貼上或 Web 處理常式)
    auth_response_uri = await get_user_input(
        f'在此處貼上完整的回呼 URL：\n> '
    )
    auth_response_uri = auth_response_uri.strip() # 清理輸入

    if not auth_response_uri:
        print("未提供回呼 URL。中止。")
        return

    # 使用回呼詳細資訊更新收到的 AuthConfig
    auth_config.exchanged_auth_credential.oauth2.auth_response_uri = auth_response_uri
    # 同時包含所使用的 redirect_uri，因為權杖交換可能需要它
    auth_config.exchanged_auth_credential.oauth2.redirect_uri = redirect_uri

    # 建構 FunctionResponse Content 物件
    auth_content = types.Content(
        role='user', # 傳送 FunctionResponse 時，角色可以是 'user'
        parts=[
            types.Part(
                function_response=types.FunctionResponse(
                    id=auth_request_function_call_id,       # 連結到原始請求
                    name='adk_request_credential', # 特殊的框架函式名稱
                    response=auth_config.model_dump() # 傳回*更新後*的 AuthConfig
                )
            )
        ],
    )

    # --- 恢復執行 ---
    print("\n正在將驗證詳細資訊提交回代理程式...")
    events_async_after_auth = runner.run_async(
        session_id=session.id,
        user_id='user',
        new_message=auth_content, # 將 FunctionResponse 傳回
    )

    # --- 處理最終代理程式輸出 ---
    print("\n--- 驗證後的代理程式回應 ---")
    async for event in events_async_after_auth:
        # 正常處理事件，預期工具呼叫現在會成功
        print(event) # 列印完整的事件以供檢查

```

**步驟 5：ADK 處理權杖交換和工具重試並取得工具結果**

* ADK 收到 `adk_request_credential` 的 `FunctionResponse`。
* 它使用更新後的 `AuthConfig` 中的資訊（包括包含程式碼的回呼 URL）與提供者的權杖端點執行 OAuth **權杖交換**，以取得存取權杖（以及可能的重新整理權杖）。
* ADK 在內部透過將這些權杖設定在會話狀態中來使其可用。
* ADK **自動重試**原始的工具呼叫（最初因缺少驗證而失敗的那個）。
* 這一次，工具找到有效的權杖（透過 `tool_context.get_auth_response()`）並成功執行經過驗證的 API 呼叫。
* 代理程式從工具收到實際結果，並產生對使用者的最終回應。

---

驗證回應流程（其中代理程式用戶端傳回驗證回應，ADK 重試工具呼叫）的序列圖如下所示：

![驗證](../assets/auth_part2.svg)

## 旅程 2：建構需要驗證的自訂工具 (`FunctionTool`)

本節重點介紹在建立新的 ADK 工具時，在您的自訂 Python 函式*內部*實作驗證邏輯。我們將實作一個 `FunctionTool` 作為範例。

### 先決條件

您的函式簽章*必須*包含 [`tool_context: ToolContext`](../tools/index.md#tool-context)。ADK 會自動注入此物件，提供對狀態和驗證機制的存取。

```python
from google.adk.tools import FunctionTool, ToolContext
from typing import Dict

def my_authenticated_tool_function(param1: str, ..., tool_context: ToolContext) -> dict:
    # ... 您的邏輯 ...
    pass

my_tool = FunctionTool(func=my_authenticated_tool_function)

```

### 工具函式內的驗證邏輯

在您的函式內部實作以下步驟：

**步驟 1：檢查快取且有效的憑證：**

在您的工具函式內部，首先檢查是否已在此會話的先前執行中儲存了有效的憑證（例如，存取/重新整理權杖）。目前會話的憑證應儲存在 `tool_context.invocation_context.session.state`（一個狀態字典）中。透過檢查 `tool_context.invocation_context.session.state.get(credential_name, None)` 來檢查現有憑證是否存在。

```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# 在您的工具函式內部
TOKEN_CACHE_KEY = "my_tool_tokens" # 選擇一個唯一的鍵
SCOPES = ["scope1", "scope2"] # 定義所需的範圍

creds = None
cached_token_info = tool_context.state.get(TOKEN_CACHE_KEY)
if cached_token_info:
    try:
        creds = Credentials.from_authorized_user_info(cached_token_info, SCOPES)
        if not creds.valid and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            tool_context.state[TOKEN_CACHE_KEY] = json.loads(creds.to_json()) # 更新快取
        elif not creds.valid:
            creds = None # 無效，需要重新驗證
            tool_context.state[TOKEN_CACHE_KEY] = None
    except Exception as e:
        print(f"載入/重新整理快取憑證時出錯：{e}")
        creds = None
        tool_context.state[TOKEN_CACHE_KEY] = None

if creds and creds.valid:
    # 跳至步驟 5：進行經過驗證的 API 呼叫
    pass
else:
    # 繼續步驟 2...
    pass

```

**步驟 2：檢查來自客戶端的驗證回應**

* 如果步驟 1 沒有產生有效的憑證，請透過呼叫 `exchanged_credential = tool_context.get_auth_response()` 來檢查客戶端是否剛完成互動流程。
* 這會傳回客戶端傳回的更新後的 `exchanged_credential` 物件（在 `auth_response_uri` 中包含回呼 URL）。

```python
# 使用在工具中設定的 auth_scheme 和 auth_credential。
# exchanged_credential: AuthCredential | None

exchanged_credential = tool_context.get_auth_response(AuthConfig(
  auth_scheme=auth_scheme,
  raw_auth_credential=auth_credential,
))
# 如果 exchanged_credential 不是 None，則表示已經有來自驗證回應的交換憑證。
if exchanged_credential:
   # ADK 已經為我們交換了存取權杖
        access_token = exchanged_credential.oauth2.access_token
        refresh_token = exchanged_credential.oauth2.refresh_token
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri=auth_scheme.flows.authorizationCode.tokenUrl,
            client_id=auth_credential.oauth2.client_id,
            client_secret=auth_credential.oauth2.client_secret,
            scopes=list(auth_scheme.flows.authorizationCode.scopes.keys()),
        )
    # 將權杖快取在會話狀態中並呼叫 API，跳至步驟 5
```

**步驟 3：啟動驗證請求**

如果找不到有效的憑證（步驟 1）和驗證回應（步驟 2），工具需要啟動 OAuth 流程。定義 AuthScheme 和初始 AuthCredential 並呼叫 `tool_context.request_credential()`。傳回一個表示需要授權的回應。

```python
# 使用在工具中設定的 auth_scheme 和 auth_credential。

  tool_context.request_credential(AuthConfig(
    auth_scheme=auth_scheme,
    raw_auth_credential=auth_credential,
  ))
  return {'pending': true, 'message': '正在等待使用者驗證。'}

# 透過設定 request_credential，ADK 會偵測到一個待處理的驗證事件。它會暫停執行並要求終端使用者登入。
```

**步驟 4：將授權碼交換為權杖**

ADK 會自動產生 oauth 授權 URL 並將其呈現給您的代理程式用戶端應用程式。您的代理程式用戶端應用程式應遵循旅程 1 中描述的相同方式將使用者重新導向到授權 URL（附加 `redirect_uri`）。一旦使用者遵循授權 URL 完成登入流程，ADK 會從代理程式用戶端應用程式中提取驗證回呼 URL，自動解析驗證碼，並產生驗證權杖。在下一次工具呼叫時，步驟 2 中的 `tool_context.get_auth_response` 將包含一個有效的憑證，可用於後續的 API 呼叫。

**步驟 5：快取取得的憑證**

在成功從 ADK 取得權杖（步驟 2）或如果權杖仍然有效（步驟 1）之後，**立即將**新的 `Credentials` 物件儲存在 `tool_context.state` 中（序列化，例如，作為 JSON），使用您的快取鍵。

```python
# 在您的工具函式內部，取得 'creds' 之後（無論是重新整理的還是新交換的）
# 快取新的/重新整理的權杖
tool_context.state[TOKEN_CACHE_KEY] = json.loads(creds.to_json())
print(f"DEBUG：在鍵下快取/更新的權杖：{TOKEN_CACHE_KEY}")
# 繼續步驟 6（進行 API 呼叫）

```

**步驟 6：進行經過驗證的 API 呼叫**

* 一旦您有了有效的 `Credentials` 物件（來自步驟 1 或步驟 4 的 `creds`），請使用它來使用適當的用戶端函式庫（例如 `googleapiclient`、`requests`）對受保護的 API 進行實際呼叫。傳遞 `credentials=creds` 參數。
* 包括錯誤處理，特別是對於 `HttpError` 401/403，這可能意味著權杖在呼叫之間已過期或被撤銷。如果您遇到此類錯誤，請考慮清除快取的權杖 (`tool_context.state.pop(...)`)，並可能再次傳回 `auth_required` 狀態以強制重新驗證。

```python
# 在您的工具函式內部，使用有效的 'creds' 物件
# 在繼續之前確保 creds 有效
if not creds or not creds.valid:
   return {"status": "error", "error_message": "沒有有效憑證無法繼續。"}

try:
   service = build("calendar", "v3", credentials=creds) # 範例
   api_result = service.events().list(...).execute()
   # 繼續步驟 7
except Exception as e:
   # 處理 API 錯誤 (例如，檢查 401/403，或許清除快取並重新請求驗證)
   print(f"錯誤：API 呼叫失敗：{e}")
   return {"status": "error", "error_message": f"API 呼叫失敗：{e}"}
```

**步驟 7：傳回工具結果**

* 成功進行 API 呼叫後，將結果處理為對 LLM 有用的字典格式。
* **至關重要的是，** 連同資料一起包含一個 。

```python
# 在您的工具函式內部，成功進行 API 呼叫後
    processed_result = [...] # 為 LLM 處理 api_result
    return {"status": "success", "data": processed_result}

```

??? "完整程式碼"

    === "工具和代理程式"

         ```py title="tools_and_agent.py"
         --8<-- "examples/python/snippets/tools/auth/tools_and_agent.py"
         ```
    === "代理程式 CLI"

         ```py title="agent_cli.py"
         --8<-- "examples/python/snippets/tools/auth/agent_cli.py"
         ```
    === "輔助函式"

         ```py title="helpers.py"
         --8<-- "examples/python/snippets/tools/auth/helpers.py"
         ```
    === "規格"

         ```yaml
         openapi: 3.0.1
         info:
         title: Okta 使用者資訊 API
         version: 1.0.0
         description: |-
            基於有效的 Okta OIDC 存取權杖檢索使用者個人資料資訊的 API。
            驗證是透過與 Okta 的 OpenID Connect 處理的。
         contact:
            name: API 支援
            email: support@example.com # 如果可用，請替換為實際的聯絡方式
         servers:
         - url: <用您的伺服器名稱替換>
            description: 生產環境
         paths:
         /okta-jwt-user-api:
            get:
               summary: 取得已驗證的使用者資訊
               description: |-
               擷取使用者的個人資料詳細資訊
               operationId: getUserInfo
               tags:
               - 使用者個人資料
               security:
               - okta_oidc:
                     - openid
                     - email
                     - profile
               responses:
               '200':
                  description: 成功檢索使用者資訊。
                  content:
                     application/json:
                     schema:
                        type: object
                        properties:
                           sub:
                           type: string
                           description: 使用者的主體識別碼。
                           example: "abcdefg"
                           name:
                           type: string
                           description: 使用者的全名。
                           example: "範例 姓氏"
                           locale:
                           type: string
                           description: 使用者的地區設定，例如 en-US 或 en_US。
                           example: "en_US"
                           email:
                           type: string
                           format: email
                           description: 使用者的主要電子郵件地址。
                           example: "username@example.com"
                           preferred_username:
                           type: string
                           description: 使用者的偏好使用者名稱 (通常是電子郵件)。
                           example: "username@example.com"
                           given_name:
                           type: string
                           description: 使用者的名字。
                           example: "範例"
                           family_name:
                           type: string
                           description: 使用者的姓氏。
                           example: "姓氏"
                           zoneinfo:
                           type: string
                           description: 使用者的時區，例如 America/Los_Angeles。
                           example: "America/Los_Angeles"
                           updated_at:
                           type: integer
                           format: int64 # 使用 int64 表示 Unix 時間戳
                           description: 使用者個人資料上次更新的時間戳 (Unix epoch time)。
                           example: 1743617719
                           email_verified:
                           type: boolean
                           description: 表示使用者的電子郵件地址是否已驗證。
                           example: true
                        required:
                           - sub
                           - name
                           - locale
                           - email
                           - preferred_username
                           - given_name
                           - family_name
                           - zoneinfo
                           - updated_at
                           - email_verified
               '401':
                  description: 未經授權。提供的持有人權杖遺失、無效或已過期。
                  content:
                     application/json:
                     schema:
                        $ref: '#/components/schemas/Error'
               '403':
                  description: 禁止。提供的權杖沒有存取此資源所需的範圍或權限。
                  content:
                     application/json:
                     schema:
                        $ref: '#/components/schemas/Error'
         components:
         securitySchemes:
            okta_oidc:
               type: openIdConnect
               description: 透過 Okta 使用 OpenID Connect 進行驗證。需要持有人存取權杖。
               openIdConnectUrl: https://your-endpoint.okta.com/.well-known/openid-configuration
         schemas:
            Error:
               type: object
               properties:
               code:
                  type: string
                  description: 錯誤代碼。
               message:
                  type: string
                  description: 人類可讀的錯誤訊息。
               required:
                  - code
                  - message
         ```
