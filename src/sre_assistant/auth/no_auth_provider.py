# src/sre_assistant/auth/no_auth_provider.py
"""
提供一個「無認證」的提供者, 用於本地開發和測試.

此提供者會繞過所有實際的認證檢查, 並始終返回一個固定的,
模擬的用戶資訊, 讓開發者可以專注於測試代理的核心邏輯.
"""
from typing import Dict, Any, Optional, Tuple
from .base import AuthProvider
from ..contracts import AuthConfig

class NoAuthProvider(AuthProvider):
    """
    一個用於開發的無認證提供者, 它符合 AuthProvider 介面.
    """

    MOCK_USER_INFO = {
        "user_id": "local_dev_user",
        "email": "dev@example.com",
        "name": "Local Developer",
        "roles": ["admin", "developer"]
    }

    def __init__(self, config: AuthConfig):
        """
        初始化 NoAuthProvider.
        此處的 config 參數是為了符合工廠的調用簽名, 但未使用.
        """
        pass

    async def authenticate(self, credentials: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        總是返回成功和一個模擬的用戶物件.
        """
        return True, self.MOCK_USER_INFO

    async def authorize(self, user_info: Dict[str, Any], resource: str, action: str) -> bool:
        """
        在無認證模式下, 總是授權所有操作.
        """
        return True

    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        無認證模式下無需刷新令牌.
        """
        return None

    async def health_check(self) -> bool:
        """
        無認證提供者總是健康的.
        """
        return True
