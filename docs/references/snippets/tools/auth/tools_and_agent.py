import os

from google.adk.auth.auth_schemes import OpenIdConnectWithConfig
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset
from google.adk.agents.llm_agent import LlmAgent

# --- 驗證設定 ---
# 本節設定代理如何使用 OpenID Connect (OIDC) 處理驗證，
# OIDC 通常建立在 OAuth 2.0 之上。

# 使用 OpenID Connect 定義驗證方案。
# 此物件告訴 ADK *如何*執行 OIDC/OAuth2 流程。
# 它需要您的身分識別提供者（IDP）的特定詳細資訊，例如 Google OAuth、Okta、Auth0 等。
# 注意：請將範例中的 Okta URL 和憑證替換為您實際的 IDP 詳細資訊。
# 以下所有欄位都是必要的，且可從您的 IDP 取得。
auth_scheme = OpenIdConnectWithConfig(
    # 使用者被重新導向以登入的 IDP 授權端點 URL。
    authorization_endpoint="https://your-endpoint.okta.com/oauth2/v1/authorize",
    # 授權碼被交換為權杖的 IDP 權杖端點 URL。
    token_endpoint="https://your-token-endpoint.okta.com/oauth2/v1/token",
    # 您的應用程式向 IDP 請求的範圍（權限）。
    # 'openid' 是 OIDC 的標準。'profile' 和 'email' 請求使用者個人資料資訊。
    scopes=['openid', 'profile', "email"]
)

# 為您的特定應用程式定義驗證憑證。
# 此物件持有您的應用程式在 OAuth2 流程中用來向 IDP
# 識別自己的用戶端識別碼和密鑰。
# !! 安全警告：避免在生產程式碼中硬式編碼密鑰。!!
# !! 請改用環境變數或密鑰管理系統。!!
auth_credential = AuthCredential(
  auth_type=AuthCredentialTypes.OPEN_ID_CONNECT,
  oauth2=OAuth2Auth(
    client_id="CLIENT_ID",
    client_secret="CIENT_SECRET",
  )
)


# --- 從 OpenAPI 規格設定工具集 ---
# 本節定義了代理可以使用的範例工具集，並使用
# 上述步驟中的驗證進行設定。
# 此範例工具集使用受 Okta 保護的端點，並需要 OpenID Connect 流程
# 以取得終端使用者憑證。
with open(os.path.join(os.path.dirname(__file__), 'spec.yaml'), 'r') as f:
    spec_content = f.read()

userinfo_toolset = OpenAPIToolset(
   spec_str=spec_content,
   spec_str_type='yaml',
   # ** 至關重要，將驗證方案和憑證與這些工具關聯起來。**
   # 這告訴 ADK 這些工具需要定義的 OIDC/OAuth2 流程。
   auth_scheme=auth_scheme,
   auth_credential=auth_credential,
)

# --- 代理設定 ---
# 設定並建立主要的 LLM 代理。
root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='enterprise_assistant',
    instruction='協助使用者與多個企業系統整合，包括擷取可能需要驗證的使用者資訊。',
    tools=userinfo_toolset.get_tools(),
)

# --- 準備就緒 ---
# `root_agent` 現在已設定了受 OIDC/OAuth2 驗證保護的工具。
# 當代理嘗試使用其中一個工具時，如果會話中沒有有效的憑證，
# ADK 框架將自動觸發由 `auth_scheme` 和 `auth_credential` 定義的
# 驗證流程。
# 後續的互動流程將引導使用者完成登入過程並處理
# 權杖交換，並自動將交換的權杖附加到
# 工具中定義的端點。
