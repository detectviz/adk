# src/sre_assistant/auth/tools.py
"""
為 SRE Assistant 提供無狀態的認證與授權工具。

此模組中的工具取代了舊有的 AuthManager，並被設計為在 ADK 工作流程中、
基於 InvocationContext 進行操作，完全符合 ADK 的無狀態設計理念。
"""
import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple

from google.adk.agents.invocation_context import InvocationContext

from ..config.config_manager import config_manager
from .auth_factory import AuthFactory

logger = logging.getLogger(__name__)


# --- 輔助函數 (從 AuthManager 遷移) ---

def _get_cache_key(credentials: Dict[str, Any]) -> str:
    """
    根據憑證生成一個安全的快取鍵 (cache key)。

    為了安全，此函數會忽略密碼、密鑰或權杖等敏感欄位，
    並對權杖進行 SHA256 雜湊處理。

    Args:
        credentials (Dict[str, Any]): 用戶提供的憑證字典。

    Returns:
        str: 一個代表此憑證的唯一且安全的雜湊字串。
    """
    safe_creds = {k: v for k, v in credentials.items() if k not in ['password', 'secret', 'token']}
    creds_str = json.dumps(safe_creds, sort_keys=True)
    if 'token' in credentials:
        creds_str += hashlib.sha256(credentials['token'].encode()).hexdigest()
    return f"user:auth_cache_{hashlib.sha256(creds_str.encode()).hexdigest()}"


def _check_rate_limit(ctx: InvocationContext, user_info: Dict, auth_config) -> bool:
    """
    基於 InvocationContext 中的狀態，檢查用戶的速率限制。

    Args:
        ctx (InvocationContext): 代理的調用上下文，用於讀寫時間戳列表。
        user_info (Dict): 已認證的用戶資訊，用於獲取用戶 ID。
        auth_config: 包含速率限制設定 (max_requests_per_minute) 的配置對象。

    Returns:
        bool: 如果請求未超過限制，則返回 True，否則返回 False。
    """
    user_id = user_info.get('user_id', user_info.get('email', 'anonymous'))
    rate_limit_key = f"user:rate_limit_timestamps_{user_id}"

    now = datetime.now(timezone.utc).timestamp()
    # 從上下文中讀取該用戶的所有請求時間戳
    timestamps = ctx.session.state.get(rate_limit_key, [])

    # 清理掉一分鐘前過期的時間戳
    minute_ago = now - 60
    valid_timestamps = [t for t in timestamps if t > minute_ago]

    # 檢查有效時間戳的數量是否已達上限
    if len(valid_timestamps) >= auth_config.max_requests_per_minute:
        return False

    # 添加當前時間戳並寫回上下文
    valid_timestamps.append(now)
    ctx.session.state[rate_limit_key] = valid_timestamps
    return True


# --- ADK Agent 工具 ---

async def authenticate(ctx: InvocationContext, credentials: Dict[str, Any]) -> Tuple[bool, Optional[Dict]]:
    """
    使用配置的提供者對用戶進行認證，並將結果快取。

    此工具是 AuthManager.authenticate 的無狀態替代品。它首先檢查上下文中是否存在
    有效的快取，如果沒有，則調用相應的認證提供者 (如 OAuth2, JWT) 進行驗證，
    並將成功的結果寫回上下文的 state 和快取中。

    Args:
        ctx (InvocationContext): ADK 的調用上下文，用於狀態管理和快取。
        credentials (Dict[str, Any]): 包含認證資訊的字典，
                                     例如 `{'token': '...'}` 或 `{'api_key': '...'}`。

    Returns:
        Tuple[bool, Optional[Dict]]: 一個元組，包含布林值的成功狀態和一個可選的用戶資訊字典。
    """
    auth_config = config_manager.get_auth_config()
    provider = AuthFactory.create(auth_config)

    # 步驟 1: 檢查 InvocationContext 中是否存在有效的快取
    cache_key = _get_cache_key(credentials)
    cached = ctx.session.state.get(cache_key)
    if cached and cached.get('expires') > datetime.now(timezone.utc).timestamp():
        logger.info(f"認證快取命中，使用者: {cached['user_info'].get('user_id')}")
        # 如果上下文中沒有 user_info，則從快取中補上，以供後續步驟使用
        if "user_info" not in ctx.session.state:
            ctx.session.state["user_info"] = cached['user_info']
        return True, cached['user_info']

    # 步驟 2: 如果沒有快取，則使用提供者執行實際的認證
    success, user_info = await provider.authenticate(credentials)

    # 步驟 3: 如果認證成功，將結果寫入 InvocationContext 的 state 和快取中
    if success and user_info:
        ctx.session.state[cache_key] = {
            'user_info': user_info,
            'expires': (datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()
        }
        ctx.session.state["user_info"] = user_info  # 確保 user_info 存在於 state 的頂層
        logger.info(f"認證成功，結果已快取。使用者: {user_info.get('user_id')}")

    # 步驟 4: 記錄審計日誌
    if auth_config.enable_audit_logging:
        logger.info(
            "Authentication attempt",
            extra={
                "event": "authentication",
                "success": success,
                "provider": auth_config.provider.value,
                "auth_method": credentials.get('auth_method', 'unknown'),
            },
        )

    return success, user_info


async def check_authorization(ctx: InvocationContext, resource: str, action: str) -> bool:
    """
    檢查用戶是否有權限在指定資源上執行特定操作。

    此工具是 AuthManager.authorize 的無狀態替代品。它依賴於 `InvocationContext`
    的 state 中已存在 `user_info` 物件 (應由 `authenticate` 工具預先填充)。
    它會先檢查速率限制，然後調用配置的授權提供者來判斷權限。

    Args:
        ctx (InvocationContext): ADK 的調用上下文，用於速率限制和獲取用戶資訊。
        resource (str): 正在被存取的資源名稱 (例如 'deployment')。
        action (str): 正在執行的操作 (例如 'restart', 'read')。

    Returns:
        bool: 一個布林值，表示操作是否被授權。
    """
    user_info = ctx.session.state.get("user_info")
    if not user_info:
        logger.error("授權檢查失敗: 在上下文中找不到 user_info。是否已先呼叫 authenticate？")
        return False

    auth_config = config_manager.get_auth_config()
    provider = AuthFactory.create(auth_config)

    # 步驟 1: 檢查速率限制
    if auth_config.enable_rate_limiting:
        if not _check_rate_limit(ctx, user_info, auth_config):
            logger.warning(f"使用者 {user_info.get('user_id', 'anonymous')} 已超過速率限制。")
            return False

    # 步驟 2: 使用提供者執行授權檢查
    authorized = await provider.authorize(user_info, resource, action)

    # 步驟 3: 記錄審計日誌
    if auth_config.enable_audit_logging:
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

    return authorized
