"""
標準 ADK 認證實作
整合 Google Cloud IAM 替代簡化的 API key 驗證
"""
from __future__ import annotations
import os
import logging
from typing import Dict, List, Optional, Any
from functools import wraps
from fastapi import HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

try:
    from google.adk.auth import authenticate_request, AuthContext
    from google.auth import default
    from google.cloud import iam
    ADK_AUTH_AVAILABLE = True
except ImportError:
    ADK_AUTH_AVAILABLE = False
    AuthContext = None

logger = logging.getLogger(__name__)

class SRERole:
    """SRE 角色定義"""
    VIEWER = "sre.viewer"
    OPERATOR = "sre.operator"
    ADMIN = "sre.admin"

class StandardAuthService:
    """標準 ADK 認證服務"""
    
    def __init__(self):
        self.dev_api_key = os.getenv("DEV_API_KEY", "devkey")
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.required_roles = {
            "/api/v1/chat": [SRERole.VIEWER, SRERole.OPERATOR, SRERole.ADMIN],
            "/api/v1/execute": [SRERole.OPERATOR, SRERole.ADMIN],
            "/api/v1/admin": [SRERole.ADMIN],
        }
        
        if ADK_AUTH_AVAILABLE and self.project_id:
            logger.info("使用 Google Cloud IAM 認證")
        else:
            logger.warning("降級使用開發模式 API Key 認證")
    
    async def authenticate_request(
        self,
        authorization: Optional[str] = None,
        required_roles: List[str] = None
    ) -> Dict[str, Any]:
        """
        認證請求
        
        Args:
            authorization: Authorization header
            required_roles: 必要的角色列表
            
        Returns:
            認證上下文
        """
        if ADK_AUTH_AVAILABLE and self.project_id:
            return await self._use_cloud_iam_auth(authorization, required_roles)
        else:
            return await self._fallback_api_key_auth(authorization, required_roles)
    
    async def _use_cloud_iam_auth(
        self,
        authorization: Optional[str],
        required_roles: List[str]
    ) -> Dict[str, Any]:
        """使用 Google Cloud IAM 認證"""
        try:
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=401,
                    detail="需要 Bearer token"
                )
            
            token = authorization.split(" ", 1)[1]
            
            # 使用 ADK 認證框架
            @authenticate_request(roles=required_roles or [])
            async def protected_operation(auth_context: AuthContext):
                return {
                    "authenticated": True,
                    "user_id": auth_context.user_id,
                    "roles": auth_context.roles,
                    "project_id": auth_context.project_id
                }
            
            return await protected_operation()
            
        except Exception as e:
            logger.error(f"Cloud IAM 認證失敗: {e}")
            raise HTTPException(
                status_code=401,
                detail="認證失敗"
            )
    
    async def _fallback_api_key_auth(
        self,
        authorization: Optional[str],
        required_roles: List[str]
    ) -> Dict[str, Any]:
        """回退 API Key 認證（開發模式）"""
        
        # 支持 Bearer token 和 X-API-Key header
        api_key = None
        if authorization:
            if authorization.startswith("Bearer "):
                api_key = authorization.split(" ", 1)[1]
            elif authorization.startswith("ApiKey "):
                api_key = authorization.split(" ", 1)[1]
        
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="需要 API Key (Bearer token 或 X-API-Key header)"
            )
        
        # 驗證 API Key
        if api_key != self.dev_api_key:
            logger.warning(f"無效的 API Key: {api_key}")
            raise HTTPException(
                status_code=401,
                detail="無效的 API Key"
            )
        
        # 開發模式下，假定擁有所有角色
        return {
            "authenticated": True,
            "user_id": "dev_user",
            "roles": [SRERole.VIEWER, SRERole.OPERATOR, SRERole.ADMIN],
            "project_id": self.project_id or "dev-project",
            "auth_mode": "dev_api_key"
        }
    
    def check_role_permission(
        self,
        user_roles: List[str],
        required_roles: List[str]
    ) -> bool:
        """檢查角色權限"""
        if not required_roles:
            return True
        
        return any(role in user_roles for role in required_roles)

# 全局認證服務
_auth_service = StandardAuthService()

# FastAPI Dependencies
security = HTTPBearer(auto_error=False)

async def authenticate_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """FastAPI 認證依賴項"""
    authorization = None
    
    if credentials:
        authorization = f"Bearer {credentials.credentials}"
    elif x_api_key:
        authorization = f"ApiKey {x_api_key}"
    
    return await _auth_service.authenticate_request(authorization)

def require_roles(roles: List[str]):
    """角色權限裝飾器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 從 kwargs 中獲取認證上下文
            auth_context = kwargs.get("auth_context")
            if not auth_context:
                raise HTTPException(
                    status_code=401,
                    detail="認證上下文缺失"
                )
            
            if not _auth_service.check_role_permission(
                auth_context.get("roles", []), roles
            ):
                raise HTTPException(
                    status_code=403,
                    detail=f"需要角色: {roles}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_sre_operator():
    """需要 SRE 操作員權限的裝飾器"""
    return require_roles([SRERole.OPERATOR, SRERole.ADMIN])

def require_sre_admin():
    """需要 SRE 管理員權限的裝飾器"""
    return require_roles([SRERole.ADMIN])

# 便利函數
async def authenticate_request(
    authorization: Optional[str] = None,
    required_roles: List[str] = None
) -> Dict[str, Any]:
    """認證請求的便利函數"""
    return await _auth_service.authenticate_request(authorization, required_roles)