# src/sre_assistant/auth/auth_factory.py
"""
此檔案實現了認證與授權的工廠模式 (Factory Pattern).
"""

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

# Import the ABC from the new base file
from .base import AuthProvider
# Import shared contracts and concrete providers
from ..contracts import AuthConfig
from .no_auth_provider import NoAuthProvider


class GoogleIAMProvider(AuthProvider):
    def __init__(self, config: AuthConfig):
        self.config = config
        self.credentials = None
        self._init_credentials()

    def _init_credentials(self):
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
        role_mapping = {
            'sre-team@company.com': ['sre-operator', 'viewer'],
            'admin@company.com': ['admin', 'sre-operator'],
        }
        return role_mapping.get(email, ['viewer'])

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
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
        if self.credentials and self.credentials.expired:
            self.credentials.refresh(Request())
            return self.credentials.token
        return None

    async def health_check(self) -> bool:
        try:
            if self.credentials:
                if self.credentials.expired:
                    self.credentials.refresh(Request())
                return True
        except Exception:
            return False
        return False

class OAuth2Provider(AuthProvider):
    def __init__(self, config: AuthConfig):
        self.config = config
        self.http_client = httpx.AsyncClient()
        self.token_endpoint = "https://oauth2.googleapis.com/token"
        self.auth_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
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
        headers = {'Authorization': f'Bearer {access_token}'}
        response = await self.http_client.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
        return response.json() if response.status_code == 200 else {}

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        scopes = user_info.get('scopes', [])
        required_scope = f"{resource}:{action}"
        return required_scope in scopes or 'admin' in scopes

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
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
        try:
            response = await self.http_client.get(self.auth_endpoint)
            return response.status_code < 500
        except Exception:
            return False

class JWTProvider(AuthProvider):
    def __init__(self, config: AuthConfig):
        self.config = config
        self.secret = config.jwt_secret
        self.algorithm = config.jwt_algorithm

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
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
        claims = user_info.get('claims', {})
        permissions = claims.get('permissions', [])
        required_permission = f"{resource}:{action}"
        return required_permission in permissions or 'admin' in user_info.get('roles', [])

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        try:
            payload = jwt.decode(refresh_token, self.secret, algorithms=[self.algorithm])
            new_payload = {**payload, 'exp': datetime.now(timezone.utc) + timedelta(seconds=self.config.jwt_expiry_seconds), 'iat': datetime.now(timezone.utc)}
            return jwt.encode(new_payload, self.secret, algorithm=self.algorithm)
        except jwt.InvalidTokenError:
            return None

    async def health_check(self) -> bool:
        return True

class APIKeyProvider(AuthProvider):
    def __init__(self, config: AuthConfig):
        self.config = config
        self.api_keys = self._load_api_keys()

    def _load_api_keys(self) -> Dict[str, Dict]:
        return {
            hashlib.sha256("test-api-key-123".encode()).hexdigest(): {
                'client_id': 'test-client', 'roles': ['sre-operator'], 'rate_limit': 100
            }
        }

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
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
        roles = user_info.get('roles', [])
        if 'admin' in roles:
            return True
        if 'sre-operator' in roles and action != 'delete':
            return True
        if 'viewer' in roles and action == 'read':
            return True
        return False

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        return None

    async def health_check(self) -> bool:
        return True

class MTLSProvider(AuthProvider):
    def __init__(self, config: AuthConfig):
        self.config = config
        self.ssl_context = self._create_ssl_context()

    def _create_ssl_context(self) -> ssl.SSLContext:
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
        cert = credentials.get('client_cert')
        if not cert:
            return False, None
        try:
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
        org = user_info.get('org', '')
        if org == 'SRE-Team':
            return True
        if org == 'Dev-Team' and action == 'read':
            return True
        return False

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        return None

    async def health_check(self) -> bool:
        try:
            import os
            if self.config.mtls_cert_path:
                return os.path.exists(self.config.mtls_cert_path)
        except Exception:
            return False
        return True

class LocalAuthProvider(AuthProvider):
    def __init__(self, config: AuthConfig):
        self.config = config

    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        return True, {'user_id': 'dev-user', 'email': 'dev@localhost', 'roles': ['admin'], 'auth_method': 'local'}

    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        return True

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        return "local-dev-token"

    async def health_check(self) -> bool:
        return True

class AuthFactory:
    """
    認證提供者工廠類別.
    """

    @staticmethod
    def create(config: AuthConfig) -> AuthProvider:
        """
        根據配置, 創建並返回一個對應的 AuthProvider 實例.
        """
        provider_map = {
            "google_iam": GoogleIAMProvider,
            "oauth2": OAuth2Provider,
            "jwt": JWTProvider,
            "api_key": APIKeyProvider,
            "mtls": MTLSProvider,
            "local": LocalAuthProvider,
            "none": NoAuthProvider,
        }

        provider_key = "none"
        if config and hasattr(config, 'provider') and config.provider:
            provider_key = config.provider.value

        provider_class = provider_map.get(provider_key)

        if not provider_class:
            raise ValueError(f"Unsupported auth provider: {provider_key}")
        return provider_class(config)
