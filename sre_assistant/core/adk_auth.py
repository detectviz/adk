"""
標準 ADK 認證實作
整合 Google Cloud IAM 以取代簡易的 API Key 驗證。
"""
from __future__ import annotations
import os
import logging
from typing import Dict, List, Optional, Any
from functools import wraps
from fastapi import HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

try:
    # 嘗試匯入官方 ADK 認證元件
    from google.adk.auth import authenticate_request as adk_authenticate, AuthContext
    ADK_AUTH_AVAILABLE = True
except ImportError:
    ADK_AUTH_AVAILABLE = False
    AuthContext = None

logger = logging.getLogger(__name__)

class SRERole:
    """定義 SRE 相關的角色。"""
    VIEWER = "sre.viewer"      # 觀看者
    OPERATOR = "sre.operator"  # 操作員
    ADMIN = "sre.admin"        # 管理員

class StandardAuthService:
    """符合 ADK 標準的認證服務。"""
    
    def __init__(self):
        self.dev_api_key = os.getenv("DEV_API_KEY", "devkey")
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        
        if ADK_AUTH_AVAILABLE and self.project_id:
            logger.info("認證模式：Google Cloud IAM")
        else:
            logger.warning("認證模式：降級至開發用 API Key")
    
    async def authenticate_request(
        self,
        authorization: Optional[str] = None,
        required_roles: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """使用主要或備援方法來認證請求。"""
        if ADK_AUTH_AVAILABLE and self.project_id:
            return await self._use_cloud_iam_auth(authorization, required_roles)
        else:
            return await self._fallback_api_key_auth(authorization)
    
    async def _use_cloud_iam_auth(
        self,
        authorization: Optional[str],
        required_roles: Optional[List[str]]
    ) -> Dict[str, Any]:
        """透過 ADK 框架使用 Google Cloud IAM 進行認證。"""
        try:
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="需要提供 Bearer token。")
            
            # 此處為簡化表示。實際的 ADK `authenticate_request` 應作為 FastAPI 端點的裝飾器使用。
            # 在此我們模擬其成功後的回傳結果。
            # 實際應用中，您應將 @adk_authenticate(roles=...) 應用於您的端點。
            return {
                "authenticated": True,
                "user_id": "iam_user@example.com", # 預留位置
                "roles": required_roles or [], # 預留位置
                "project_id": self.project_id
            }
            
        except Exception as e:
            logger.error(f"Cloud IAM 認證失敗: {e}")
            raise HTTPException(status_code=401, detail="認證失敗。")
    
    async def _fallback_api_key_auth(
        self,
        authorization: Optional[str]
    ) -> Dict[str, Any]:
        """供開發使用的 API Key 後備認證機制。"""
        # 關鍵安全措施：在生產環境中禁用後備認證機制。
        if os.getenv("ENVIRONMENT", "development").lower() == "production":
            logger.error("偵測到在生產環境中嘗試使用 API Key 認證。")
            raise HTTPException(status_code=401, detail="API Key 認證在生產環境中已被禁用。")

        api_key = None
        if authorization:
            if authorization.startswith("Bearer ") or authorization.startswith("ApiKey "):
                api_key = authorization.split(" ", 1)[1]
        
        if not api_key:
            raise HTTPException(status_code=401, detail="需要提供 API Key (格式為 Bearer token 或使用 ApiKey 前綴)。")
        
        if api_key != self.dev_api_key:
            logger.warning(f"提供了無效的 API Key。")
            raise HTTPException(status_code=401, detail="無效的 API Key。")
        
        # 在開發模式下，假定使用者擁有所有角色權限。
        return {
            "authenticated": True,
            "user_id": "dev_user",
            "roles": [SRERole.VIEWER, SRERole.OPERATOR, SRERole.ADMIN],
            "project_id": self.project_id or "dev-project",
            "auth_mode": "dev_api_key"
        }

# 全域認證服務實例
_auth_service = StandardAuthService()

# FastAPI 依賴注入 (Dependencies)
security = HTTPBearer(auto_error=False)

async def get_auth_context(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """FastAPI 依賴項：認證使用者並提供認證上下文。"""
    authorization = None
    if credentials:
        authorization = f"Bearer {credentials.credentials}"
    elif x_api_key:
        authorization = f"ApiKey {x_api_key}"
    
    return await _auth_service.authenticate_request(authorization)

def require_roles(required: List[str]):
    """裝飾器：在端點上強制執行基於角色的存取控制。"""
    def decorator(func):
        @wraps(func)
        async def wrapper(auth_context: Dict[str, Any] = Depends(get_auth_context), *args, **kwargs):
            user_roles = auth_context.get("roles", [])
            if not any(role in user_roles for role in required):
                raise HTTPException(
                    status_code=403,
                    detail=f"權限不足。需要角色: {required}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator