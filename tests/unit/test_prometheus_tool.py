import os
import datetime as dt
import pytest
import tenacity
from unittest.mock import MagicMock, call
import httpx

# Set a dummy PROM_URL for the tests
os.environ['PROM_URL'] = 'http://prometheus.local'

# Import the module to be tested
from agents.sre_assistant.tools import prometheus_tool as prom

# --- Fixtures ---

@pytest.fixture(autouse=True)
def clear_cache():
    """Fixture to automatically clear the cache before each test."""
    prom.cache.clear()
    yield

@pytest.fixture
def mock_httpx(monkeypatch):
    """Fixture to mock the httpx.Client."""
    mock_client_instance = MagicMock()
    # This mocks the `with httpx.Client(...) as client:` context manager
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.__exit__.return_value = None
    
    # We mock the class, so `httpx.Client()` returns our instance
    mock_client_class = MagicMock(return_value=mock_client_instance)
    monkeypatch.setattr(prom.httpx, "Client", mock_client_class)
    return mock_client_instance

# --- Test Cases ---

def test_query_success(mock_httpx):
    """Test a single successful query call."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success", "data": {}}
    mock_httpx.get.return_value = mock_response

    result = prom.query("up")

    assert result["status"] == "success"
    mock_httpx.get.assert_called_once()

# --- Caching Tests ---

def test_query_is_cached(mock_httpx):
    """Test that a repeated query call uses the cache."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success", "data": {"key": "value"}}
    mock_httpx.get.return_value = mock_response

    # Call the function twice with the same arguments
    result1 = prom.query("up", timeout=15)
    result2 = prom.query("up", timeout=15)

    # Assert that the result is the same
    assert result1 is result2
    # Assert that the underlying HTTP call was only made once
    mock_httpx.get.assert_called_once()

# --- Retry Tests ---

def test_retry_on_network_error(mock_httpx):
    """Test that the function retries on httpx.RequestError."""
    mock_success_response = MagicMock()
    mock_success_response.status_code = 200
    mock_success_response.json.return_value = {"status": "success"}
    
    # First call raises an error, second call succeeds
    mock_httpx.get.side_effect = [
        httpx.RequestError("Connection failed", request=None),
        mock_success_response
    ]

    result = prom.query("up")

    assert result["status"] == "success"
    assert mock_httpx.get.call_count == 2

def test_retry_on_5xx_error(mock_httpx):
    """Test that the function retries on a 503 Server Error."""
    mock_503_response = MagicMock()
    mock_503_response.status_code = 503
    mock_503_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Service Unavailable", request=None, response=mock_503_response
    )
    
    mock_success_response = MagicMock()
    mock_success_response.status_code = 200
    mock_success_response.json.return_value = {"status": "success"}

    mock_httpx.get.side_effect = [mock_503_response, mock_success_response]

    result = prom.query("up")

    assert result["status"] == "success"
    assert mock_httpx.get.call_count == 2

def test_no_retry_on_4xx_error(mock_httpx):
    """Test that the function does not retry on a 400 Client Error."""
    mock_400_response = MagicMock()
    mock_400_response.status_code = 400
    mock_400_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=None, response=mock_400_response
    )
    mock_httpx.get.return_value = mock_400_response

    with pytest.raises(httpx.HTTPStatusError):
        prom.query("invalid_query")

    # Should not retry, so call count is 1
    mock_httpx.get.assert_called_once()

def test_retry_fails_after_max_attempts(mock_httpx):
    """Test that the function gives up after all retry attempts fail."""
    # All attempts fail with a network error
    mock_httpx.get.side_effect = httpx.RequestError("Connection failed", request=None)

    with pytest.raises(tenacity.RetryError):
        prom.query("up")

    # Should be called 3 times (1 initial + 2 retries)
    assert mock_httpx.get.call_count == 3
