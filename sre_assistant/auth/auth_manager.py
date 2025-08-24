# sre_assistant/auth/auth_manager.py
"""
統一的認證授權管理器
整合多種認證方式和授權策略
"""

from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from functools import wraps
import asyncio
import hashlib
import json

# Note: These imports will cause errors until the config system is updated.
# This is expected as per the plan.
from ..config.config_manager import config_manager
from .auth_factory import AuthFactory

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
                print(f"Rate limit exceeded for user {user_info.get('user_id', 'anonymous')}")
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
        # 移除敏感資訊
        safe_creds = {k: v for k, v in credentials.items()
                     if k not in ['password', 'secret', 'token']}

        creds_str = json.dumps(safe_creds, sort_keys=True)
        # Add token hash to key if present
        if 'token' in credentials:
            creds_str += hashlib.sha256(credentials['token'].encode()).hexdigest()

        return hashlib.sha256(creds_str.encode()).hexdigest()

    def _check_rate_limit(self, user_info: Dict) -> bool:
        """檢查速率限制"""
        user_id = user_info.get('user_id', user_info.get('email', 'anonymous'))
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
                'timestamp': datetime.utcnow().isoformat(),
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
                'timestamp': datetime.utcnow().isoformat(),
                'event': 'authorization',
                'user': user_info.get('email', user_info.get('user_id')),
                'resource': resource,
                'action': action,
                'authorized': authorized
            })

# 單例模式
# Using a function to create a singleton instance
_auth_manager_instance = None

def get_auth_manager():
    global _auth_manager_instance
    if _auth_manager_instance is None:
        _auth_manager_instance = AuthManager()
    return _auth_manager_instance

auth_manager = get_auth_manager()


# 裝飾器便利函數
def require_auth(resource: str = None, action: str = None):
    """
    認證授權裝飾器

    使用範例：
        @require_auth(resource="deployment", action="restart")
        async def restart_deployment(**kwargs):
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
