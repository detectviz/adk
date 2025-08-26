import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from sre_assistant.auth.auth_manager import AuthManager
from google.adk.agents.invocation_context import InvocationContext

# Since we are testing the auth manager, we need to mock the factory it depends on.
@patch('sre_assistant.auth.auth_manager.AuthFactory')
@pytest.mark.asyncio
async def test_auth_manager_local_provider(MockAuthFactory):
    """
    Tests that the AuthManager correctly uses the local provider with a context.
    """
    # 1. Setup
    # Mock the provider that the factory will create
    mock_provider = AsyncMock()
    mock_provider.authenticate.return_value = (True, {'user_id': 'local-user', 'roles': ['admin']})
    mock_provider.authorize.return_value = True

    # Configure the factory to return our mock provider
    MockAuthFactory.create.return_value = mock_provider

    # Instantiate the manager
    manager = AuthManager()
    manager.provider = mock_provider

    # Create a mock invocation context
    mock_context = InvocationContext()

    # 2. Execution
    credentials = {'token': 'any'}
    success, user_info = await manager.authenticate(mock_context, credentials)
    authorized = await manager.authorize(mock_context, user_info=user_info, resource="test", action="write")

    # 3. Assertions
    assert success is True
    assert user_info['user_id'] == 'local-user'
    assert authorized is True
    mock_provider.authenticate.assert_called_once_with(credentials)
    mock_provider.authorize.assert_called_once_with(user_info, "test", "write")

@patch('sre_assistant.auth.auth_manager.AuthFactory')
@pytest.mark.asyncio
async def test_auth_manager_caching_with_context(MockAuthFactory):
    """
    Tests that the AuthManager correctly caches authentication results in the context.
    """
    # 1. Setup
    mock_provider = AsyncMock()
    mock_provider.authenticate.return_value = (True, {'user_id': 'cached-user'})
    MockAuthFactory.create.return_value = mock_provider

    manager = AuthManager()
    manager.provider = mock_provider

    # Create a mock invocation context. The state is a simple dict.
    mock_context = InvocationContext()

    credentials = {'token': 'cache-test'}

    # 2. Execution
    # First call - should call the provider and write to context state
    await manager.authenticate(mock_context, credentials)

    # Second call - should be served from context state
    await manager.authenticate(mock_context, credentials)

    # 3. Assertions
    # The provider's authenticate method should have been called only once.
    mock_provider.authenticate.assert_called_once()

    # Check that the context state was used for caching
    cache_key = manager._get_cache_key(credentials)
    user_cache_key = f"user:auth_cache_{cache_key}"
    assert user_cache_key in mock_context.state
    assert mock_context.state[user_cache_key]['user_info']['user_id'] == 'cached-user'

@patch('sre_assistant.auth.auth_manager.AuthFactory')
@pytest.mark.asyncio
async def test_auth_manager_rate_limiting_with_context(MockAuthFactory):
    """
    Tests that the AuthManager correctly rate limits using the context.
    """
    # 1. Setup
    mock_provider = AsyncMock()
    mock_provider.authorize.return_value = True
    MockAuthFactory.create.return_value = mock_provider

    manager = AuthManager()
    manager.provider = mock_provider
    # Configure manager for this test
    manager.config = MagicMock()
    manager.config.enable_rate_limiting = True
    manager.config.max_requests_per_minute = 2

    mock_context = InvocationContext()
    user_info = {'user_id': 'rate-limited-user'}

    # 2. Execution & Assertions
    # First two calls should succeed
    assert await manager.authorize(mock_context, user_info, "test", "action1") is True
    assert await manager.authorize(mock_context, user_info, "test", "action2") is True

    # The third call should be rate limited
    assert await manager.authorize(mock_context, user_info, "test", "action3") is False

    # Verify the context state
    rate_limit_key = f"user:rate_limit_timestamps_{user_info['user_id']}"
    assert rate_limit_key in mock_context.state
    assert len(mock_context.state[rate_limit_key]) == 2
