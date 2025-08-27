# tests/test_session.py
"""
此檔案包含對會話/任務存儲功能的單元測試。

主要測試對象：
1. `FirestoreTaskStore`: 驗證其與 Firestore 互動的邏輯是否正確（使用模擬）。
2. `get_task_store`: 驗證此工廠函式是否能根據配置返回正確的 TaskStore 實例。
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone

# --- 模組導入 ---
# 嘗試導入必要的模組。如果模組不存在（例如，因為功能尚未實現），
# 我們會優雅地將它們設置為 None，並在測試中使用 skipif 來跳過相關測試。
try:
    from sre_assistant.main import get_task_store, InMemoryTaskStore
    from sre_assistant.session.firestore_task_store import FirestoreTaskStore, Task
    from sre_assistant.config.config_manager import SREAssistantConfig, SessionBackend, config_manager
    import_error = None
except ImportError as e:
    get_task_store = None
    InMemoryTaskStore = None
    FirestoreTaskStore = None
    Task = None
    SREAssistantConfig = None
    SessionBackend = None
    config_manager = None
    import_error = e

# --- FirestoreTaskStore 測試 (使用依賴注入) ---

@pytest.mark.skipif(import_error is not None, reason=f"無法導入所需模組: {import_error}")
@pytest.fixture
def mock_firestore_client():
    """
    提供一個模擬的 Firestore AsyncClient。

    此 fixture 精確地模擬了真實客戶端的異步行為，
    使得我們可以在不實際連接到 Firestore 的情況下測試 `FirestoreTaskStore`。
    """
    mock_get_result = MagicMock()
    mock_get_result.exists = True
    mock_get_result.to_dict.return_value = {
        "task_id": "test-task-123",
        "data": {"key": "value"},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    mock_doc_ref = MagicMock()
    mock_doc_ref.get = AsyncMock(return_value=mock_get_result)
    mock_doc_ref.set = AsyncMock()
    mock_doc_ref.update = AsyncMock()
    mock_collection_ref = MagicMock()
    mock_collection_ref.document.return_value = mock_doc_ref
    mock_client = MagicMock()
    mock_client.collection.return_value = mock_collection_ref
    return mock_client

@pytest.mark.skipif(import_error is not None, reason=f"無法導入所需模組: {import_error}")
@pytest.mark.asyncio
async def test_firestore_task_store_get(mock_firestore_client):
    """
    測試目的：驗證 `FirestoreTaskStore.get` 方法。

    透過注入一個模擬的 Firestore 客戶端，我們測試 `get` 方法是否能
    正確地呼叫 Firestore API，並將返回的資料成功解析為 Task 物件。
    """
    store = FirestoreTaskStore(project_id="test-project", client=mock_firestore_client)
    task = await store.get("test-task-123")

    assert task is not None
    assert task.task_id == "test-task-123"
    assert task.data["key"] == "value"
    mock_firestore_client.collection.assert_called_with("sre_assistant_sessions")
    mock_firestore_client.collection.return_value.document.assert_called_with("test-task-123")
    mock_firestore_client.collection.return_value.document.return_value.get.assert_called_once()

@pytest.mark.skipif(import_error is not None, reason=f"無法導入所需模組: {import_error}")
@pytest.mark.asyncio
async def test_firestore_task_store_save(mock_firestore_client):
    """
    測試目的：驗證 `FirestoreTaskStore.save` 方法。

    透過注入一個模擬的 Firestore 客戶端，我們測試 `save` 方法是否能
    將一個 Task 物件正確地序列化，並呼叫 Firestore 的 `set` 方法來保存它。
    """
    store = FirestoreTaskStore(project_id="test-project", client=mock_firestore_client)
    new_task = Task(task_id="new-task-456", data={"new_key": "new_value"})

    await store.save(new_task)

    mock_set_method = mock_firestore_client.collection.return_value.document.return_value.set
    mock_set_method.assert_called_once()
    saved_data = mock_set_method.call_args[0][0]
    assert saved_data["task_id"] == "new-task-456"

# --- get_task_store 工廠函式測試 ---

@pytest.mark.skipif(import_error is not None, reason=f"無法導入所需模組: {import_error}")
def test_get_task_store_returns_in_memory():
    """
    測試目的：驗證當配置設定為 'in_memory' 時，
              `get_task_store` 工廠函式是否能正確返回 `InMemoryTaskStore` 的實例。
    """
    mock_config = MagicMock(spec=SREAssistantConfig)
    mock_config.session_backend = SessionBackend.IN_MEMORY

    with patch.object(config_manager, 'config', mock_config):
        task_store = get_task_store()

    assert isinstance(task_store, InMemoryTaskStore)

@pytest.mark.skipif(import_error is not None, reason=f"無法導入所需模組: {import_error}")
@patch('sre_assistant.session.firestore_task_store.FirestoreTaskStore')
def test_get_task_store_returns_firestore(MockFirestoreTaskStore):
    """
    測試目的：驗證當配置設定為 'firestore' 時，
              `get_task_store` 工廠函式是否能正確返回 `FirestoreTaskStore` 的實例，
              並使用正確的參數進行初始化。
    """
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
