# src/sre_assistant/session/backend_factory.py
"""
此檔案包含用於創建會話提供者 (Session Provider) 的工廠函式。

根據 `ARCHITECTURE.md` 的設計，系統的短期記憶體（會話狀態）管理
應透過 ADK 的 `session_service_builder` 擴展點實現。
此工廠將根據應用的配置 (`config.yaml`)，動態創建並返回一個
符合 ADK `SessionService` 協議的實例（例如 `DatabaseSessionService`
或 `InMemorySessionService`）。

"""

from google.adk.sessions import BaseSessionService, InMemorySessionService, DatabaseSessionService
from ..config.config_manager import config_manager, SessionBackend

class SessionFactory:
    """
    會話服務提供者的工廠類別。
    """

    @staticmethod
    def create() -> BaseSessionService:
        """
        根據應用程式配置，創建並返回一個會話服務實例。

        Raises:
            ValueError: 如果配置了不受支援的會話後端。

        Returns:
            BaseSessionService: 一個符合 ADK SessionService 協議的實例。
        """
        session_backend = config_manager.config.session_backend

        if session_backend == SessionBackend.POSTGRESQL:
            db_uri = config_manager.get_memory_config().postgres_connection_string
            if not db_uri:
                raise ValueError("PostgreSQL session backend requires a connection string.")
            print(f"Initializing PostgreSQL session backend with URI: {db_uri}")
            return DatabaseSessionService(db_uri=db_uri)

        elif session_backend == SessionBackend.IN_MEMORY:
            print("Initializing in-memory session backend.")
            return InMemorySessionService()

        # TODO: 在未來實現 FirestoreSessionService
        # elif session_backend == SessionBackend.FIRESTORE:
        #     project_id = config_manager.config.firestore_project_id
        #     if not project_id:
        #         raise ValueError("Firestore session backend requires a project_id.")
        #     return FirestoreSessionService(project_id=project_id)

        else:
            raise ValueError(f"Unsupported session backend: {session_backend}")

# 創建 SessionFactory 的單例，供整個應用程式導入和使用。
session_factory = SessionFactory()
