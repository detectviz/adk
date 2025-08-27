# tests/test_tools.py
"""
針對無狀態認證與授權工具的單元測試。
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import uuid

from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import BaseSessionService, Session
from google.adk.agents.base_agent import BaseAgent
from sre_assistant.auth.tools import authenticate, check_authorization

# Mock classes to satisfy Pydantic validation for InvocationContext
class MockSessionService(BaseSessionService):
    async def create_session(self, **kwargs): pass
    async def get_session(self, **kwargs): pass
    async def update_session(self, **kwargs): pass
    async def delete_session(self, **kwargs): pass
    async def list_sessions(self, **kwargs): return []

class MockAgent(BaseAgent):
    async def run_async(self, **kwargs): pass

class MockSession(Session):
    def __init__(self):
        super().__init__(
            id="mock_session_id",
            appName="mock_app",
            userId="mock_user"
        )

def create_mock_context() -> InvocationContext:
    """Creates a valid mock InvocationContext for testing."""
    return InvocationContext(
        session_service=MockSessionService(),
        invocation_id=f"inv-{uuid.uuid4()}",
        agent=MockAgent(name="MockAgent"),
        session=MockSession()
    )

# 將此檔案中的所有測試標記為異步執行
pytestmark = pytest.mark.asyncio


@patch('sre_assistant.auth.tools.AuthFactory')
@patch('sre_assistant.auth.tools.config_manager')
async def test_authenticate_success_and_cache(mock_config_manager, mock_auth_factory):
    """
    測試目的：驗證 `authenticate` 工具能否成功認證用戶、返回正確的用戶資訊，
              並將結果正確地快取到上下文中。
    """
    # --- 準備階段 (Arrange) ---
    # 模擬配置，以隔離對檔案系統的依賴
    mock_auth_config = MagicMock()
    mock_auth_config.enable_audit_logging = False
    mock_config_manager.get_auth_config.return_value = mock_auth_config

    # 模擬認證提供者，使其總是返回成功
    mock_provider = AsyncMock()
    mock_provider.authenticate.return_value = (True, {'user_id': 'test-user', 'roles': ['viewer']})
    mock_auth_factory.create.return_value = mock_provider

    # 準備測試用的輸入資料
    ctx = create_mock_context()
    credentials = {'token': 'valid-token'}

    # --- 執行階段 (Act) ---
    success, user_info = await authenticate(ctx, credentials)

    # --- 斷言階段 (Assert) ---
    # 1. 檢查工具的直接回傳值是否正確
    assert success is True
    assert user_info == {'user_id': 'test-user', 'roles': ['viewer']}

    # 2. 驗證模擬的提供者是否被以正確的參數呼叫了一次
    mock_provider.authenticate.assert_called_once_with(credentials)

    # 3. 檢查上下文狀態是否被正確更新
    assert "user_info" in ctx.session.state
    assert ctx.session.state["user_info"] == {'user_id': 'test-user', 'roles': ['viewer']}

    # 4. 檢查結果是否被快取（透過檢查 state 中是否存在符合格式的鍵）
    assert any(key.startswith('user:auth_cache_') for key in ctx.session.state.keys())

    # --- 第二次執行：測試快取是否生效 ---
    await authenticate(ctx, credentials)

    # --- 第二次斷言 ---
    # 由於快取命中，提供者的 `authenticate` 方法不應該被再次呼叫
    assert mock_provider.authenticate.call_count == 1


@patch('sre_assistant.auth.tools.AuthFactory')
@patch('sre_assistant.auth.tools.config_manager')
async def test_check_authorization_success(mock_config_manager, mock_auth_factory):
    """
    測試目的：驗證 `check_authorization` 工具在用戶擁有正確權限時，
              能否成功返回 `True`。
    """
    # --- 準備階段 (Arrange) ---
    mock_auth_config = MagicMock()
    mock_auth_config.enable_audit_logging = False
    mock_auth_config.enable_rate_limiting = False
    mock_config_manager.get_auth_config.return_value = mock_auth_config

    mock_provider = AsyncMock()
    mock_provider.authorize.return_value = True # 模擬授權成功
    mock_auth_factory.create.return_value = mock_provider

    # 準備一個已包含 `user_info` 的上下文
    ctx = create_mock_context()
    ctx.session.state['user_info'] = {'user_id': 'test-user', 'roles': ['sre-operator']}
    resource = 'deployment'
    action = 'restart'

    # --- 執行階段 (Act) ---
    is_authorized = await check_authorization(ctx, resource, action)

    # --- 斷言階段 (Assert) ---
    assert is_authorized is True
    # 驗證模擬的提供者是否被以正確的參數呼叫
    mock_provider.authorize.assert_called_once_with(
        {'user_id': 'test-user', 'roles': ['sre-operator']},
        resource,
        action
    )


@patch('sre_assistant.auth.tools.AuthFactory')
@patch('sre_assistant.auth.tools.config_manager')
async def test_check_authorization_failure_no_user_info(mock_config_manager, mock_auth_factory):
    """
    測試目的：驗證當上下文中缺少 `user_info` 時，`check_authorization`
              能否優雅地失敗並返回 `False`，且不應觸發任何提供者呼叫。
    """
    # --- 準備階段 (Arrange) ---
    ctx = create_mock_context() # 故意不設置 user_info
    resource = 'deployment'
    action = 'restart'

    # --- 執行階段 (Act) ---
    is_authorized = await check_authorization(ctx, resource, action)

    # --- 斷言階段 (Assert) ---
    assert is_authorized is False
    # 在這種情況下，不應該嘗試創建或呼叫任何認證提供者
    mock_auth_factory.create.assert_not_called()
