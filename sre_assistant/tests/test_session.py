# sre_assistant/tests/test_session.py
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone

# Add the project root to the path to allow for absolute imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sre_assistant.session.firestore_task_store import FirestoreTaskStore, Task
from sre_assistant.config.config_manager import SREAssistantConfig, SessionBackend, config_manager
from sre_assistant import get_task_store, InMemoryTaskStore

# --- FirestoreTaskStore Tests (with Dependency Injection) ---

@pytest.fixture
def mock_firestore_client():
    """
    Provides a mock of the Firestore AsyncClient that correctly models the
    sync/async behavior of the real client.
    - .collection() and .document() are sync methods returning mocks.
    - .get() and .set() are async methods returning awaitables.
    """
    # 1. Mock the I/O-bound methods first (the end of the call chain)
    mock_get_result = MagicMock()
    mock_get_result.exists = True
    mock_get_result.to_dict.return_value = {
        "task_id": "test-task-123",
        "data": {"key": "value"},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    # 2. Mock the document reference object. Its methods are async.
    mock_doc_ref = MagicMock()
    mock_doc_ref.get = AsyncMock(return_value=mock_get_result)
    mock_doc_ref.set = AsyncMock()
    mock_doc_ref.update = AsyncMock()

    # 3. Mock the collection reference object. Its methods are sync.
    mock_collection_ref = MagicMock()
    mock_collection_ref.document.return_value = mock_doc_ref

    # 4. Mock the client object. Its methods are sync.
    mock_client = MagicMock()
    mock_client.collection.return_value = mock_collection_ref

    return mock_client

@pytest.mark.asyncio
async def test_firestore_task_store_get(mock_firestore_client):
    """Tests retrieving a task by injecting a mock client."""
    store = FirestoreTaskStore(project_id="test-project", client=mock_firestore_client)
    task = await store.get("test-task-123")

    assert task is not None
    assert task.task_id == "test-task-123"
    assert task.data["key"] == "value"
    mock_firestore_client.collection.assert_called_with("sre_assistant_sessions")
    mock_firestore_client.collection.return_value.document.assert_called_with("test-task-123")
    mock_firestore_client.collection.return_value.document.return_value.get.assert_called_once()

@pytest.mark.asyncio
async def test_firestore_task_store_save(mock_firestore_client):
    """Tests saving a task by injecting a mock client."""
    store = FirestoreTaskStore(project_id="test-project", client=mock_firestore_client)
    new_task = Task(task_id="new-task-456", data={"new_key": "new_value"})

    await store.save(new_task)

    mock_set_method = mock_firestore_client.collection.return_value.document.return_value.set
    mock_set_method.assert_called_once()
    saved_data = mock_set_method.call_args[0][0]
    assert saved_data["task_id"] == "new-task-456"

# --- get_task_store Factory Tests ---

def test_get_task_store_returns_in_memory():
    """Tests that the factory returns InMemoryTaskStore when config is set to in_memory."""
    mock_config = MagicMock(spec=SREAssistantConfig)
    mock_config.session_backend = SessionBackend.IN_MEMORY

    with patch.object(config_manager, 'config', mock_config):
        task_store = get_task_store()

    assert isinstance(task_store, InMemoryTaskStore)

@patch('sre_assistant.FirestoreTaskStore')
def test_get_task_store_returns_firestore(MockFirestoreTaskStore):
    """Tests that the factory returns FirestoreTaskStore when config is set to firestore."""
    mock_config = MagicMock(spec=SREAssistantConfig)
    mock_config.session_backend = SessionBackend.FIRESTORE
    mock_config.firestore_project_id = "test-project-from-config"
    mock_config.firestore_collection = "test_collection"

    with patch.object(config_manager, 'config', mock_config):
      task_store = get_task_store()

    MockFirestoreTaskStore.assert_called_once_with(
        project_id="test-project-from-config",
        collection="test_collection"
    )
    assert task_store == MockFirestoreTaskStore.return_value
