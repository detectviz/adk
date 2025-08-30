# src/sre_assistant/auth/base.py
"""
Defines the abstract base class for all authentication providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple

class AuthProvider(ABC):
    """
    統一的認證提供者抽象基礎類別 (Interface).

    所有具體的認證提供者都必須繼承此類別並實現其定義的抽象方法.
    這確保了所有提供者都有一致的介面.
    """

    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
        pass

    @abstractmethod
    async def authorize(self, user_info: Dict, resource: str, action: str) -> bool:
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass
