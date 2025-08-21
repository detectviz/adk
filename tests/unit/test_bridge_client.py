# -*- coding: utf-8 -*-
import asyncio
import json
import pytest
from unittest.mock import MagicMock, AsyncMock

from agents.sre_assistant.runtime.bridge_client import BridgeClient

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_subprocess(monkeypatch):
    """Fixture to mock asyncio.create_subprocess_exec."""
    mock = AsyncMock()
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock)

    # Configure the mock to return a mock process
    mock_process = AsyncMock()
    mock.return_value = mock_process

    # Set default stdout/stderr
    mock_process.communicate.return_value = (
        json.dumps({"status": "ok", "data": {"echo": True}}).encode(),
        b""
    )
    return mock, mock_process

async def test_bridge_client_success(mock_subprocess):
    """Test successful execution and parsing."""
    bc = BridgeClient(bin_path="/nonexistent")
    out = await bc.exec("diagnostic", "check_disk", "80")
    assert out["status"] == "ok"
    assert out["data"]["echo"] is True

@pytest.mark.parametrize("invalid_input", ["bad-name", "name with space", "name;-injection"])
async def test_bridge_client_invalid_input(invalid_input):
    """Test that invalid category or name raises ValueError."""
    bc = BridgeClient()
    with pytest.raises(ValueError, match="Invalid format"):
        await bc.exec("diagnostic", invalid_input)
    with pytest.raises(ValueError, match="Invalid format"):
        await bc.exec(invalid_input, "good_name")

async def test_bridge_client_exec_failure(mock_subprocess):
    """Test handling of a failed subprocess execution."""
    mock, mock_process = mock_subprocess
    mock_process.communicate.return_value = (b"", b"command not found")

    bc = BridgeClient()
    with pytest.raises(RuntimeError, match="bridge empty output: command not found"):
        await bc.exec("diagnostic", "check_disk")

async def test_bridge_client_non_json_output(mock_subprocess):
    """Test handling of non-JSON output from the bridge."""
    mock, mock_process = mock_subprocess
    mock_process.communicate.return_value = (b"this is not json", b"")

    bc = BridgeClient()
    with pytest.raises(RuntimeError, match="bridge non-json output: this is not json"):
        await bc.exec("diagnostic", "check_disk")
