# src/sre_assistant/auth/auth_factory.py
"""
此檔案實現了認證與授權的工廠模式 (Factory Pattern)。

核心思想是定義一個抽象的 `AuthProvider` 介面，並為每種認證方式
（如 Google IAM, OAuth2, JWT 等）提供一個具體的實現。
`AuthFactory` 類別則根據應用程式的配置，動態地創建並返回
一個對應的認證提供者實例。

這種設計模式有以下優點：
- **解耦 (Decoupling)**: 將認證邏輯與使用它的業務邏輯分離。
- **可擴展性 (Scalability)**: 新增一種認證方式時，只需實現一個新的提供者類別，
  而無需修改現有程式碼。
- **易於測試 (Testability)**: 可以輕鬆地為每種提供者編寫單獨的測試，
  或在測試環境中使用一個模擬的提供者 (如 `LocalAuthProvider`)。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta, timezone
import jwt
import httpx
from google.auth import default
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import ssl
import hashlib
import hmac

# 這是 AuthConfig 的前向宣告 (Forward Declaration)。
# 由於 AuthConfig 在 config_manager.py 中定義，為了避免循環依賴，
# 此處使用 TypeVar 或字串提示。
from typing import TypeVar
AuthConfig = TypeVar('AuthConfig')

class AuthProvider(ABC):
    """
    統一的認證提供者抽象基礎類別 (Interface)。

    所有具體的認證提供者都必須繼承此類別並實現其定義的抽象方法。
    這確保了所有提供者都有一致的介面。
    """

    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """
        驗證使用者提供的憑證。

        Args:
            credentials (Dict[str, Any]): 一個包含認證資訊的字典，
                                         例如 `{'token': '...'}` 或 `{'api_key': '...'}`。

        Returns:
            Tuple[bool, Optional[Dict]]: 一個元組，包含布林值的成功狀態和一個可選的用戶資訊字典。
        """
        pass

    @abstractmethod
    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """
        根據用戶資訊，檢查其是否有權限在指定資源上執行特定操作。

        Args:
            user_info (Dict): 經過 `authenticate` 方法驗證後返回的用戶資訊。
            resource (str): 正在被存取的資源名稱 (例如 'deployment')。
            action (str): 正在執行的操作 (例如 'restart', 'read')。

        Returns:
            bool: 如果用戶有權限，返回 True，否則返回 False。
        """
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        使用 refresh token 來獲取一個新的 access token。

        Args:
            refresh_token (str): 用於刷新憑證的令牌。

        Returns:
            Optional[str]: 一個新的 access token，如果刷新失敗則返回 None。
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        檢查認證提供者自身的健康狀況。

        例如，檢查是否能連線到遠端的認證伺服器。

        Returns:
            bool: 如果提供者健康，返回 True，否則返回 False。
        """
        pass

class GoogleIAMProvider(AuthProvider):
    """
    Google Cloud Identity and Access Management (IAM) 認證提供者。

    此提供者適用於在 Google Cloud 環境中運行的服務，
    它利用服務帳號 (Service Account) 或應用程式預設憑證 (ADC) 進行認證。
    """

    def __init__(self, config: AuthConfig):
        """
        初始化 GoogleIAMProvider。

        Args:
            config (AuthConfig): 包含認證設定的配置物件。
        """
        self.config = config
        self.credentials = None
        self._init_credentials()

    def _init_credentials(self):
        """
        初始化 Google Cloud IAM 憑證。

        此方法會根據配置嘗試載入服務帳號檔案，如果未提供路徑，
        則會嘗試使用應用程式預設憑證 (ADC)。
        這使得代理在本地和 Google Cloud 環境中都能無縫工作。
        """
        try:
            if self.config.service_account_path:
                self.credentials = service_account.Credentials.from_service_account_file(
                    self.config.service_account_path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
            else:
                self.credentials, _ = default()
        except Exception as e:
            print(f"Failed to initialize Google IAM credentials: {e}")
            self.credentials = None

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """
        使用 Google IAM 驗證一個 OAuth2 ID Token。

        此方法會驗證傳入的 token，並從中提取用戶的 email 等資訊。

        Args:
            credentials (Dict[str, Any]): 包含 'token' 鍵的字典。

        Returns:
            Tuple[bool, Optional[Dict]]: 驗證成功時返回 True 和用戶資訊，否則返回 False 和 None。
        """
        try:
            token = credentials.get('token')
            if not token:
                return False, None

            import google.auth.transport.requests
            import google.oauth2.id_token

            request = google.auth.transport.requests.Request()
            claims = google.oauth2.id_token.verify_oauth2_token(
                token, request, self.config.oauth_client_id
            )

            user_info = {
                'email': claims.get('email'),
                'sub': claims.get('sub'),
                'roles': self._get_user_roles(claims.get('email'))
            }
            return True, user_info
        except Exception as e:
            print(f"Google IAM authentication failed: {e}")
            return False, None

    def _get_user_roles(self, email: str) -> List[str]:
        """
        根據用戶 email 從 IAM 獲取其角色列表。

        注意：這是一個簡化的實現。在生產環境中，應調用 Google Cloud IAM API
        來動態查詢用戶的角色和權限。

        Args:
            email (str): 用戶的電子郵件地址。

        Returns:
            List[str]: 該用戶所擁有的角色列表。
        """
        role_mapping = {
            'sre-team@company.com': ['sre-operator', 'viewer'],
            'admin@company.com': ['admin', 'sre-operator'],
        }
        return role_mapping.get(email, ['viewer'])

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """
        基於 IAM 角色的授權檢查 (RBAC)。

        此方法會檢查用戶的角色是否包含執行特定操作的權限。

        Args:
            user_info (Dict): 包含 'roles' 列表的用戶資訊。
            resource (str): 資源名稱。
            action (str): 操作類型。

        Returns:
            bool: 如果授權，返回 True，否則返回 False。
        """
        if not self.config.enable_rbac:
            return True

        user_roles = user_info.get('roles', [])
        rbac_policies = {
            'admin': ['*:*'],
            'sre-operator': ['deployment:restart', 'pod:restart', 'config:read', 'metrics:read', 'logs:read'],
            'viewer': ['*:read']
        }

        for role in user_roles:
            if role in rbac_policies:
                for policy in rbac_policies[role]:
                    resource_pattern, action_pattern = policy.split(':')
                    if (resource_pattern == '*' or resource_pattern == resource) and \
                       (action_pattern == '*' or action_pattern == action):
                        return True
        return False

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        刷新 Google OAuth token。

        如果當前的 access token 已過期，則使用 refresh token 獲取新的 token。

        Args:
            refresh_token (str): Google OAuth refresh token。

        Returns:
            Optional[str]: 新的 access token，如果失敗則返回 None。
        """
        if self.credentials and self.credentials.expired:
            self.credentials.refresh(Request())
            return self.credentials.token
        return None

    async def health_check(self) -> bool:
        """
        檢查 Google IAM 服務的健康狀態。

        透過嘗試刷新憑證來驗證與 IAM 服務的連通性。

        Returns:
            bool: 如果健康，返回 True。
        """
        try:
            if self.credentials:
                if self.credentials.expired:
                    self.credentials.refresh(Request())
                return True
        except Exception:
            return False
        return False

class OAuth2Provider(AuthProvider):
    """
    標準的 OAuth 2.0 認證提供者 (Authorization Code Flow)。

    此提供者用於與任何支援 OAuth 2.0 的身份提供者 (如 Google) 整合。
    """

    def __init__(self, config: AuthConfig):
        """
        初始化 OAuth2Provider。

        Args:
            config (AuthConfig): 包含 OAuth2 客戶端設定的配置物件。
        """
        self.config = config
        self.http_client = httpx.AsyncClient()
        self.token_endpoint = "https://oauth2.googleapis.com/token"
        self.auth_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """
        執行 OAuth 2.0 認證流程。

        使用授權碼 (authorization code) 從 token 端點交換 access token。

        Args:
            credentials (Dict[str, Any]): 包含 'code' 的字典。

        Returns:
            Tuple[bool, Optional[Dict]]: 驗證成功時返回 True 和用戶資訊，否則返回 False 和 None。
        """
        code = credentials.get('code')
        if not code:
            return False, None

        token_data = {
            'code': code,
            'client_id': self.config.oauth_client_id,
            'client_secret': self.config.oauth_client_secret,
            'redirect_uri': self.config.oauth_redirect_uri,
            'grant_type': 'authorization_code'
        }
        response = await self.http_client.post(self.token_endpoint, data=token_data)

        if response.status_code == 200:
            token_info = response.json()
            user_info = await self._get_user_info(token_info['access_token'])
            user_info['access_token'] = token_info['access_token']
            user_info['refresh_token'] = token_info.get('refresh_token')
            return True, user_info
        return False, None

    async def _get_user_info(self, access_token: str) -> Dict:
        """
        使用 access token 從身份提供者獲取用戶資訊。

        Args:
            access_token (str): 用於 API 請求的 access token。

        Returns:
            Dict: 包含用戶 email, sub 等資訊的字典。
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        response = await self.http_client.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
        return response.json() if response.status_code == 200 else {}

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """
        基於 OAuth scope 的授權檢查。

        這是一個簡化的實現，真實場景可能需要更複雜的授權服務。

        Args:
            user_info (Dict): 包含 'scopes' 列表的用戶資訊。
            resource (str): 資源名稱。
            action (str): 操作類型。

        Returns:
            bool: 如果授權，返回 True。
        """
        scopes = user_info.get('scopes', [])
        required_scope = f"{resource}:{action}"
        return required_scope in scopes or 'admin' in scopes

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        使用 refresh token 刷新 OAuth 2.0 的 access token。

        Args:
            refresh_token (str): 用於刷新的令牌。

        Returns:
            Optional[str]: 新的 access token，如果失敗則返回 None。
        """
        token_data = {
            'refresh_token': refresh_token,
            'client_id': self.config.oauth_client_id,
            'client_secret': self.config.oauth_client_secret,
            'grant_type': 'refresh_token'
        }
        response = await self.http_client.post(self.token_endpoint, data=token_data)
        if response.status_code == 200:
            return response.json().get('access_token')
        return None

    async def health_check(self) -> bool:
        """
        檢查 OAuth 2.0 身份提供者的健康狀態。

        Args:
            bool: 如果端點可達，返回 True。
        """
        try:
            response = await self.http_client.get(self.auth_endpoint)
            return response.status_code < 500
        except Exception:
            return False

class JWTProvider(AuthProvider):
    """
    JSON Web Token (JWT) 認證提供者。

    此提供者用於驗證傳入的 JWT，並從其 payload 中提取用戶資訊和權限。
    """

    def __init__(self, config: AuthConfig):
        """
        初始化 JWTProvider。

        Args:
            config (AuthConfig): 包含 JWT 密鑰和演算法的配置物件。
        """
        self.config = config
        self.secret = config.jwt_secret
        self.algorithm = config.jwt_algorithm

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """
        驗證 JWT token 的簽名和過期時間。

        Args:
            credentials (Dict[str, Any]): 包含 'token' 的字典。

        Returns:
            Tuple[bool, Optional[Dict]]: 驗證成功時返回 True 和用戶資訊，否則返回 False 和 None。
        """
        token = credentials.get('token')
        if not token:
            return False, None
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            if 'exp' in payload and datetime.fromtimestamp(payload['exp'], tz=timezone.utc) < datetime.now(timezone.utc):
                return False, None
            user_info = {'user_id': payload.get('sub'), 'email': payload.get('email'), 'roles': payload.get('roles', []), 'claims': payload}
            return True, user_info
        except jwt.InvalidTokenError as e:
            print(f"JWT validation failed: {e}")
            return False, None

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """
        基於 JWT payload 中的 claims (如 permissions) 進行授權。

        Args:
            user_info (Dict): 包含 'claims' 和 'roles' 的用戶資訊。
            resource (str): 資源名稱。
            action (str): 操作類型。

        Returns:
            bool: 如果授權，返回 True。
        """
        claims = user_info.get('claims', {})
        permissions = claims.get('permissions', [])
        required_permission = f"{resource}:{action}"
        return required_permission in permissions or 'admin' in user_info.get('roles', [])

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        驗證 refresh token 並生成一個新的 JWT access token。

        Args:
            refresh_token (str): 用於刷新的 JWT。

        Returns:
            Optional[str]: 新的 JWT，如果失敗則返回 None。
        """
        try:
            payload = jwt.decode(refresh_token, self.secret, algorithms=[self.algorithm])
            new_payload = {**payload, 'exp': datetime.now(timezone.utc) + timedelta(seconds=self.config.jwt_expiry_seconds), 'iat': datetime.now(timezone.utc)}
            return jwt.encode(new_payload, self.secret, algorithm=self.algorithm)
        except jwt.InvalidTokenError:
            return None

    async def health_check(self) -> bool:
        """
        JWT 提供者是無狀態的，因此總是健康的。

        Returns:
            bool: 總是 True。
        """
        return True

class APIKeyProvider(AuthProvider):
    """
    API Key 認證提供者。

    這是一種簡單的認證方式，客戶端在請求頭中提供一個預共享的 API Key。
    """

    def __init__(self, config: AuthConfig):
        """
        初始化 APIKeyProvider。

        Args:
            config (AuthConfig): 相關配置。
        """
        self.config = config
        self.api_keys = self._load_api_keys()

    def _load_api_keys(self) -> Dict[str, Dict]:
        """
        從安全的位置載入 API Key 及其對應的權限。

        注意：這是一個簡化的實現。生產環境應從安全的秘密管理器或
        加密的檔案中載入。絕不能將 Key 硬編碼。

        Returns:
            Dict[str, Dict]: 一個映射，鍵是 API Key 的雜湊值，值是用戶資訊。
        """
        return {
            hashlib.sha256("test-api-key-123".encode()).hexdigest(): {
                'client_id': 'test-client', 'roles': ['sre-operator'], 'rate_limit': 100
            }
        }

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """
        驗證 API Key。

        為了安全，此方法會對傳入的 Key 進行雜湊，然後與已存儲的雜湊值進行比較。

        Args:
            credentials (Dict[str, Any]): 包含 'api_key' 的字典。

        Returns:
            Tuple[bool, Optional[Dict]]: 驗證成功時返回 True 和用戶資訊。
        """
        api_key = credentials.get('api_key')
        if not api_key:
            return False, None
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        if key_hash in self.api_keys:
            user_info = self.api_keys[key_hash].copy()
            user_info['auth_method'] = 'api_key'
            return True, user_info
        return False, None

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """
        基於與 API Key 關聯的角色進行授權。

        Args:
            user_info (Dict): 包含 'roles' 的用戶資訊。
            resource (str): 資源名稱。
            action (str): 操作類型。

        Returns:
            bool: 如果授權，返回 True。
        """
        roles = user_info.get('roles', [])
        if 'admin' in roles:
            return True
        if 'sre-operator' in roles and action != 'delete':
            return True
        if 'viewer' in roles and action == 'read':
            return True
        return False

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        API Key 通常是靜態的，不需要刷新。

        Returns:
            None
        """
        return None

    async def health_check(self) -> bool:
        """
        API Key 提供者是無狀態的，總是健康的。

        Returns:
            bool: 總是 True。
        """
        return True

class MTLSProvider(AuthProvider):
    """
    mTLS (Mutual TLS) 相互傳輸層安全性協定認證提供者。

    此提供者透過驗證客戶端提供的 TLS 證書來進行認證。
    """

    def __init__(self, config: AuthConfig):
        """
        初始化 MTLSProvider。

        Args:
            config (AuthConfig): 包含 CA、證書和金鑰路徑的配置。
        """
        self.config = config
        self.ssl_context = self._create_ssl_context()

    def _create_ssl_context(self) -> ssl.SSLContext:
        """
        根據配置創建用於 mTLS 的 SSL 上下文。

        Returns:
            ssl.SSLContext: 配置好的 SSL 上下文。
        """
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        try:
            if self.config.mtls_ca_path:
                context.load_verify_locations(self.config.mtls_ca_path)
            if self.config.mtls_cert_path and self.config.mtls_key_path:
                context.load_cert_chain(self.config.mtls_cert_path, self.config.mtls_key_path)
        except Exception as e:
            print(f"Failed to create SSL context for mTLS: {e}")
        return context

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """
        驗證客戶端證書並提取用戶資訊。

        Args:
            credentials (Dict[str, Any]): 包含 'client_cert' 的字典。

        Returns:
            Tuple[bool, Optional[Dict]]: 驗證成功時返回 True 和用戶資訊。
        """
        cert = credentials.get('client_cert')
        if not cert:
            return False, None
        try:
            # 注意: _test_decode_cert 不是公開 API，生產環境應使用 cryptography.x509
            cert_dict = ssl._ssl._test_decode_cert(cert)
            subject = dict(x[0] for x in cert_dict['subject'])
            user_info = {
                'cn': subject.get('commonName'), 'org': subject.get('organizationName'),
                'email': subject.get('emailAddress'), 'serial': cert_dict.get('serialNumber'),
                'auth_method': 'mtls'
            }
            return True, user_info
        except Exception as e:
            print(f"mTLS authentication failed: {e}")
            return False, None

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """
        基於客戶端證書中的屬性（如組織名稱）進行授權。

        Args:
            user_info (Dict): 從證書中提取的用戶資訊。
            resource (str): 資源名稱。
            action (str): 操作類型。

        Returns:
            bool: 如果授權，返回 True。
        """
        org = user_info.get('org', '')
        if org == 'SRE-Team':
            return True
        if org == 'Dev-Team' and action == 'read':
            return True
        return False

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        mTLS 不使用令牌，因此無需刷新。

        Returns:
            None
        """
        return None

    async def health_check(self) -> bool:
        """
        檢查 mTLS 證書檔案是否存在且可讀。

        Returns:
            bool: 如果健康，返回 True。
        """
        try:
            import os
            if self.config.mtls_cert_path:
                return os.path.exists(self.config.mtls_cert_path)
        except Exception:
            return False
        return True

class LocalAuthProvider(AuthProvider):
    """
    本地開發用的認證提供者。

    此提供者不執行任何實際的認證或授權檢查，主要用於簡化本地開發和測試流程。
    它總是返回一個固定的、具有管理員權限的開發用戶。
    """

    def __init__(self, config: AuthConfig):
        """
        初始化 LocalAuthProvider。

        Args:
            config (AuthConfig): 相關配置。
        """
        self.config = config

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """
        在本地開發環境中，總是返回認證成功。

        Returns:
            Tuple[bool, Optional[Dict]]: 總是 (True, dev_user_info)。
        """
        return True, {'user_id': 'dev-user', 'email': 'dev@localhost', 'roles': ['admin'], 'auth_method': 'local'}

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """
        在本地開發環境中，總是授權成功。

        Returns:
            bool: 總是 True。
        """
        return True

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        本地開發不需要刷新令牌。

        Returns:
            str: 一個固定的開發令牌。
        """
        return "local-dev-token"

    async def health_check(self) -> bool:
        """
        本地開發提供者總是健康的。

        Returns:
            bool: 總是 True。
        """
        return True

class AuthFactory:
    """
    認證提供者工廠類別。

    這是一個靜態類別，其唯一的職責是根據配置創建正確的認證提供者實例。
    """

    @staticmethod
    def create(config: AuthConfig) -> AuthProvider:
        """
        根據配置，創建並返回一個對應的 AuthProvider 實例。

        這利用了一個映射 (dictionary) 來將配置中的提供者名稱
        對應到具體的提供者類別，從而實現了動態創建。

        Args:
            config (AuthConfig): 包含 `provider` 名稱的配置物件。

        Raises:
            ValueError: 如果配置中指定的提供者不被支援。

        Returns:
            AuthProvider: 一個具體的認證提供者實例。
        """
        provider_map = {
            "google_iam": GoogleIAMProvider,
            "oauth2": OAuth2Provider,
            "jwt": JWTProvider,
            "api_key": APIKeyProvider,
            "mtls": MTLSProvider,
            "local": LocalAuthProvider
        }
        provider_class = provider_map.get(config.provider.value)
        if not provider_class:
            raise ValueError(f"Unsupported auth provider: {config.provider}")
        return provider_class(config)
