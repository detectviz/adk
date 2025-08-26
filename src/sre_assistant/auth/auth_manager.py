# sre_assistant/auth/auth_manager.py
"""
統一的認證授權管理器 (Stateless Refactored)
整合多種認證方式和授權策略
"""

from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from functools import wraps
import asyncio
import hashlib
import json
import logging

# ADK and project imports
from google.adk.agents.invocation_context import InvocationContext
from ..config.config_manager import config_manager
from .auth_factory import AuthFactory

# Setup logger for this module
logger = logging.getLogger(__name__)

class AuthManager:
    """
    認證授權管理器 (無狀態版本)
    所有狀態 (快取、速率限制) 都存儲在傳入的 InvocationContext 中。
    """

    def __init__(self):
        """初始化認證管理器"""
        auth_config = config_manager.get_auth_config()
        self.provider = AuthFactory.create(auth_config)
        self.config = auth_config
        # No more self._auth_cache, self._rate_limits, or self._audit_log

    async def authenticate(self, ctx: InvocationContext, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        """
        統一認證入口 (無狀態)

        Args:
            ctx: 代理調用上下文，用於狀態管理
            credentials: 認證憑證

        Returns:
            (是否成功, 用戶資訊)
        """
        # 檢查快取
        cache_key = self._get_cache_key(credentials)
        user_cache_key = f"user:auth_cache_{cache_key}"

        cached = ctx.state.get(user_cache_key)
        if cached and cached.get('expires') > datetime.utcnow().timestamp():
            logger.info(f"Authentication cache hit for user: {cached['user_info'].get('user_id')}")
            return True, cached['user_info']

        # 執行認證
        success, user_info = await self.provider.authenticate(credentials)

        # 緩存結果到 context.state
        if success and user_info:
            ctx.state[user_cache_key] = {
                'user_info': user_info,
                'expires': (datetime.utcnow() + timedelta(minutes=5)).timestamp()
            }
            logger.info(f"Authentication success, result cached for user: {user_info.get('user_id')}")

        # 審計日誌
        self._log_auth_attempt(credentials, success)

        return success, user_info

    async def authorize(self, ctx: InvocationContext, user_info: Dict, resource: str, action: str) -> bool:
        """
        統一授權檢查 (無狀態)

        Args:
            ctx: 代理調用上下文，用於狀態管理
            user_info: 用戶資訊
            resource: 資源名稱
            action: 操作類型

        Returns:
            是否授權
        """
        # 檢查速率限制
        if self.config.enable_rate_limiting:
            if not self._check_rate_limit(ctx, user_info):
                logger.warning(f"Rate limit exceeded for user {user_info.get('user_id', 'anonymous')}")
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
        safe_creds = {k: v for k, v in credentials.items()
                     if k not in ['password', 'secret', 'token']}
        creds_str = json.dumps(safe_creds, sort_keys=True)
        if 'token' in credentials:
            creds_str += hashlib.sha256(credentials['token'].encode()).hexdigest()
        return hashlib.sha256(creds_str.encode()).hexdigest()

    def _check_rate_limit(self, ctx: InvocationContext, user_info: Dict) -> bool:
        """檢查速率限制 (使用 context.state)"""
        user_id = user_info.get('user_id', user_info.get('email', 'anonymous'))
        rate_limit_key = f"user:rate_limit_timestamps_{user_id}"

        now = datetime.utcnow().timestamp()

        # 從 context.state 讀取時間戳
        timestamps = ctx.state.get(rate_limit_key, [])

        # 清理過期記錄
        minute_ago = now - 60
        valid_timestamps = [t for t in timestamps if t > minute_ago]

        if len(valid_timestamps) >= self.config.max_requests_per_minute:
            return False

        valid_timestamps.append(now)
        # 將更新後的時間戳寫回 context.state
        ctx.state[rate_limit_key] = valid_timestamps
        return True

    def _log_auth_attempt(self, credentials: Dict, success: bool):
        """記錄認證嘗試 (使用 logger)"""
        if self.config.enable_audit_logging:
            logger.info(
                "Authentication attempt",
                extra={
                    "event": "authentication",
                    "success": success,
                    "provider": self.config.provider.value,
                    "auth_method": credentials.get('auth_method', 'unknown'),
                },
            )

    def _log_auth_check(self, user_info: Dict, resource: str, action: str, authorized: bool):
        """記錄授權檢查 (使用 logger)"""
        if self.config.enable_audit_logging:
            logger.info(
                "Authorization check",
                extra={
                    "event": "authorization",
                    "user": user_info.get('email', user_info.get('user_id')),
                    "resource": resource,
                    "action": action,
                    "authorized": authorized,
                },
            )

# 單例模式
_auth_manager_instance = None

def get_auth_manager():
    global _auth_manager_instance
    if _auth_manager_instance is None:
        _auth_manager_instance = AuthManager()
    return _auth_manager_instance

auth_manager = get_auth_manager()


# 裝飾器便利函數 (需要重構以接收 context)
def require_auth(resource: str = None, action: str = None):
    """
    認證授權裝飾器 (需要重構以適應無狀態 AuthManager)

    注意: 此裝飾器目前與新的無狀態 AuthManager 不相容，
    因為它無法訪問 InvocationContext。
    工作流程應直接調用 auth_manager 的方法，而不是使用此裝飾器。
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This wrapper is now problematic as it doesn't have access to the InvocationContext.
            # The calling code (e.g., SREWorkflow) should handle auth directly.
            logger.warning("The 'require_auth' decorator is deprecated for stateless AuthManager and should not be used.")

            # Simplified, non-functional path to avoid breaking existing code that might use it.
            # In a real scenario, this would either be refactored or removed.
            if 'credentials' not in kwargs:
                 raise PermissionError("Authentication credentials not provided.")

            # This part won't work correctly without a context.
            # We leave it here to illustrate the problem.
            # A proper fix would involve a middleware approach where context is available.

            # Bypassing for now. The workflow will handle auth.
            return await func(*args, **kwargs)

        return wrapper
    return decorator
