# sre_assistant/tests/test_auth.py
import pytest
import asyncio
from unittest.mock import MagicMock, patch

# --- Mocking the configuration ---
# We mock the config objects and manager because the real one depends on file I/O and environment variables.
# This makes our tests more isolated and predictable.

from sre_assistant.config.config_manager import AuthConfig, AuthProvider as AuthProviderEnum

# Mock config_manager to avoid dependency on the actual file-based config manager
mock_config_manager = MagicMock()

def mock_get_auth_config(provider_enum, **kwargs):
    params = {
        "provider": provider_enum,
        "enable_rbac": True,
        "enable_rate_limiting": True,
        "max_requests_per_minute": 5,
        "enable_audit_logging": True,
        **kwargs
    }
    return AuthConfig(**params)

# --- End of Mocking ---

# We patch the config_manager singleton within the auth_manager module
@patch('sre_assistant.auth.auth_manager.config_manager', mock_config_manager)
def test_imports_after_patch():
    # This test is just to ensure our patching setup is correct before running other tests.
    from sre_assistant.auth.auth_factory import AuthFactory
    from sre_assistant.auth.auth_manager import AuthManager
    assert AuthFactory is not None
    assert AuthManager is not None


@pytest.mark.asyncio
@patch('sre_assistant.auth.auth_manager.config_manager', mock_config_manager)
async def test_local_provider():
    """測試本地開發提供者"""
    from sre_assistant.auth.auth_factory import AuthFactory

    mock_config_manager.get_auth_config.return_value = mock_get_auth_config(AuthProviderEnum.LOCAL)

    config = mock_config_manager.get_auth_config()
    provider = AuthFactory.create(config)

    # 本地提供者應該總是認證成功
    success, user_info = await provider.authenticate({})
    assert success
    assert user_info['roles'] == ['admin']

    # 本地提供者應該總是授權
    authorized = await provider.authorize(user_info, 'any_resource', 'any_action')
    assert authorized


@pytest.mark.asyncio
@patch('sre_assistant.auth.auth_manager.config_manager', mock_config_manager)
async def test_jwt_provider():
    """測試 JWT 提供者"""
    import jwt
    from datetime import datetime, timedelta
    from sre_assistant.auth.auth_factory import AuthFactory

    secret = "test-secret"
    algo = "HS256"

    mock_config_manager.get_auth_config.return_value = mock_get_auth_config(
        AuthProviderEnum.JWT,
        jwt_secret=secret,
        jwt_algorithm=algo
    )

    config = mock_config_manager.get_auth_config()
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

    # 測試授權
    authorized = await provider.authorize(user_info, 'deployment', 'restart')
    assert not authorized # Not in permissions claim

    user_info['claims'] = {'permissions': ['deployment:restart']}
    authorized = await provider.authorize(user_info, 'deployment', 'restart')
    assert authorized


@pytest.mark.asyncio
@patch('sre_assistant.auth.auth_manager.config_manager', mock_config_manager)
async def test_auth_manager_caching():
    """測試認證管理器緩存"""
    from sre_assistant.auth.auth_manager import AuthManager

    mock_config_manager.get_auth_config.return_value = mock_get_auth_config(
        AuthProviderEnum.LOCAL, enable_audit_logging=False
    )

    manager = AuthManager()

    # Mock the underlying provider's authenticate method to track calls
    manager.provider.authenticate = MagicMock(wraps=manager.provider.authenticate)

    credentials = {'user': 'test-user'}

    # 第一次認證，應該會呼叫 provider
    success1, user_info1 = await manager.authenticate(credentials)
    manager.provider.authenticate.assert_called_once()

    # 第二次認證（應該從緩存返回）
    success2, user_info2 = await manager.authenticate(credentials)

    assert success1 and success2
    assert user_info1 == user_info2
    # 確認第二次沒有再次呼叫 provider
    manager.provider.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('sre_assistant.auth.auth_manager.config_manager', mock_config_manager)
async def test_rate_limiting():
    """測試速率限制"""
    from sre_assistant.auth.auth_manager import AuthManager

    # Set a low rate limit for testing
    mock_config_manager.get_auth_config.return_value = mock_get_auth_config(
        AuthProviderEnum.LOCAL,
        enable_rate_limiting=True,
        max_requests_per_minute=5,
        enable_audit_logging=False
    )

    manager = AuthManager()

    user_info = {'user_id': 'rate-limit-user', 'roles': ['admin']}

    # 前 5 次應該成功
    for i in range(5):
        authorized = await manager.authorize(user_info, 'resource', 'action')
        assert authorized, f"Request {i+1} should have been authorized"

    # 第 6 次應該失敗（超過速率限制）
    authorized = await manager.authorize(user_info, 'resource', 'action')
    assert not authorized, "6th request should have been rate limited"


@pytest.mark.asyncio
@patch('sre_assistant.auth.auth_manager.config_manager', mock_config_manager)
async def test_rbac_authorization():
    """測試基於角色的授權"""
    from sre_assistant.auth.auth_factory import GoogleIAMProvider

    mock_config_manager.get_auth_config.return_value = mock_get_auth_config(
        AuthProviderEnum.GOOGLE_IAM,
        enable_rbac=True
    )

    config = mock_config_manager.get_auth_config()
    provider = GoogleIAMProvider(config)

    # 測試管理員權限
    admin_user = {'roles': ['admin']}
    assert await provider.authorize(admin_user, 'deployment', 'delete')

    # 測試操作員權限
    operator_user = {'roles': ['sre-operator']}
    assert await provider.authorize(operator_user, 'deployment', 'restart')
    assert not await provider.authorize(operator_user, 'deployment', 'delete') # 操作員不能刪除

    # 測試查看者權限
    viewer_user = {'roles': ['viewer']}
    assert await provider.authorize(viewer_user, 'metrics', 'read')
    assert not await provider.authorize(viewer_user, 'deployment', 'restart') # 查看者不能執行操作
