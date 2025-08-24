# sre_assistant/auth/auth_factory.py
"""
認證授權工廠模式實現
支援多種認證提供者的動態切換
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import jwt
import httpx
from google.auth import default
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import ssl
import hashlib
import hmac

# This is a forward declaration, as AuthConfig will be defined in config_manager.py
# We use a TypeVar or a string hint to avoid circular dependencies.
from typing import TypeVar
AuthConfig = TypeVar('AuthConfig')

class AuthProvider(ABC):
    """統一的認證提供者介面"""

    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """
        驗證憑證

        Returns:
            Tuple[bool, Optional[Dict]]: (是否認證成功, 用戶資訊)
        """
        pass

    @abstractmethod
    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """
        授權檢查

        Args:
            user_info: 用戶資訊
            resource: 資源名稱
            action: 操作類型

        Returns:
            是否授權
        """
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """刷新 token"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """健康檢查"""
        pass

class GoogleIAMProvider(AuthProvider):
    """Google IAM 認證提供者"""

    def __init__(self, config: AuthConfig):
        self.config = config
        self.credentials = None
        self._init_credentials()

    def _init_credentials(self):
        """初始化 Google 憑證"""
        try:
            if self.config.service_account_path:
                self.credentials = service_account.Credentials.from_service_account_file(
                    self.config.service_account_path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
            else:
                # 使用預設憑證（例如在 GCE 上）
                self.credentials, _ = default()
        except Exception as e:
            print(f"Failed to initialize Google IAM credentials: {e}")
            self.credentials = None

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """使用 Google IAM 進行認證"""
        try:
            # 驗證 service account token
            token = credentials.get('token')
            if not token:
                return False, None

            # 驗證 token
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
        """從 IAM 獲取用戶角色"""
        # 實際實現會調用 IAM API
        # 這裡簡化為靜態映射
        role_mapping = {
            'sre-team@company.com': ['sre-operator', 'viewer'],
            'admin@company.com': ['admin', 'sre-operator'],
        }
        return role_mapping.get(email, ['viewer'])

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """基於 IAM 角色的授權"""
        if not self.config.enable_rbac:
            return True

        user_roles = user_info.get('roles', [])

        # 定義 RBAC 策略
        rbac_policies = {
            'admin': ['*:*'],  # 所有資源的所有操作
            'sre-operator': [
                'deployment:restart', # Changed from wildcard to be more specific
                'pod:restart',
                'config:read',
                'metrics:read',
                'logs:read'
            ],
            'viewer': [
                '*:read'
            ]
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
        """刷新 Google OAuth token"""
        if self.credentials and self.credentials.expired:
            self.credentials.refresh(Request())
            return self.credentials.token
        return None

    async def health_check(self) -> bool:
        """檢查 IAM 服務健康狀態"""
        try:
            # 嘗試獲取 token 來驗證憑證有效性
            if self.credentials:
                if self.credentials.expired:
                    self.credentials.refresh(Request())
                return True
        except Exception:
            return False
        return False

class OAuth2Provider(AuthProvider):
    """OAuth2 認證提供者"""

    def __init__(self, config: AuthConfig):
        self.config = config
        self.http_client = httpx.AsyncClient()
        self.token_endpoint = "https://oauth2.googleapis.com/token"
        self.auth_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """OAuth2 認證流程"""
        code = credentials.get('code')
        if not code:
            return False, None

        # 交換 authorization code 為 access token
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

            # 獲取用戶資訊
            user_info = await self._get_user_info(token_info['access_token'])
            user_info['access_token'] = token_info['access_token']
            user_info['refresh_token'] = token_info.get('refresh_token')

            return True, user_info

        return False, None

    async def _get_user_info(self, access_token: str) -> Dict:
        """從 OAuth provider 獲取用戶資訊"""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = await self.http_client.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers=headers
        )
        return response.json() if response.status_code == 200 else {}

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """OAuth2 授權（通常需要額外的授權服務）"""
        # 簡化實現：檢查 scope
        scopes = user_info.get('scopes', [])
        required_scope = f"{resource}:{action}"

        return required_scope in scopes or 'admin' in scopes

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """刷新 OAuth2 token"""
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
        """檢查 OAuth2 端點健康狀態"""
        try:
            response = await self.http_client.get(self.auth_endpoint)
            return response.status_code < 500
        except Exception:
            return False

class JWTProvider(AuthProvider):
    """JWT 認證提供者"""

    def __init__(self, config: AuthConfig):
        self.config = config
        self.secret = config.jwt_secret
        self.algorithm = config.jwt_algorithm

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """驗證 JWT token"""
        token = credentials.get('token')
        if not token:
            return False, None

        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )

            # 檢查過期時間
            if 'exp' in payload:
                if datetime.fromtimestamp(payload['exp']) < datetime.utcnow():
                    return False, None

            user_info = {
                'user_id': payload.get('sub'),
                'email': payload.get('email'),
                'roles': payload.get('roles', []),
                'claims': payload
            }

            return True, user_info

        except jwt.InvalidTokenError as e:
            print(f"JWT validation failed: {e}")
            return False, None

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """基於 JWT claims 的授權"""
        claims = user_info.get('claims', {})
        permissions = claims.get('permissions', [])

        required_permission = f"{resource}:{action}"
        return required_permission in permissions or 'admin' in user_info.get('roles', [])

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """生成新的 JWT token"""
        try:
            # 驗證 refresh token
            payload = jwt.decode(
                refresh_token,
                self.secret,
                algorithms=[self.algorithm]
            )

            # 生成新 token
            new_payload = {
                **payload,
                'exp': datetime.utcnow() + timedelta(seconds=self.config.jwt_expiry_seconds),
                'iat': datetime.utcnow()
            }

            return jwt.encode(new_payload, self.secret, algorithm=self.algorithm)

        except jwt.InvalidTokenError:
            return None

    async def health_check(self) -> bool:
        """JWT 提供者總是健康的（無外部依賴）"""
        return True

class APIKeyProvider(AuthProvider):
    """API Key 認證提供者"""

    def __init__(self, config: AuthConfig):
        self.config = config
        self.api_keys = self._load_api_keys()

    def _load_api_keys(self) -> Dict[str, Dict]:
        """載入 API keys"""
        # 實際實現會從文件或數據庫載入
        # 這裡使用硬編碼示例
        return {
            hashlib.sha256("test-api-key-123".encode()).hexdigest(): {
                'client_id': 'test-client',
                'roles': ['sre-operator'],
                'rate_limit': 100
            }
        }

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """驗證 API key"""
        api_key = credentials.get('api_key')
        if not api_key:
            return False, None

        # Hash API key for comparison
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        if key_hash in self.api_keys:
            user_info = self.api_keys[key_hash].copy()
            user_info['auth_method'] = 'api_key'
            return True, user_info

        return False, None

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """基於 API key 權限的授權"""
        roles = user_info.get('roles', [])

        # 簡化的角色權限映射
        if 'admin' in roles:
            return True
        if 'sre-operator' in roles and action != 'delete':
            return True
        if 'viewer' in roles and action == 'read':
            return True

        return False

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """API keys 不需要刷新"""
        return None

    async def health_check(self) -> bool:
        """API key 提供者總是健康的"""
        return True

class MTLSProvider(AuthProvider):
    """mTLS (Mutual TLS) 認證提供者"""

    def __init__(self, config: AuthConfig):
        self.config = config
        self.ssl_context = self._create_ssl_context()

    def _create_ssl_context(self) -> ssl.SSLContext:
        """創建 SSL context"""
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

        try:
            if self.config.mtls_ca_path:
                context.load_verify_locations(self.config.mtls_ca_path)

            if self.config.mtls_cert_path and self.config.mtls_key_path:
                context.load_cert_chain(
                    self.config.mtls_cert_path,
                    self.config.mtls_key_path
                )
        except Exception as e:
            print(f"Failed to create SSL context for mTLS: {e}")

        return context

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """驗證客戶端證書"""
        cert = credentials.get('client_cert')
        if not cert:
            return False, None

        try:
            # 解析證書
            # Note: ssl._ssl._test_decode_cert is not a public API.
            # A more robust solution would use cryptography.x509
            cert_dict = ssl._ssl._test_decode_cert(cert)

            # 提取證書資訊
            subject = dict(x[0] for x in cert_dict['subject'])
            user_info = {
                'cn': subject.get('commonName'),
                'org': subject.get('organizationName'),
                'email': subject.get('emailAddress'),
                'serial': cert_dict.get('serialNumber'),
                'auth_method': 'mtls'
            }

            return True, user_info

        except Exception as e:
            print(f"mTLS authentication failed: {e}")
            return False, None

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """基於證書屬性的授權"""
        # 基於組織的簡單授權
        org = user_info.get('org', '')

        if org == 'SRE-Team':
            return True
        if org == 'Dev-Team' and action == 'read':
            return True

        return False

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """mTLS 不使用 token"""
        return None

    async def health_check(self) -> bool:
        """檢查證書有效性"""
        try:
            # 檢查證書文件是否存在且可讀
            import os
            if self.config.mtls_cert_path:
                return os.path.exists(self.config.mtls_cert_path)
        except Exception:
            return False
        return True

class LocalAuthProvider(AuthProvider):
    """本地開發用認證提供者（無實際認證）"""

    def __init__(self, config: AuthConfig):
        self.config = config

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """本地開發總是認證成功"""
        return True, {
            'user_id': 'dev-user',
            'email': 'dev@localhost',
            'roles': ['admin'],
            'auth_method': 'local'
        }

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """本地開發總是授權"""
        return True

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """本地開發不需要 token"""
        return "local-dev-token"

    async def health_check(self) -> bool:
        """本地開發總是健康"""
        return True

class AuthFactory:
    """認證提供者工廠"""

    @staticmethod
    def create(config: AuthConfig) -> AuthProvider:
        """根據配置創建認證提供者"""

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
