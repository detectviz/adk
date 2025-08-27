# Tool Testing Guide

This document outlines the best practices for testing tools within the SRE Assistant project. Adhering to these guidelines is crucial for ensuring the reliability, predictability, and maintainability of our agent ecosystem.

## Core Philosophy: Test Tools in Isolation

As per the official Google ADK guidelines, **tools must be tested locally and in isolation**. A tool is a self-contained unit of business logic. Its correctness should not depend on the LLM or the full agent workflow.

Unit tests for tools should focus on a single responsibility:
- Does the tool correctly process its inputs?
- Does it produce the expected outputs for successful cases?
- Does it handle errors and edge cases gracefully?
- Does it interact with external dependencies (like APIs or databases) as expected? (These dependencies should be **mocked**).

## How to Write a Tool Test

We use `pytest` as our testing framework and `pytest-asyncio` for asynchronous code. All tool tests should be placed in the `tests/` directory, mirroring the structure of the `src/` directory. For example, tests for tools in `src/sre_assistant/auth/tools.py` should be in `tests/test_auth_tools.py`.

### Example: Testing the `authenticate` Tool

Let's look at the test for our `authenticate` tool in `tests/test_tools.py`. This serves as a template for all future tool tests.

```python
# tests/test_tools.py

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from google.adk.agents.invocation_context import InvocationContext
from src.sre_assistant.auth.tools import authenticate

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


@patch('src.sre_assistant.auth.tools.AuthFactory')
@patch('src.sre_assistant.auth.tools.config_manager')
async def test_authenticate_success_and_cache(mock_config_manager, mock_auth_factory):
    """
    Tests that the authenticate tool successfully authenticates a user,
    returns the correct user info, and caches the result in the context.
    """
    # 1. Arrange: Set up all mocks and test data
    # Mock external dependencies to isolate the tool.
    mock_auth_config = MagicMock()
    mock_config_manager.get_auth_config.return_value = mock_auth_config

    mock_provider = AsyncMock()
    mock_provider.authenticate.return_value = (True, {'user_id': 'test-user'})
    mock_auth_factory.create.return_value = mock_provider

    # Create a clean InvocationContext for the test.
    ctx = InvocationContext()
    credentials = {'token': 'valid-token'}

    # 2. Act: Call the tool function with the test data.
    success, user_info = await authenticate(ctx, credentials)

    # 3. Assert: Verify the results.
    # Check the direct output of the tool.
    assert success is True
    assert user_info == {'user_id': 'test-user'}

    # Check that mocked dependencies were called as expected.
    mock_provider.authenticate.assert_called_once_with(credentials)

    # Check for side effects (e.g., changes to the context state).
    assert "user_info" in ctx.state
    assert any(key.startswith('user:auth_cache_') for key in ctx.state.keys())

    # You can even test more complex behavior, like caching.
    # Act again and assert that the mocked dependency was NOT called again.
    await authenticate(ctx, credentials)
    assert mock_provider.authenticate.call_count == 1
```

### Key Principles Illustrated

1.  **Use `@patch` Decorators**: The `@patch` decorator from `unittest.mock` is used to replace external dependencies (`AuthFactory`, `config_manager`) with mock objects. This is the most important step for isolating your tool.
2.  **Arrange, Act, Assert**: Structure your tests clearly using this pattern. It makes the test's purpose easy to understand.
3.  **Test One Thing**: Each test function should have a single, clear purpose. In the example, we test the success and caching path. A separate test should be written for authentication failure.
4.  **Mock Asynchronously**: When mocking asynchronous functions or methods, use `AsyncMock`.
5.  **Check Inputs, Outputs, and Side Effects**: A good test verifies three things:
    - **Outputs**: Are the return values correct?
    - **Dependency Calls**: Was the mocked dependency called with the correct arguments? (`.assert_called_once_with(...)`)
    - **Side Effects**: Did the tool modify the `InvocationContext` state as expected?

By following this template, we can build a robust suite of tests for our tools, which is the foundation of a reliable SRE Assistant.
