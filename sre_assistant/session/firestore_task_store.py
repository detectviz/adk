# sre_assistant/session/firestore_task_store.py
# 說明：此檔案提供了基於 Google Cloud Firestore 的 TaskStore/SessionService 持久化實現。
# 這取代了預設的 InMemoryTaskStore，使得會話和任務狀態能夠在應用程式重啟後依然存在。

from typing import Dict, Any, Optional
import os
from datetime import datetime, timezone

# 假設的 Task/Session 基礎模型
class Task:
    def __init__(self, task_id: str, data: Dict[str, Any]):
        self.task_id = task_id
        self.data = data
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "data": self.data,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(source: Dict[str, Any]) -> 'Task':
        task = Task(task_id=source['task_id'], data=source.get('data', {}))
        task.created_at = source.get('created_at', datetime.now(timezone.utc))
        task.updated_at = source.get('updated_at', datetime.now(timezone.utc))
        return task

class FirestoreTaskStore:
    """
    使用 Google Cloud Firestore 作為後端的 TaskStore。
    提供了獲取、保存和更新任務/會話狀態的持久化方法。
    """
    def __init__(self, project_id: str, collection: str = "sre_assistant_sessions", client: Optional[Any] = None):
        """
        初始化 FirestoreTaskStore，支援依賴注入以方便測試。

        Args:
            project_id (str): Google Cloud 專案 ID。
            collection (str, optional): 用於存儲會話的 Firestore 集合名稱。
            client (Any, optional): 一個預先存在的 Firestore AsyncClient 實例。如果提供，則使用此實例。
        """
        if client:
            self.db = client
        else:
            if not project_id:
                raise ValueError("project_id must be provided for FirestoreTaskStore if client is not.")
            try:
                from google.cloud import firestore
                self.db = firestore.AsyncClient(project=project_id)
            except ImportError:
                raise ImportError("google-cloud-firestore is not installed. Please install it to use FirestoreTaskStore.")

        self.collection = self.db.collection(collection)
        print(f"FirestoreTaskStore initialized for collection '{collection}'.")

    async def get(self, task_id: str) -> Optional[Task]:
        """
        根據 task_id 從 Firestore 中獲取一個任務。

        Args:
            task_id (str): 任務的唯一標識符。

        Returns:
            如果找到，則返回 Task 物件；否則返回 None。
        """
        doc_ref = self.collection.document(task_id)
        doc = await doc_ref.get()
        if doc.exists:
            return Task.from_dict(doc.to_dict())
        return None

    async def save(self, task: Task) -> None:
        """
        將一個新的任務保存到 Firestore 中。

        Args:
            task (Task): 要保存的任務物件。
        """
        task.updated_at = datetime.now(timezone.utc)
        await self.collection.document(task.task_id).set(task.to_dict())

    async def update(self, task_id: str, data: Dict[str, Any]) -> None:
        """
        更新 Firestore 中一個現有任務的數據。

        Args:
            task_id (str): 要更新的任務的 ID。
            data (Dict[str, Any]): 要更新的數據字段。
        """
        doc_ref = self.collection.document(task_id)
        update_data = {
            "data": data,
            "updated_at": datetime.now(timezone.utc)
        }
        await doc_ref.update(update_data)

    async def health_check(self) -> bool:
        """
        執行一個簡單的操作來檢查與 Firestore 的連接是否正常。
        """
        try:
            # 嘗試獲取一個不存在的文檔，這是一個輕量級的讀取操作。
            await self.collection.document("__health_check__").get()
            return True
        except Exception as e:
            print(f"Firestore health check failed: {e}")
            return False
