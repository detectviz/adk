# tests/test_citation.py
import pytest
import asyncio
from unittest.mock import AsyncMock
from typing import Any, List

# --- Mock ADK components to avoid real dependency ---
# The application code now imports from google.adk.runtime, but the test still needs
# placeholders for these classes so we don't need the real library to run the test.

class MockEvent:
    def __init__(self, role: str, content: Any, type: str = "result"):
        self.role = role
        self.content = content
        self.type = type

class MockInvocationContext:
    def __init__(self):
        self.history: List[MockEvent] = []

# --- End Mock ADK components ---

# We need to import the classes we are testing *after* defining the mocks.
# And we need to ensure the system can find the parent 'sre_assistant' package.
import sys
from pathlib import Path
# Add the project root to the path to allow for absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Now, we can import the code we want to test.
# The imports inside these files should now work because we installed the dependencies
# and fixed the import paths.
from sre_assistant.workflow import CitingParallelDiagnosticsAgent
from sre_assistant.sub_agents.diagnostic.agent import DiagnosticAgent


@pytest.mark.asyncio
async def test_citing_parallel_diagnostics_agent_formats_citations():
    """
    Tests that the CitingParallelDiagnosticsAgent correctly
    1. Runs its inner agent.
    2. Collects citation information from the context history.
    3. Appends a formatted citation block to the final result.
    """
    # 1. Setup
    citing_agent = CitingParallelDiagnosticsAgent(name="TestCitingAgent")
    inner_agent_mock = AsyncMock()

    final_result_event = MockEvent(
        role="assistant",
        content="Diagnosis: The database is slow."
    )
    inner_agent_mock.run_async.return_value = final_result_event
    citing_agent.parallel_diagnostics = inner_agent_mock

    # 2. Prepare Context
    context = MockInvocationContext()
    context.history.extend([
        MockEvent(role="assistant", content="Thinking..."),
        MockEvent(
            role="tool",
            content=('{"data": "..."}', {"type": "log", "source_name": "database-1", "timestamp": "2025-01-01T12:00:00Z"})
        ),
        MockEvent(role="assistant", content="Thinking more..."),
        MockEvent(
            role="tool",
            content=('{"data": "..."}', {"type": "config", "file_path": "/etc/db.conf", "key": "max_connections"})
        ),
    ])

    # 3. Execute
    await citing_agent._run_async_impl(context)

    # 4. Assert
    final_content = final_result_event.content

    assert final_content is not None
    assert "Diagnosis: The database is slow." in final_content
    assert "References:" in final_content
    assert "[Log] Source: database-1" in final_content
    assert "[Config] File: /etc/db.conf" in final_content
    assert "1. " in final_content
    assert "2. " in final_content

    print("\n--- Test Result ---")
    print(final_content)
    print("--- End Test Result ---")
