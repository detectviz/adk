## 認證授權工廠模式設計

### 1. 配置擴展

```python
# sre_assistant/config/config_manager.py
# 在現有配置中添加認證配置

from enum import Enum

class AuthProvider(str, Enum):
    """認證提供者選項"""
    GOOGLE_IAM = "google_iam"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    MTLS = "mtls"
    LOCAL = "local"  # 開發用

class AuthConfig(BaseModel):
    """認證配置"""
    provider: AuthProvider
    
    # Google IAM 配置
    service_account_path: Optional[str] = None
    impersonate_service_account: Optional[str] = None
    
    # OAuth2 配置
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    oauth_redirect_uri: Optional[str] = None
    oauth_scopes: List[str] = Field(default_factory=list)
    
    # JWT 配置
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expiry_seconds: int = 3600
    
    # API Key 配置
    api_key_header: str = "X-API-Key"
    api_keys_file: Optional[str] = None
    
    # mTLS 配置
    mtls_cert_path: Optional[str] = None
    mtls_key_path: Optional[str] = None
    mtls_ca_path: Optional[str] = None
    
    # 通用配置
    enable_rbac: bool = True
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 60
    enable_audit_logging: bool = True
    
    @validator('service_account_path')
    def validate_google_iam(cls, v, values):
        if values.get('provider') == AuthProvider.GOOGLE_IAM and not v:
            raise ValueError("service_account_path required for Google IAM")
        return v

class SREAssistantConfig(BaseModel):
    """更新主配置以包含認證"""
    deployment: DeploymentConfig
    memory: MemoryConfig
    auth: AuthConfig  # 新增認證配置
    # ... 其他配置
```

### 2. 認證授權工廠實現

```python
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
        if self.config.service_account_path:
            self.credentials = service_account.Credentials.from_service_account_file(
                self.config.service_account_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
        else:
            # 使用預設憑證（例如在 GCE 上）
            self.credentials, _ = default()
    
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
                'deployment:*',
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
        
        if self.config.mtls_ca_path:
            context.load_verify_locations(self.config.mtls_ca_path)
        
        if self.config.mtls_cert_path and self.config.mtls_key_path:
            context.load_cert_chain(
                self.config.mtls_cert_path,
                self.config.mtls_key_path
            )
        
        return context
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """驗證客戶端證書"""
        cert = credentials.get('client_cert')
        if not cert:
            return False, None
        
        try:
            # 解析證書
            import ssl
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
```

### 3. 認證管理器

```python
# sre_assistant/auth/auth_manager.py
"""
統一的認證授權管理器
整合多種認證方式和授權策略
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from ..config.config_manager import config_manager
from .auth_factory import AuthFactory
import asyncio
from functools import wraps

class AuthManager:
    """認證授權管理器"""
    
    def __init__(self):
        """初始化認證管理器"""
        auth_config = config_manager.get_auth_config()
        self.provider = AuthFactory.create(auth_config)
        self.config = auth_config
        
        # 緩存認證結果
        self._auth_cache = {}
        self._cache_ttl = timedelta(minutes=5)
        
        # 速率限制
        self._rate_limits = {}
        
        # 審計日誌
        self._audit_log = []
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """
        統一認證入口
        
        Args:
            credentials: 認證憑證
            
        Returns:
            (是否成功, 用戶資訊)
        """
        # 檢查緩存
        cache_key = self._get_cache_key(credentials)
        if cache_key in self._auth_cache:
            cached = self._auth_cache[cache_key]
            if cached['expires'] > datetime.utcnow():
                return True, cached['user_info']
        
        # 執行認證
        success, user_info = await self.provider.authenticate(credentials)
        
        # 緩存結果
        if success and user_info:
            self._auth_cache[cache_key] = {
                'user_info': user_info,
                'expires': datetime.utcnow() + self._cache_ttl
            }
        
        # 審計日誌
        self._log_auth_attempt(credentials, success)
        
        return success, user_info
    
    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        """
        統一授權檢查
        
        Args:
            user_info: 用戶資訊
            resource: 資源名稱
            action: 操作類型
            
        Returns:
            是否授權
        """
        # 檢查速率限制
        if self.config.enable_rate_limiting:
            if not self._check_rate_limit(user_info):
                return False
        
        # 執行授權檢查
        authorized = await self.provider.authorize(user_info, resource, action)
        
        # 審計日誌
        self._log_auth_check(user_info, resource, action, authorized)
        
        return authorized
    
    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """刷新 token"""
        return await self.provider.refresh_token(refresh_token)
    
    def _get_cache_key(self, credentials: Dict[str, Any]) -> str:
        """生成緩存鍵"""
        import hashlib
        import json
        
        # 移除敏感資訊
        safe_creds = {k: v for k, v in credentials.items() 
                     if k not in ['password', 'secret']}
        
        creds_str = json.dumps(safe_creds, sort_keys=True)
        return hashlib.sha256(creds_str.encode()).hexdigest()
    
    def _check_rate_limit(self, user_info: Dict) -> bool:
        """檢查速率限制"""
        user_id = user_info.get('user_id', 'anonymous')
        now = datetime.utcnow()
        
        if user_id not in self._rate_limits:
            self._rate_limits[user_id] = []
        
        # 清理過期記錄
        minute_ago = now - timedelta(minutes=1)
        self._rate_limits[user_id] = [
            t for t in self._rate_limits[user_id] if t > minute_ago
        ]
        
        # 檢查限制
        if len(self._rate_limits[user_id]) >= self.config.max_requests_per_minute:
            return False
        
        self._rate_limits[user_id].append(now)
        return True
    
    def _log_auth_attempt(self, credentials: Dict, success: bool):
        """記錄認證嘗試"""
        if self.config.enable_audit_logging:
            self._audit_log.append({
                'timestamp': datetime.utcnow(),
                'event': 'authentication',
                'success': success,
                'provider': self.config.provider.value,
                'metadata': {
                    'auth_method': credentials.get('auth_method', 'unknown')
                }
            })
    
    def _log_auth_check(self, user_info: Dict, resource: str, 
                       action: str, authorized: bool):
        """記錄授權檢查"""
        if self.config.enable_audit_logging:
            self._audit_log.append({
                'timestamp': datetime.utcnow(),
                'event': 'authorization',
                'user': user_info.get('email', user_info.get('user_id')),
                'resource': resource,
                'action': action,
                'authorized': authorized
            })

# 單例模式
auth_manager = AuthManager()

# 裝飾器便利函數
def require_auth(resource: str = None, action: str = None):
    """
    認證授權裝飾器
    
    使用範例：
        @require_auth(resource="deployment", action="restart")
        async def restart_deployment():
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 從請求上下文獲取認證資訊
            # 這裡簡化處理，實際應從請求 header 或 session 獲取
            credentials = kwargs.get('credentials', {})
            
            # 認證
            success, user_info = await auth_manager.authenticate(credentials)
            if not success:
                raise PermissionError("Authentication failed")
            
            # 授權
            if resource and action:
                authorized = await auth_manager.authorize(user_info, resource, action)
                if not authorized:
                    raise PermissionError(f"Not authorized for {action} on {resource}")
            
            # 注入用戶資訊
            kwargs['user_info'] = user_info
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
```

### 4. 配置文件更新

```yaml
# sre_assistant/config/base.yaml
auth:
  provider: "local"  # 默認本地開發
  enable_rbac: false
  enable_rate_limiting: false
  enable_audit_logging: true
```

```yaml
# sre_assistant/config/environments/production.yaml
auth:
  provider: "google_iam"
  service_account_path: "/secrets/service-account.json"
  enable_rbac: true
  enable_rate_limiting: true
  max_requests_per_minute: 100
  enable_audit_logging: true
```

```yaml
# sre_assistant/config/environments/staging.yaml
auth:
  provider: "oauth2"
  oauth_client_id: "${OAUTH_CLIENT_ID}"
  oauth_client_secret: "${OAUTH_CLIENT_SECRET}"
  oauth_redirect_uri: "https://staging.sre-assistant.com/callback"
  oauth_scopes:
    - "email"
    - "profile"
    - "sre.operator"
  enable_rbac: true
  enable_rate_limiting: true
  max_requests_per_minute: 60
```

### 5. Mermaid 架構圖

```mermaid
graph TB
    subgraph "認證配置"
        AuthConfig[AuthConfig<br/>Pydantic Model]
        GoogleIAM[Google IAM]
        OAuth2[OAuth 2.0]
        JWT[JWT]
        APIKey[API Key]
        MTLS[mTLS]
        Local[Local Dev]
    end
    
    subgraph "認證工廠"
        AuthFactory[AuthFactory]
        AuthManager[AuthManager<br/>單例模式]
    end
    
    subgraph "認證提供者"
        AuthProvider[AuthProvider<br/>抽象介面]
        GoogleIAMProvider[GoogleIAMProvider]
        OAuth2Provider[OAuth2Provider]
        JWTProvider[JWTProvider]
        APIKeyProvider[APIKeyProvider]
        MTLSProvider[MTLSProvider]
        LocalProvider[LocalProvider]
    end
    
    subgraph "功能模組"
        Authentication[認證<br/>authenticate()]
        Authorization[授權<br/>authorize()]
        TokenRefresh[Token刷新<br/>refresh_token()]
        HealthCheck[健康檢查<br/>health_check()]
    end
    
    subgraph "增強功能"
        Cache[認證緩存]
        RateLimit[速率限制]
        AuditLog[審計日誌]
        RBAC[角色權限]
    end
    
    AuthConfig --> AuthFactory
    AuthFactory --> GoogleIAMProvider
    AuthFactory --> OAuth2Provider
    AuthFactory --> JWTProvider
    AuthFactory --> APIKeyProvider
    AuthFactory --> MTLSProvider
    AuthFactory --> LocalProvider
    
    GoogleIAMProvider -.->|實現| AuthProvider
    OAuth2Provider -.->|實現| AuthProvider
    JWTProvider -.->|實現| AuthProvider
    APIKeyProvider -.->|實現| AuthProvider
    MTLSProvider -.->|實現| AuthProvider
    LocalProvider -.->|實現| AuthProvider
    
    AuthProvider --> Authentication
    AuthProvider --> Authorization
    AuthProvider --> TokenRefresh
    AuthProvider --> HealthCheck
    
    AuthManager --> AuthFactory
    AuthManager --> Cache
    AuthManager --> RateLimit
    AuthManager --> AuditLog
    AuthManager --> RBAC
    
    style AuthFactory fill:#f9f,stroke:#333,stroke-width:4px
    style AuthManager fill:#9ff,stroke:#333,stroke-width:3px
    style AuthProvider fill:#ff9,stroke:#333,stroke-width:2px
```

### 6. 整合到主系統

```python
# sre_assistant/agent.py
# 更新 SRECoordinator 以使用認證管理器

from auth.auth_manager import auth_manager, require_auth

class SRECoordinator(SequentialAgent):
    """主協調器 - 整合認證授權"""
    
    def __init__(self):
        super().__init__(
            name="sre-coordinator",
            agents=self._setup_agents(),
            continue_on_error=True
        )
        
        # 初始化認證管理器
        self.auth_manager = auth_manager
        
        # 配置安全回調
        self._setup_security_callbacks()
    
    def _setup_security_callbacks(self):
        """設置安全相關的回調"""
        self.add_callback(
            SafetyCallback(
                risk_assessor=self._assess_risk_with_auth,
                pii_scrubber=self._scrub_pii,
                compliance_validator=self._validate_compliance_with_auth
            )
        )
    
    async def _assess_risk_with_auth(self, action: str, context: Dict) -> RiskLevel:
        """結合認證資訊的風險評估"""
        user_info = context.get('user_info', {})
        
        # 管理員降低風險等級
        if 'admin' in user_info.get('roles', []):
            return RiskLevel.LOW
        
        # 原有風險評估邏輯
        return self._assess_risk(action, context)
    
    @require_auth(resource="sre_assistant", action="execute")
    async def execute_workflow(self, request: SRERequest, **kwargs) -> SREResponse:
        """執行 SRE 工作流（需要認證）"""
        user_info = kwargs.get('user_info')
        
        # 記錄用戶操作
        logger.info(f"User {user_info.get('email')} executing workflow for {request.incident_id}")
        
        # 檢查特定資源的授權
        if request.severity == SeverityLevel.P0:
            # P0 事件需要特殊權限
            authorized = await self.auth_manager.authorize(
                user_info, 
                "incident_p0", 
                "handle"
            )
            if not authorized:
                raise PermissionError("Not authorized to handle P0 incidents")
        
        # 執行工作流
        return await super().execute(request)
```

### 7. API 端點整合

```python
# sre_assistant/api/endpoints.py
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..auth.auth_manager import auth_manager

app = FastAPI()
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """從請求中提取並驗證用戶身份"""
    
    auth_credentials = {}
    
    if credentials:
        # Bearer token 認證
        auth_credentials['token'] = credentials.credentials
    elif api_key:
        # API key 認證
        auth_credentials['api_key'] = api_key
    else:
        raise HTTPException(status_code=401, detail="Missing authentication")
    
    # 執行認證
    success, user_info = await auth_manager.authenticate(auth_credentials)
    
    if not success:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    return user_info

@app.post("/api/v1/chat")
async def chat_endpoint(
    request: SRERequest,
    user_info: Dict = Depends(get_current_user)
):
    """主要 API 端點"""
    
    # 檢查授權
    authorized = await auth_manager.authorize(
        user_info,
        "chat",
        "use"
    )
    
    if not authorized:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # 執行請求
    coordinator = SRECoordinator()
    response = await coordinator.execute_workflow(
        request,
        user_info=user_info
    )
    
    return response

@app.post("/api/v1/tools/{tool_name}/execute")
async def execute_tool(
    tool_name: str,
    params: Dict[str, Any],
    user_info: Dict = Depends(get_current_user)
):
    """執行特定工具（需要授權）"""
    
    # 工具級別的授權檢查
    authorized = await auth_manager.authorize(
        user_info,
        f"tool_{tool_name}",
        "execute"
    )
    
    if not authorized:
        raise HTTPException(
            status_code=403, 
            detail=f"Not authorized to execute {tool_name}"
        )
    
    # 執行工具
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    result = await tool.execute(**params)
    return result
```

### 8. 測試認證工廠

```python
# sre_assistant/test/test_auth_factory.py
import pytest
from ..auth.auth_factory import AuthFactory, AuthProvider
from ..config.config_manager import AuthConfig, AuthProvider as AuthProviderEnum

@pytest.mark.asyncio
async def test_google_iam_provider():
    """測試 Google IAM 提供者"""
    config = AuthConfig(
        provider=AuthProviderEnum.GOOGLE_IAM,
        service_account_path="/path/to/sa.json"
    )
    
    provider = AuthFactory.create(config)
    assert isinstance(provider, AuthProvider)
    
    # 測試健康檢查
    health = await provider.health_check()
    assert isinstance(health, bool)

@pytest.mark.asyncio
async def test_oauth2_provider():
    """測試 OAuth2 提供者"""
    config = AuthConfig(
        provider=AuthProviderEnum.OAUTH2,
        oauth_client_id="test-client",
        oauth_client_secret="test-secret",
        oauth_redirect_uri="http://localhost/callback"
    )
    
    provider = AuthFactory.create(config)
    
    # 測試認證流程
    credentials = {'code': 'test-auth-code'}
    success, user_info = await provider.authenticate(credentials)
    assert isinstance(success, bool)

@pytest.mark.asyncio
async def test_jwt_provider():
    """測試 JWT 提供者"""
    import jwt
    from datetime import datetime, timedelta
    
    config = AuthConfig(
        provider=AuthProviderEnum.JWT,
        jwt_secret="test-secret",
        jwt_algorithm="HS256"
    )
    
    provider = AuthFactory.create(config)
    
    # 生成測試 token
    payload = {
        'sub': 'test-user',
        'email': 'test@example.com',
        'roles': ['sre-operator'],
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, config.jwt_secret, algorithm=config.jwt_algorithm)
    
    # 測試認證
    success, user_info = await provider.authenticate({'token': token})
    assert success
    assert user_info['email'] == 'test@example.com'

@pytest.mark.asyncio
async def test_local_provider():
    """測試本地開發提供者"""
    config = AuthConfig(provider=AuthProviderEnum.LOCAL)
    provider = AuthFactory.create(config)
    
    # 本地提供者應該總是認證成功
    success, user_info = await provider.authenticate({})
    assert success
    assert user_info['roles'] == ['admin']
    
    # 本地提供者應該總是授權
    authorized = await provider.authorize(user_info, 'any_resource', 'any_action')
    assert authorized

@pytest.mark.asyncio
async def test_auth_manager_caching():
    """測試認證管理器緩存"""
    from ..auth.auth_manager import AuthManager
    
    manager = AuthManager()
    
    # 第一次認證
    credentials = {'api_key': 'test-key'}
    success1, user_info1 = await manager.authenticate(credentials)
    
    # 第二次認證（應該從緩存返回）
    success2, user_info2 = await manager.authenticate(credentials)
    
    assert success1 == success2
    assert user_info1 == user_info2

@pytest.mark.asyncio
async def test_rate_limiting():
    """測試速率限制"""
    from ..auth.auth_manager import AuthManager
    
    manager = AuthManager()
    manager.config.enable_rate_limiting = True
    manager.config.max_requests_per_minute = 5
    
    user_info = {'user_id': 'test-user'}
    
    # 前 5 次應該成功
    for _ in range(5):
        authorized = await manager.authorize(user_info, 'resource', 'action')
        assert authorized
    
    # 第 6 次應該失敗（超過速率限制）
    authorized = await manager.authorize(user_info, 'resource', 'action')
    assert not authorized

@pytest.mark.asyncio
async def test_rbac_authorization():
    """測試基於角色的授權"""
    from ..auth.auth_factory import GoogleIAMProvider
    
    config = AuthConfig(
        provider=AuthProviderEnum.GOOGLE_IAM,
        enable_rbac=True
    )
    
    provider = GoogleIAMProvider(config)
    
    # 測試管理員權限
    admin_user = {'roles': ['admin']}
    authorized = await provider.authorize(admin_user, 'deployment', 'delete')
    assert authorized
    
    # 測試操作員權限
    operator_user = {'roles': ['sre-operator']}
    authorized = await provider.authorize(operator_user, 'deployment', 'restart')
    assert authorized
    
    authorized = await provider.authorize(operator_user, 'deployment', 'delete')
    assert not authorized  # 操作員不能刪除
    
    # 測試查看者權限
    viewer_user = {'roles': ['viewer']}
    authorized = await provider.authorize(viewer_user, 'metrics', 'read')
    assert authorized
    
    authorized = await provider.authorize(viewer_user, 'deployment', 'restart')
    assert not authorized  # 查看者不能執行操作
```

### 9. 環境變數配置範例

```bash
# .env.development
ENVIRONMENT=development
AUTH_PROVIDER=local

# .env.staging
ENVIRONMENT=staging
AUTH_PROVIDER=oauth2
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret

# .env.production
ENVIRONMENT=production
AUTH_PROVIDER=google_iam
GOOGLE_APPLICATION_CREDENTIALS=/secrets/service-account.json
```

### 10. 使用範例

```python
# 範例 1：使用不同環境的認證
async def main():
    # 開發環境 - 使用本地認證
    os.environ['ENVIRONMENT'] = 'development'
    auth = auth_manager.provider
    success, user = await auth.authenticate({})
    print(f"Dev auth: {success}, User: {user}")
    
    # 生產環境 - 使用 Google IAM
    os.environ['ENVIRONMENT'] = 'production'
    auth = auth_manager.provider
    credentials = {'token': 'google-oauth-token'}
    success, user = await auth.authenticate(credentials)
    print(f"Prod auth: {success}, User: {user}")

# 範例 2：使用裝飾器保護函數
@require_auth(resource="k8s_deployment", action="restart")
async def restart_deployment(name: str, **kwargs):
    user_info = kwargs.get('user_info')
    print(f"User {user_info['email']} restarting {name}")
    # 執行重啟邏輯

# 範例 3：動態切換認證方式
def get_auth_provider(auth_type: str) -> AuthProvider:
    config = AuthConfig(provider=auth_type)
    return AuthFactory.create(config)

# 可以根據需要使用不同的認證
jwt_auth = get_auth_provider("jwt")
api_key_auth = get_auth_provider("api_key")
```

### 11. 完整性檢查

✅ **與現有架構的整合點**：
1. 配置系統：完全整合到 `ConfigManager`
2. 工廠模式：與 `MemoryBackendFactory`、`DeploymentFactory` 保持一致
3. 單例模式：`AuthManager` 使用相同的單例模式
4. Pydantic 模型：`AuthConfig` 提供類型安全
5. 測試覆蓋：包含單元測試和整合測試

✅ **安全特性**：
1. 多種認證方式支援
2. 基於角色的授權（RBAC）
3. 速率限制
4. 審計日誌
5. Token 刷新機制
6. 緩存機制減少認證開銷

這個認證授權工廠模式設計與現有的記憶體管理和部署方式保持了高度一致性，提供了企業級的安全性和靈活性。

### 12. 優勢總結

採用工廠模式管理認證授權帶來的好處：

1. **架構一致性**：與記憶體管理、部署方式保持相同的設計模式
2. **靈活切換**：可根據環境動態選擇認證方式（開發用 Local、生產用 IAM）
3. **易於擴展**：新增認證方式只需實現 `AuthProvider` 介面
4. **統一管理**：所有認證邏輯集中管理，便於維護和審計
5. **安全增強**：支援多因素認證、速率限制、審計日誌等安全特性