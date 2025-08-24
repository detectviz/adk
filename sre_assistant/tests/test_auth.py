import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from sre_assistant.auth.auth_manager import AuthManager

# Since we are testing the auth manager, we need to mock the factory it depends on.
@patch('sre_assistant.auth.auth_manager.AuthFactory')
@pytest.mark.asyncio
async def test_auth_manager_local_provider(MockAuthFactory):
    """
    Tests that the AuthManager correctly uses the local provider.
    """
    # 1. Setup
    # Mock the provider that the factory will create
    mock_provider = AsyncMock()
    mock_provider.authenticate.return_value = (True, {'user': 'local-user', 'roles': ['admin']})
    mock_provider.authorize.return_value = True

    # Configure the factory to return our mock provider
    MockAuthFactory.create.return_value = mock_provider

    # Instantiate the manager. Because of the patch, it will get our mock factory.
    # We add a random number to bypass the singleton for this test.
    manager = AuthManager()
    manager._initialized = False
    manager.provider = mock_provider

    # 2. Execution
    success, user_info = await manager.authenticate(credentials={'token': 'any'})
    authorized = await manager.authorize(user_info=user_info, resource="test", action="write")

    # 3. Assertions
    assert success is True
    assert user_info['user'] == 'local-user'
    assert authorized is True
    mock_provider.authenticate.assert_called_once_with(credentials={'token': 'any'})
    mock_provider.authorize.assert_called_once_with(user_info=user_info, resource="test", action="write")

@patch('sre_assistant.auth.auth_manager.AuthFactory')
@pytest.mark.asyncio
async def test_auth_manager_caching(MockAuthFactory):
    """
    Tests that the AuthManager correctly caches authentication results.
    """
    # 1. Setup
    mock_provider = AsyncMock()
    mock_provider.authenticate.return_value = (True, {'user': 'cached-user'})
    MockAuthFactory.create.return_value = mock_provider

    manager = AuthManager()
    manager._initialized = False
    manager.provider = mock_provider
    manager._auth_cache = {} # Ensure cache is empty

    # 2. Execution
    # First call - should call the provider
    await manager.authenticate(credentials={'token': 'cache-test'})

    # Second call - should be served from cache
    await manager.authenticate(credentials={'token': 'cache-test'})

    # 3. Assertions
    # The provider's authenticate method should have been called only once.
    mock_provider.authenticate.assert_called_once()
